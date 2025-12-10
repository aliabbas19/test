const ProfileHeader = () => {
    // Images from legacy app.py
    const COVER_IMAGE = "https://i.ibb.co/RkWC7YZm/photo-2025-10-22-12-53-24.jpg";
    const PROFILE_IMAGE = "https://i.postimg.cc/3RnCZ8Wy/1447-04-22-10-34-02-7d49049c.jpg";

    return (
        <div className="mb-8">
            {/* Header (Cover + Profile Picture) */}
            <header className="relative mb-24">
                <div className="h-[200px] lg:h-[300px] bg-slate-900/50 shadow-md rounded-2xl overflow-hidden relative">
                    <img
                        src={COVER_IMAGE}
                        alt="صورة الغلاف"
                        className="w-full h-full object-contain"
                    />
                </div>
                <div className="absolute -bottom-[75px] right-5 lg:right-[40px] z-10 p-1 bg-transparent">
                    <img
                        src={PROFILE_IMAGE}
                        alt="الصورة الشخصية"
                        className="w-[120px] h-[120px] lg:w-[150px] lg:h-[150px] rounded-full border-[5px] border-white shadow-xl object-cover bg-white"
                    />
                </div>
            </header>

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
