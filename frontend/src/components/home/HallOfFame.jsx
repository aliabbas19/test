
import { useState, useEffect } from 'react'
import api from '../../services/api'

const HallOfFame = () => {
    const [heroes, setHeroes] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchHeroes = async () => {
            try {
                const response = await api.get('/api/heroes')
                setHeroes(response.data)
            } catch (error) {
                console.error("Failed to fetch heroes:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchHeroes()
    }, [])

    if (loading || heroes.length === 0) return null

    const superheroes = heroes.filter(h => h.rank_type === 'superhero')
    const weeklyHeroes = heroes.filter(h => h.rank_type === 'hero')

    return (
        <div className="mb-12 space-y-8 animate-fade-in">

            {/* Superheroes Section - The Champions */}
            {superheroes.length > 0 && (
                <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/20 to-amber-500/20 blur-xl rounded-full opacity-50"></div>
                    <div className="relative bg-white/80 backdrop-blur-sm border-2 border-amber-400 rounded-2xl p-6 shadow-xl overflow-hidden">
                        {/* Header */}
                        <div className="text-center mb-8 relative z-10">
                            <div className="inline-block p-3 rounded-full bg-gradient-to-br from-amber-300 to-yellow-500 shadow-lg mb-3">
                                <i className="fa-solid fa-crown text-3xl text-white animate-bounce-slow"></i>
                            </div>
                            <h2 className="text-3xl lg:text-4xl font-black text-amber-600 drop-shadow-sm font-messiri">
                                أبـطـال الـشـهـر
                            </h2>
                            <p className="text-amber-700/80 font-bold mt-2">النخبة المتميزة (10 نجمات فأكثر)</p>
                        </div>

                        {/* Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-center">
                            {superheroes.map((hero) => (
                                <div key={hero.user_id} className="relative group perspective-1000">
                                    <div className="absolute -inset-1 bg-gradient-to-r from-yellow-400 via-amber-500 to-yellow-400 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-500"></div>
                                    <div className="relative bg-white rounded-xl p-4 border border-amber-200 shadow-lg transform transition duration-300 group-hover:-translate-y-1">
                                        <div className="flex items-center gap-4">
                                            {/* Avatar with Gold Ring */}
                                            <div className="relative">
                                                <div className="w-20 h-20 rounded-full p-1 bg-gradient-to-tr from-yellow-300 via-amber-500 to-yellow-300">
                                                    <img
                                                        src={hero.profile_image ? `${import.meta.env.VITE_API_URL || ''}/data/uploads/${hero.profile_image}` : '/default.png'}
                                                        alt={hero.full_name}
                                                        className="w-full h-full rounded-full object-cover border-2 border-white"
                                                    />
                                                </div>
                                                <div className="absolute -bottom-2 -right-2 bg-amber-500 text-white text-xs font-bold px-2 py-0.5 rounded-full border-2 border-white shadow-sm">
                                                    {hero.banked_stars} <i className="fa-solid fa-star text-yellow-200 text-[10px]"></i>
                                                </div>
                                            </div>

                                            {/* Info */}
                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-bold text-lg text-gray-800 truncate mb-1">
                                                    {hero.full_name}
                                                </h3>
                                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                                    <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-md border border-amber-200 truncate max-w-[120px]">
                                                        {hero.class_name || 'طالب نجيب'}
                                                    </span>
                                                </div>
                                            </div>

                                            <div className="absolute top-2 left-3 text-amber-400 opacity-20 group-hover:opacity-100 transition-opacity">
                                                <i className="fa-solid fa-trophy text-2xl"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Heroes Section - Stars of the Week */}
            {weeklyHeroes.length > 0 && (
                <div className="bg-white rounded-xl shadow-md border border-indigo-100 p-6">
                    <div className="flex items-center gap-3 mb-6 border-b border-indigo-50 pb-4">
                        <div className="bg-indigo-100 p-2 rounded-lg">
                            <i className="fa-solid fa-medal text-2xl text-indigo-600"></i>
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-800">أبطال الأسبوع</h3>
                            <p className="text-xs text-gray-500">المتميزون (4 نجمات فأكثر)</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {weeklyHeroes.map((hero) => (
                            <div key={hero.user_id} className="text-center group">
                                <div className="relative inline-block mb-2">
                                    <div className="w-16 h-16 rounded-full p-0.5 bg-gradient-to-tr from-indigo-400 to-purple-400 group-hover:scale-105 transition-transform duration-300">
                                        <img
                                            src={hero.profile_image ? `${import.meta.env.VITE_API_URL || ''}/data/uploads/${hero.profile_image}` : '/default.png'}
                                            alt={hero.full_name}
                                            className="w-full h-full rounded-full object-cover border-2 border-white"
                                        />
                                    </div>
                                    <div className="absolute -top-1 -right-1 bg-white rounded-full p-1 shadow-md border border-gray-100">
                                        <i className="fa-solid fa-face-smile text-yellow-400 text-sm"></i>
                                    </div>
                                </div>
                                <h4 className="text-sm font-bold text-gray-700 truncate w-full px-1">{hero.full_name}</h4>
                                <div className="inline-flex items-center gap-1 bg-indigo-50 px-2 py-0.5 rounded-full mt-1">
                                    <span className="text-xs font-bold text-indigo-600">{hero.banked_stars}</span>
                                    <i className="fa-solid fa-star text-[10px] text-indigo-400"></i>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </div>
    )
}

export default HallOfFame
