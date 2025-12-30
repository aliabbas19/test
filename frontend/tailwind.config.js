/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        arabic: ['Segoe UI', 'Tahoma', 'Arial', 'sans-serif'],
        messiri: ['El Messiri', 'sans-serif'],
      },
      keyframes: {
        animatedTextGradient: {
          '0%': { backgroundPosition: '0% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
        superheroGradient: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        superheroGlow: {
          'from': { boxShadow: '0 0 5px #ffc107, 0 0 10px #ffc107, 0 0 15px #ff4500' },
          'to': { boxShadow: '0 0 10px #ffc107, 0 0 20px #ff4500, 0 0 25px #ff4500' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'text-gradient': 'animatedTextGradient 5s linear infinite',
        'superhero-glow': 'superheroGlow 1.5s ease-in-out infinite alternate',
        'fade-in': 'fadeIn 0.5s ease-out',
        'bounce-slow': 'bounce 3s infinite',
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light"],
    darkTheme: "light",
    rtl: true,
  },
}

