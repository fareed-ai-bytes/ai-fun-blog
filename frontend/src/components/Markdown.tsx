import ReactMarkdown from 'react-markdown';

interface MdNode {
  type: string;
  value?: unknown;
  children?: MdNode[];
}

/** remark plugin: raw HTML in a post becomes literal text, so `<script>` is shown, never run.
 *  (react-markdown would otherwise drop it silently; rehype-raw is banned by rules.md.) */
export function remarkHtmlAsText() {
  const walk = (node: MdNode) => {
    if (node.type === 'html') node.type = 'text';
    node.children?.forEach(walk);
  };
  return (tree: MdNode) => walk(tree);
}

const ALLOWED_PROTOCOL = /^(https?:|mailto:|\/|#)/i;

/** Safe Markdown rendering for post bodies (no raw HTML, no javascript: URLs). */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="article-body">
      <ReactMarkdown
        remarkPlugins={[remarkHtmlAsText]}
        urlTransform={(url) => (ALLOWED_PROTOCOL.test(url) ? url : '')}
        components={{
          a: ({ href, children: label }) => (
            <a href={href} rel="noopener noreferrer nofollow">
              {label}
            </a>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
