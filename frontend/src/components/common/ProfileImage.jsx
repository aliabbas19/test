const ProfileImage = ({ src, alt = 'Profile', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-24 h-24',
    xl: 'w-32 h-32'
  }

  return (
    <div className={`avatar ${sizeClasses[size]}`}>
      <div className="rounded-full">
        <img src={src || '/default.png'} alt={alt} />
      </div>
    </div>
  )
}

export default ProfileImage

