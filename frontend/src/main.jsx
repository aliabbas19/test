import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Version Check Log
console.log('%c APP VERSION: NUCLEAR_FIX_V2 (HTTPS FORCED) ', 'background: #222; color: #bada55; font-size: 20px');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

