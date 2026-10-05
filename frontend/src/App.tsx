import { Route, Routes } from 'react-router';

import { Layout } from './components/Layout';
import { RequireAuth } from './features/auth/RequireAuth';
import { ComingSoonPage } from './pages/ComingSoonPage';
import { EditPage, WritePage } from './pages/EditorPage';
import { FeedPage } from './pages/FeedPage';
import { LoginPage } from './pages/LoginPage';
import { MyPostsPage } from './pages/MyPostsPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { PostPage } from './pages/PostPage';
import { RegisterPage } from './pages/RegisterPage';

// Every route from docs/design.md (v1 screens).
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<FeedPage />} />
        <Route path="p/:slug" element={<PostPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route
          path="me/posts"
          element={
            <RequireAuth>
              <MyPostsPage />
            </RequireAuth>
          }
        />
        <Route
          path="write"
          element={
            <RequireAuth>
              <WritePage />
            </RequireAuth>
          }
        />
        <Route
          path="edit/:slug"
          element={
            <RequireAuth>
              <EditPage />
            </RequireAuth>
          }
        />
        <Route path="u/:username" element={<ComingSoonPage title="Author" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
