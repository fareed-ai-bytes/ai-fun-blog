import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';

// T-016 smoke: register → write → publish → a second user likes and comments.
const run = Date.now().toString(36);
const author = { username: `author_${run}`, email: `author_${run}@example.com` };
const reader = { username: `reader_${run}`, email: `reader_${run}@example.com` };
const title = `Smoke test post ${run}`;

async function register(page: Page, user: { username: string; email: string }) {
  await page.goto('/register');
  await page.getByLabel('Email', { exact: true }).fill(user.email);
  await page.getByLabel('Username').fill(user.username);
  await page.getByLabel('Display name').fill(user.username);
  await page.getByLabel('Password', { exact: true }).fill('smoke-test-password');
  await page.getByRole('button', { name: 'Sign up', exact: true }).click();
  await expect(page.getByTestId('header-username')).toHaveText(user.username);
}

test('author publishes, another user likes and comments', async ({ browser }) => {
  // Author: register, write, publish.
  const authorPage = await (await browser.newContext()).newPage();
  await register(authorPage, author);
  await authorPage.getByRole('link', { name: 'Write', exact: true }).click();
  await authorPage.getByLabel('Title', { exact: true }).fill(title);
  await authorPage.getByLabel('Body (Markdown)').fill('Hello from **Playwright**.');
  await authorPage.getByRole('button', { name: 'Publish', exact: true }).click();
  await expect(authorPage.getByRole('heading', { level: 1, name: title })).toBeVisible();
  // Own post: count only, no like button.
  await expect(authorPage.getByRole('button', { name: /like this post/i })).toHaveCount(0);
  const postUrl = authorPage.url();

  // The post is in the public feed.
  await authorPage.goto('/');
  await expect(authorPage.getByRole('link', { name: title })).toBeVisible();

  // Reader (separate cookie jar): like and comment.
  const readerPage = await (await browser.newContext()).newPage();
  await register(readerPage, reader);
  await readerPage.goto(postUrl);
  const like = readerPage.getByRole('button', { name: 'Like this post' });
  await like.click();
  await expect(readerPage.getByRole('button', { name: 'Unlike this post' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await expect(readerPage.getByTestId('like-count')).toHaveText('1');

  await readerPage.getByLabel('Add a comment').fill('Great smoke test!');
  await readerPage.getByRole('button', { name: 'Comment', exact: true }).click();
  await expect(readerPage.getByText('Great smoke test!')).toBeVisible();

  // The author sees the comment and may delete it (BR-07).
  await authorPage.goto(postUrl);
  await expect(authorPage.getByText('Great smoke test!')).toBeVisible();
  await expect(authorPage.getByRole('button', { name: 'Delete' })).toBeVisible();
});
