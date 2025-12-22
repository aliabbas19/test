import { useState, useEffect } from 'react'

const ImageSlider = () => {
    const [currentIndex, setCurrentIndex] = useState(0)

    const slides = [
        {
            id: 1,
            title: "وحدة المعالجة المركزية (CPU)",
            description: "العقل المدبر للحاسوب، المسؤولة عن تنفيذ التعليمات ومعالجة البيانات بسرعة فائقة.",
            icon: "fa-solid fa-microchip",
            color: "from-blue-600 to-cyan-400",
            bgPattern: "opacity-10"
        },
        {
            id: 2,
            title: "ذاكرة الوصول العشوائي (RAM)",
            description: "الذاكرة المؤقتة التي تخزن البيانات قيد الاستخدام لتسريع الوصول إليها.",
            icon: "fa-solid fa-memory",
            color: "from-purple-600 to-pink-400",
            bgPattern: "opacity-10"
        },
        {
            id: 3,
            title: "وحدة معالجة الرسوميات (GPU)",
            description: "المسؤولة عن معالجة الصور والفيديوهات والالعاب بدقة عالية.",
            icon: "fa-solid fa-gamepad", // Or fa-display if available, gamepad is good for GPU association
            color: "from-green-600 to-emerald-400",
            bgPattern: "opacity-10"
        },
        {
            id: 4,
            title: "الذكاء الاصطناعي (AI)",
            description: "محاكاة الذكاء البشري في الآلات لتسهيل حياتنا وحل المشكلات المعقدة.",
            icon: "fa-solid fa-robot",
            color: "from-orange-500 to-yellow-400",
            bgPattern: "opacity-10"
        }
    ]

    // Auto slide
    useEffect(() => {
        const interval = setInterval(() => {
            nextSlide()
        }, 5000)
        return () => clearInterval(interval)
    }, [currentIndex])

    const nextSlide = () => {
        setCurrentIndex((prev) => (prev + 1) % slides.length)
    }

    const prevSlide = () => {
        setCurrentIndex((prev) => (prev - 1 + slides.length) % slides.length)
    }

    return (
        <div className="relative w-full max-w-5xl mx-auto h-[280px] md:h-[400px] rounded-3xl overflow-hidden shadow-2xl my-8 group border border-white/20" dir="rtl">

            {/* Slides */}
            {slides.map((slide, index) => (
                <div
                    key={slide.id}
                    className={`absolute inset-0 transition-opacity duration-700 ease-in-out ${index === currentIndex ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}
                >
                    {/* Background with Rich Gradient */}
                    <div className={`w-full h-full bg-gradient-to-br ${slide.color} relative overflow-hidden flex items-center justify-center`}>

                        {/* Animated Background Shapes */}
                        <div className="absolute inset-0 overflow-hidden">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 animate-pulse"></div>
                            <div className="absolute bottom-0 left-0 w-96 h-96 bg-black/10 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3"></div>
                        </div>

                        {/* Glassmorphism Content Card */}
                        <div className="relative z-20 flex flex-col md:flex-row items-center justify-center gap-6 md:gap-12 px-6 md:px-12 w-full max-w-4xl">

                            {/* Icon Container with Glow */}
                            <div className="relative shrink-0">
                                <div className="absolute inset-0 bg-white/30 blur-2xl rounded-full scale-110"></div>
                                <div className="relative w-24 h-24 md:w-32 md:h-32 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 flex items-center justify-center shadow-lg transform transition-transform hover:scale-105 duration-500">
                                    <i className={`${slide.icon} text-5xl md:text-7xl text-white drop-shadow-lg`}></i>
                                </div>
                            </div>

                            {/* Text Content */}
                            <div className="text-center md:text-right text-white max-w-lg">
                                <h2 className="text-3xl md:text-5xl font-bold mb-3 drop-shadow-md tracking-tight">{slide.title}</h2>
                                <p className="text-lg md:text-xl text-white/90 leading-relaxed font-light hidden md:block border-r-4 border-white/30 pr-4 mt-4">
                                    {slide.description}
                                </p>
                                {/* Mobile Short Desc */}
                                <p className="text-sm text-white/90 leading-relaxed font-light md:hidden mt-2">
                                    {slide.description}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            ))}

            {/* Navigation Arrows - Glass Style */}
            <button
                onClick={nextSlide}
                className="absolute right-4 top-1/2 -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white flex items-center justify-center hover:bg-white/20 transition-all cursor-pointer group-hover:scale-100 scale-0 md:scale-100"
            >
                <i className="fa-solid fa-chevron-right text-xl"></i>
            </button>
            <button
                onClick={prevSlide}
                className="absolute left-4 top-1/2 -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white flex items-center justify-center hover:bg-white/20 transition-all cursor-pointer group-hover:scale-100 scale-0 md:scale-100"
            >
                <i className="fa-solid fa-chevron-left text-xl"></i>
            </button>

            {/* Pagination Indicators */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-30 flex space-x-2 space-x-reverse bg-black/20 backdrop-blur-sm px-4 py-2 rounded-full border border-white/10">
                {slides.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => setCurrentIndex(index)}
                        className={`transition-all duration-300 rounded-full h-2 ${index === currentIndex ? 'bg-white w-8' : 'bg-white/40 w-2 hover:bg-white/60'}`}
                    ></button>
                ))}
            </div>
        </div>
    )
}

export default ImageSlider
