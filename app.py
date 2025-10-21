import sqlite3
import os
import av
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime, timedelta, date


# الصورة الأولى ستكون للغلاف، والثانية للصورة الشخصية
professor_image_url_1 = "https://i.postimg.cc/pT65Tppc/1447-04-22-10-34-03-b1930844.jpg" # استبدل هذا الرابط (صورة الغلاف)
professor_image_url_2 = "https://i.postimg.cc/3RnCZ8Wy/1447-04-22-10-34-02-7d49049c.jpg" # استبدل هذا الرابط (الصورة الشخصية)

# ----------------- HTML TEMPLATES (Embedded) -----------------
# All HTML code is now stored in Python strings.

base_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الاستاذ بسام الجنابي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <style>
        /* General Styles with New Animated Background */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            color: #212529; /* Default dark text color for light theme */
            overflow-x: hidden;
            /* START: New Computer-themed Animated Background */
            background-image: url('https://i.pinimg.com/originals/ca/2c/31/ca2c31828e83a45a332a9a463b21b7cc.gif');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            position: relative;
            z-index: 0;
            /* END: Animated Background */
        }
        
        /* The dark overlay has been REMOVED for the light theme */

        .container-fluid { padding-left: 0; padding-right: 0; }
        .page-wrapper { display: flex; flex-direction: row-reverse; }

        /* Circular Navigation (Left) */
        .circular-nav {
            background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent white works well */
            backdrop-filter: blur(10px); /* Frosted glass effect */
            -webkit-backdrop-filter: blur(10px);
            padding: 20px 10px;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            box-shadow: 2px 0 15px rgba(0,0,0,0.2);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
        }
        .circular-nav ul { list-style: none; padding: 0; margin: 0; }
        .circular-nav li { margin: 25px 0; }
        .circular-nav a {
            text-decoration: none;
            color: #0d6efd;
            background-color: #ffffff;
            border: 2px solid #0d6efd;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s ease;
            position: relative; /* For badge positioning */
        }
        .circular-nav a:hover {
            background-color: #0d6efd;
            color: #ffffff;
            transform: scale(1.1);
            box-shadow: 0 0 15px rgba(13, 110, 253, 0.5);
        }
        .nav-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            font-size: 0.7rem;
            padding: 0.2em 0.5em;
        }

        /* Main Content (Right) */
        .main-content { margin-left: 120px; padding: 30px; width: 100%; }
        
        /* Animated Gradient Header Text */
        .animated-gradient-text {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(90deg, #0d6efd, #6f42c1, #20c997, #0d6efd);
            background-size: 200% auto;
            color: #fff;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: animatedTextGradient 5s linear infinite;
        }
        @keyframes animatedTextGradient { to { background-position: -200% center; } }

        /* Style for Admin Username */
        .admin-username-gradient {
            font-weight: bold;
            background: linear-gradient(90deg, #ff8c00, #ff4500, #ff8c00);
            background-size: 200% auto;
            color: #fff;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: animatedTextGradient 3s linear infinite;
        }
        
        /* START: NEW Superhero status style */
        .superhero-status {
            font-weight: bold;
            padding: 0.35em 0.65em;
            font-size: 0.9em;
            border-radius: 50rem;
            color: #fff;
            background: linear-gradient(45deg, #ffd700, #ff6b6b, #feca57, #ff6b6b, #ff9f43, #ff4757, #ffd700);
            background-size: 400% 400%;
            animation: superheroGradient 3s ease infinite, superheroGlow 1.5s ease-in-out infinite alternate;
            border: 2px solid #fff;
            text-shadow: 0 0 5px rgba(0,0,0,0.5);
            display: inline-block;
        }

        @keyframes superheroGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes superheroGlow {
            from { box-shadow: 0 0 5px #ffc107, 0 0 10px #ffc107, 0 0 15px #ff4500; }
            to { box-shadow: 0 0 10px #ffc107, 0 0 20px #ff4500, 0 0 25px #ff4500; }
        }
        /* END: NEW Superhero status style */

        /* Header (Cover + Profile Picture) Styles */
        .new-profile-header { position: relative; margin-bottom: 90px; }
        .cover-image-container {
            height: 300px;
            /* START: MODIFICATION 1 - Changed background color */
            background-color: rgba(23, 32, 42, 0.5); /* A dark, semi-transparent background */
            /* END: MODIFICATION 1 */
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 15px;
            overflow: hidden;
        }
        .cover-image { 
            width: 100%; 
            height: 100%; 
            /* START: MODIFICATION 2 - Changed object-fit to contain */
            object-fit: contain; 
            /* END: MODIFICATION 2 */
        }
        .profile-picture-container { position: absolute; bottom: -75px; right: 40px; z-index: 2; }
        .profile-picture {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 5px solid #ffffff;
            box-shadow: 0 0 15px rgba(0,0,0,0.25);
            object-fit: cover;
        }
        .header-title-container { 
            text-align: center; 
            padding: 15px; 
            background-color: rgba(255, 255, 255, 0.7); /* Added background for readability */
            backdrop-filter: blur(5px);
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        /* Card styles - semi-transparent for a "glass" effect over the background */
        .card {
            border: 1px solid rgba(0, 0, 0, 0.1);
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
        }
        .table { color: #212529; }
        
        /* ========================================================= */
        /* START: New Professional Admin Post Styles (MODIFIED)      */
        /* ========================================================= */
        .admin-post {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
            position: relative;
            /* MODIFICATION: Changed border to a thicker left border with a gradient */
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-right: 5px solid;
            border-image: linear-gradient(to top, #0d6efd, #20c997) 1;
            /* MODIFICATION: Enhanced transition */
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .admin-post:hover {
            /* MODIFICATION: More dynamic hover effect */
            transform: translateY(-8px) scale(1.01);
            box-shadow: 0 12px 25px rgba(0,0,0,0.2);
        }
        .admin-post-header {
            display: flex;
            align-items: center;
            padding: 1rem 1.25rem;
            background-color: rgba(248, 249, 250, 0.8); /* Lighter header bg */
            border-bottom: 1px solid #e9ecef;
        }
        .admin-post-header .admin-icon {
            margin-left: 1rem; /* For RTL */
        }
        .admin-post-header .info {
            display: flex;
            flex-direction: column;
        }
        .admin-post-body {
            padding: 1.25rem;
            font-size: 1.1rem;
            line-height: 1.6;
            white-space: pre-wrap;
            color: #343a40;
        }
        .admin-post-footer {
            padding: 0.75rem 1.25rem;
            text-align: left; /* Timestamp on the left for modern feel */
            font-size: 0.85rem;
            color: #6c757d;
            background-color: rgba(248, 249, 250, 0.8);
            border-top: 1px solid #e9ecef;
        }
        /* ========================================================= */
        /* END: New Professional Admin Post Styles                 */
        /* ========================================================= */

        /* Responsive Design */
        @media (max-width: 992px) {
            .page-wrapper { flex-direction: column; }
            
            /* MODIFICATION: Removed 'order' properties and adjusted layout */
            .main-content { 
                margin-left: 0; 
                padding: 20px; 
                width: 100%; 
                margin-top: 0;
            }
            .circular-nav {
                height: auto; 
                width: 100%; 
                position: relative; /* Changed from fixed */
                flex-direction: row; 
                justify-content: center;
                padding: 10px 2px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                /* MODIFICATION: Placed at bottom of its container, creating space */
                margin-top: 0;
                margin-bottom: 20px; 
                border-radius: 15px;
            }

            .circular-nav ul { display: flex; flex-direction: row; width: 100%; justify-content: space-around; }
            
            .circular-nav li { margin: 0 2px; }
            .circular-nav a { 
                width: 48px; 
                height: 48px; 
                font-size: 0.6rem;
                border-width: 1px;
                padding: 2px;
            }
            .nav-badge {
                top: -2px;
                right: -2px;
            }
            .cover-image-container { height: 200px; }
            .profile-picture { width: 120px; height: 120px; }
            .profile-picture-container { bottom: -60px; right: 20px; }
            .animated-gradient-text { font-size: 1.8rem; }
        }
    </style>
</head>
<body>
    <div class="page-wrapper">
        <nav class="circular-nav d-none d-lg-flex">
            <ul>
                <li><a href="{{ url_for('index') }}">الرئيسية</a></li>
                {% if session['user_id'] %}
                    <li><a href="{{ url_for('profile', username=session['username']) }}">ملفي</a></li>
                    <li><a href="{{ url_for('archive') }}">الأرشيف</a></li>
                    
                    {% if session['role'] == 'student' %}
                    <li>
                        <a href="{{ url_for('my_messages') }}">
                            الرسائل
                            {% if g.unread_count > 0 %}
                            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                                {{ g.unread_count }}
                            </span>
                            {% endif %}
                        </a>
                    </li>
                    {% endif %}

                    {% if session['role'] == 'admin' %}
                    <li><a href="{{ url_for('admin_dashboard') }}">التحكم</a></li>
                    <li>
                        <a href="{{ url_for('video_review') }}">
                            مراجعة
                            {% if g.unapproved_count > 0 %}
                            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger nav-badge">
                                {{ g.unapproved_count }}
                            </span>
                            {% endif %}
                        </a>
                    </li>
                    <li><a href="{{ url_for('reports') }}">التقارير</a></li>
                    <li><a href="{{ url_for('students') }}">الطلاب</a></li>
                    <li><a href="{{ url_for('conversations') }}">المحادثات</a></li>
                    {% endif %}
                    <li><a href="{{ url_for('logout') }}">الخروج</a></li>
                {% else %}
                    <li><a href="{{ url_for('login') }}">الدخول</a></li>
                {% endif %}
            </ul>
        </nav>
        <main class="main-content">
            <header class="new-profile-header">
                <div class="cover-image-container">
                    <img src="{{ professor_image_url_1 }}" alt="صورة الغلاف" class="cover-image">
                </div>
                <div class="profile-picture-container">
                    <img src="{{ professor_image_url_2 }}" alt="الصورة الشخصية" class="profile-picture">
                </div>
            </header>
            
            <div class="header-title-container">
                <h1 class="animated-gradient-text">منصة الاستاذ بسام الجنابي مادة الحاسوب</h1>
            </div>
            
            <nav class="circular-nav d-lg-none">
                 <ul>
                    <li><a href="{{ url_for('index') }}">الرئيسية</a></li>
                    {% if session['user_id'] %}
                        <li><a href="{{ url_for('profile', username=session['username']) }}">ملفي</a></li>
                        <li><a href="{{ url_for('archive') }}">الأرشيف</a></li>
                        
                        {% if session['role'] == 'student' %}
                        <li>
                            <a href="{{ url_for('my_messages') }}">
                                الرسائل
                                {% if g.unread_count > 0 %}
                                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger nav-badge">
                                    {{ g.unread_count }}
                                </span>
                                {% endif %}
                            </a>
                        </li>
                        {% endif %}

                        {% if session['role'] == 'admin' %}
                        <li><a href="{{ url_for('admin_dashboard') }}">التحكم</a></li>
                        <li>
                            <a href="{{ url_for('video_review') }}">
                                مراجعة
                                {% if g.unapproved_count > 0 %}
                                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger nav-badge">
                                    {{ g.unapproved_count }}
                                </span>
                                {% endif %}
                            </a>
                        </li>
                        <li><a href="{{ url_for('reports') }}">التقارير</a></li>
                        <li><a href="{{ url_for('students') }}">الطلاب</a></li>
                        <li><a href="{{ url_for('conversations') }}">المحادثات</a></li>
                        {% endif %}
                        <li><a href="{{ url_for('logout') }}">الخروج</a></li>
                    {% else %}
                        <li><a href="{{ url_for('login') }}">الدخول</a></li>
                    {% endif %}
                </ul>
            </nav>

            <div class="container">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                {% block content %}{% endblock %}
            </div>
        </main>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
index_content_block = """
{% if session.role == 'admin' %}
<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <h3 class="card-title">إنشاء منشور جديد</h3>
        <form action="{{ url_for('create_post') }}" method="post">
            <div class="mb-3">
                <textarea name="content" class="form-control" rows="3" placeholder="اكتب إعلانك أو نشاطك هنا..." required></textarea>
            </div>
            <button type="submit" class="btn btn-primary">نشر</button>
        </form>
    </div>
</div>
{% endif %}

<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <h3 class="card-title">فلترة الفيديوهات</h3>
        <form action="{{ url_for('index') }}" method="get" class="row g-3 align-items-end">
            <div class="col-md-4">
                <label for="video_type_filter" class="form-label">نوع الفيديو:</label>
                <select name="video_type" id="video_type_filter" class="form-select">
                    <option value="" {% if not selected_video_type %}selected{% endif %}>الكل</option>
                    <option value="منهجي" {% if selected_video_type == 'منهجي' %}selected{% endif %}>منهجي</option>
                    <option value="اثرائي" {% if selected_video_type == 'اثرائي' %}selected{% endif %}>اثرائي</option>
                </select>
            </div>
            {% if session.role == 'admin' %}
            <div class="col-md-3">
                <label for="class_name" class="form-label">الصف:</label>
                <select name="class_name" id="class_name" class="form-select">
                    <option value="">اختر الصف</option>
                    {% for c in all_classes %}
                        <option value="{{ c.class_name }}" {% if c.class_name == selected_class %}selected{% endif %}>{{ c.class_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="section_name" class="form-label">الشعبة:</label>
                <select name="section_name" id="section_name" class="form-select">
                     <option value="">اختر الشعبة</option>
                     {% for s in all_sections %}
                        <option value="{{ s.section_name }}" {% if s.section_name == selected_section %}selected{% endif %}>{{ s.section_name }}</option>
                    {% endfor %}
                </select>
            </div>
            {% endif %}
            <div class="col-auto">
                <button type="submit" class="btn btn-primary w-100">فلترة</button>
            </div>
            <div class="col-auto">
                <a href="{{ url_for('index') }}" class="btn btn-secondary w-100">إلغاء</a>
            </div>
        </form>
    </div>
</div>

{% if session.role == 'student' %}
<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <h3 class="card-title">رفع فيديو جديد</h3>
        <form action="{{ url_for('upload_video') }}" method="post" enctype="multipart/form-data">
            <div class="mb-3">
                <input type="text" name="title" class="form-control" placeholder="عنوان الفيديو" required>
            </div>
            <div class="mb-3">
                <label for="video_type" class="form-label">نوع الفيديو (إجباري):</label>
                <select name="video_type" id="video_type" class="form-select" required>
                    <option value="" disabled selected>اختر نوع الفيديو...</option>
                    <option value="منهجي">منهجي</option>
                    <option value="اثرائي">اثرائي</option>
                </select>
            </div>
            <div class="mb-3">
                <input type="file" name="video_file" class="form-control" accept="video/*" required>
            </div>
            <button type="submit" class="btn btn-primary">رفع الفيديو</button>
        </form>
    </div>
</div>
{% endif %}

<div class="mb-4 shadow-sm rounded overflow-hidden">
    <div id="techCarousel" class="carousel slide carousel-fade" data-bs-ride="carousel">
        <div class="carousel-indicators">
            <button type="button" data-bs-target="#techCarousel" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
            <button type="button" data-bs-target="#techCarousel" data-bs-slide-to="1" aria-label="Slide 2"></button>
            <button type="button" data-bs-target="#techCarousel" data-bs-slide-to="2" aria-label="Slide 3"></button>
            <button type="button" data-bs-target="#techCarousel" data-bs-slide-to="3" aria-label="Slide 4"></button>
            <button type="button" data-bs-target="#techCarousel" data-bs-slide-to="4" aria-label="Slide 5"></button>
        </div>
        <div class="carousel-inner">
            <div class="carousel-item active" data-bs-interval="3000">
                <img src="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=2069" class="d-block w-100" alt="صورة برمجة" style="height: 400px; object-fit: cover; filter: brightness(0.8);">
                <div class="carousel-caption d-none d-md-block" style="background-color: rgba(0, 0, 0, 0.5); border-radius: 0.5rem; padding: 1rem;">
                    <h5>عالم البرمجة الحديثة</h5>
                    <p>استكشف لغات البرمجة التي تشكل مستقبل التكنولوجيا.</p>
                </div>
            </div>
            <div class="carousel-item" data-bs-interval="3000">
                <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726a?q=80&w=2070" class="d-block w-100" alt="تقنيات قديمة" style="height: 400px; object-fit: cover; filter: brightness(0.8);">
                <div class="carousel-caption d-none d-md-block" style="background-color: rgba(0, 0, 0, 0.5); border-radius: 0.5rem; padding: 1rem;">
                    <h5>من الماضي إلى الحاضر</h5>
                    <p>رحلة عبر تطور أجهزة الحاسوب والتقنيات.</p>
                </div>
            </div>
            <div class="carousel-item" data-bs-interval="3000">
                <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070" class="d-block w-100" alt="مكونات الحاسوب" style="height: 400px; object-fit: cover; filter: brightness(0.8);">
                <div class="carousel-caption d-none d-md-block" style="background-color: rgba(0, 0, 0, 0.5); border-radius: 0.5rem; padding: 1rem;">
                    <h5>قلب الحاسوب</h5>
                    <p>تعرف على المكونات الداخلية التي تمنح حاسوبك القوة.</p>
                </div>
            </div>
            <div class="carousel-item" data-bs-interval="3000">
                <img src="https://images.unsplash.com/photo-1610563166126-cabc413939a9?q=80&w=2070" class="d-block w-100" alt="بيئة عمل المطور" style="height: 400px; object-fit: cover; filter: brightness(0.8);">
                <div class="carousel-caption d-none d-md-block" style="background-color: rgba(0, 0, 0, 0.5); border-radius: 0.5rem; padding: 1rem;">
                    <h5>بيئة العمل المثالية</h5>
                    <p>أدوات وتقنيات تساعد على زيادة الإنتاجية والإبداع.</p>
                </div>
            </div>
            <div class="carousel-item" data-bs-interval="3000">
                <img src="https://images.unsplash.com/photo-1526374965328-5f61d4dc18c5?q=80&w=2070" class="d-block w-100" alt="البيانات الرقمية" style="height: 400px; object-fit: cover; filter: brightness(0.8);">
                <div class="carousel-caption d-none d-md-block" style="background-color: rgba(0, 0, 0, 0.5); border-radius: 0.5rem; padding: 1rem;">
                    <h5>لغة البيانات</h5>
                    <p>الغوص في عالم البيانات والأرقام الثنائية.</p>
                </div>
            </div>
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#techCarousel" data-bs-slide="prev"><span class="carousel-control-prev-icon" aria-hidden="true"></span><span class="visually-hidden">السابق</span></button>
        <button class="carousel-control-next" type="button" data-bs-target="#techCarousel" data-bs-slide="next"><span class="carousel-control-next-icon" aria-hidden="true"></span><span class="visually-hidden">التالي</span></button>
    </div>
</div>

<hr style="border-color: rgba(0,0,0,0.1);">
<h2 class="text-center mb-4">آخر الأخبار والنشاطات</h2>

{% for post in posts %}
<div class="admin-post">
    <div class="admin-post-header">
        <div class="admin-icon">
            <span class="admin-username-gradient fs-2"><i class="fas fa-bullhorn"></i></span>
        </div>
        <div class="info">
            <span class="admin-username-gradient fw-bold">{{ post.username }}</span>
            <small class="text-muted">إعلان إداري</small>
        </div>
    </div>
    <div class="admin-post-body">
        <p>{{ post.content }}</p>
    </div>
    <div class="admin-post-footer">
        <span>نشر في: {{ post.timestamp | strftime }}</span>
    </div>
</div>
{% else %}
    <p class="text-center text-muted">لا توجد منشورات حالياً.</p>
{% endfor %}
<hr style="border-color: rgba(0,0,0,0.1);">
<h2 class="text-center mb-4">أحدث الفيديوهات</h2>
{% for video in videos %}
<div class="card video-post shadow-sm mb-4">
    <div class="card-header bg-transparent border-0 pt-3">
        <div class="d-flex align-items-center">
             <img src="{{ url_for('static', filename='uploads/' + (video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
            <div class="ms-3">
                <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                    {% if video.role == 'admin' %}
                        <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ video.username }}</span>
                    {% else %}
                        <span class="text-primary">{{ video.username }}</span>
                    {% endif %}
                </a>
                
                {# START: MODIFIED Champion Status Display #}
                {% set user_status = champion_statuses.get(video.user_id) %}
                {% if user_status %}
                    {% if user_status == 'بطل خارق' %}
                        <span class="superhero-status"><i class="fas fa-meteor me-1"></i> {{ user_status }}</span>
                    {% else %}
                        <span class="badge bg-warning text-dark">🏆 {{ user_status }}</span>
                    {% endif %}
                {% endif %}
                {# END: MODIFIED Champion Status Display #}

                 <small class="d-block"><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime }}</span></small>
            </div>
        </div>
    </div>
    <div class="card-body">
        <h5 class="card-title">{{ video.title }}</h5>
        {# START: MODIFICATION - Wrapped video for better sizing on desktop #}
        <div class="video-container mx-auto" style="max-width: 720px;">
            <video width="100%" controls class="rounded" style="background-color:#000;">
                <source src="{{ url_for('static', filename='uploads/' + video.filepath) }}" type="video/mp4">
            </video>
        </div>
        {# END: MODIFICATION #}
        <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="like-section">
                <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"> <i class="fas fa-heart fa-lg"></i> </button>
                <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
            </div>
            {# START: MODIFIED Star Display #}
            <div class="rating-display-stars" style="color: #ffc107; font-size: 1.5rem;">
                {% set rating = video_ratings.get(video.id) %}
                <span id="stars-display-{{ video.id }}">
                    {% if rating and rating.total_stars > 0 %} 
                        <i class="fas fa-star"></i> 
                        {{ rating.total_stars }} / {% if video.video_type == 'اثرائي' %}10{% else %}4{% endif %}
                    {% else %} 
                        <small class="text-muted">لم يُقيّم بعد</small> 
                    {% endif %}
                </span>
            </div>
            {# END: MODIFIED Star Display #}
        </div>
        
        {# START: MODIFIED Rating Form #}
        {% if session.role == 'admin' %}
        <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
            <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
            {% set current_rating = video_ratings.get(video.id) %}
            <div class="mt-2">
                {% if video.video_type == 'اثرائي' %}
                    {# 10-star rating form #}
                    <div class="row">
                        {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل'), ('filming_lighting', 'التصوير والإضاءة'), ('sound_quality', 'جودة الصوت'), ('behavior', 'السلوك'), ('cleanliness', 'النظافة'), ('location', 'موقع التصوير'), ('confidence', 'الثقة')] %}
                        <div class="col-md-4 col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    {# 4-star rating form #}
                    <div class="d-flex justify-content-around flex-wrap">
                        {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل')] %}
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                            <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </form>
        {% endif %}
        {# END: MODIFIED Rating Form #}

        <div class="comments-section mt-3">
            <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                {% for comment in video_comments[video.id]['toplevel'] %}
                <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                    <img src="{{ url_for('static', filename='uploads/' + (comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                    <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                        <div class="d-flex justify-content-between">
                            <p class="comment-author fw-bold mb-0">
                                {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                {% if comment.role == 'admin' %}
                                    <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.username }}</span>
                                {% else %}
                                    <span class="text-primary">{{ comment.username }}</span>
                                {% endif %}
                            </p>
                            <div class="comment-actions">
                                {% if session['role'] == 'admin' %}
                                    <button class="btn btn-sm btn-link text-secondary pin-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-thumbtack"></i></button>
                                {% endif %}
                                {% if session['user_id'] == comment.user_id %}
                                    <button class="btn btn-sm btn-link text-secondary edit-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-edit"></i></button>
                                {% endif %}
                                {% if session['user_id'] == comment.user_id or session['role'] == 'admin' %}
                                    <button class="btn btn-sm btn-link text-danger delete-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-trash"></i></button>
                                {% endif %}
                            </div>
                        </div>
                        <div class="comment-content-wrapper">
                            <p class="comment-content mb-0" style="white-space: pre-wrap;">{{ comment.content }}</p>
                        </div>
                    </div>
                </li>
                {% endfor %}
            </ul>
            <form class="comment-form-new d-flex mt-2" data-video-id="{{ video.id }}">
                <input name="comment_content" class="form-control" placeholder="اكتب تعليقاً..." rows="1" required>
                <button type="submit" class="btn btn-sm btn-primary ms-2">نشر</button>
            </form>
        </div>
    </div>
</div>
{% else %}
<p class="text-center text-muted">لا توجد فيديوهات لعرضها حالياً.</p>
{% endfor %}
"""

archive_content_block = """
<h1 class="mb-2 text-center">أرشيف الفيديوهات</h1>
<p class="text-center text-muted">هنا تجد الفيديوهات التي تم نشرها منذ أكثر من 7 أيام.</p>

<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <h3 class="card-title">فلترة الأرشيف</h3>
        <form action="{{ url_for('archive') }}" method="get" class="row g-3 align-items-end">
            <div class="col-md-3">
                <label for="class_name" class="form-label">الصف:</label>
                <select name="class_name" id="class_name" class="form-select">
                    <option value="">كل الصفوف</option>
                    {% for c in all_classes %}
                        <option value="{{ c.class_name }}" {% if c.class_name == selected_class %}selected{% endif %}>{{ c.class_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="video_type_filter" class="form-label">نوع الفيديو:</label>
                <select name="video_type" id="video_type_filter" class="form-select">
                    <option value="" {% if not selected_video_type %}selected{% endif %}>الكل</option>
                    <option value="منهجي" {% if selected_video_type == 'منهجي' %}selected{% endif %}>منهجي</option>
                    <option value="اثرائي" {% if selected_video_type == 'اثرائي' %}selected{% endif %}>اثرائي</option>
                </select>
            </div>
            <div class="col-md-2">
                <label for="start_date" class="form-label">من تاريخ:</label>
                <input type="date" name="start_date" id="start_date" class="form-control" value="{{ start_date or '' }}">
            </div>
            <div class="col-md-2">
                <label for="end_date" class="form-label">إلى تاريخ:</label>
                <input type="date" name="end_date" id="end_date" class="form-control" value="{{ end_date or '' }}">
            </div>
            <div class="col-md-1 d-grid">
                <button type="submit" class="btn btn-primary">بحث</button>
            </div>
            <div class="col-md-1 d-grid">
                <a href="{{ url_for('archive') }}" class="btn btn-secondary">إلغاء</a>
            </div>
        </form>
    </div>
</div>

<hr style="border-color: rgba(0,0,0,0.1);">
{% for video in videos %}
<div class="card video-post shadow-sm mb-4">
    <div class="card-header bg-transparent border-0 pt-3">
        <div class="d-flex align-items-center">
             <img src="{{ url_for('static', filename='uploads/' + (video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
            <div class="ms-3">
                <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                    {% if video.role == 'admin' %}
                        <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ video.username }}</span>
                    {% else %}
                        <span class="text-primary">{{ video.username }}</span>
                    {% endif %}
                </a>
                
                {% set user_status = champion_statuses.get(video.user_id) %}
                {% if user_status %}
                    {% if user_status == 'بطل خارق' %}
                        <span class="superhero-status"><i class="fas fa-meteor me-1"></i> {{ user_status }}</span>
                    {% else %}
                        <span class="badge bg-warning text-dark">🏆 {{ user_status }}</span>
                    {% endif %}
                {% endif %}

                <small class="d-block"><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime }}</span></small>
            </div>
        </div>
    </div>
    <div class="card-body">
        <h5 class="card-title">{{ video.title }}</h5>
        {# START: MODIFICATION - Wrapped video for better sizing on desktop #}
        <div class="video-container mx-auto" style="max-width: 720px;">
            <video width="100%" controls class="rounded" style="background-color:#000;">
                <source src="{{ url_for('static', filename='uploads/' + video.filepath) }}" type="video/mp4">
            </video>
        </div>
        {# END: MODIFICATION #}
        <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="like-section">
                <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"><i class="fas fa-heart fa-lg"></i></button>
                <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
            </div>
            <div class="rating-display-stars" style="color: #ffc107; font-size: 1.5rem;">
                {% set rating = video_ratings.get(video.id) %}
                <span id="stars-display-{{ video.id }}">
                     {% if rating and rating.total_stars > 0 %} 
                        <i class="fas fa-star"></i> 
                        {{ rating.total_stars }} / {% if video.video_type == 'اثرائي' %}10{% else %}4{% endif %}
                    {% else %} 
                        <small class="text-muted">لم يُقيّم بعد</small> 
                    {% endif %}
                </span>
            </div>
        </div>
        {% if session.role == 'admin' %}
        <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
            <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
            {% set current_rating = video_ratings.get(video.id) %}
            <div class="mt-2">
                {% if video.video_type == 'اثرائي' %}
                    <div class="row">
                        {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل'), ('filming_lighting', 'التصوير والإضاءة'), ('sound_quality', 'جودة الصوت'), ('behavior', 'السلوك'), ('cleanliness', 'النظافة'), ('location', 'موقع التصوير'), ('confidence', 'الثقة')] %}
                        <div class="col-md-4 col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="d-flex justify-content-around flex-wrap">
                        {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل')] %}
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                            <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </form>
        {% endif %}
        <div class="comments-section mt-3">
            <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                {% for comment in video_comments[video.id]['toplevel'] %}
                <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                    <img src="{{ url_for('static', filename='uploads/' + (comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                    <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                        <div class="d-flex justify-content-between">
                            <p class="comment-author fw-bold mb-0">
                                {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                {% if comment.role == 'admin' %}
                                    <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.username }}</span>
                                {% else %}
                                    <span class="text-primary">{{ comment.username }}</span>
                                {% endif %}
                            </p>
                            <div class="comment-actions">
                                {% if session['role'] == 'admin' %}
                                    <button class="btn btn-sm btn-link text-secondary pin-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-thumbtack"></i></button>
                                {% endif %}
                                {% if session['user_id'] == comment.user_id %}
                                    <button class="btn btn-sm btn-link text-secondary edit-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-edit"></i></button>
                                {% endif %}
                                {% if session['user_id'] == comment.user_id or session['role'] == 'admin' %}
                                    <button class="btn btn-sm btn-link text-danger delete-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-trash"></i></button>
                                {% endif %}
                            </div>
                        </div>
                        <div class="comment-content-wrapper">
                            <p class="comment-content mb-0" style="white-space: pre-wrap;">{{ comment.content }}</p>
                        </div>
                    </div>
                </li>
                {% endfor %}
            </ul>
            <form class="comment-form-new d-flex mt-2" data-video-id="{{ video.id }}">
                <input name="comment_content" class="form-control" placeholder="اكتب تعليقاً..." required>
                <button type="submit" class="btn btn-sm btn-primary ms-2">نشر</button>
            </form>
        </div>
    </div>
</div>
{% else %}
<p class="text-center text-muted">لا توجد فيديوهات في الأرشيف تطابق معايير البحث.</p>
{% endfor %}
"""

login_content_block = """
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm">
            <div class="card-header"><h3>تسجيل الدخول</h3></div>
            <div class="card-body">
                <form method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">اسم المستخدم</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">كلمة المرور</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">دخول</button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

admin_dashboard_content_block = """
<h1 class="mb-4">لوحة تحكم المسؤول</h1>

{# START: NEW - Start New School Year Card #}
<div class="card mb-4 shadow-sm border-danger">
    <div class="card-header bg-danger text-white"><h4><i class="fas fa-exclamation-triangle me-2"></i>منطقة الخطر</h4></div>
    <div class="card-body">
        <h5 class="card-title">بدء سنة دراسية جديدة</h5>
        <p class="card-text">
            سيؤدي هذا الإجراء إلى حذف جميع الفيديوهات، والمنشورات، والتعليقات، والرسائل، والتقييمات، والإعجابات، وتصفير سجل الأبطال.
            <strong>سيتم الاحتفاظ بحسابات الطلاب والمسؤولين</strong>، ولكن سيُطلب من جميع الطلاب إدخال معلومات الصف والشعبة الجديدة عند تسجيل الدخول التالي.
            <br>
            <strong class="text-danger">تحذير: لا يمكن التراجع عن هذا الإجراء.</strong>
        </p>
        <form action="{{ url_for('start_new_year') }}" method="post" onsubmit="return confirm('هل أنت متأكد تماماً من رغبتك في بدء سنة دراسية جديدة؟ سيتم حذف جميع البيانات بشكل نهائي!');">
            <button type="submit" class="btn btn-danger">بدء سنة جديدة الآن</button>
        </form>
    </div>
</div>
{# END: NEW - Start New School Year Card #}

<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card h-100 shadow-sm">
            <div class="card-header"><h4>إنشاء حساب طالب</h4></div>
            <div class="card-body">
                <form action="{{ url_for('create_student') }}" method="post">
                    <div class="mb-3"><input type="text" name="username" class="form-control" placeholder="اسم المستخدم" required></div>
                    <div class="mb-3"><input type="password" name="password" class="form-control" placeholder="كلمة المرور" required></div>
                    <button type="submit" class="btn btn-primary">إنشاء طالب</button>
                </form>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card h-100 shadow-sm">
            <div class="card-header"><h4>إنشاء حساب مسؤول</h4></div>
            <div class="card-body">
                <form action="{{ url_for('create_admin') }}" method="post">
                    <div class="mb-3"><input type="text" name="username" class="form-control" placeholder="اسم المستخدم" required></div>
                    <div class="mb-3"><input type="password" name="password" class="form-control" placeholder="كلمة المرور" required></div>
                    <button type="submit" class="btn btn-success">إنشاء مسؤول</button>
                </form>
            </div>
        </div>
    </div>
</div>
<div class="card mt-4 shadow-sm">
    <div class="card-header"><h4>إدارة الطلاب</h4></div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr><th>اسم الطالب</th><th>الحالة</th><th>إجراءات</th></tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>
                           <a href="{{ url_for('profile', username=student.username) }}">{{ student.username }}</a>
                        </td>
                        <td>
                            {% if student.end_date %}
                                <span class="badge bg-danger">موقوف حتى {{ student.end_date.strftime('%Y-%m-%d %H:%M') }}</span>
                            {% elif student.is_muted %}
                                <span class="badge bg-secondary">مكتوم</span>
                            {% else %}
                                <span class="badge bg-success">نشط</span>
                            {% endif %}
                             {% if student.end_date %}<br><small>السبب: {{ student.reason }}</small>{% endif %}
                        </td>
                        <td>
                            <div class="btn-group" role="group">
                                <a href="{{ url_for('edit_user', user_id=student.id) }}" class="btn btn-sm btn-secondary">تعديل</a>
                                <form action="{{ url_for('kick_student', student_id=student.id) }}" method="post" class="d-inline">
                                    <button type="submit" class="btn btn-sm btn-dark">طرد</button>
                                </form>
                                <form action="{{ url_for('toggle_mute', student_id=student.id) }}" method="post" class="d-inline">
                                    {% if student.is_muted %}
                                        <button type="submit" class="btn btn-sm btn-info">إلغاء الكتم</button>
                                    {% else %}
                                        <button type="submit" class="btn btn-sm btn-secondary">كتم</button>
                                    {% endif %}
                                </form>
                                {% if student.end_date %}
                                    <form action="{{ url_for('lift_suspension', student_id=student.id) }}" method="post" class="d-inline">
                                        <button type="submit" class="btn btn-sm btn-success">رفع الإيقاف</button>
                                    </form>
                                {% else %}
                                    <form action="{{ url_for('suspend_student', student_id=student.id) }}" method="post" class="d-inline-flex align-items-center gap-1">
                                        <select name="duration" class="form-select form-select-sm" style="width: auto;">
                                            <option value="hour">ساعة</option>
                                            <option value="day">يوم</option>
                                            <option value="week">أسبوع</option>
                                            <option value="month">شهر</option>
                                            <option value="year">سنة</option>
                                            <option value="permanent">دائم</option>
                                        </select>
                                        <input type="text" name="reason" placeholder="السبب" class="form-control form-control-sm">
                                        <button type="submit" class="btn btn-sm btn-warning text-nowrap">إيقاف</button>
                                    </form>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

reports_content_block = """
<div class="container mt-4">
    <h1 class="mb-4 text-center">تقرير نشاط الطلاب</h1>

    <div class="card mb-4 shadow-sm">
        <div class="card-body">
            <h3 class="card-title">فلترة التقارير حسب الصف</h3>
            <form action="{{ url_for('reports') }}" method="get" class="row g-3 align-items-end">
                <div class="col-md-8">
                    <label for="class_name" class="form-label">اختر الصف:</label>
                    <select name="class_name" id="class_name" class="form-select">
                        <option value="">كل الصفوف</option>
                        {% for c in all_classes %}
                            <option value="{{ c.class_name }}" {% if c.class_name == selected_class %}selected{% endif %}>{{ c.class_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2 d-grid">
                    <button type="submit" class="btn btn-primary">عرض التقرير</button>
                </div>
                <div class="col-md-2 d-grid">
                    <a href="{{ url_for('reports') }}" class="btn btn-secondary">عرض الكل</a>
                </div>
            </form>
        </div>
    </div>

    {% if report_data %}
        {% for student in report_data %}
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h4>الطالب: {{ student.username }}</h4>
                <p class="mb-0 small text-muted">الصف: {{ student.class_name or 'غير محدد' }} | الشعبة: {{ student.section_name or 'غير محدد' }}</p>
            </div>
            <div class="card-body">
                <h5 class="card-title">ملخص النشاط الأسبوعي</h5>
                <div class="row text-center mb-4">
                    <div class="col-md-4 mb-3">
                        <div class="stat-card p-3 rounded bg-light">
                            <h6 class="text-muted text-uppercase">الفيديوهات</h6>
                            <p class="display-4 fw-bold">{{ student.weekly_activity.uploads }}</p>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="stat-card p-3 rounded bg-light">
                            <h6 class="text-muted text-uppercase">التعليقات</h6>
                            <p class="display-4 fw-bold">{{ student.weekly_activity.comments }}</p>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="stat-card p-3 rounded bg-light">
                            <h6 class="text-muted text-uppercase">بطل الأسبوع</h6>
                            <p class="display-4 fw-bold">
                                {% if student.weekly_activity.is_champion %}<i class="fas fa-trophy text-warning"></i>
                                {% else %}<span class="text-muted">-</span>{% endif %}
                            </p>
                        </div>
                    </div>
                </div>
                <hr>
                <h5 class="card-title mt-4">الفيديوهات المنهجية والتقييمات</h5>
                {% if student.videos %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>عنوان الفيديو</th><th>تاريخ الرفع</th>
                                    <th title="المشاركة"><i class="fas fa-users"></i></th>
                                    <th title="الحفظ"><i class="fas fa-brain"></i></th>
                                    <th title="اللفظ"><i class="fas fa-microphone-alt"></i></th>
                                    <th title="الوسيلة"><i class="fas fa-paint-brush"></i></th>
                                    <th>مجموع <i class="fas fa-star text-warning"></i></th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for video in student.videos %}
                                <tr>
                                    <td>{{ video.title }}</td>
                                    <td>{{ video.timestamp | strftime('%Y-%m-%d') }}</td>
                                    <td>{% if video.participation == 1 %}<i class="fas fa-check-circle text-success fa-lg"></i>{% else %}<i class="fas fa-times-circle text-danger fa-lg"></i>{% endif %}</td>
                                    <td>{% if video.memorization == 1 %}<i class="fas fa-check-circle text-success fa-lg"></i>{% else %}<i class="fas fa-times-circle text-danger fa-lg"></i>{% endif %}</td>
                                    <td>{% if video.pronunciation == 1 %}<i class="fas fa-check-circle text-success fa-lg"></i>{% else %}<i class="fas fa-times-circle text-danger fa-lg"></i>{% endif %}</td>
                                    <td>{% if video.use_of_aids == 1 %}<i class="fas fa-check-circle text-success fa-lg"></i>{% else %}<i class="fas fa-times-circle text-danger fa-lg"></i>{% endif %}</td>
                                    <td class="fw-bold">{{ video.total_stars }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">لم يقم هذا الطالب برفع أي فيديوهات منهجية بعد.</p>
                {% endif %}

                {# NEW: Enrichment videos report section #}
                <hr>
                <h5 class="card-title mt-4">تقرير الفيديوهات الإثرائية</h5>
                {% if student.enrichment_videos %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover small">
                            <thead>
                                <tr>
                                    <th>عنوان الفيديو</th>
                                    <th>التاريخ</th>
                                    <th title="المشاركة"><i class="fas fa-users"></i></th>
                                    <th title="الحفظ"><i class="fas fa-brain"></i></th>
                                    <th title="النطق"><i class="fas fa-microphone-alt"></i></th>
                                    <th title="الوسائل"><i class="fas fa-paint-brush"></i></th>
                                    <th title="التصوير والإضاءة"><i class="fas fa-camera"></i></th>
                                    <th title="جودة الصوت"><i class="fas fa-volume-up"></i></th>
                                    <th title="السلوك"><i class="fas fa-user-check"></i></th>
                                    <th title="النظافة"><i class="fas fa-soap"></i></th>
                                    <th title="موقع التصوير"><i class="fas fa-map-marker-alt"></i></th>
                                    <th title="الثقة"><i class="fas fa-award"></i></th>
                                    <th>المجموع <i class="fas fa-star text-warning"></i></th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for video in student.enrichment_videos %}
                                <tr>
                                    <td>{{ video.title }}</td>
                                    <td>{{ video.timestamp | strftime('%Y-%m-%d') }}</td>
                                    <td>{% if video.participation == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.memorization == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.pronunciation == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.use_of_aids == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.filming_lighting == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.sound_quality == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.behavior == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.cleanliness == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.location == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td>{% if video.confidence == 1 %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
                                    <td class="fw-bold">{{ video.total_stars }} / 10</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">لم يقم هذا الطالب برفع أي فيديوهات إثرائية بعد.</p>
                {% endif %}
                {# END: New section #}
                
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p class="text-center text-muted mt-5">لا توجد بيانات لعرضها تطابق معايير البحث.</p>
    {% endif %}
</div>
"""
profile_content_block = """
<div class="profile-header p-4 rounded mb-4 bg-white shadow-sm" style="background-color: rgba(255, 255, 255, 0.95);">
    <div class="d-flex align-items-center">
        <img src="{{ url_for('static', filename='uploads/' + user.profile_image) }}" alt="Profile Image" class="rounded-circle" width="150" height="150" style="border: 4px solid #0d6efd;">
        <div class="profile-info ms-4">
            {% if user.role == 'admin' %}
                <h1 class="admin-username-gradient"><i class="fas fa-crown"></i> {{ user.username }}</h1>
            {% else %}
                <h1 class="text-primary">{{ user.username }}</h1>
                 <h4 class="text-muted fw-light">{{ user.full_name or '' }}</h4>
            {% endif %}
            <p class="text-muted">الصف: {{ user.class_name or 'غير محدد' }} | الشعبة: {{ user.section_name or 'غير محدد' }}</p>
            
            {% if user_status %}
                {% if user_status == 'بطل خارق' %}
                    <p><span class="superhero-status fs-5"><i class="fas fa-meteor me-1"></i> {{ user_status }}</span></p>
                {% else %}
                    <p class="fw-bold text-warning fs-5"><i class="fas fa-trophy"></i> {{ user_status }}</p>
                {% endif %}
            {% endif %}

            {% if session['user_id'] == user.id or session['role'] == 'admin' %}
                <a href="{{ url_for('edit_user', user_id=user.id) }}" class="btn btn-outline-primary">تعديل الملف الشخصي</a>
            {% endif %}
        </div>
    </div>
</div>

{% if (session['user_id'] == user.id or session['role'] == 'admin') and user.role == 'student' %}
<div class="card shadow-sm mb-4">
    <div class="card-header">
        <h4 class="mb-0">المعلومات الشخصية</h4>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-6 mb-3">
                <strong><i class="fas fa-phone-alt me-2"></i>رقم الهاتف:</strong>
                <p class="text-muted d-inline">{{ user.phone_number or 'لم يتم إدخاله' }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <strong><i class="fas fa-map-marker-alt me-2"></i>عنوان السكن:</strong>
                <p class="text-muted d-inline">{{ user.address or 'لم يتم إدخاله' }}</p>
            </div>
            <hr class="my-2">
            <div class="col-md-6 mb-3">
                <strong><i class="fas fa-user-graduate me-2"></i>التحصيل الدراسي للأب:</strong>
                <p class="text-muted d-inline">{{ user.father_education or 'لم يتم إدخاله' }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <strong><i class="fas fa-user-graduate me-2"></i>التحصيل الدراسي للأم:</strong>
                <p class="text-muted d-inline">{{ user.mother_education or 'لم يتم إدخاله' }}</p>
            </div>
        </div>
    </div>
</div>
{% endif %}
<hr style="border-color: rgba(0,0,0,0.1);">
<h2 class="mb-4 text-center">مقاطع الفيديو الخاصة بـ {{ user.username }}</h2>
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
    {% for video in videos %}
    <div class="col">
        <div class="card h-100 video-card shadow-sm">
            <video controls class="card-img-top" style="background-color:#000;">
                <source src="{{ url_for('static', filename='uploads/' + video.filepath) }}" type="video/mp4">
            </video>
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ video.title }}</h5>
                
                {# START: NEW Moderation Block #}
                {% if video.is_approved == 0 %}
                    <div class="alert alert-warning p-2 d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold"><i class="fas fa-clock me-2"></i>بانتظار الموافقة</span>
                        {% if session.role == 'admin' %}
                        <div class="btn-group">
                            <form action="{{ url_for('approve_video', video_id=video.id) }}" method="post" class="d-inline">
                                <button type="submit" class="btn btn-sm btn-success">موافقة</button>
                            </form>
                            <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                                <button type="submit" class="btn btn-sm btn-danger">حذف</button>
                            </form>
                        </div>
                        {% endif %}
                    </div>
                {% else %}
                    <span class="badge bg-success mb-2"><i class="fas fa-check-circle me-1"></i>تمت الموافقة</span>
                {% endif %}
                {# END: NEW Moderation Block #}

                 <small><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime('%Y-%m-%d') }}</span></small>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <div class="like-section">
                        <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"><i class="fas fa-heart fa-lg"></i></button>
                        <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
                    </div>
                    <div class="rating-display-stars text-warning" style="font-size: 1.5rem;">
                        {% set rating = video_ratings.get(video.id) %}
                        <span id="stars-display-{{ video.id }}">
                            {% if rating and rating.total_stars > 0 %} 
                                <i class="fas fa-star"></i> 
                                {{ rating.total_stars }} / {% if video.video_type == 'اثرائي' %}10{% else %}4{% endif %}
                            {% else %} 
                                <small class="text-muted">لم يُقيّم</small> 
                            {% endif %}
                        </span>
                    </div>
                </div>
                {% if session.role == 'admin' %}
                <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
                     <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
                    {% set current_rating = video_ratings.get(video.id) %}
                     <div class="mt-2">
                        {% if video.video_type == 'اثرائي' %}
                            <div class="row">
                                {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل'), ('filming_lighting', 'التصوير والإضاءة'), ('sound_quality', 'جودة الصوت'), ('behavior', 'السلوك'), ('cleanliness', 'النظافة'), ('location', 'موقع التصوير'), ('confidence', 'الثقة')] %}
                                <div class="col-md-6 col-12">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                        <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="d-flex justify-content-around flex-wrap">
                                {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل')] %}
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                    <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                                </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                </form>
                {% endif %}
                <div class="comments-section mt-auto pt-3">
                     <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                        {% set comments = video_comments.get(video.id, {}).get('toplevel', []) %}
                        {% for comment in comments %}
                        <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                            <img src="{{ url_for('static', filename='uploads/' + (comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                            <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                                <div class="d-flex justify-content-between">
                                    <p class="comment-author fw-bold mb-0">
                                        {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                        {% if comment.role == 'admin' %}
                                            <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.username }}</span>
                                        {% else %}
                                            <span class="text-primary">{{ comment.username }}</span>
                                        {% endif %}
                                    </p>
                                    <div class="comment-actions">
                                        {% if session['role'] == 'admin' %}
                                            <button class="btn btn-sm btn-link text-secondary pin-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-thumbtack"></i></button>
                                        {% endif %}
                                        {% if session['user_id'] == comment.user_id %}
                                            <button class="btn btn-sm btn-link text-secondary edit-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-edit"></i></button>
                                        {% endif %}
                                        {% if session['user_id'] == comment.user_id or session['role'] == 'admin' %}
                                            <button class="btn btn-sm btn-link text-danger delete-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-trash"></i></button>
                                        {% endif %}
                                    </div>
                                </div>
                                <div class="comment-content-wrapper">
                                    <p class="comment-content mb-0" style="white-space: pre-wrap;">{{ comment.content }}</p>
                                </div>
                            </div>
                        </li>
                        {% endfor %}
                    </ul>
                    <form class="comment-form-new d-flex mt-2" data-video-id="{{ video.id }}">
                        <input name="comment_content" class="form-control" placeholder="اكتب تعليقاً..." required>
                        <button type="submit" class="btn btn-sm btn-primary ms-2">نشر</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <p class="text-center text-muted">{{ user.username }} لم يقم بنشر أي مقاطع فيديو بعد.</p>
    {% endfor %}
</div>
"""

students_content_block = """
<h1 class="mb-4 text-center">عرض الطلاب</h1>

<div class="card mb-4 shadow-sm">
    <div class="card-body">
        <h3 class="card-title">فلترة الطلاب</h3>
        <form action="{{ url_for('students') }}" method="get" class="row g-3 align-items-end">
            <div class="col-md-3">
                <label for="class_name" class="form-label">الصف:</label>
                <select name="class_name" id="class_name" class="form-select">
                    <option value="">كل الصفوف</option>
                    {% for c in all_classes %}
                        <option value="{{ c.class_name }}" {% if c.class_name == selected_class %}selected{% endif %}>{{ c.class_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="section_name" class="form-label">الشعبة:</label>
                <select name="section_name" id="section_name" class="form-select">
                    <option value="">كل الشعب</option>
                    {% for s in all_sections %}
                        <option value="{{ s.section_name }}" {% if s.section_name == selected_section %}selected{% endif %}>{{ s.section_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="search_name" class="form-label">اسم الطالب:</label>
                <input type="text" name="search_name" id="search_name" class="form-control" value="{{ search_name or '' }}" placeholder="ابحث بالاسم...">
            </div>
            <div class="col-md-1 d-grid">
                <button type="submit" class="btn btn-primary">بحث</button>
            </div>
            <div class="col-md-2 d-grid">
                <a href="{{ url_for('students') }}" class="btn btn-secondary">إلغاء الفلترة</a>
            </div>
        </form>
    </div>
</div>

<hr style="border-color: rgba(0,0,0,0.1);">

<div class="row">
    {% for student in students %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm text-center">
            <div class="card-body d-flex flex-column align-items-center">
                <img src="{{ url_for('static', filename='uploads/' + (student.profile_image or 'default.png')) }}" alt="Profile Image" class="rounded-circle mb-3" width="100" height="100" style="border: 3px solid #0d6efd; object-fit: cover;">
                <h5 class="card-title text-primary">{{ student.username }}</h5>
                <p class="card-text text-muted">
                    {{ student.class_name or 'صف غير محدد' }} - {{ student.section_name or 'شعبة غير محددة' }}
                </p>
                <a href="{{ url_for('profile', username=student.username) }}" class="btn btn-outline-primary mt-auto">عرض الملف الشخصي</a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <p class="text-center text-muted mt-5">لا يوجد طلاب يطابقون معايير البحث.</p>
    </div>
    {% endfor %}
</div>
"""

conversations_content_block = """
<style>
    .chat-container {
        display: flex;
        height: 75vh;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        overflow: hidden;
        background-color: #fff;
    }
    .chat-sidebar {
        width: 30%;
        border-left: 1px solid #ddd;
        display: flex;
        flex-direction: column;
    }
    .chat-main {
        width: 70%;
        display: flex;
        flex-direction: column;
    }
    .chat-sidebar-header, .chat-header {
        padding: 1rem;
        border-bottom: 1px solid #ddd;
        background-color: #f8f9fa;
    }
    .chat-user-list {
        overflow-y: auto;
        flex-grow: 1;
    }
    .chat-user-list .list-group-item {
        cursor: pointer;
    }
     .chat-user-list .list-group-item.active {
        background-color: #0d6efd;
        color: white;
    }
    .chat-messages {
        flex-grow: 1;
        padding: 1rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .message {
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
        max-width: 70%;
        white-space: pre-wrap;
    }
    .message.sent {
        background-color: #0d6efd;
        color: white;
        align-self: flex-end;
    }
    .message.received {
        background-color: #e9ecef;
        color: #212529;
        align-self: flex-start;
    }
    .chat-footer {
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
    #chat-welcome {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        text-align: center;
        color: #6c757d;
    }
</style>

<h1 class="mb-4 text-center">المحادثات</h1>

<div class="chat-container shadow-sm">
    <div class="chat-sidebar">
        <div class="chat-sidebar-header">
            <h5 class="mb-0">قائمة الطلاب</h5>
        </div>
        <div class="p-3 border-bottom">
            <div class="row g-2">
                <div class="col-12">
                    <select id="class_filter" class="form-select form-select-sm">
                        <option value="">كل الصفوف</option>
                        {% for c in all_classes %}
                            <option value="{{ c.class_name }}">{{ c.class_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-12">
                    <select id="section_filter" class="form-select form-select-sm">
                        <option value="">كل الشعب</option>
                        {% for s in all_sections %}
                            <option value="{{ s.section_name }}">{{ s.section_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-12">
                    <input type="text" id="name_filter" class="form-control form-control-sm" placeholder="ابحث بالاسم...">
                </div>
            </div>
        </div>
        <div class="chat-user-list">
            <div id="user-list-group" class="list-group list-group-flush">
                </div>
        </div>
    </div>

    <div class="chat-main">
        <div id="chat-welcome">
            <div class="text-center">
                <i class="fas fa-comments fa-3x mb-3"></i>
                <h4>اختر طالباً أو صفاً لبدء المحادثة</h4>
            </div>
        </div>
        
        <div id="chat-area" class="d-none">
            <div class="chat-header">
                <h5 id="chat-with-name" class="mb-0"></h5>
                <small id="chat-with-info" class="text-muted"></small>
            </div>
            <div class="chat-messages" id="chat-messages-container">
                </div>
            <div class="chat-footer">
                <form id="message-form" class="d-flex">
                    <input type="text" id="message-input" class="form-control" placeholder="اكتب رسالتك هنا..." autocomplete="off" required>
                    <button type="submit" class="btn btn-primary ms-2"><i class="fas fa-paper-plane"></i></button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

student_chat_content_block = """
<style>
    .student-chat-window {
        height: 70vh;
        display: flex;
        flex-direction: column;
    }
    .chat-messages {
        flex-grow: 1;
        padding: 1rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
    }
    .message {
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
        max-width: 70%;
        white-space: pre-wrap;
    }
    .message.sent {
        background-color: #0d6efd;
        color: white;
        align-self: flex-end;
    }
    .message.received {
        background-color: #e9ecef;
        color: #212529;
        align-self: flex-start;
    }
    .chat-footer {
        padding-top: 1rem;
    }
</style>

<div class="row justify-content-center">
    <div class="col-md-10 col-lg-8">
        <div class="card shadow-sm">
            <div class="card-header">
                <h4 class="mb-0"><i class="fas fa-comments me-2"></i>محادثة مع الإدارة</h4>
            </div>
            <div class="card-body student-chat-window">
                <div id="chat-messages-container" class="chat-messages mb-3">
                    </div>
                <div class="chat-footer">
                    <form id="student-message-form" class="d-flex">
                        <input type="text" id="message-input" class="form-control" placeholder="اكتب رسالتك..." autocomplete="off" required>
                        <button type="submit" class="btn btn-primary ms-2"><i class="fas fa-paper-plane"></i> إرسال</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
"""

# --- START: NEW TEMPLATE FOR VIDEO REVIEW ---
video_review_content_block = """
<h1 class="mb-4 text-center">مراجعة الفيديوهات</h1>
<p class="text-center text-muted">هنا تظهر جميع الفيديوهات التي بانتظار الموافقة.</p>

<div class="row row-cols-1 row-cols-md-2 g-4">
    {% for video in videos %}
    <div class="col">
        <div class="card h-100 video-card shadow-sm">
            <div class="card-header bg-transparent border-0 pt-3">
                <div class="d-flex align-items-center">
                     <img src="{{ url_for('static', filename='uploads/' + (video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
                    <div class="ms-3">
                        <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                            <span class="text-primary">{{ video.username }}</span>
                        </a>
                         <small class="d-block"><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime }}</span></small>
                    </div>
                </div>
            </div>
            
            <video controls class="card-img-top" style="background-color:#000; border-radius: 0;">
                <source src="{{ url_for('static', filename='uploads/' + video.filepath) }}" type="video/mp4">
            </video>
            
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ video.title }}</h5>
                
                <div class="alert alert-warning p-2 d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-bold"><i class="fas fa-clock me-2"></i>بانتظار الموافقة</span>
                    <div class="btn-group">
                        <form action="{{ url_for('approve_video', video_id=video.id) }}" method="post" class="d-inline">
                            <button type="submit" class="btn btn-sm btn-success">موافقة</button>
                        </form>
                        <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                            <button type="submit" class="btn btn-sm btn-danger">حذف</button>
                        </form>
                    </div>
                </div>

                 <small><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime('%Y-%m-%d') }}</span></small>
                
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <div class="like-section">
                        <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"><i class="fas fa-heart fa-lg"></i></button>
                        <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
                    </div>
                    <div class="rating-display-stars text-warning" style="font-size: 1.5rem;">
                        {% set rating = video_ratings.get(video.id) %}
                        <span id="stars-display-{{ video.id }}">
                            {% if rating and rating.total_stars > 0 %} 
                                <i class="fas fa-star"></i> 
                                {{ rating.total_stars }} / {% if video.video_type == 'اثرائي' %}10{% else %}4{% endif %}
                            {% else %} 
                                <small class="text-muted">لم يُقيّم</small> 
                            {% endif %}
                        </span>
                    </div>
                </div>
                
                <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
                     <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
                    {% set current_rating = video_ratings.get(video.id) %}
                     <div class="mt-2">
                        {% if video.video_type == 'اثرائي' %}
                            <div class="row">
                                {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل'), ('filming_lighting', 'التصوير والإضاءة'), ('sound_quality', 'جودة الصوت'), ('behavior', 'السلوك'), ('cleanliness', 'النظافة'), ('location', 'موقع التصوير'), ('confidence', 'الثقة')] %}
                                <div class="col-md-6 col-12">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                        <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="d-flex justify-content-around flex-wrap">
                                {% for key, label in [('participation', 'المشاركة'), ('memorization', 'الحفظ'), ('pronunciation', 'النطق'), ('use_of_aids', 'الوسائل')] %}
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}-{{video.id}}" {% if current_rating and current_rating[key] %}checked{% endif %}>
                                    <label class="form-check-label" for="{{ key }}-{{video.id}}">{{ label }}</label>
                                </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                </form>
                
                <div class="comments-section mt-auto pt-3">
                     <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                        {% set comments = video_comments.get(video.id, {}).get('toplevel', []) %}
                        {% for comment in comments %}
                        <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                            <img src="{{ url_for('static', filename='uploads/' + (comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                            <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                                <div class="d-flex justify-content-between">
                                    <p class="comment-author fw-bold mb-0">
                                        {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                        {% if comment.role == 'admin' %}
                                            <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.username }}</span>
                                        {% else %}
                                            <span class="text-primary">{{ comment.username }}</span>
                                        {% endif %}
                                    </p>
                                    <div class="comment-actions">
                                        {% if session['role'] == 'admin' %}
                                        <button class="btn btn-sm btn-link text-secondary pin-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-thumbtack"></i></button>
                                        {% endif %}
                                        {% if session['user_id'] == comment.user_id %}
                                            <button class="btn btn-sm btn-link text-secondary edit-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-edit"></i></button>
                                        {% endif %}
                                        {% if session['user_id'] == comment.user_id or session['role'] == 'admin' %}
                                        <button class="btn btn-sm btn-link text-danger delete-comment-btn" data-comment-id="{{ comment.id }}"><i class="fas fa-trash"></i></button>
                                        {% endif %}
                                    </div>
                                </div>
                                <div class="comment-content-wrapper">
                                    <p class="comment-content mb-0" style="white-space: pre-wrap;">{{ comment.content }}</p>
                                </div>
                            </div>
                        </li>
                        {% endfor %}
                    </ul>
                    <form class="comment-form-new d-flex mt-2" data-video-id="{{ video.id }}">
                        <input name="comment_content" class="form-control" placeholder="اكتب تعليقاً..." required>
                        <button type="submit" class="btn btn-sm btn-primary ms-2">نشر</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <p class="text-center text-muted mt-5 fs-4">لا توجد فيديوهات للمراجعة حالياً. <i class="fas fa-check-circle text-success"></i></p>
    </div>
    {% endfor %}
</div>
"""
# --- END: NEW TEMPLATE ---
edit_user_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل الملف الشخصي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style> body { background-color: #f8f9fa; } </style>
</head>
<body>
    <div class="container mt-5 mb-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h2>تعديل حساب: {{ user.username }}</h2>
                        {# START: NEW/MODIFIED - Conditional Alerts #}
                        {% if user.profile_reset_required and user.role == 'student' %}
                        <div class="alert alert-info mt-2"><b>سنة دراسية جديدة!</b> الرجاء تحديث الصف والشعبة للمتابعة.</div>
                        {% elif not user.is_profile_complete and user.role == 'student' %}
                        <div class="alert alert-warning mt-2"><b>ملاحظة:</b> يجب عليك إكمال جميع الحقول التي تحمل علامة (*) للمتابعة.</div>
                        {% endif %}
                        {# END: NEW/MODIFIED - Conditional Alerts #}
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}{% for category, message in messages %}<div class="alert alert-{{ category }}">{{ message }}</div>{% endfor %}{% endif %}
                        {% endwith %}
                        <form method="post" enctype="multipart/form-data">
                            
                            <h4>معلومات الحساب الأساسية</h4>
                            <hr>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="username" class="form-label">اسم المستخدم</label>
                                    <input type="text" class="form-control" id="username" name="username" value="{{ user.username or '' }}" {% if session['role'] != 'admin' %}readonly{% endif %} required>
                                </div>
                                
                                {% if session['role'] == 'admin' %}
                                <div class="col-md-6 mb-3">
                                    <label for="password" class="form-label">كلمة المرور الجديدة (اتركه فارغاً لعدم التغيير)</label>
                                    <input type="password" class="form-control" id="password" name="password">
                                </div>
                                {% endif %}
                            </div>

                            {% if user.role == 'student' %}
                            <h4 class="mt-4">المعلومات الشخصية للطالب</h4>
                            <hr>
                            
                            {# START: MODIFIED - Added required class/section for new year #}
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="class_name" class="form-label">الصف <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="class_name" name="class_name" value="{{ user.class_name or '' }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="section_name" class="form-label">الشعبة <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="section_name" name="section_name" value="{{ user.section_name or '' }}" required>
                                </div>
                            </div>
                            {# END: MODIFIED - Added required class/section for new year #}

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="full_name" class="form-label">الاسم الرباعي <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="full_name" name="full_name" value="{{ user.full_name or '' }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="phone_number" class="form-label">رقم الهاتف <span class="text-danger">*</span></label>
                                    <input type="tel" class="form-control" id="phone_number" name="phone_number" value="{{ user.phone_number or '' }}" required>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="address" class="form-label">عنوان السكن <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="address" name="address" value="{{ user.address or '' }}" required>
                            </div>
                            
                             <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="father_education" class="form-label">التحصيل الدراسي للأب <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="father_education" name="father_education" value="{{ user.father_education or '' }}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="mother_education" class="form-label">التحصيل الدراسي للأم <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="mother_education" name="mother_education" value="{{ user.mother_education or '' }}" required>
                                </div>
                            </div>
                            {% endif %}

                            <h4 class="mt-4">الصورة الشخصية</h4>
                            <hr>
                            <div class="mb-3">
                                <label for="profile_image" class="form-label">تغيير الصورة الشخصية (اختياري)</label>
                                <input type="file" class="form-control" id="profile_image" name="profile_image" accept="image/*">
                                {% if user.profile_image %}<img src="{{ url_for('static', filename='uploads/' + user.profile_image) }}" alt="Profile Image" width="100" class="mt-2 rounded">{% endif %}
                            </div>

                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary btn-lg">حفظ التغييرات</button>
                                {# START: MODIFIED - Disable cancel button if profile update is required #}
                                <a href="{{ url_for('profile', username=user.username) }}" class="btn btn-secondary {% if user.is_profile_complete == 0 or user.profile_reset_required == 1 %}disabled{% endif %}">إلغاء والعودة للملف الشخصي</a>
                                {# END: MODIFIED #}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# START: MODIFIED CODE BLOCK FOR ADMIN CHAT
conversations_script_block = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const classFilter = document.getElementById('class_filter');
    const sectionFilter = document.getElementById('section_filter');
    const nameFilter = document.getElementById('name_filter');
    const userListGroup = document.getElementById('user-list-group');
    
    const chatWelcome = document.getElementById('chat-welcome');
    const chatArea = document.getElementById('chat-area');
    const chatWithName = document.getElementById('chat-with-name');
    const chatWithInfo = document.getElementById('chat-with-info');
    const messagesContainer = document.getElementById('chat-messages-container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');

    let currentConversation = { type: null, id: null, name: null, class: null, section: null };
    let pollingInterval = null; // To hold the interval for fetching messages

    // Function to fetch and display users
    async function fetchUsers() {
        const className = classFilter.value;
        const sectionName = sectionFilter.value;
        const searchName = nameFilter.value;

        try {
            const response = await fetch(`/api/conversations/users?class_name=${className}&section_name=${sectionName}&search_name=${searchName}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const users = await response.json();
            
            userListGroup.innerHTML = ''; // Clear current list

            // Add group chat option if a class is selected
            if (className) {
                 const groupName = sectionName ? `جميع طلاب ${className} - ${sectionName}` : `جميع طلاب ${className}`;
                 const groupId = sectionName ? `${className}__${sectionName}` : `${className}`;
                 const groupItem = document.createElement('a');
                 groupItem.className = 'list-group-item list-group-item-action fw-bold text-primary';
                 groupItem.href = '#';
                 groupItem.dataset.type = 'group';
                 groupItem.dataset.class = className;
                 groupItem.dataset.section = sectionName || '';
                 groupItem.innerHTML = `<i class="fas fa-users me-2"></i> ${groupName}`;
                 userListGroup.appendChild(groupItem);
            }

            // Add individual students
            users.forEach(user => {
                const userItem = document.createElement('a');
                userItem.className = 'list-group-item list-group-item-action';
                userItem.href = '#';
                userItem.dataset.type = 'user';
                userItem.dataset.id = user.id;
                userItem.dataset.name = user.username;
                userItem.innerHTML = `
                    <div class="d-flex align-items-center">
                        <img src="/static/uploads/${user.profile_image || 'default.png'}" class="rounded-circle me-2" width="40" height="40">
                        <div>
                            <div>${user.username}</div>
                            <small class="text-muted">${user.class_name || ''} - ${user.section_name || ''}</small>
                        </div>
                    </div>`;
                userListGroup.appendChild(userItem);
            });

        } catch (error) {
            console.error('Failed to fetch users:', error);
            userListGroup.innerHTML = '<li class="list-group-item">خطأ في تحميل قائمة الطلاب.</li>';
        }
    }

    // Function to fetch and display messages
    async function fetchMessages(userId) {
        try {
            const response = await fetch(`/api/messages/${userId}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            messagesContainer.innerHTML = ''; // Clear messages
            data.messages.forEach(msg => {
                appendMessage(msg.sender_id, msg.content, msg.timestamp);
            });
            if (data.messages.length > 0) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

        } catch (error) {
            console.error('Failed to fetch messages:', error);
            if (pollingInterval) clearInterval(pollingInterval);
        }
    }
    
    // Helper function to format timestamp
    function formatChatTimestamp(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit', hour12: true });
    }

    // CORRECTED function to append a single message
    function appendMessage(senderId, content, timestamp) {
        const messageDiv = document.createElement('div');
        const adminId = {{ session['user_id'] }};
        messageDiv.classList.add('message', senderId == adminId ? 'sent' : 'received');
        
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-timestamp" style="font-size: 0.7rem; text-align: left; margin-top: 5px; opacity: 0.8;">
                ${formatChatTimestamp(timestamp)}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
    }
    
    // Handle submitting the message form
    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = messageInput.value.trim();
        if (!content || !currentConversation.type) return;

        const body = {
            content: content,
            type: currentConversation.type,
            id: currentConversation.id,
            class_name: currentConversation.class,
            section_name: currentConversation.section
        };

        try {
            const response = await fetch('/api/messages/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) throw new Error('Failed to send message');
            const result = await response.json();
            
            if (result.status === 'success') {
                if (currentConversation.type === 'user') {
                    appendMessage({{ session['user_id'] }}, content, new Date().toISOString());
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                } else {
                    alert('تم إرسال الرسالة إلى جميع الطلاب المحددين بنجاح.');
                }
                messageInput.value = '';
            } else {
                alert('خطأ: ' + result.message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('حدث خطأ أثناء إرسال الرسالة.');
        }
    });
    
    // Event listener for user/group selection
    userListGroup.addEventListener('click', function(e) {
        const target = e.target.closest('.list-group-item');
        if (!target) return;
        
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }

        document.querySelectorAll('.list-group-item.active').forEach(item => item.classList.remove('active'));
        target.classList.add('active');

        const type = target.dataset.type;
        
        if (type === 'user') {
            const userId = target.dataset.id;
            const userName = target.dataset.name;
            currentConversation = { type: 'user', id: userId, name: userName, class: null, section: null };
            chatWithName.textContent = userName;
            chatWithInfo.textContent = 'محادثة فردية';
            
            fetchMessages(userId);
            pollingInterval = setInterval(() => fetchMessages(userId), 5000);

        } else if (type === 'group') {
            const className = target.dataset.class;
            const sectionName = target.dataset.section;
            currentConversation = { type: 'group', id: null, name: null, class: className, section: sectionName };
            chatWithName.textContent = sectionName ? `رسالة إلى: ${className} - ${sectionName}` : `رسالة إلى: ${className}`;
            chatWithInfo.textContent = 'رسالة جماعية';
            messagesContainer.innerHTML = '<div class="text-center text-muted p-3">أنت على وشك إرسال رسالة جماعية. لن يظهر سجل المحادثات هنا.</div>';
        }
        
        chatWelcome.classList.add('d-none');
        chatArea.classList.remove('d-none');
        messageInput.focus();
    });

    [classFilter, sectionFilter, nameFilter].forEach(el => {
        el.addEventListener('input', fetchUsers);
    });

    fetchUsers();
});
</script>
"""
# END: MODIFIED CODE BLOCK

# START: MODIFIED CODE BLOCK FOR STUDENT CHAT
student_chat_script_block = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('chat-messages-container');
    const messageForm = document.getElementById('student-message-form');
    const messageInput = document.getElementById('message-input');
    const adminId = {{ admin_id }};
    const studentId = {{ session['user_id'] }};

    // Helper function to format timestamp
    function formatChatTimestamp(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit', hour12: true });
    }

    // CORRECTED function to append a message with its content and timestamp
    function appendMessage(senderId, content, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', senderId == studentId ? 'sent' : 'received');
        
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-timestamp" style="font-size: 0.7rem; text-align: left; margin-top: 5px; opacity: 0.8;">
                ${formatChatTimestamp(timestamp)}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
    }

    // CORRECTED function to fetch messages and pass the timestamp
    async function fetchMessages() {
        try {
            const response = await fetch('/api/student/messages');
            if (!response.ok) return;
            const data = await response.json();
            
            messagesContainer.innerHTML = ''; // Clear before redraw
            
            // Pass the timestamp to the appendMessage function
            data.messages.forEach(msg => {
                appendMessage(msg.sender_id, msg.content, msg.timestamp);
            });

            if (data.messages.length > 0) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
        } catch (error) {
            console.error("Error fetching messages:", error);
        }
    }

    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = messageInput.value.trim();
        if (!content) return;

        try {
            const response = await fetch('/api/student/messages/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content, receiver_id: adminId })
            });
            if (!response.ok) throw new Error('Failed to send');
            const result = await response.json();

            if(result.status === 'success') {
                // Pass the current time for the new message
                appendMessage(studentId, content, new Date().toISOString());
                messageInput.value = '';
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                alert(result.message || 'Failed to send message');
            }
        } catch (error) {
            console.error("Error sending message:", error);
            alert('An error occurred while sending the message.');
        }
    });

    // Fetch messages on load and then every 5 seconds
    fetchMessages();
    setInterval(fetchMessages, 5000); 
});
</script>
"""
# END: MODIFIED CODE BLOCK

content_blocks = {
    'index': index_content_block,
    'archive': archive_content_block,
    'login': login_content_block,
    'admin_dashboard': admin_dashboard_content_block,
    'reports': reports_content_block,
    'profile': profile_content_block,
    'students': students_content_block,
    'conversations': conversations_content_block,
    'student_chat': student_chat_content_block,
    'video_review': video_review_content_block, # <--- السطر الجديد المضاف
}

def render_page(template_name, **context):
    """Helper function to render pages by injecting content into the base template."""
    content_block = content_blocks.get(template_name, '')
    final_html = base_html.replace('{% block content %}{% endblock %}', content_block)
    
    scripts_block = context.get("scripts_block", "")
    final_html = final_html.replace('{% block scripts %}{% endblock %}', scripts_block)
    
    context['professor_image_url_1'] = professor_image_url_1
    context['professor_image_url_2'] = professor_image_url_2

    return render_template_string(final_html, **context)
# ----------------- CONFIGURATION -----------------
app = Flask(__name__)
PERSISTENT_DATA_PATH = '/data'
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_changed'

# --- DYNAMICALLY SET UPLOAD FOLDER PATH ---
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER_PATH = os.path.join(PERSISTENT_DATA_PATH, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_PATH
# ---

app.config['DATABASE'] = os.path.join(PERSISTENT_DATA_PATH, 'school_platform.db')
ALLOWED_EXTENSIONS_IMAGES = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi'}
VIDEO_ARCHIVE_DAYS = 7


# ----------------- DATABASE SETUP -----------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    # --- AUTOMATICALLY CREATE FOLDER AND DEFAULT IMAGE ---
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        print(f"Creating upload folder at: {app.config['UPLOAD_FOLDER']}")
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    default_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default.png')
    if not os.path.exists(default_image_path):
        try:
            # This is a trick to create a tiny, valid, transparent PNG file programmatically.
            import base64
            png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')
            with open(default_image_path, 'wb') as f:
                f.write(png_data)
            print("Created default.png in the uploads folder.")
        except Exception as e:
            print(f"Could not create default.png: {e}")
    # ---

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create base tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
                profile_image TEXT DEFAULT 'default.png',
                class_name TEXT,
                section_name TEXT,
                session_revocation_token INTEGER DEFAULT 0,
                
                full_name TEXT,
                address TEXT,
                phone_number TEXT,
                father_education TEXT,
                mother_education TEXT,
                is_profile_complete INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0
            )''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, filepath TEXT NOT NULL,
                user_id INTEGER NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, user_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL, parent_id INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (video_id) REFERENCES videos (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT, video_id INTEGER NOT NULL, admin_id INTEGER NOT NULL,
                participation INTEGER DEFAULT 0, memorization INTEGER DEFAULT 0,
                pronunciation INTEGER DEFAULT 0, use_of_aids INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (video_id) REFERENCES videos (id),
                FOREIGN KEY (admin_id) REFERENCES users (id), UNIQUE(video_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, video_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (video_id) REFERENCES videos (id),
                FOREIGN KEY (user_id) REFERENCES users (id), UNIQUE(video_id, user_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suspensions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                end_date DATETIME NOT NULL, reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS star_bank (
                user_id INTEGER PRIMARY KEY,
                banked_stars INTEGER NOT NULL DEFAULT 0,
                last_updated_week_start_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )''')

        # --- Schema Migration (Automatically add missing columns) ---
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column['name'] for column in cursor.fetchall()]
        
        new_profile_cols = {
            'full_name': 'TEXT', 'address': 'TEXT', 'phone_number': 'TEXT',
            'father_education': 'TEXT', 'mother_education': 'TEXT',
            'is_profile_complete': 'INTEGER DEFAULT 0', 'is_muted': 'INTEGER DEFAULT 0',
            'profile_reset_required': 'INTEGER DEFAULT 0'
        }
        for col, col_type in new_profile_cols.items():
            if col not in user_columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")

        cursor.execute("PRAGMA table_info(videos)")
        video_columns = [column['name'] for column in cursor.fetchall()]
        if 'video_type' not in video_columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN video_type TEXT NOT NULL CHECK(video_type IN ('منهجي', 'اثرائي')) DEFAULT 'منهجي'")
        
        # --- START: MODIFICATION FOR VIDEO APPROVAL ---
        if 'is_approved' not in video_columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN is_approved INTEGER DEFAULT 0")
        # --- END: MODIFICATION FOR VIDEO APPROVAL ---

        cursor.execute("PRAGMA table_info(comments)")
        comment_columns = [column['name'] for column in cursor.fetchall()]
        if 'is_pinned' not in comment_columns:
            cursor.execute("ALTER TABLE comments ADD COLUMN is_pinned INTEGER DEFAULT 0")

        cursor.execute("PRAGMA table_info(video_ratings)")
        rating_columns = [c['name'] for c in cursor.fetchall()]
        new_rating_cols = {
            'filming_lighting': 'INTEGER DEFAULT 0', 'sound_quality': 'INTEGER DEFAULT 0',
            'behavior': 'INTEGER DEFAULT 0', 'cleanliness': 'INTEGER DEFAULT 0',
            'location': 'INTEGER DEFAULT 0', 'confidence': 'INTEGER DEFAULT 0'
        }
        for col, col_type in new_rating_cols.items():
            if col not in rating_columns:
                cursor.execute(f"ALTER TABLE video_ratings ADD COLUMN {col} {col_type}")

        # --- End Schema Migration ---

        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        if cursor.fetchone() is None:
            hashed_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password, role, is_profile_complete) VALUES (?, ?, ?, 1)",
                           ('admin', hashed_password, 'admin'))
        
        db.commit()
        print("Database structure is ready.")

# ----------------- HELPER FUNCTIONS -----------------
def get_champion_statuses():
    db = get_db()
    today = date.today()
    statuses = {}
    start_of_month = today.replace(day=1)
    days_since_saturday = (today.weekday() + 2) % 7
    start_of_week = today - timedelta(days=days_since_saturday)
    start_of_previous_week = start_of_week - timedelta(days=7)
    superhero_query = """
        SELECT v.user_id FROM video_ratings vr JOIN videos v ON vr.video_id = v.id
        WHERE v.video_type = 'اثرائي' AND 
              (vr.participation + vr.memorization + vr.pronunciation + vr.use_of_aids +
               vr.filming_lighting + vr.sound_quality + vr.behavior + vr.cleanliness +
               vr.location + vr.confidence) = 10 AND date(v.timestamp) >= ?
    """
    superhero_rows = db.execute(superhero_query, (start_of_month.strftime('%Y-%m-%d'),)).fetchall()
    for row in superhero_rows:
        statuses[row['user_id']] = 'بطل خارق'
    end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1)) if start_of_month.month != 12 else date(start_of_month.year, 12, 31)
    monthly_champions_query = """
        SELECT v.user_id, SUM(vr.participation + vr.memorization + vr.pronunciation + vr.use_of_aids +
                vr.filming_lighting + vr.sound_quality + vr.behavior + vr.cleanliness +
                vr.location + vr.confidence) as total_stars
        FROM video_ratings vr JOIN videos v ON vr.video_id = v.id
        WHERE v.video_type = 'اثرائي' AND date(v.timestamp) BETWEEN ? AND ?
        GROUP BY v.user_id ORDER BY total_stars DESC LIMIT 1;
    """
    monthly_champion_row = db.execute(monthly_champions_query, (start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d'))).fetchone()
    if monthly_champion_row and monthly_champion_row['total_stars'] and monthly_champion_row['total_stars'] > 0:
        monthly_champion_id = monthly_champion_row['user_id']
        if monthly_champion_id not in statuses:
            statuses[monthly_champion_id] = 'بطل الشهر'
    students = db.execute("SELECT id FROM users WHERE role = 'student'").fetchall()
    for student in students:
        student_id = student['id']
        carried_stars = 0
        bank_entry = db.execute(
            "SELECT banked_stars FROM star_bank WHERE user_id = ? AND last_updated_week_start_date = ?",
            (student_id, start_of_previous_week.strftime('%Y-%m-%d'))
        ).fetchone()
        if bank_entry: carried_stars = bank_entry['banked_stars']
        new_stars_row = db.execute("""
            SELECT SUM(vr.participation + vr.memorization + vr.pronunciation + vr.use_of_aids) as stars
            FROM video_ratings vr JOIN videos v ON vr.video_id = v.id
            WHERE v.video_type = 'منهجي' AND v.user_id = ? AND date(v.timestamp) >= ?
        """, (student_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
        new_stars = new_stars_row['stars'] if new_stars_row and new_stars_row['stars'] is not None else 0
        total_score_this_week = carried_stars + new_stars
        stars_to_bank_for_next_week = 0
        if total_score_this_week >= 4:
            if student_id not in statuses: statuses[student_id] = 'بطل الأسبوع'
            stars_to_bank_for_next_week = 0 
        else:
            stars_to_bank_for_next_week = total_score_this_week
        db.execute("""
            INSERT INTO star_bank (user_id, banked_stars, last_updated_week_start_date) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            banked_stars = excluded.banked_stars, last_updated_week_start_date = excluded.last_updated_week_start_date;
        """, (student_id, stars_to_bank_for_next_week, start_of_week.strftime('%Y-%m-%d')))
    db.commit()
    return statuses

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    if not value: return ""
    dt_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if isinstance(value, str) else value
    return dt_obj.strftime(format) if dt_obj else value

app.jinja_env.filters['strftime'] = format_datetime

@app.before_request
def before_request_handler():
    # Session revocation and profile completion check
    if 'user_id' in session and 'token' in session:
        db = get_db()
        user = db.execute('SELECT session_revocation_token, is_profile_complete, role, profile_reset_required FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if not user or user['session_revocation_token'] != session['token']:
            session.clear()
            flash('تم تسجيل خروجك بواسطة المسؤول.', 'warning')
            return redirect(url_for('login'))
        
        allowed_endpoints = ['login', 'logout', 'edit_user', 'static', 'my_messages', 'api_get_student_messages', 'api_send_student_message']
    
        if user['role'] == 'student' and request.endpoint not in allowed_endpoints:
            if not user['is_profile_complete']:
                flash('الرجاء إكمال ملفك الشخصي أولاً للمتابعة. الحقول إلزامية.', 'warning')
                return redirect(url_for('edit_user', user_id=session['user_id']))
            
            if user['profile_reset_required']:
                flash('سنة دراسية جديدة! الرجاء تحديث الصف والشعبة للمتابعة.', 'info')
                return redirect(url_for('edit_user', user_id=session['user_id']))
    
    # Unread message count for students
    g.unread_count = 0
    if session.get('role') == 'student':
        db = get_db()
        count = db.execute(
            'SELECT COUNT(id) FROM messages WHERE receiver_id = ? AND is_read = 0',
            (session['user_id'],)
        ).fetchone()[0]
        g.unread_count = count

    # --- START: NEW CODE FOR VIDEO REVIEW COUNT ---
    g.unapproved_count = 0
    if session.get('role') == 'admin':
        db = get_db()
        count = db.execute(
            'SELECT COUNT(id) FROM videos WHERE is_approved = 0'
        ).fetchone()[0]
        g.unapproved_count = count
    # --- END: NEW CODE ---


# ----------------- AUTHENTICATION ROUTES -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            suspension = db.execute('SELECT * FROM suspensions WHERE user_id = ? AND end_date > ?', (user['id'], datetime.now())).fetchone()
            if suspension:
                end_date_formatted = suspension["end_date"].split('.')[0]
                flash(f'حسابك موقوف حتى {end_date_formatted}. السبب: {suspension["reason"]}', 'danger')
                return render_page('login')

            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['token'] = user['session_revocation_token']
            
            if user['role'] == 'student' and not user['is_profile_complete']:
                flash('مرحباً بك! يرجى إكمال معلومات ملفك الشخصي للمتابعة.', 'info')
                return redirect(url_for('edit_user', user_id=user['id']))
            
            if user['role'] == 'student' and user['profile_reset_required']:
                flash('سنة دراسية جديدة! يرجى تحديث الصف والشعبة للمتابعة.', 'info')
                return redirect(url_for('edit_user', user_id=user['id']))
                
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
            
    return render_page('login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
# ----------------- SHARED DATA FETCHING LOGIC -----------------
def get_common_video_data(video_ids):
    db = get_db()
    video_ratings = {}
    video_likes = {}
    user_liked_videos = set()
    video_comments = defaultdict(lambda: defaultdict(list))

    if not video_ids:
        return video_ratings, video_likes, user_liked_videos, video_comments

    placeholders = ','.join('?' for _ in video_ids)
    
    ratings_data = db.execute(f'''
        SELECT vr.*, v.video_type 
        FROM video_ratings vr JOIN videos v ON vr.video_id = v.id 
        WHERE vr.video_id IN ({placeholders})
    ''', video_ids).fetchall()

    for item in ratings_data:
        rating_dict = dict(item)
        if rating_dict['video_type'] == 'اثرائي':
            total_stars = sum(rating_dict.get(key, 0) for key in 
                              ['participation', 'memorization', 'pronunciation', 'use_of_aids', 
                               'filming_lighting', 'sound_quality', 'behavior', 'cleanliness', 
                               'location', 'confidence'])
        else: # منهجي
            total_stars = sum(rating_dict.get(key, 0) for key in 
                              ['participation', 'memorization', 'pronunciation', 'use_of_aids'])
        rating_dict['total_stars'] = total_stars
        video_ratings[item['video_id']] = rating_dict

    likes_data = db.execute(f'SELECT video_id, COUNT(id) as count FROM video_likes WHERE video_id IN ({placeholders}) GROUP BY video_id', video_ids).fetchall()
    video_likes = {item['video_id']: item['count'] for item in likes_data}

    if 'user_id' in session:
        user_likes_rows = db.execute(f'SELECT video_id FROM video_likes WHERE user_id = ? AND video_id IN ({placeholders})', [session['user_id']] + video_ids).fetchall()
        user_liked_videos = {row['video_id'] for row in user_likes_rows}

    comments_data = db.execute(f'''
        SELECT c.id, c.content, c.video_id, c.parent_id, c.timestamp, u.username, u.role, u.profile_image, c.user_id, c.is_pinned
        FROM comments c JOIN users u ON c.user_id = u.id 
        WHERE c.video_id IN ({placeholders}) ORDER BY c.is_pinned DESC, c.timestamp ASC
    ''', video_ids).fetchall()
    
    for comment in comments_data:
        video_comments[comment['video_id']]['toplevel'].append(dict(comment))

    return video_ratings, video_likes, user_liked_videos, video_comments
    
common_scripts_block = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const videoId = this.dataset.videoId;
            fetch(`/video/${videoId}/like`, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById(`likes-count-${videoId}`).textContent = data.likes_count;
                    this.classList.toggle('text-danger', data.user_likes);
                    this.classList.toggle('text-secondary', !data.user_likes);
                }
            }).catch(console.error);
        });
    });
    
    document.querySelectorAll('.comment-form-new').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const videoId = this.dataset.videoId;
            const commentInput = this.querySelector('input[name="comment_content"]');
            if (!commentInput.value.trim()) return;
            const formData = new FormData();
            formData.append('comment_content', commentInput.value.trim());
            fetch(`/video/${videoId}/comment`, { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else { alert(data.message || "An error occurred"); }
            }).catch(console.error);
        });
    });

    document.querySelectorAll('.rating-form').forEach(form => {
        form.addEventListener('change', function() {
            const videoId = this.dataset.videoId;
            const videoType = this.dataset.videoType;
            const ratingData = {};

            this.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                ratingData[checkbox.name] = checkbox.checked ? 1 : 0;
            });

            fetch(`/video/${videoId}/rate`, { 
                method: 'POST', 
                body: JSON.stringify(ratingData), 
                headers: { 'Content-Type': 'application/json' } 
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const starsDisplay = document.getElementById(`stars-display-${videoId}`);
                    if (starsDisplay) {
                        if (data.total_stars > 0) {
                            const max_stars = videoType === 'اثرائي' ? 10 : 4;
                            starsDisplay.innerHTML = `<i class="fas fa-star"></i> ${data.total_stars} / ${max_stars}`;
                        } else {
                            starsDisplay.innerHTML = `<small class="text-muted">لم يُقيّم بعد</small>`;
                        }
                    }
                    if (data.champion_message) { 
                        location.reload();
                    }
                }
            }).catch(console.error);
        });
    });

    document.body.addEventListener('click', function(event) {
        const deleteButton = event.target.closest('.delete-comment-btn');
        if (deleteButton) {
            event.preventDefault();
            const commentId = deleteButton.dataset.commentId;
            if (confirm('هل أنت متأكد من حذف هذا التعليق؟')) {
                fetch(`/comment/${commentId}/delete`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const commentElement = document.getElementById(`comment-${commentId}`);
                        if(commentElement) commentElement.remove();
                    } else { alert('خطأ: ' + data.message); }
                }).catch(console.error);
            }
        }
    
        const pinButton = event.target.closest('.pin-comment-btn');
        if (pinButton) {
            event.preventDefault();
            const commentId = pinButton.dataset.commentId;
            fetch(`/comment/${commentId}/pin`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') { location.reload(); } 
                else { alert('خطأ: ' + data.message); }
            }).catch(console.error);
        }
    
        const editButton = event.target.closest('.edit-comment-btn');
        if (editButton) {
            event.preventDefault();
            const commentId = editButton.dataset.commentId;
            const commentLi = document.getElementById(`comment-${commentId}`);
            const contentWrapper = commentLi.querySelector('.comment-content-wrapper');
            const currentContent = contentWrapper.querySelector('.comment-content').innerText;
            if (contentWrapper.querySelector('.edit-form')) return;
            contentWrapper.innerHTML = `
                <form class="edit-form d-flex mt-2" data-comment-id="${commentId}">
                    <textarea name="content" class="form-control" rows="2" required>${currentContent}</textarea>
                    <div class="ms-2 d-flex flex-column">
                        <button type="submit" class="btn btn-sm btn-success mb-1">حفظ</button>
                        <button type="button" class="btn btn-sm btn-secondary cancel-edit">إلغاء</button>
                    </div>
                </form>`;
        }

        const cancelButton = event.target.closest('.cancel-edit');
        if (cancelButton) {
            event.preventDefault();
            const form = cancelButton.closest('.edit-form');
            const originalContent = form.querySelector('textarea').defaultValue;
            const contentWrapper = form.parentElement;
            contentWrapper.innerHTML = `<p class="comment-content mb-0" style="white-space: pre-wrap;">${originalContent}</p>`;
        }
    });

    document.body.addEventListener('submit', function(event) {
        if (event.target.matches('.edit-form')) {
            event.preventDefault();
            const form = event.target;
            const commentId = form.dataset.commentId;
            const contentWrapper = form.parentElement;
            const contentInput = form.querySelector('textarea[name="content"]');
            const formData = new FormData();
            formData.append('content', contentInput.value.trim());
            fetch(`/comment/${commentId}/edit`, { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    contentWrapper.innerHTML = `<p class="comment-content mb-0" style="white-space: pre-wrap;">${data.new_content}</p>`;
                } else { alert('خطأ: ' + data.message); }
            }).catch(console.error);
        }
    });
});
</script>
"""

# ----------------- CORE APPLICATION ROUTES -----------------
@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    
    all_classes = []
    all_sections = []
    selected_class = request.args.get('class_name', '')
    selected_section = request.args.get('section_name', '')
    selected_video_type = request.args.get('video_type', '')

    if session.get('role') == 'admin':
        all_classes = db.execute("SELECT DISTINCT class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND class_name != '' ORDER BY class_name").fetchall()
        all_sections = db.execute("SELECT DISTINCT section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND section_name != '' ORDER BY section_name").fetchall()

    posts = db.execute('SELECT p.content, p.timestamp, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE u.role = "admin" ORDER BY p.timestamp DESC').fetchall()
    cutoff_date = datetime.now() - timedelta(days=VIDEO_ARCHIVE_DAYS)
    
    # --- START: MODIFICATION FOR VIDEO APPROVAL ---
    video_query = '''
        SELECT v.id, v.title, v.filepath, v.timestamp, v.video_type, v.is_approved, u.username, u.role, u.id as user_id, u.profile_image 
        FROM videos v JOIN users u ON v.user_id = u.id 
        WHERE v.timestamp >= ? AND v.is_approved = 1
    '''
    # --- END: MODIFICATION FOR VIDEO APPROVAL ---
    params = [cutoff_date]

    if session.get('role') == 'admin' and selected_class:
        video_query += ' AND u.class_name = ?'
        params.append(selected_class)
    if session.get('role') == 'admin' and selected_section:
        video_query += ' AND u.section_name = ?'
        params.append(selected_section)
        
    if selected_video_type in ['منهجي', 'اثرائي']:
        video_query += ' AND v.video_type = ?'
        params.append(selected_video_type)

    video_query += ' ORDER BY v.timestamp DESC'
    
    videos = db.execute(video_query, tuple(params)).fetchall()
    
    video_ids = [v['id'] for v in videos]
    video_ratings, video_likes, user_liked_videos, video_comments = get_common_video_data(video_ids)
    
    return render_page('index', 
                       posts=posts, 
                       videos=videos, 
                       video_ratings=video_ratings, 
                       video_comments=video_comments, 
                       champion_statuses=get_champion_statuses(),
                       video_likes=video_likes, 
                       user_liked_videos=user_liked_videos, 
                       scripts_block=common_scripts_block,
                       all_classes=all_classes,
                       all_sections=all_sections,
                       selected_class=selected_class,
                       selected_section=selected_section,
                       selected_video_type=selected_video_type
                       )

@app.route('/archive')
def archive():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()

    selected_class = request.args.get('class_name', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    selected_video_type = request.args.get('video_type', '')
    
    all_classes = db.execute("SELECT DISTINCT class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND class_name != '' ORDER BY class_name").fetchall()

    cutoff_date = datetime.now() - timedelta(days=VIDEO_ARCHIVE_DAYS)
    
    # --- START: MODIFICATION FOR VIDEO APPROVAL ---
    query = '''
        SELECT v.id, v.title, v.filepath, v.timestamp, v.video_type, v.is_approved, u.username, u.role, u.id as user_id, u.profile_image
        FROM videos v JOIN users u ON v.user_id = u.id 
        WHERE v.timestamp < ? AND v.is_approved = 1
    '''
    # --- END: MODIFICATION FOR VIDEO APPROVAL ---
    params = [cutoff_date]

    if selected_class:
        query += ' AND u.class_name = ?'
        params.append(selected_class)
    if start_date:
        query += ' AND date(v.timestamp) >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date(v.timestamp) <= ?'
        params.append(end_date)
    if selected_video_type in ['منهجي', 'اثرائي']:
        query += ' AND v.video_type = ?'
        params.append(selected_video_type)
    
    query += ' ORDER BY v.timestamp DESC'
    
    archived_videos = db.execute(query, tuple(params)).fetchall()

    video_ids = [v['id'] for v in archived_videos]
    video_ratings, video_likes, user_liked_videos, video_comments = get_common_video_data(video_ids)

    return render_page('archive', 
                       videos=archived_videos, 
                       video_ratings=video_ratings, 
                       video_comments=video_comments, 
                       champion_statuses=get_champion_statuses(),
                       video_likes=video_likes, 
                       user_liked_videos=user_liked_videos, 
                       scripts_block=common_scripts_block,
                       all_classes=all_classes,
                       selected_class=selected_class,
                       start_date=start_date,
                       end_date=end_date,
                       selected_video_type=selected_video_type
                      )


@app.route('/profile/<username>')
def profile(username):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if not user: return "User not found", 404

    # --- START: MODIFICATION FOR VIDEO APPROVAL ---
    # تعديل منطق الاستعلام عن الفيديوهات
    video_query = 'SELECT * FROM videos WHERE user_id = ?'
    params = [user['id']]
    
    # إذا كان الشخص الذي يشاهد الصفحة ليس المدير وليس صاحب الحساب
    if session.get('role') != 'admin' and session.get('user_id') != user['id']:
        video_query += ' AND is_approved = 1'
        
    video_query += ' ORDER BY timestamp DESC'
    
    user_videos = db.execute(video_query, tuple(params)).fetchall()
    # --- END: MODIFICATION FOR VIDEO APPROVAL ---

    video_ids = [v['id'] for v in user_videos]
    video_ratings, video_likes, user_liked_videos, video_comments = get_common_video_data(video_ids)
    
    return render_page('profile', user=user, videos=user_videos, user_status=get_champion_statuses().get(user['id']),
                       video_ratings=video_ratings, video_likes=video_likes, user_liked_videos=user_liked_videos, 
                       video_comments=video_comments, scripts_block=common_scripts_block)

# --- START: NEW ROUTE FOR VIDEO REVIEW ---
@app.route('/video_review')
def video_review():
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للوصول لهذه الصفحة.', 'danger')
        return redirect(url_for('index'))

    db = get_db()
    
    # جلب جميع الفيديوهات التي تنتظر الموافقة
    videos_to_review = db.execute('''
        SELECT v.id, v.title, v.filepath, v.timestamp, v.video_type, v.is_approved, 
               u.username, u.role, u.id as user_id, u.profile_image 
        FROM videos v JOIN users u ON v.user_id = u.id 
        WHERE v.is_approved = 0
        ORDER BY v.timestamp ASC
    ''').fetchall()

    video_ids = [v['id'] for v in videos_to_review]
    video_ratings, video_likes, user_liked_videos, video_comments = get_common_video_data(video_ids)

    return render_page('video_review',
                       videos=videos_to_review,
                       video_ratings=video_ratings,
                       video_likes=video_likes,
                       user_liked_videos=user_liked_videos,
                       video_comments=video_comments,
                       scripts_block=common_scripts_block # لإضافة وظائف التعليق والإعجاب...الخ
                      )
# --- END: NEW ROUTE ---

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['user_id'] != user_id and session['role'] != 'admin':
        flash('ليس لديك الصلاحية لتعديل هذا الحساب.', 'danger')
        return redirect(url_for('index'))

    db = get_db()
    user_to_edit = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user_to_edit:
        flash('المستخدم غير موجود.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if session['role'] == 'admin':
            new_username = request.form['username']
            if new_username != user_to_edit['username']:
                existing_user = db.execute('SELECT id FROM users WHERE username = ?', (new_username,)).fetchone()
                if existing_user:
                    flash('اسم المستخدم هذا موجود بالفعل. الرجاء اختيار اسم آخر.', 'danger')
                    return redirect(url_for('edit_user', user_id=user_id))
            
            db.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))

            new_password = request.form.get('password')
            if new_password:
                hashed_password = generate_password_hash(new_password)
                db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
        else:
            new_username = user_to_edit['username']

        if user_to_edit['role'] == 'student':
            full_name = request.form.get('full_name')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            class_name = request.form.get('class_name')
            section_name = request.form.get('section_name')
            father_education = request.form.get('father_education')
            mother_education = request.form.get('mother_education')

            is_profile_complete = all([full_name, phone_number, address, father_education, mother_education, class_name, section_name])
            
            profile_reset_required = 1
            if class_name and section_name:
                profile_reset_required = 0

            db.execute('''
                UPDATE users SET 
                    full_name = ?, phone_number = ?, address = ?, class_name = ?, 
                    section_name = ?, father_education = ?, mother_education = ?,
                    is_profile_complete = ?, profile_reset_required = ?
                WHERE id = ?
            ''', (full_name, phone_number, address, class_name, section_name, 
                  father_education, mother_education, 1 if is_profile_complete else 0, profile_reset_required, user_id))
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '' and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMAGES):
                filename = secure_filename(f"user_{user_id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, user_id))
        
        db.commit()
        
        if user_id == session.get('user_id') and new_username != session.get('username'):
             session['username'] = new_username

        flash('تم تحديث الحساب بنجاح!', 'success')
        if session['role'] == 'admin' or (not profile_reset_required and is_profile_complete):
             return redirect(url_for('profile', username=new_username))
        else:
            return redirect(url_for('edit_user', user_id=user_id))

    return render_template_string(edit_user_html, user=user_to_edit)
# ----------------- VIDEO & INTERACTION ROUTES -----------------
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    title = request.form['title']
    video_file = request.files.get('video_file')
    video_type = request.form.get('video_type')

    if not (title and video_file and video_file.filename and video_type and allowed_file(video_file.filename, ALLOWED_EXTENSIONS_VIDEOS)):
        flash('حدث خطأ أثناء رفع الفيديو. تأكد من ملء جميع الحقول وأن الملف من نوع مسموح.', 'danger')
        return redirect(url_for('index'))

    # --- بداية: التحقق من مدة الفيديو (باستخدام PyAV) ---
    
    temp_filename = f"temp_upload_{session['user_id']}_{secure_filename(video_file.filename)}"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    
    try:
        video_file.save(temp_filepath)

        # 2. التحقق من مدة الفيديو باستخدام PyAV
        try:
            with av.open(temp_filepath) as container:
                # container.duration يعطي المدة بالميكروثانية، نقسمها على 1,000,000 للتحويل إلى ثوانٍ
                duration = container.duration / 1000000.0
        except Exception as e:
            print(f"خطأ أثناء قراءة ملف الفيديو (PyAV): {e}")
            flash('حدث خطأ أثناء معالجة ملف الفيديو. قد يكون الملف تالفاً.', 'danger')
            return redirect(url_for('index'))

        # 3. تطبيق حد الـ 60 ثانية
        if duration > 60:
            flash(f'خطأ: مدة الفيديو هي {int(duration)} ثانية. الحد الأقصى المسموح به هو 60 ثانية فقط.', 'danger')
            return redirect(url_for('index'))

        # 4. إذا كانت المدة مقبولة، أنشئ اسماً نهائياً وانقل الملف
        final_filename = secure_filename(f"vid_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.filename}")
        final_filepath = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
        
        os.rename(temp_filepath, final_filepath)

        # --- نهاية: التحقق من مدة الفيديو ---

        is_approved = 1 if session.get('role') == 'admin' else 0
        
        db = get_db()
        db.execute('INSERT INTO videos (title, filepath, user_id, video_type, is_approved) VALUES (?, ?, ?, ?, ?)', 
                   (title, final_filename, session['user_id'], video_type, is_approved))
        db.commit()
        
        if is_approved == 0:
            flash('تم رفع الفيديو بنجاح (أقل من 60 ثانية)، وهو الآن بانتظار موافقة المدير.', 'success')
        else:
            flash('تم رفع الفيديو بنجاح (أقل من 60 ثانية)!', 'success')
            
    finally:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
    return redirect(url_for('index'))

@app.route('/video/<int:video_id>/like', methods=['POST'])
def like_video(video_id):
    if 'user_id' not in session: return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
    user_id = session['user_id']
    db = get_db()
    existing_like = db.execute('SELECT id FROM video_likes WHERE video_id = ? AND user_id = ?', (video_id, user_id)).fetchone()
    if existing_like:
        db.execute('DELETE FROM video_likes WHERE id = ?', (existing_like['id'],))
        user_likes = False
    else:
        db.execute('INSERT INTO video_likes (video_id, user_id) VALUES (?, ?)', (video_id, user_id))
        user_likes = True
    db.commit()
    likes_count = db.execute('SELECT COUNT(id) FROM video_likes WHERE video_id = ?', (video_id,)).fetchone()[0]
    return jsonify({'status': 'success', 'likes_count': likes_count, 'user_likes': user_likes})

@app.route('/video/<int:video_id>/rate', methods=['POST'])
def rate_video(video_id):
    if session.get('role') != 'admin': 
        return jsonify({'status': 'error', 'message': 'Admins only.'}), 403
    
    data = request.get_json()
    db = get_db()

    video = db.execute('SELECT video_type FROM videos WHERE id = ?', (video_id,)).fetchone()
    if not video:
        return jsonify({'status': 'error', 'message': 'Video not found.'}), 404

    base_fields = ['participation', 'memorization', 'pronunciation', 'use_of_aids']
    extra_fields = ['filming_lighting', 'sound_quality', 'behavior', 'cleanliness', 'location', 'confidence']
    all_fields = base_fields + extra_fields

    values = {'video_id': video_id, 'admin_id': session['user_id']}
    total_stars = 0
    champion_message = None

    if video['video_type'] == 'اثرائي':
        for field in all_fields:
            values[field] = data.get(field, 0)
        total_stars = sum(values[f] for f in all_fields)
        if total_stars == 10:
            champion_message = "أصبح هذا الطالب بطلاً خارقاً!"
    else: # منهجي
        for field in base_fields:
            values[field] = data.get(field, 0)
        for field in extra_fields:
            values[field] = 0
        total_stars = sum(values[f] for f in base_fields)
        
    update_set_clause = ', '.join([f'{field}=excluded.{field}' for field in all_fields])
    
    query = f'''
        INSERT INTO video_ratings (video_id, admin_id, {', '.join(all_fields)}) 
        VALUES (:{', :'.join(['video_id', 'admin_id'] + all_fields)}) 
        ON CONFLICT(video_id) DO UPDATE SET {update_set_clause}
    '''
    
    db.execute(query, values)
    db.commit()

    return jsonify({'status': 'success', 'total_stars': total_stars, 'champion_message': champion_message})

# --- START: NEW ROUTES FOR VIDEO APPROVAL ---
@app.route('/video/<int:video_id>/approve', methods=['POST'])
def approve_video(video_id):
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('UPDATE videos SET is_approved = 1 WHERE id = ?', (video_id,))
    db.commit()
    flash('تمت الموافقة على الفيديو بنجاح!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/video/<int:video_id>/delete', methods=['POST'])
def delete_video(video_id):
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(url_for('index'))
    
    db = get_db()
    # ابحث عن الفيديو أولاً لجلب اسم الملف
    video = db.execute('SELECT filepath FROM videos WHERE id = ?', (video_id,)).fetchone()
    
    if not video:
        flash('الفيديو غير موجود.', 'danger')
        return redirect(request.referrer or url_for('index'))

    try:
        # 1. حذف ملف الفيديو من المجلد
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filepath'])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # 2. حذف جميع البيانات المتعلقة بالفيديو من قاعدة البيانات
        db.execute('DELETE FROM video_ratings WHERE video_id = ?', (video_id,))
        db.execute('DELETE FROM video_likes WHERE video_id = ?', (video_id,))
        db.execute('DELETE FROM comments WHERE video_id = ?', (video_id,))
        db.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        
        db.commit()
        flash('تم حذف الفيديو وجميع البيانات المتعلقة به بنجاح.', 'success')
    
    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء حذف الفيديو: {e}', 'danger')
    
    # أعد التوجيه إلى الصفحة السابقة
    return redirect(request.referrer or url_for('index'))
# --- END: NEW ROUTES FOR VIDEO APPROVAL ---


@app.route('/video/<int:video_id>/comment', methods=['POST'])
def comment_video(video_id):
    if 'user_id' not in session: return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
    
    db = get_db()
    user = db.execute('SELECT is_muted FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user and user['is_muted']:
        return jsonify({'status': 'error', 'message': 'أنت ممنوع من التعليق.'}), 403

    content = request.form.get('comment_content')
    if content:
        cursor = db.execute('INSERT INTO comments (content, user_id, video_id) VALUES (?, ?, ?)', (content, session['user_id'], video_id))
        db.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Empty comment.'}), 400

# ----------------- COMMENT MANAGEMENT ROUTES -----------------
@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401

    db = get_db()
    comment = db.execute('SELECT user_id FROM comments WHERE id = ?', (comment_id,)).fetchone()

    if not comment or comment['user_id'] != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    new_content = request.form.get('content')
    if not new_content or not new_content.strip():
        return jsonify({'status': 'error', 'message': 'Content cannot be empty'}), 400

    db.execute('UPDATE comments SET content = ? WHERE id = ?', (new_content, comment_id))
    db.commit()
    return jsonify({'status': 'success', 'new_content': new_content})

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401

    db = get_db()
    comment = db.execute('SELECT user_id FROM comments WHERE id = ?', (comment_id,)).fetchone()

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment not found'}), 404

    is_owner = comment['user_id'] == session['user_id']
    is_admin = session.get('role') == 'admin'

    if not is_owner and not is_admin:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    db.commit()
    return jsonify({'status': 'success'})


@app.route('/comment/<int:comment_id>/pin', methods=['POST'])
def pin_comment(comment_id):
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Admins only.'}), 403

    db = get_db()
    comment = db.execute('SELECT is_pinned FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment: return jsonify({'status': 'error', 'message': 'Comment not found'}), 404
    
    new_status = 0 if comment['is_pinned'] else 1
    
    db.execute('UPDATE comments SET is_pinned = ? WHERE id = ?', (new_status, comment_id))
    db.commit()

    return jsonify({'status': 'success', 'is_pinned': new_status})

# ----------------- REPORTS & ADMIN ROUTES -----------------
@app.route('/students')
def students():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    db = get_db()
    selected_class = request.args.get('class_name', '')
    selected_section = request.args.get('section_name', '')
    search_name = request.args.get('search_name', '')

    all_classes = db.execute("SELECT DISTINCT class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND class_name != '' ORDER BY class_name").fetchall()
    all_sections = db.execute("SELECT DISTINCT section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND section_name != '' ORDER BY section_name").fetchall()
    
    query = "SELECT id, username, profile_image, class_name, section_name FROM users WHERE role = 'student'"
    params = []
    
    if selected_class:
        query += " AND class_name = ?"
        params.append(selected_class)
    if selected_section:
        query += " AND section_name = ?"
        params.append(selected_section)
    if search_name:
        query += " AND username LIKE ?"
        params.append(f'%{search_name}%')
    
    query += " ORDER BY username"
    
    students_data = db.execute(query, tuple(params)).fetchall()

    return render_page('students', 
                       students=students_data,
                       all_classes=all_classes,
                       all_sections=all_sections,
                       selected_class=selected_class,
                       selected_section=selected_section,
                       search_name=search_name)

@app.route('/reports')
def reports():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    db = get_db()

    selected_class = request.args.get('class_name', '')
    all_classes = db.execute("SELECT DISTINCT class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND class_name != '' ORDER BY class_name").fetchall()
    
    student_query = "SELECT id, username, class_name, section_name FROM users WHERE role = 'student'"
    params = []
    if selected_class:
        student_query += " AND class_name = ?"
        params.append(selected_class)
    student_query += " ORDER BY username"
    
    students = db.execute(student_query, tuple(params)).fetchall()
    
    report_data = []
    champion_statuses = get_champion_statuses()
    start_of_week_dt = datetime.combine(date.today() - timedelta(days=date.today().weekday()), datetime.min.time())

    for student in students:
        student_info = dict(student)
        
        videos = db.execute("""
            SELECT v.title, v.timestamp, vr.* FROM videos v LEFT JOIN video_ratings vr ON v.id = vr.video_id 
            WHERE v.user_id = ? AND v.video_type = 'منهجي' 
            ORDER BY v.timestamp DESC
        """, (student['id'],)).fetchall()
        student_info['videos'] = [{'total_stars': sum((v[key] or 0) for key in ['participation', 'memorization', 'pronunciation', 'use_of_aids']), **dict(v)} for v in videos]
        
        enrichment_videos = db.execute("""
            SELECT v.title, v.timestamp, vr.*
            FROM videos v LEFT JOIN video_ratings vr ON v.id = vr.video_id
            WHERE v.user_id = ? AND v.video_type = 'اثرائي'
            ORDER BY v.timestamp DESC
        """, (student['id'],)).fetchall()
        
        student_info['enrichment_videos'] = []
        for v in enrichment_videos:
            video_data = dict(v)
            total_stars = sum((v[key] or 0) for key in [
                'participation', 'memorization', 'pronunciation', 'use_of_aids', 'filming_lighting', 
                'sound_quality', 'behavior', 'cleanliness', 'location', 'confidence'
            ])
            video_data['total_stars'] = total_stars
            student_info['enrichment_videos'].append(video_data)

        student_info['weekly_activity'] = {
            'uploads': db.execute("SELECT COUNT(id) as count FROM videos WHERE user_id = ? AND timestamp >= ?", (student['id'], start_of_week_dt)).fetchone()['count'],
            'comments': db.execute("SELECT COUNT(id) as count FROM comments WHERE user_id = ? AND timestamp >= ?", (student['id'], start_of_week_dt)).fetchone()['count'],
            'is_champion': champion_statuses.get(student['id']) == 'بطل الأسبوع'
        }
        report_data.append(student_info)
        
    return render_page('reports', 
                       report_data=report_data,
                       all_classes=all_classes,
                       selected_class=selected_class)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    db = get_db()
    students = db.execute("""
        SELECT u.*, s.end_date, s.reason 
        FROM users u 
        LEFT JOIN suspensions s ON u.id = s.user_id AND s.end_date > ? 
        WHERE u.role = 'student'
    """, (datetime.now(),)).fetchall()
    students = [{**s, 'end_date': datetime.strptime(s['end_date'].split('.')[0], '%Y-%m-%d %H:%M:%S') if s['end_date'] else None} for s in students]
    return render_page('admin_dashboard', students=students)

@app.route('/admin/create_student', methods=['POST'])
def create_student():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    username, password = request.form['username'], request.form['password']
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (username, generate_password_hash(password)))
        db.commit()
        flash(f'تم إنشاء حساب الطالب {username} بنجاح!', 'success')
    except sqlite3.IntegrityError:
        flash(f'اسم المستخدم {username} موجود بالفعل!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_admin', methods=['POST'])
def create_admin():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    username, password = request.form['username'], request.form['password']
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password, role, is_profile_complete) VALUES (?, ?, 'admin', 1)", (username, generate_password_hash(password)))
        db.commit()
        flash(f'تم إنشاء حساب المدير {username} بنجاح!', 'success')
    except sqlite3.IntegrityError:
        flash(f'اسم المستخدم {username} موجود بالفعل!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_post', methods=['POST'])
def create_post():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    content = request.form['content']
    if content:
        db = get_db()
        db.execute('INSERT INTO posts (content, user_id) VALUES (?, ?)', (content, session['user_id']))
        db.commit()
        flash('تم نشر المنشور بنجاح!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/kick_student/<int:student_id>', methods=['POST'])
def kick_student(student_id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    db = get_db()
    db.execute('UPDATE users SET session_revocation_token = session_revocation_token + 1 WHERE id = ?', (student_id,))
    db.commit()
    flash('تم طرد الطالب.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/suspend_student/<int:student_id>', methods=['POST'])
def suspend_student(student_id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    duration = request.form.get('duration')
    reason = request.form.get('reason', 'لا يوجد سبب.')
    
    duration_map = {
        'hour': timedelta(hours=1), 'day': timedelta(days=1), 
        'week': timedelta(weeks=1), 'month': timedelta(days=30),
        'year': timedelta(days=365)
    }
    
    end_date = None
    if duration in duration_map:
        end_date = datetime.now() + duration_map[duration]
    elif duration == 'permanent':
        end_date = datetime(9999, 12, 31)

    if end_date:
        db = get_db()
        db.execute('INSERT INTO suspensions (user_id, end_date, reason) VALUES (?, ?, ?)', (student_id, end_date, reason))
        db.commit()
        kick_student(student_id)
        flash(f'تم إيقاف الطالب بنجاح.', 'success')
    else:
        flash('مدة الإيقاف غير صالحة.', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lift_suspension/<int:student_id>', methods=['POST'])
def lift_suspension(student_id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    db = get_db()
    db.execute('DELETE FROM suspensions WHERE user_id = ?', (student_id,))
    db.commit()
    flash('تم رفع الإيقاف عن الطالب.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_mute/<int:student_id>', methods=['POST'])
def toggle_mute(student_id):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    db = get_db()
    student = db.execute('SELECT is_muted FROM users WHERE id = ?', (student_id,)).fetchone()
    if student:
        new_status = 0 if student['is_muted'] else 1
        db.execute('UPDATE users SET is_muted = ? WHERE id = ?', (new_status, student_id))
        db.commit()
        flash('تم تحديث حالة الكتم للطالب بنجاح.', 'success')
    else:
        flash('الطالب غير موجود.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/start_new_year', methods=['POST'])
def start_new_year():
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(url_for('index'))
    
    db = get_db()
    try:
        # --- START: MODIFICATION ---
        # حذف ملفات الفيديوهات المرفوعة
        videos_to_delete = db.execute("SELECT filepath FROM videos").fetchall()
        for video in videos_to_delete:
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filepath'])
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file {video['filepath']}: {e}")
        # --- END: MODIFICATION ---

        db.execute('DELETE FROM comments')
        db.execute('DELETE FROM video_likes')
        db.execute('DELETE FROM video_ratings')
        db.execute('DELETE FROM videos')
        db.execute('DELETE FROM posts')
        db.execute('DELETE FROM star_bank')
        db.execute('DELETE FROM suspensions')
        db.execute('DELETE FROM messages')
        
        db.execute("""
            UPDATE users 
            SET class_name = NULL, section_name = NULL, profile_reset_required = 1 
            WHERE role = 'student'
        """)
        
        db.commit()
        flash('تم بدء سنة دراسية جديدة بنجاح! تم مسح جميع البيانات وتجهيز النظام للعام الجديد.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء بدء السنة الجديدة: {e}', 'danger')
        
    return redirect(url_for('admin_dashboard'))

# ----------------- CONVERSATION ROUTES (Main Pages + APIs) -----------------
@app.route('/conversations')
def conversations():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    db = get_db()
    all_classes = db.execute("SELECT DISTINCT class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND class_name != '' ORDER BY class_name").fetchall()
    all_sections = db.execute("SELECT DISTINCT section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND section_name != '' ORDER BY section_name").fetchall()

    return render_page('conversations', 
                       all_classes=all_classes, 
                       all_sections=all_sections,
                       scripts_block=conversations_script_block)

@app.route('/my_messages')
def my_messages():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    db = get_db()
    admin = db.execute('SELECT id FROM users WHERE role = "admin" LIMIT 1').fetchone()
    if not admin:
        flash('لا يوجد حساب مدير للتواصل معه.', 'danger')
        return redirect(url_for('index'))
    
    # Mark messages from admin as read
    db.execute('UPDATE messages SET is_read = 1 WHERE receiver_id = ? AND sender_id = ?', (session['user_id'], admin['id']))
    db.commit()
    
    return render_page('student_chat', admin_id=admin['id'], scripts_block=student_chat_script_block)

@app.route('/api/conversations/users')
def api_get_users():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    class_name = request.args.get('class_name', '')
    section_name = request.args.get('section_name', '')
    search_name = request.args.get('search_name', '')

    query = "SELECT id, username, profile_image, class_name, section_name FROM users WHERE role = 'student'"
    params = []

    if class_name:
        query += " AND class_name = ?"
        params.append(class_name)
    if section_name:
        query += " AND section_name = ?"
        params.append(section_name)
    if search_name:
        query += " AND username LIKE ?"
        params.append(f'%{search_name}%')
        
    query += " ORDER BY username"
    
    users = db.execute(query, tuple(params)).fetchall()
    return jsonify([dict(user) for user in users])

@app.route('/api/messages/<int:student_id>')
def api_get_admin_messages(student_id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    admin_id = session['user_id']
    db = get_db()
    
    messages = db.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (admin_id, student_id, student_id, admin_id)).fetchall()
    
    return jsonify({"messages": [dict(msg) for msg in messages]})

@app.route('/api/messages/send', methods=['POST'])
def api_send_admin_message():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    content = data.get('content')
    msg_type = data.get('type')
    sender_id = session['user_id']

    if not content:
        return jsonify({"status": "error", "message": "Message content cannot be empty."}), 400

    db = get_db()
    
    if msg_type == 'user':
        receiver_id = data.get('id')
        if not receiver_id:
            return jsonify({"status": "error", "message": "Receiver ID is required."}), 400
        db.execute(
            "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
            (sender_id, receiver_id, content)
        )
    elif msg_type == 'group':
        class_name = data.get('class_name')
        section_name = data.get('section_name')
        
        if not class_name:
            return jsonify({"status": "error", "message": "Class name is required for group message."}), 400
            
        student_query = "SELECT id FROM users WHERE role = 'student' AND class_name = ?"
        params = [class_name]
        if section_name:
            student_query += " AND section_name = ?"
            params.append(section_name)
        
        students = db.execute(student_query, tuple(params)).fetchall()
        for student in students:
            db.execute(
                "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
                (sender_id, student['id'], content)
            )
    else:
        return jsonify({"status": "error", "message": "Invalid message type."}), 400

    db.commit()
    return jsonify({"status": "success", "message": "Message sent."})

@app.route('/api/student/messages')
def api_get_student_messages():
    if session.get('role') != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    student_id = session['user_id']
    admin = db.execute('SELECT id FROM users WHERE role = "admin" LIMIT 1').fetchone()
    if not admin:
        return jsonify({"error": "Admin account not found"}), 500

    admin_id = admin['id']
    messages = db.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (admin_id, student_id, student_id, admin_id)).fetchall()
    
    return jsonify({"messages": [dict(msg) for msg in messages]})

@app.route('/api/student/messages/send', methods=['POST'])
def api_send_student_message():
    if session.get('role') != 'student':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    content = data.get('content')
    receiver_id = data.get('receiver_id') # Admin's ID
    sender_id = session['user_id']

    if not content or not receiver_id:
        return jsonify({"status": "error", "message": "Invalid data."}), 400

    db = get_db()
    db.execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
        (sender_id, receiver_id, content)
    )
    db.commit()
    return jsonify({"status": "success"})


init_db() # تأكد من تهيئة قاعدة البيانات
if __name__ == '__main__':
    from waitress import serve
    print("Starting server on http://0.0.0.0:5000")
    # لا تستخدم app.run() في الوضع العام
    # app.run(host='0.0.0.0', debug=True) 

    # استخدم waitress بدلاً عنه
    serve(app, host='0.0.0.0', port=5000)