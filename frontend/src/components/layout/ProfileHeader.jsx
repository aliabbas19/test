const ProfileHeader = () => {
    return (
        <div className="mb-8">
            {/* Header Title Container */}
            <div className="text-center p-4 bg-white/70 backdrop-blur-sm rounded-xl mb-4">
                <div className="ship-frame text-4xl lg:text-5xl lg:px-8 lg:py-6 border-image-gradient-purple">
                    <span className="animate-text-gradient bg-gradient-to-r from-primary via-purple-600 to-green-400 bg-[length:200%_auto] bg-clip-text text-transparent">
                        منصة
                    </span>
                </div>
                <div className="ship-frame text-2xl lg:text-3xl border-image-gradient-blue mt-4">
                    <span className="animate-text-gradient bg-gradient-to-r from-green-400 via-primary to-green-400 bg-[length:200%_auto] bg-clip-text text-transparent">
                        الاستاذ بسام الجنابي مادة الحاسوب
                    </span>
                </div>
            </div>
        </div>
    );
};

export default ProfileHeader;
