import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const ProtectedRoute = ({ children, requireProfileComplete = false }) => {
  const { isAuthenticated, loading, user } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  // Check profile completion for students
  if (requireProfileComplete && user?.role === 'student') {
    if (!user.is_profile_complete) {
      return <Navigate to="/complete-profile" replace />
    }
  }

  return children
}

export default ProtectedRoute

