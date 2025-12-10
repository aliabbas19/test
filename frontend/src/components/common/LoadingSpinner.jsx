const LoadingSpinner = ({ size = 'lg' }) => {
  return (
    <div className="flex justify-center items-center">
      <span className={`loading loading-spinner loading-${size}`}></span>
    </div>
  )
}

export default LoadingSpinner

