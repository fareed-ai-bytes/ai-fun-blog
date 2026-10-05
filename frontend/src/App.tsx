import { Route, Routes } from 'react-router';

import { Layout } from './components/Layout';
import { ComingSoonPage } from './pages/ComingSoonPage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { RegisterPage } from './pages/RegisterPage';

// Every route from docs/design.md (v1 screens).
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ComingSoonPage title="Feed" />} />
        <Route path="p/:slug" element={<ComingSoonPage title="Post" />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="me/posts" element={<ComingSoonPage title="My posts" />} />
        <Route path="write" element={<ComingSoonPage title="Write" />} />
        <Route path="edit/:slug" element={<ComingSoonPage title="Edit" />} />
        <Route path="u/:username" element={<ComingSoonPage title="Author" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
