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
        <div className="relative w-full max-w-5xl mx-auto h-[250px] md:h-[350px] rounded-2xl overflow-hidden shadow-2xl my-6 group" dir="rtl">

            {/* Slides */}
            <div
                className="w-full h-full duration-500 ease-out transition-transform"
                style={{ transform: `translateX(${currentIndex * 100}%)` }} // Helper for RTL sliding logic usually needs testing, but for full width single slide simple replacement is easier. 
            // Actually simple translateX might be tricky with RTL. Let's strictly render the active slide with animation/fade instead for simplicity and robustness in RTL.
            >
                {/* Easier approach: Render all, translate. For RTL, translateX needs to be positive or logic inverted. 
                   Let's use a simple Fade/block approach or relative positioning.
               */}
            </div>

            {/* Better Implementation: Map and Absolute positioning */}
            {slides.map((slide, index) => (
                <div
                    key={slide.id}
                    className={`absolute top-0 left-0 w-full h-full transition-opacity duration-700 ease-in-out ${index === currentIndex ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}
                >
                    {/* Background Gradient */}
                    <div className={`w-full h-full bg-gradient-to-br ${slide.color} relative overflow-hidden flex items-center justify-center`}>

                        {/* Decorative Background Pattern */}
                        <div className={`absolute inset-0 ${slide.bgPattern} grid grid-cols-6 gap-2 rotate-12 scale-150`}>
                            {[...Array(20)].map((_, i) => (
                                <div key={i} className="w-8 h-8 border border-white rounded-full opacity-20 transform rotate-45"></div>
                            ))}
                        </div>

                        {/* Content */}
                        <div className="relative z-20 text-center text-white px-4 md:px-12 max-w-3xl">
                            <div className="mb-4 transform transition-all duration-700 translate-y-0">
                                <i className={`${slide.icon} text-6xl md:text-8xl drop-shadow-lg animate-bounce-slow`}></i>
                            </div>
                            <h2 className="text-3xl md:text-5xl font-bold mb-3 drop-shadow-md">{slide.title}</h2>
                            <p className="text-lg md:text-xl opacity-90 leading-relaxed max-w-xl mx-auto hidden md:block">{slide.description}</p>
                            {/* Mobile short desc if needed */}
                            <p className="text-sm opacity-90 leading-relaxed max-w-xl mx-auto md:hidden line-clamp-2">{slide.description}</p>
                        </div>
                    </div>
                </div>
            ))}

            {/* Navigation Arrows */}
            <button
                onClick={prevSlide}
                className="absolute right-4 top-1/2 -translate-y-1/2 z-30 p-2 rounded-full bg-black/30 text-white hover:bg-black/50 transition-all cursor-pointer group-hover:block hidden md:block"
            >
                <i className="fa-solid fa-chevron-right text-2xl"></i>
            </button>
            <button
                onClick={nextSlide}
                className="absolute left-4 top-1/2 -translate-y-1/2 z-30 p-2 rounded-full bg-black/30 text-white hover:bg-black/50 transition-all cursor-pointer group-hover:block hidden md:block"
            >
                <i className="fa-solid fa-chevron-left text-2xl"></i>
            </button>

            {/* Dot Indicators */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-30 flex space-x-2 space-x-reverse">
                {slides.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => setCurrentIndex(index)}
                        className={`w-3 h-3 rounded-full transition-all duration-300 ${index === currentIndex ? 'bg-white w-8' : 'bg-white/50 hover:bg-white/80'}`}
                    ></button>
                ))}
            </div>
        </div>
    )
}

export default ImageSlider
