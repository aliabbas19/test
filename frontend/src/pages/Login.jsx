import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'فشل تسجيل الدخول')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="card w-96 bg-white shadow-xl border border-gray-200">
        <div className="card-body">
          <h2 className="card-title justify-center text-2xl mb-4 text-gray-800">تسجيل الدخول</h2>


          {error && (
            <div className="alert alert-error mb-4">
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-control mb-4">
              <label className="label">
                <span className="label-text text-gray-700 font-medium">اسم المستخدم</span>
              </label>
              <input
                type="text"
                className="input input-bordered bg-gray-50 text-gray-800 border-gray-300 focus:border-primary focus:bg-white"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="أدخل اسم المستخدم"
                required
              />
            </div>

            <div className="form-control mb-6">
              <label className="label">
                <span className="label-text text-gray-700 font-medium">كلمة المرور</span>
              </label>
              <input
                type="password"
                className="input input-bordered bg-gray-50 text-gray-800 border-gray-300 focus:border-primary focus:bg-white"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="أدخل كلمة المرور"
                required
              />
            </div>



            <button
              type="submit"
              className="btn btn-primary w-full text-white font-bold"
              disabled={loading}
            >
              {loading ? (
                <span className="loading loading-spinner"></span>
              ) : (
                'دخول'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login


