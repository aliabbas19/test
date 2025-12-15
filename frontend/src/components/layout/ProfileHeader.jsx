const ProfileHeader = () => {
    // Image URLs - Using external URLs (same as legacy app.py)
    // Can be changed to local paths like "/images/classroom.jpg" when images are deployed
    const coverImageUrl = "https://i.ibb.co/RkWC7YZm/photo-2025-10-22-12-53-24.jpg";
    const profileImageUrl = "https://i.postimg.cc/3RnCZ8Wy/1447-04-22-10-34-02-7d49049c.jpg";

    return (
        <div className="mb-8">
            {/* Cover Image with Frame */}
            <div className="relative mb-20">
                <div className="h-[200px] lg:h-[300px] rounded-2xl overflow-hidden shadow-xl border-4 border-transparent bg-gradient-to-br from-primary via-purple-500 to-green-400 p-1">
                    <div className="h-full w-full rounded-xl overflow-hidden bg-slate-800/50">
                        <img
                            src={coverImageUrl}
                            alt="صورة الغلاف - الأستاذ مع الطلاب"
                            className="w-full h-full object-contain"
                        />
                    </div>
                </div>

                {/* Profile Picture with Circular Gradient Frame */}
                <div className="absolute -bottom-16 right-8 lg:right-12">
                    <div className="w-32 h-32 lg:w-40 lg:h-40 rounded-full p-1 bg-gradient-to-br from-primary via-purple-500 to-green-400 shadow-2xl animate-superhero-glow">
                        <img
                            src={profileImageUrl}
                            alt="صورة الأستاذ بسام الجنابي"
                            className="w-full h-full object-cover rounded-full border-4 border-white"
                        />
                    </div>
                </div>
            </div>

            {/* Header Title Container */}
            <div className="text-center p-4 bg-white/70 backdrop-blur-sm rounded-xl mb-4">
                <div className="ship-frame text-4xl lg:text-5xl lg:px-8 lg:py-6 border-image-gradient-purple">
                    <span className="animate-text-gradient bg-gradient-to-r from-primary via-purple-600 to-green-400 bg-[length:200%_auto] bg-clip-text text-transparent">
                        منصة
                    </span>
                </div>
                <div className="ship-frame text-2xl lg:text-3xl border-image-gradient-blue mt-4">
                    <span className="animate-text-gradient bg-gradient-to-r from-green-400 via-primary to-green-400 bg-[length:200%_auto] bg-clip-text text-transparent">
                        <i className="fa-solid fa-crown text-yellow-500 ml-2 animate-pulse"></i>
                        الاستاذ بسام الجنابي مادة الحاسوب
                    </span>
                </div>
            </div>
        </div>
    );
};

export default ProfileHeader;

