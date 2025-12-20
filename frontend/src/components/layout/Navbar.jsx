import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="navbar bg-base-100 shadow-md">
      <div className="flex-1">
        <h2 className={`text-xl font-bold ${user?.role === 'admin' ? 'admin-username-gradient' : ''}`}>
          مرحباً، {user?.role === 'admin' && (
            <i className="fa-solid fa-crown admin-crown-icon"></i>
          )}
          {user?.full_name || user?.username}
        </h2>
      </div>
      <div className="flex-none gap-2">
        <div className="dropdown dropdown-end">
          <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
            <div className="w-10 rounded-full">
              <img
                src={user?.profile_image || '/default.png'}
                alt="Profile"
              />
            </div>
          </label>
          <ul
            tabIndex={0}
            className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
          >
            <li>
              <a onClick={() => navigate(`/profile/${user?.username}`)}>
                الملف الشخصي
              </a>
            </li>
            <li>
              <a onClick={handleLogout}>تسجيل الخروج</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Navbar

