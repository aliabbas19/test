import { useEffect, useRef } from 'react'

const FocusTrap = ({ children, isActive }) => {
    const rootRef = useRef(null)

    useEffect(() => {
        if (!isActive) return

        const focusableElementsString = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]'
        const root = rootRef.current
        let focusableElements = root.querySelectorAll(focusableElementsString)
        focusableElements = Array.prototype.slice.call(focusableElements)

        const firstTabStop = focusableElements[0]
        const lastTabStop = focusableElements[focusableElements.length - 1]

        // Focus first element on mount
        if (firstTabStop) {
            firstTabStop.focus()
        }

        const handleTabKey = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstTabStop) {
                        e.preventDefault()
                        lastTabStop.focus()
                    }
                } else {
                    if (document.activeElement === lastTabStop) {
                        e.preventDefault()
                        firstTabStop.focus()
                    }
                }
            }
            // Close on Escape
            if (e.key === 'Escape') {
                // Optional: Trigger close handler if passed
            }
        }

        root.addEventListener('keydown', handleTabKey)
        return () => root.removeEventListener('keydown', handleTabKey)
    }, [isActive])

    return <div ref={rootRef}>{children}</div>
}

export default FocusTrap
