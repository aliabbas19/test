// Default profile image - using reliable UI Avatars API
const DEFAULT_PROFILE_IMAGE = "https://ui-avatars.com/api/?name=User&background=6366f1&color=fff&size=200"


const ProfileImage = ({ src, alt = 'Profile', size = 'md', showBorder = true }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-24 h-24',
    xl: 'w-32 h-32'
  }

  // Use default image if src is empty, null, 'default.png', or fails to load
  const imageSrc = (!src || src === 'default.png' || src.endsWith('/default.png'))
    ? DEFAULT_PROFILE_IMAGE
    : src

  const borderClass = showBorder
    ? 'p-0.5 bg-gradient-to-br from-primary via-purple-500 to-green-400 rounded-full'
    : ''

  return (
    <div className={`avatar ${sizeClasses[size]} ${borderClass}`}>
      <div className="rounded-full bg-white">
        <img
          src={imageSrc}
          alt={alt}
          className="object-cover"
          onError={(e) => { e.target.src = DEFAULT_PROFILE_IMAGE }}
        />
      </div>
    </div>
  )
}

export default ProfileImage

