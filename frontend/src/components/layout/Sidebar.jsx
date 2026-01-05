import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const Sidebar = () => {
  const location = useLocation()
  const { isAdmin } = useAuth()

  const menuItems = [
    { path: '/', label: 'الصفحة الرئيسية', icon: '🏠' },
    { path: '/archive', label: 'الأرشيف', icon: '📦' },
    { path: '/students', label: 'الطلاب', icon: '👥' },
    { path: '/conversations', label: 'المحادثات', icon: '💬' },
    ...(isAdmin ? [
      { path: '/admin', label: 'لوحة التحكم', icon: '⚙️' },
      { path: '/reports', label: 'التقارير', icon: '📊' }
    ] : []),
  ]

  return (
    <div className="w-64 bg-base-100 shadow-lg">
      <div className="p-4">
        <h1 className="text-xl font-bold text-center mb-4">منصة الأستاذ بسام</h1>
        <ul className="menu menu-vertical">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                <span className="text-2xl ml-3">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default Sidebar

