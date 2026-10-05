import { Route, Routes } from 'react-router';

import { Layout } from './components/Layout';
import { ComingSoonPage } from './pages/ComingSoonPage';
import { NotFoundPage } from './pages/NotFoundPage';

// Every route from docs/design.md (v1 screens).
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ComingSoonPage title="Feed" />} />
        <Route path="p/:slug" element={<ComingSoonPage title="Post" />} />
        <Route path="login" element={<ComingSoonPage title="Log in" />} />
        <Route path="register" element={<ComingSoonPage title="Sign up" />} />
        <Route path="me/posts" element={<ComingSoonPage title="My posts" />} />
        <Route path="write" element={<ComingSoonPage title="Write" />} />
        <Route path="edit/:slug" element={<ComingSoonPage title="Edit" />} />
        <Route path="u/:username" element={<ComingSoonPage title="Author" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
