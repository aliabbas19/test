import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Home from './pages/Home'
import Archive from './pages/Archive'
import Profile from './pages/Profile'
import Students from './pages/Students'
import Conversations from './pages/Conversations'
import AdminDashboard from './pages/AdminDashboard'
import Reports from './pages/Reports'
import VideoReview from './pages/VideoReview'
import CompleteProfile from './pages/CompleteProfile'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/complete-profile"
            element={
              <ProtectedRoute>
                <CompleteProfile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute requireProfileComplete={true}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Home />} />
            <Route path="archive" element={<Archive />} />
            <Route path="profile/:username" element={<Profile />} />
            <Route path="conversations" element={<Conversations />} />

            {/* Admin Routes */}
            <Route element={<ProtectedRoute requiredRole="admin"><Outlet /></ProtectedRoute>}>
              <Route path="admin/dashboard" element={<AdminDashboard />} />
              <Route path="admin/videos" element={<VideoReview />} />
              <Route path="admin/students" element={<Students />} />
              <Route path="admin/reports" element={<Reports />} />
            </Route>

            {/* Redirect legacy/root admin paths */}
            <Route path="admin" element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="students" element={<Navigate to="/admin/students" replace />} />
            <Route path="reports" element={<Navigate to="/admin/reports" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App

