import { Outlet } from 'react-router-dom'
import CircularNav from './CircularNav'
import ProfileHeader from './ProfileHeader'

const Layout = () => {
  return (
    <div className="min-h-screen relative">
      <CircularNav />
      <div className="w-full lg:ml-[120px] p-4 lg:p-8 pb-32 lg:pb-8 transition-all duration-300">
        <ProfileHeader />
        <main className="min-h-[80vh]">
          <Outlet />
        </main>

        <footer className="mt-12 text-center p-4 bg-white/90 backdrop-blur-md border-t border-primary/20 rounded-t-xl mx-auto max-w-4xl">
          <span className="inline-block px-4 py-2 bg-primary/10 rounded-full border border-primary/30 font-medium text-gray-700">
            Powered by <span className="font-bold text-primary">Iraq Tech</span> {new Date().getFullYear()} <i className="fa-solid fa-copyright text-primary ml-1"></i>
          </span>
        </footer>
      </div>
    </div>
  )
}

export default Layout

