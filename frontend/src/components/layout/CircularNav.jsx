import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const CircularNav = () => {
    const { user, logout } = useAuth();

    // Helper for active link styles
    const getLinkClass = ({ isActive }) => {
        const common = "flex flex-col justify-center items-center w-16 h-16 lg:w-24 lg:h-20 rounded-xl border-2 border-primary transition-all duration-300 hover:scale-105 hover:shadow-[0_0_15px_rgba(13,110,253,0.5)] relative shrink-0 mx-2 lg:mx-0 lg:my-4";
        const inactiveState = "bg-white text-primary hover:bg-primary hover:text-white";
        const activeState = "bg-primary text-white scale-105 shadow-[0_0_15px_rgba(13,110,253,0.5)]";

        return `${common} ${isActive ? activeState : inactiveState}`;
    };

    return (
        <nav className="
            flex lg:flex-col items-center justify-start lg:justify-center
            fixed lg:top-0 lg:right-0 
            w-full lg:w-[100px] 
            h-auto lg:h-screen 
            z-50
            bg-white/95 backdrop-blur-md 
            border-t lg:border-t-0 lg:border-r border-white/20 shadow-lg
            bottom-0 lg:bottom-auto
            overflow-x-auto lg:overflow-x-visible lg:overflow-y-auto
            py-2 lg:py-10 px-4 lg:px-2
            no-scrollbar
        ">
            <ul className="flex lg:flex-col items-center gap-2 lg:gap-0 w-max lg:w-full p-0 m-0 list-none">
                <li>
                    <NavLink to="/" className={getLinkClass} title="الرئيسية">
                        <i className="fa-solid fa-house text-xl mb-1"></i>
                        <span className="text-[10px] font-bold">الرئيسية</span>
                    </NavLink>
                </li>

                {user ? (
                    <>
                        <li>
                            <NavLink to={`/profile/${user.username}`} className={getLinkClass} title="ملفي">
                                <i className="fa-solid fa-user text-xl mb-1"></i>
                                <span className="text-[10px] font-bold">ملفي</span>
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/archive" className={getLinkClass} title="الأرشيف">
                                <i className="fa-solid fa-box-archive text-xl mb-1"></i>
                                <span className="text-[10px] font-bold">الأرشيف</span>
                            </NavLink>
                        </li>

                        {user.role === 'student' && (
                            <li>
                                <NavLink to="/conversations" className={getLinkClass} title="الرسائل">
                                    <i className="fa-solid fa-envelope text-xl mb-1"></i>
                                    <span className="text-[10px] font-bold">الرسائل</span>
                                </NavLink>
                            </li>
                        )}

                        {user.role === 'admin' && (
                            <>
                                <li>
                                    <NavLink to="/admin/dashboard" className={getLinkClass} title="التحكم">
                                        <i className="fa-solid fa-gauge text-xl mb-1"></i>
                                        <span className="text-[10px] font-bold">التحكم</span>
                                    </NavLink>
                                </li>
                                <li>
                                    <NavLink to="/conversations" className={getLinkClass} title="الرسائل">
                                        <i className="fa-solid fa-envelope text-xl mb-1"></i>
                                        <span className="text-[10px] font-bold">الرسائل</span>
                                    </NavLink>
                                </li>
                                <li>
                                    <NavLink to="/admin/videos" className={getLinkClass} title="مراجعة الفيديو">
                                        <i className="fa-solid fa-video text-xl mb-1"></i>
                                        <span className="text-[10px] font-bold">مراجعة</span>
                                    </NavLink>
                                </li>
                                <li>
                                    <NavLink to="/admin/reports" className={getLinkClass} title="التقارير">
                                        <i className="fa-solid fa-chart-line text-xl mb-1"></i>
                                        <span className="text-[10px] font-bold">التقارير</span>
                                    </NavLink>
                                </li>
                                <li>
                                    <NavLink to="/admin/students" className={getLinkClass} title="الطلاب">
                                        <i className="fa-solid fa-users text-xl mb-1"></i>
                                        <span className="text-[10px] font-bold">الطلاب</span>
                                    </NavLink>
                                </li>
                            </>
                        )}

                        <li>
                            <button onClick={logout} className="flex flex-col justify-center items-center w-16 h-16 lg:w-24 lg:h-20 rounded-xl border-2 border-red-500 bg-white text-red-500 transition-all duration-300 hover:bg-red-500 hover:text-white hover:scale-105 hover:shadow-lg relative shrink-0 mx-2 lg:mx-0 lg:my-4" title="تسجيل الخروج">
                                <i className="fa-solid fa-right-from-bracket text-xl mb-1"></i>
                                <span className="text-[10px] font-bold">خروج</span>
                            </button>
                        </li>
                    </>
                ) : (
                    <li>
                        <NavLink to="/login" className={getLinkClass} title="تسجيل الدخول">
                            <i className="fa-solid fa-right-to-bracket text-xl mb-1"></i>
                            <span className="text-[10px] font-bold">دخول</span>
                        </NavLink>
                    </li>
                )}
            </ul>
        </nav>
    );
};

export default CircularNav;
