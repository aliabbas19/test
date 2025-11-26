import sqlite3
import os
import av
import hashlib
import secrets
import json
import io
import tempfile
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
# --- تعديل 1: إضافة send_from_directory ---
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, g, jsonify, send_from_directory, abort, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime, timedelta, date
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging


# الصورة الأولى ستكون للغلاف، والثانية للصورة الشخصية
professor_image_url_1 = "https://i.ibb.co/RkWC7YZm/photo-2025-10-22-12-53-24.jpg" # استبدل هذا الرابط (صورة الغلاف)
professor_image_url_2 = "https://i.postimg.cc/3RnCZ8Wy/1447-04-22-10-34-02-7d49049c.jpg" # استبدل هذا الرابط (الصورة الشخصية)

# ----------------- HTML TEMPLATES (Embedded) -----------------
# --- تعديل 3: تم استبدال url_for('static', filename='uploads/...) بـ url_for('uploaded_file', filename=...) في كل قوالب HTML ---
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
            overflow-y: auto;
            overflow-x: hidden;
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

        /* Ship-like framed headers */
        .ship-frame {
            font-weight: bold;
            padding: 15px 20px;
            margin: 10px auto;
            border-radius: 15px;
            background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,245,250,0.9));
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            border: 3px solid;
            border-image: linear-gradient(45deg, #0d6efd, #20c997) 1;
            color: #0d2640;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
            max-width: 800px;
        }
        .ship-frame.main-title {
            font-size: 4.5rem;
            padding: 20px 30px;
            border-image: linear-gradient(45deg, #0d6efd, #6f42c1) 1;
        }
        .ship-frame.sub-title {
            font-size: 2.5rem;
            border-image: linear-gradient(45deg, #20c997, #0d6efd) 1;
        }
        .ship-frame:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .ship-frame span {
            display: inline-block;
            direction: rtl;
            background: linear-gradient(90deg, #0d6efd, #6f42c1, #20c997);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200% auto;
            animation: textGradient 5s linear infinite;
        }
        @keyframes textGradient {
            to { background-position: -200% center; }
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .ship-frame.main-title {
                font-size: 3.5rem;
                padding: 15px 20px;
            }
            .ship-frame.sub-title {
                font-size: 1.8rem;
                padding: 12px 15px;
            }
        }
        @media (max-width: 480px) {
            .ship-frame.main-title {
                font-size: 2.8rem;
                padding: 12px 15px;
            }
            .ship-frame.sub-title {
                font-size: 1.5rem;
                padding: 10px 12px;
            }
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
                justify-content: flex-start;
                padding: 10px 2px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                /* MODIFICATION: Placed at bottom of its container, creating space */
                margin-top: 0;
                margin-bottom: 20px;
                border-radius: 15px;
                overflow-x: auto;
                overflow-y: hidden;
                -webkit-overflow-scrolling: touch;
                white-space: nowrap;
                scrollbar-width: thin;
                scrollbar-color: rgba(13, 110, 253, 0.5) rgba(255, 255, 255, 0.1);
            }
            
            /* Custom scrollbar for webkit browsers */
            .circular-nav::-webkit-scrollbar {
                height: 6px;
            }
            .circular-nav::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            .circular-nav::-webkit-scrollbar-thumb {
                background: rgba(13, 110, 253, 0.5);
                border-radius: 10px;
            }
            .circular-nav::-webkit-scrollbar-thumb:hover {
                background: rgba(13, 110, 253, 0.7);
            }

            .circular-nav ul { 
                display: flex; 
                flex-direction: row; 
                width: auto;
                min-width: 100%;
                justify-content: flex-start;
                flex-wrap: nowrap;
                white-space: nowrap;
            }

            .circular-nav li { 
                margin: 0 2px;
                flex-shrink: 0;
                white-space: nowrap;
            }
            .circular-nav a {
                width: 48px;
                height: 48px;
                font-size: 0.6rem;
                border-width: 1px;
                padding: 2px;
                flex-shrink: 0;
                white-space: nowrap;
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

        /* Copyright Footer Styles */
        .copyright-footer {
            text-align: center;
            padding: 15px 20px;
            margin-top: 30px;
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-top: 2px solid rgba(13, 110, 253, 0.2);
            border-radius: 10px 10px 0 0;
            font-size: 0.9rem;
            color: #495057;
        }
        .copyright-footer .copyright-label {
            display: inline-block;
            padding: 8px 15px;
            background: linear-gradient(135deg, rgba(13, 110, 253, 0.1), rgba(32, 201, 151, 0.1));
            border-radius: 20px;
            border: 1px solid rgba(13, 110, 253, 0.3);
            font-weight: 500;
        }
        .copyright-footer .copyright-label i {
            margin-left: 5px;
            color: #0d6efd;
        }

        /* ================== START: RESPONSIVE IMPROVEMENTS ================== */
        /* RTL Support */
        [dir="rtl"] {
            direction: rtl;
            text-align: right;
        }

        /* Tables - Horizontal scroll on mobile instead of shrinking */
        .table-responsive {
            overflow-x: auto;
            overflow-y: visible;
            -webkit-overflow-scrolling: touch;
        }
        @media (max-width: 768px) {
            .table-responsive {
                display: block;
                width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            .table {
                min-width: 600px; /* Prevent table from shrinking too much */
                width: 100%;
            }
        }

        /* Forms - Full width on mobile, vertical layout */
        @media (max-width: 768px) {
            .form-control,
            .form-select,
            .form-check-input {
                width: 100%;
            }
            .row.g-3 > *,
            .row > .col-md-3,
            .row > .col-md-4,
            .row > .col-md-6,
            .row > .col-md-8 {
                width: 100%;
                flex: 0 0 100%;
                max-width: 100%;
                margin-bottom: 1rem;
            }
            /* Vertical form layout on mobile */
            .row.g-3 {
                flex-direction: column;
            }
        }

        /* Cards and containers - Better spacing on mobile */
        @media (max-width: 768px) {
            .card {
                margin-bottom: 1rem;
            }
            .main-content {
                padding: 15px !important;
            }
            .container {
                padding-left: 10px;
                padding-right: 10px;
            }
        }

        /* Video containers - Better sizing */
        .video-container {
            width: 100%;
            max-width: 100%;
        }
        @media (max-width: 768px) {
            .video-container {
                width: 100%;
            }
            video {
                width: 100%;
                height: auto;
            }
        }

        /* Button groups - Stack vertically on mobile */
        @media (max-width: 768px) {
            .btn-group {
                display: flex;
                flex-direction: column;
                width: 100%;
            }
            .btn-group .btn {
                width: 100%;
                margin-bottom: 0.25rem;
                border-radius: 0.25rem !important;
            }
            .btn-group .btn:first-child {
                border-top-left-radius: 0.25rem !important;
                border-top-right-radius: 0.25rem !important;
                border-bottom-left-radius: 0 !important;
                border-bottom-right-radius: 0 !important;
            }
            .btn-group .btn:last-child {
                border-top-left-radius: 0 !important;
                border-top-right-radius: 0 !important;
                border-bottom-left-radius: 0.25rem !important;
                border-bottom-right-radius: 0.25rem !important;
            }
        }

        /* Admin actions group - Ensure all buttons are visible on mobile */
        .admin-actions-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem;
        }
        .admin-action-form {
            display: inline-block;
            margin: 0;
        }
        .admin-action-form .btn {
            margin: 0;
        }
        @media (max-width: 768px) {
            .admin-actions-group {
                flex-direction: column;
                width: 100%;
            }
            .admin-action-form {
                display: block;
                width: 100%;
            }
            .admin-action-form .btn {
                width: 100%;
                margin-bottom: 0.25rem;
            }
            .admin-suspend-form {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .admin-suspend-form .admin-suspend-duration,
            .admin-suspend-form .admin-suspend-reason {
                width: 100% !important;
            }
            .admin-suspend-form .btn {
                width: 100%;
            }
        }

        /* Comments section - Better mobile layout */
        @media (max-width: 768px) {
            .comment {
                flex-direction: column;
            }
            .comment-body {
                margin-right: 0 !important;
                margin-top: 0.5rem;
            }
        }

        /* Admin post - Better mobile */
        @media (max-width: 768px) {
            .admin-post-header {
                flex-direction: column;
                align-items: flex-start;
            }
            .admin-post-header .admin-icon {
                margin-left: 0;
                margin-bottom: 0.5rem;
            }
        }

        /* Stat cards - Stack on mobile */
        @media (max-width: 768px) {
            .stat-card {
                margin-bottom: 1rem;
            }
        }

        /* Filter forms - Stack on mobile */
        @media (max-width: 768px) {
            form.row.g-3 {
                flex-direction: column;
            }
            form.row.g-3 .col-auto,
            form.row.g-3 .col-md-3,
            form.row.g-3 .col-md-4 {
                width: 100%;
                margin-bottom: 0.5rem;
            }
        }

        /* Rating forms - Better mobile layout */
        @media (max-width: 768px) {
            .rating-form .row {
                flex-direction: column;
            }
            .rating-form .col-md-4,
            .rating-form .col-md-6,
            .rating-form .col-6 {
                width: 100%;
                flex: 0 0 100%;
                max-width: 100%;
            }
        }

        /* Profile picture and cover - Better mobile */
        @media (max-width: 480px) {
            .cover-image-container {
                height: 150px;
            }
            .profile-picture {
                width: 100px;
                height: 100px;
            }
            .profile-picture-container {
                bottom: -50px;
                right: 15px;
            }
        }

        /* Prevent elements from shrinking - use scroll instead */
        @media (max-width: 768px) {
            .main-content {
                overflow-x: hidden;
                overflow-y: auto;
            }
            .card-body {
                overflow-x: auto;
                overflow-y: visible;
            }
        }

        /* Better spacing for small screens */
        @media (max-width: 480px) {
            .mb-4 {
                margin-bottom: 1rem !important;
            }
            .mt-4 {
                margin-top: 1rem !important;
            }
            .p-3 {
                padding: 0.75rem !important;
            }
        }

        /* Flexbox improvements for RTL */
        [dir="rtl"] .d-flex {
            flex-direction: row-reverse;
        }
        [dir="rtl"] .ms-2 {
            margin-right: 0.5rem !important;
            margin-left: 0 !important;
        }
        [dir="rtl"] .me-2 {
            margin-left: 0.5rem !important;
            margin-right: 0 !important;
        }

        /* Grid improvements for cards */
        @media (max-width: 768px) {
            .row.row-cols-1.row-cols-md-2 {
                display: flex;
                flex-direction: column;
            }
            .row.row-cols-1.row-cols-md-2 > .col {
                width: 100%;
                flex: 0 0 100%;
                max-width: 100%;
            }
        }
        /* ================== END: RESPONSIVE IMPROVEMENTS ================== */
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
                <div class="ship-frame main-title">
                    <span>منصة</span>
                </div>
                <div class="ship-frame sub-title">
                    <span>الاستاذ بسام الجنابي مادة الحاسوب</span>
                </div>
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
    <footer class="copyright-footer">
        <label class="copyright-label">
            <i class="fas fa-copyright"></i>
        شركة عراق تك- IraQ TecH للحلول البرمجية
        </label>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
# ----------------- MODIFIED index_content_block -----------------
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

{% if superhero_champions %}
<div class="card shadow-sm mb-4" style="background-color: rgba(255, 253, 240, 0.9);">
    <div class="card-body">
        <h2 class="text-center mb-3" style="color: #ff8c00;"><i class="fas fa-meteor"></i> أبطال هذا الشهر الخارقون <i class="fas fa-meteor"></i></h2>
        <p class="text-center text-muted">الطلاب المتميزون الذين حققوا العلامة الكاملة ({{ max_ithrai_stars }}/{{ max_ithrai_stars }}) في فيديو إثرائي هذا الشهر.</p>
        <div class="row g-4 mt-3">
            {% for champion in superhero_champions %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm text-center" style="border: 2px solid #ffd700; transform: scale(1); transition: all 0.3s ease;">
                    <div class="card-body d-flex flex-column align-items-center">
                        <a href="{{ url_for('profile', username=champion.username) }}" class="text-decoration-none">
                            <img src="{{ url_for('uploaded_file', filename=(champion.profile_image or 'default.png')) }}" alt="Profile Image" class="rounded-circle mb-3" width="100" height="100" style="border: 4px solid #0d6efd; object-fit: cover;">
                            <h5 class="card-title text-primary">{{ champion.full_name or champion.username }}</h5>
                        </a>
                        <span class="superhero-status mt-2 fs-6">
                            <i class="fas fa-meteor me-1"></i> بطل خارق
                        </span>
                        <p class="card-text fw-bold text-warning fs-4 mt-2 mb-0" style="color: #ffc107 !important;">
                           <i class="fas fa-star"></i> {{ max_ithrai_stars }} / {{ max_ithrai_stars }}
                        </p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endif %}
<hr style="border-color: rgba(0,0,0,0.1);">
<h2 class="text-center mb-4">آخر الأخبار والنشاطات</h2>

{% for post in posts %}
<div class="admin-post">
    <div class="admin-post-header">
        <div class="admin-icon">
            <span class="admin-username-gradient fs-2"><i class="fas fa-bullhorn"></i></span>
        </div>
        <div class="info">
            <span class="admin-username-gradient fw-bold">{{ post.full_name or post.username }}</span>
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
             <img src="{{ url_for('uploaded_file', filename=(video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
            <div class="ms-3">
                <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                    {% if video.role == 'admin' %}
                        <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ video.full_name or video.username }}</span>
                    {% else %}
                        <span class="text-primary">{{ video.full_name or video.username }}</span>
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
                <source src="{{ url_for('uploaded_file', filename=video.filepath) }}" type="video/mp4">
            </video>
        </div>
        {# END: MODIFICATION #}
        
        {# START: Delete and Archive buttons for video owner and admin - directly under video #}
        {% if session['user_id'] == video.user_id or session['role'] == 'admin' %}
        <div class="mt-2 mb-2 text-center">
            {% if session['role'] == 'admin' %}
                {% if video.is_archived == 0 %}
                <form action="{{ url_for('archive_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من نقل هذا الفيديو إلى الأرشيف؟');">
                    <button type="submit" class="btn btn-sm btn-warning"><i class="fas fa-archive me-1"></i>نقل إلى الأرشيف</button>
                </form>
                {% else %}
                <form action="{{ url_for('unarchive_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من إرجاع هذا الفيديو من الأرشيف؟');">
                    <button type="submit" class="btn btn-sm btn-info"><i class="fas fa-undo me-1"></i>إرجاع من الأرشيف</button>
                </form>
                {% endif %}
            {% endif %}
            <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline ms-2" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                <button type="submit" class="btn btn-sm btn-danger"><i class="fas fa-trash me-1"></i>حذف الفيديو</button>
            </form>
        </div>
        {% endif %}
        {# END: Delete and Archive buttons #}
        
        <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="like-section">
                <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"> <i class="fas fa-heart fa-lg"></i> </button>
                <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
            </div>
            {# START: MODIFIED Star Display #}
            <div class="rating-display-stars" style="color: #ffc107; font-size: 1.5rem;">
                {# ================== DYNAMIC RATING MODIFICATION ================== #}
                {% set rating_info = video_ratings.get(video.id) %}
                {% set total_stars = rating_info.total_stars if rating_info else 0 %}
                {% set max_stars = rating_info.max_stars if rating_info else (10 if video.video_type == 'اثرائي' else 4) %}
                <span id="stars-display-{{ video.id }}">
                    {% if total_stars > 0 %}
                        <i class="fas fa-star"></i>
                        {{ total_stars }} / {{ max_stars }}
                    {% else %}
                        <small class="text-muted">لم يُقيّم بعد</small>
                    {% endif %}
                </span>
                {# ================== END DYNAMIC RATING MODIFICATION ================== #}
            </div>
            {# END: MODIFIED Star Display #}
        </div>

        {# ================== START: DYNAMIC RATING FORM MODIFICATION ================== #}
        {% if session.role == 'admin' %}
        <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
            <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
            
            {# جلب المعايير الحالية للفيديو #}
            {% set current_video_ratings = video_ratings.get(video.id).ratings if video_ratings.get(video.id) else {} %}
            
            {# جلب قائمة المعايير الصحيحة بناءً على نوع الفيديو #}
            {% set criteria_list = all_criteria.get(video.video_type, []) %}

            <div class="mt-2">
                <div class="row">
                    {% for criterion in criteria_list %}
                    <div class="col-md-4 col-6">
                        <div class="form-check">
                            {# 
                               - نستخدم criterion.key كـ name
                               - نتحقق إذا كان المفتاح موجوداً في تقييمات الفيديو الحالية
                            #}
                            <input class="form-check-input" type="checkbox" 
                                   name="{{ criterion.key }}" 
                                   id="{{ criterion.key }}-{{video.id}}" 
                                   {% if current_video_ratings.get(criterion.key, 0) == 1 %}checked{% endif %}>
                            <label class="form-check-label" for="{{ criterion.key }}-{{video.id}}">{{ criterion.name }}</label>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </form>
        {% endif %}
        {# ================== END: DYNAMIC RATING FORM MODIFICATION ================== #}

        <div class="comments-section mt-3">
            <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                {% for comment in video_comments[video.id]['toplevel'] %}
                <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                    <img src="{{ url_for('uploaded_file', filename=(comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                    <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                        <div class="d-flex justify-content-between">
                            <p class="comment-author fw-bold mb-0">
                                {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                {% if comment.role == 'admin' %}
                                    <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.full_name or comment.username }}</span>
                                {% else %}
                                    <span class="text-primary">{{ comment.full_name or comment.username }}</span>
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

# ----------------- MODIFIED archive_content_block -----------------
archive_content_block = """
<h1 class="mb-2 text-center">أرشيف الفيديوهات</h1>
<p class="text-center text-muted">هنا تجد الفيديوهات المؤرشفة. <strong>ملاحظة:</strong> الأرشفة التلقائية تتم يوم الجمعة، ويمكن للمسؤول أرشفة الفيديوهات يدوياً في أي وقت.</p>

{% if archive_message %}
<div class="alert alert-info text-center" role="alert">
    <i class="fas fa-info-circle me-2"></i>{{ archive_message }}
</div>
{% endif %}

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
             <img src="{{ url_for('uploaded_file', filename=(video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
            <div class="ms-3">
                <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                    {% if video.role == 'admin' %}
                        <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ video.full_name or video.username }}</span>
                    {% else %}
                        <span class="text-primary">{{ video.full_name or video.username }}</span>
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
                <source src="{{ url_for('uploaded_file', filename=video.filepath) }}" type="video/mp4">
            </video>
        </div>
        {# END: MODIFICATION #}

        {# START: Delete and Archive buttons for video owner and admin - directly under video #}
        {% if session['user_id'] == video.user_id or session['role'] == 'admin' %}
        <div class="mt-2 mb-2 text-center">
            {% if session['role'] == 'admin' %}
                {% if video.is_archived == 0 %}
                <form action="{{ url_for('archive_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من نقل هذا الفيديو إلى الأرشيف؟');">
                    <button type="submit" class="btn btn-sm btn-warning"><i class="fas fa-archive me-1"></i>نقل إلى الأرشيف</button>
                </form>
                {% else %}
                <form action="{{ url_for('unarchive_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من إرجاع هذا الفيديو من الأرشيف؟');">
                    <button type="submit" class="btn btn-sm btn-info"><i class="fas fa-undo me-1"></i>إرجاع من الأرشيف</button>
                </form>
                {% endif %}
            {% endif %}
            <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline ms-2" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                <button type="submit" class="btn btn-sm btn-danger"><i class="fas fa-trash me-1"></i>حذف الفيديو</button>
            </form>
        </div>
        {% endif %}
        {# END: Delete and Archive buttons #}

        <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="like-section">
                <button class="btn btn-link text-secondary like-btn {% if video.id in user_liked_videos %}text-danger{% endif %}" data-video-id="{{ video.id }}"><i class="fas fa-heart fa-lg"></i></button>
                <span class="likes-count" id="likes-count-{{ video.id }}">{{ video_likes.get(video.id, 0) }}</span>
            </div>
            <div class="rating-display-stars" style="color: #ffc107; font-size: 1.5rem;">
                {# ================== DYNAMIC RATING MODIFICATION ================== #}
                {% set rating_info = video_ratings.get(video.id) %}
                {% set total_stars = rating_info.total_stars if rating_info else 0 %}
                {% set max_stars = rating_info.max_stars if rating_info else (10 if video.video_type == 'اثرائي' else 4) %}
                <span id="stars-display-{{ video.id }}">
                     {% if total_stars > 0 %}
                        <i class="fas fa-star"></i>
                        {{ total_stars }} / {{ max_stars }}
                    {% else %}
                        <small class="text-muted">لم يُقيّم بعد</small>
                    {% endif %}
                </span>
                {# ================== END DYNAMIC RATING MODIFICATION ================== #}
            </div>
        </div>
        
        {# ================== START: DYNAMIC RATING FORM MODIFICATION ================== #}
        {% if session.role == 'admin' %}
        <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
            <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
            
            {% set current_video_ratings = video_ratings.get(video.id).ratings if video_ratings.get(video.id) else {} %}
            {% set criteria_list = all_criteria.get(video.video_type, []) %}

            <div class="mt-2">
                <div class="row">
                    {% for criterion in criteria_list %}
                    <div class="col-md-4 col-6">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" 
                                   name="{{ criterion.key }}" 
                                   id="{{ criterion.key }}-{{video.id}}" 
                                   {% if current_video_ratings.get(criterion.key, 0) == 1 %}checked{% endif %}>
                            <label class="form-check-label" for="{{ criterion.key }}-{{video.id}}">{{ criterion.name }}</label>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </form>
        {% endif %}
        {# ================== END: DYNAMIC RATING FORM MODIFICATION ================== #}
        
        <div class="comments-section mt-3">
            <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                {% for comment in video_comments[video.id]['toplevel'] %}
                <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                    <img src="{{ url_for('uploaded_file', filename=(comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                    <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                        <div class="d-flex justify-content-between">
                            <p class="comment-author fw-bold mb-0">
                                {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                {% if comment.role == 'admin' %}
                                    <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.full_name or comment.username }}</span>
                                {% else %}
                                    <span class="text-primary">{{ comment.full_name or comment.username }}</span>
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
    {% if archive_message %}
        {# الرسالة تظهر في الأعلى #}
    {% else %}
        <p class="text-center text-muted">لا توجد فيديوهات في الأرشيف تطابق معايير البحث.</p>
    {% endif %}
{% endfor %}
"""
# ----------------- login_content_block (No Changes) -----------------
login_content_block = """
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm">
            <div class="card-header"><h3>تسجيل الدخول</h3></div>
            <div class="card-body">
                <form method="post" id="loginForm">
                    <input type="hidden" id="device_fingerprint" name="device_fingerprint" value="">
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

<script>
// Device Fingerprinting and Auto-Login System
(function() {
    'use strict';
    
    // Generate Device Fingerprint
    function generateDeviceFingerprint() {
        const components = [];
        
        // User-Agent
        components.push(navigator.userAgent || '');
        
        // Screen properties
        components.push(`${screen.width}x${screen.height}x${screen.colorDepth}`);
        
        // Timezone
        components.push(Intl.DateTimeFormat().resolvedOptions().timeZone || '');
        
        // Language
        components.push(navigator.language || '');
        components.push(navigator.languages ? navigator.languages.join(',') : '');
        
        // Hardware entropy (platform, hardwareConcurrency, deviceMemory)
        components.push(navigator.platform || '');
        components.push(navigator.hardwareConcurrency || '');
        if (navigator.deviceMemory) components.push(navigator.deviceMemory);
        
        // Canvas fingerprint
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('Device fingerprint', 2, 2);
            components.push(canvas.toDataURL());
        } catch(e) {
            components.push('canvas-error');
        }
        
        // WebGL fingerprint
        try {
            const gl = document.createElement('canvas').getContext('webgl');
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    components.push(gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL));
                    components.push(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL));
                }
            }
        } catch(e) {
            components.push('webgl-error');
        }
        
        // Local Storage key (persistent identifier)
        let storageKey = localStorage.getItem('device_id');
        if (!storageKey) {
            storageKey = 'dev_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('device_id', storageKey);
        }
        components.push(storageKey);
        
        // Hash the fingerprint
        const fingerprintString = components.join('|');
        return btoa(fingerprintString).replace(/[^a-zA-Z0-9]/g, '').substring(0, 128);
    }
    
    // Store token in multiple places
    function storeAuthToken(token) {
        // localStorage
        localStorage.setItem('auth_token', token);
        
        // IndexedDB
        if ('indexedDB' in window) {
            const request = indexedDB.open('AuthDB', 1);
            request.onupgradeneeded = function(event) {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('tokens')) {
                    db.createObjectStore('tokens');
                }
            };
            request.onsuccess = function(event) {
                const db = event.target.result;
                const transaction = db.transaction(['tokens'], 'readwrite');
                const store = transaction.objectStore('tokens');
                store.put(token, 'auth_token');
            };
        }
        
        // Cookie is set by server
    }
    
    // Get token from storage
    function getAuthToken() {
        // Try localStorage first
        let token = localStorage.getItem('auth_token');
        if (token) return token;
        
        // Try IndexedDB
        if ('indexedDB' in window) {
            return new Promise((resolve) => {
                const request = indexedDB.open('AuthDB', 1);
                request.onsuccess = function(event) {
                    const db = event.target.result;
                    if (db.objectStoreNames.contains('tokens')) {
                        const transaction = db.transaction(['tokens'], 'readonly');
                        const store = transaction.objectStore('tokens');
                        const getRequest = store.get('auth_token');
                        getRequest.onsuccess = function() {
                            resolve(getRequest.result || null);
                        };
                        getRequest.onerror = function() {
                            resolve(null);
                        };
                    } else {
                        resolve(null);
                    }
                };
                request.onerror = function() {
                    resolve(null);
                };
            });
        }
        
        return null;
    }
    
    // Clear all tokens
    function clearAuthToken() {
        localStorage.removeItem('auth_token');
        if ('indexedDB' in window) {
            const request = indexedDB.open('AuthDB', 1);
            request.onsuccess = function(event) {
                const db = event.target.result;
                if (db.objectStoreNames.contains('tokens')) {
                    const transaction = db.transaction(['tokens'], 'readwrite');
                    const store = transaction.objectStore('tokens');
                    store.delete('auth_token');
                }
            };
        }
    }
    
    let autoLoginAttempted = false;

    function updateFingerprintField() {
        const fingerprint = generateDeviceFingerprint();
        const field = document.getElementById('device_fingerprint');
        if (field) {
            field.value = fingerprint;
        }
        return fingerprint;
    }
    
    // Auto-login function
    // إصلاح: منع التكرار اللانهائي - إضافة حماية من إعادة المحاولة التلقائية
    let autoLoginInProgress = false;
    async function attemptAutoLogin(reason = 'initial') {
        // منع التكرار: إذا كانت محاولة سابقة قيد التنفيذ، تجاهل
        if (autoLoginInProgress) {
            return;
        }
        
        if (autoLoginAttempted && reason !== 'session-refresh') {
            return;
        }
        autoLoginAttempted = true;
        autoLoginInProgress = true;
        
        // Check if user manually logged out - if so, don't auto-login
        if (localStorage.getItem('manual_logout') === 'true') {
            updateFingerprintField();
            return;
        }
        
        const deviceFingerprint = updateFingerprintField();
        
        let authToken = null;
        const tokenResult = getAuthToken();
        authToken = tokenResult instanceof Promise ? await tokenResult : tokenResult;
        
        if (!authToken) {
            // No token, show login form (fingerprint already set)
            return;
        }
        
        try {
            const response = await fetch('/auto-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device_fingerprint: deviceFingerprint,
                    auth_token: authToken
                })
            });
            const data = await response.json().catch(() => ({}));

            if (response.ok && data.status === 'success') {
                if (data.auth_token) {
                    storeAuthToken(data.auth_token);
                }
                window.location.href = data.redirect || '/';
                return;
            }

            clearAuthToken();
            if (data.message) {
                console.warn('Auto-login rejected:', data.message);
            }
        } catch (error) {
            console.error('Auto-login error:', error);
            // إصلاح: منع إعادة المحاولة التلقائية عند الخطأ
            clearAuthToken();
        } finally {
            autoLoginInProgress = false;
            updateFingerprintField();
        }
    }
    
    function requestSessionRefreshAutoLogin() {
        autoLoginAttempted = false;
        attemptAutoLogin('session-refresh');
    }

    window.addEventListener('pageshow', (event) => {
        if (event.persisted && localStorage.getItem('manual_logout') !== 'true') {
            requestSessionRefreshAutoLogin();
        }
    });
    
    // Initialize device fingerprint on page load
    updateFingerprintField();
    
    // Attempt auto-login on page load
    attemptAutoLogin();
    
    // Store token after successful login (handled by form submission)
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        // Remove manual logout flag when user manually logs in
        localStorage.removeItem('manual_logout');
        updateFingerprintField();
    });
})();
</script>
"""

# ----------------- MODIFIED admin_dashboard_content_block -----------------
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
    {# ================== START: NEW Card for Criteria Management ================== #}
    <div class="col-md-6 mb-4">
        <div class="card h-100 shadow-sm">
            <div class="card-header bg-info text-white"><h4><i class="fas fa-tasks me-2"></i>إدارة النظام</h4></div>
            <div class="card-body">
                <h5 class="card-title">إدارة معايير التقييم</h5>
                <p class="card-text">إضافة أو حذف المعايير المستخدمة لتقييم الفيديوهات (مثل: الحفظ، النطق، ...).</p>
                <a href="{{ url_for('admin_criteria') }}" class="btn btn-info">الانتقال إلى صفحة المعايير</a>
            </div>
        </div>
    </div>
    {# ================== END: NEW Card for Criteria Management ================== #}
    
    {# ================== START: NEW Card for Telegram Reports ================== #}
    <div class="col-md-6 mb-4">
        <div class="card h-100 shadow-sm">
            <div class="card-header bg-success text-white"><h4><i class="fas fa-paper-plane me-2"></i>إرسال التقارير</h4></div>
            <div class="card-body">
                <h5 class="card-title">إرسال تقرير الأبطال إلى تيليجرام</h5>
                <p class="card-text">إرسال تقرير أبطال الأسبوع إلى تيليجرام يدوياً. (يتم الإرسال تلقائياً كل يوم أربعاء في الساعة 8 مساءً)</p>
                <button type="button" class="btn btn-success" onclick="sendChampionsReport()">
                    <i class="fas fa-paper-plane me-1"></i>إرسال التقرير الآن
                </button>
                <div id="telegramSendStatus" class="mt-2"></div>
            </div>
        </div>
    </div>
    {# ================== END: NEW Card for Telegram Reports ================== #}

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
        <!-- Search and Filter Controls -->
        <div class="row mb-3">
            <div class="col-md-8">
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                    <input type="text" id="studentSearchInput" class="form-control" placeholder="ابحث عن طالب (الاسم، اسم المستخدم، الصف، الشعبة)...">
                </div>
            </div>
            <div class="col-md-4">
                <select id="studentStatusFilter" class="form-select">
                    <option value="all">جميع الحالات</option>
                    <option value="active">نشط</option>
                    <option value="suspended">موقوف</option>
                    <option value="muted">مكتوم</option>
                </select>
            </div>
        </div>
        <div class="mb-2">
            <small class="text-muted" id="studentCount">إجمالي الطلاب: <span id="totalCount">{{ students|length }}</span> | النتائج: <span id="filteredCount">{{ students|length }}</span></small>
        </div>
        
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr><th>الصورة</th><th>اسم الطالب</th><th>الحالة</th><th>إجراءات</th></tr>
                </thead>
                <tbody id="studentsTableBody">
                    {% for student in students %}
                    <tr class="student-row" 
                        data-full-name="{{ (student.full_name or '')|lower }}"
                        data-username="{{ (student.username or '')|lower }}"
                        data-class-name="{{ (student.class_name or '')|lower }}"
                        data-section-name="{{ (student.section_name or '')|lower }}"
                        data-status="{% if student.end_date %}suspended{% elif student.is_muted %}muted{% else %}active{% endif %}">
                        <td>
                            <img src="{{ url_for('uploaded_file', filename=(student.profile_image or 'default.png')) }}" alt="Profile Image" class="rounded-circle" width="50" height="50" style="object-fit: cover;">
                        </td>
                        <td>
                           <a href="{{ url_for('profile', username=student.username) }}">{{ student.full_name or student.username }}</a>
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
                            <div class="d-flex flex-wrap gap-2" role="group">
                                <a href="{{ url_for('edit_user', user_id=student.id) }}" class="btn btn-sm btn-secondary">
                                    <i class="fas fa-edit me-1"></i>تعديل
                                </a>
                                <form action="{{ url_for('kick_student', student_id=student.id) }}" method="post" class="d-inline">
                                    <button type="submit" class="btn btn-sm btn-dark">
                                        <i class="fas fa-sign-out-alt me-1"></i>طرد
                                    </button>
                                </form>
                                <form action="{{ url_for('toggle_mute', student_id=student.id) }}" method="post" class="d-inline">
                                    {% if student.is_muted %}
                                        <button type="submit" class="btn btn-sm btn-info">
                                            <i class="fas fa-volume-up me-1"></i>إلغاء الكتم
                                        </button>
                                    {% else %}
                                        <button type="submit" class="btn btn-sm btn-secondary">
                                            <i class="fas fa-volume-mute me-1"></i>كتم
                                        </button>
                                    {% endif %}
                                </form>
                                <button type="button" class="btn btn-sm btn-warning" onclick="unbindDevice({{ student.id }})">
                                    <i class="fas fa-unlink me-1"></i>إلغاء ربط الجهاز
                                </button>
                                <button type="button" class="btn btn-sm btn-danger" onclick="deleteStudent({{ student.id }}, '{{ student.full_name or student.username }}')">
                                    <i class="fas fa-trash me-1"></i>حذف الحساب
                                </button>
                                {% if student.end_date %}
                                    <form action="{{ url_for('lift_suspension', student_id=student.id) }}" method="post" class="d-inline">
                                        <button type="submit" class="btn btn-sm btn-success">
                                            <i class="fas fa-check-circle me-1"></i>رفع الإيقاف
                                        </button>
                                    </form>
                                {% else %}
                                    <form action="{{ url_for('suspend_student', student_id=student.id) }}" method="post" class="d-inline-flex align-items-center gap-1 flex-wrap">
                                        <select name="duration" class="form-select form-select-sm" style="width: auto; min-width: 100px;">
                                            <option value="hour">ساعة</option>
                                            <option value="day">يوم</option>
                                            <option value="week">أسبوع</option>
                                            <option value="month">شهر</option>
                                            <option value="year">سنة</option>
                                            <option value="permanent">دائم</option>
                                        </select>
                                        <input type="text" name="reason" placeholder="السبب" class="form-control form-control-sm" style="min-width: 150px;">
                                        <button type="submit" class="btn btn-sm btn-warning text-nowrap">
                                            <i class="fas fa-ban me-1"></i>إيقاف
                                        </button>
                                    </form>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                    <tr id="noResultsRow" class="d-none">
                        <td colspan="4" class="text-center text-muted py-4">
                            <i class="fas fa-search fa-2x mb-2"></i>
                            <p class="mb-0">لا توجد نتائج مطابقة للبحث</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
function unbindDevice(userId) {
    if (!confirm('هل أنت متأكد من إلغاء ربط الجهاز لهذا المستخدم؟ سيتمكن المستخدم من تسجيل الدخول من جهاز جديد.')) {
        return;
    }
    
    fetch('/admin/unbind_device/' + userId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('تم إلغاء ربط الجهاز بنجاح');
            location.reload();
        } else {
            alert('حدث خطأ: ' + (data.error || 'غير معروف'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ أثناء إلغاء ربط الجهاز');
    });
}

function deleteStudent(studentId, studentName) {
    if (!confirm('هل أنت متأكد تماماً من حذف حساب الطالب "' + studentName + '"؟\n\nسيتم حذف:\n- حساب الطالب\n- جميع الفيديوهات\n- جميع التعليقات\n- جميع الرسائل\n- جميع التقييمات\n- جميع البيانات المرتبطة\n\nلا يمكن التراجع عن هذا الإجراء!')) {
        return;
    }
    
    if (!confirm('تأكيد نهائي: هل أنت متأكد 100% من حذف هذا الحساب؟')) {
        return;
    }
    
    fetch('/admin/delete_student/' + studentId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('تم حذف حساب الطالب بنجاح');
            location.reload();
        } else {
            alert('حدث خطأ: ' + (data.error || 'غير معروف'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ أثناء حذف حساب الطالب');
    });
}

<<<<<<< HEAD
function sendChampionsReport() {
    const statusDiv = document.getElementById('telegramSendStatus');
    const button = event.target.closest('button');
    
    if (!confirm('هل تريد إرسال تقرير أبطال الأسبوع إلى تيليجرام الآن؟')) {
        return;
    }
    
    // Disable button and show loading
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>جاري الإرسال...';
    }
    
    if (statusDiv) {
        statusDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin me-1"></i>جاري إرسال التقرير...</div>';
    }
    
    fetch('/admin/send_champions_telegram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (statusDiv) {
                statusDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle me-1"></i>' + (data.message || 'تم إرسال التقرير بنجاح') + '</div>';
            }
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-paper-plane me-1"></i>إرسال التقرير الآن';
            }
        } else {
            if (statusDiv) {
                statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-1"></i>' + (data.error || 'حدث خطأ أثناء الإرسال') + '</div>';
            }
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-paper-plane me-1"></i>إرسال التقرير الآن';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (statusDiv) {
            statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-1"></i>حدث خطأ أثناء الإرسال</div>';
        }
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane me-1"></i>إرسال التقرير الآن';
        }
    });
}

// Search and Filter Functions
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('studentSearchInput');
    const statusFilter = document.getElementById('studentStatusFilter');
    const studentRows = document.querySelectorAll('.student-row');
    const noResultsRow = document.getElementById('noResultsRow');
    const totalCountSpan = document.getElementById('totalCount');
    const filteredCountSpan = document.getElementById('filteredCount');
    
    // Check if elements exist
    if (!searchInput || !statusFilter || !noResultsRow || !totalCountSpan || !filteredCountSpan) {
        console.error('Search elements not found');
        return;
    }
    
    const totalCount = studentRows.length;
    console.log('Total students found:', totalCount);
    
    if (totalCountSpan) {
        totalCountSpan.textContent = totalCount;
    }
    
    if (totalCount === 0) {
        console.warn('No student rows found');
        return;
    }
    
    function filterStudents() {
        const searchTerm = (searchInput.value || '').toLowerCase().trim();
        const statusValue = statusFilter.value;
        let visibleCount = 0;
        let hasVisibleRows = false;
        
        studentRows.forEach(row => {
            const fullName = row.getAttribute('data-full-name') || '';
            const username = row.getAttribute('data-username') || '';
            const className = row.getAttribute('data-class-name') || '';
            const sectionName = row.getAttribute('data-section-name') || '';
            const status = row.getAttribute('data-status') || '';
            
            // Search filter - check all fields
            const matchesSearch = !searchTerm || 
                fullName.includes(searchTerm) || 
                username.includes(searchTerm) || 
                className.includes(searchTerm) || 
                sectionName.includes(searchTerm);
            
            // Status filter
            const matchesStatus = statusValue === 'all' || status === statusValue;
            
            // Show/hide row
            if (matchesSearch && matchesStatus) {
                row.style.display = '';
                row.classList.remove('d-none');
                visibleCount++;
                hasVisibleRows = true;
            } else {
                row.style.display = 'none';
                row.classList.add('d-none');
            }
        });
        
        // Show/hide "no results" message
        if (hasVisibleRows) {
            if (noResultsRow) {
                noResultsRow.classList.add('d-none');
            }
        } else {
            if (noResultsRow) {
                noResultsRow.classList.remove('d-none');
            }
        }
        
        // Update count
        if (filteredCountSpan) {
            filteredCountSpan.textContent = visibleCount;
        }
        
        console.log('Filter applied - Search:', searchTerm, 'Status:', statusValue, 'Visible:', visibleCount);
    }
    
    // Event listeners
    searchInput.addEventListener('input', filterStudents);
    searchInput.addEventListener('keyup', filterStudents);
    searchInput.addEventListener('paste', function() {
        setTimeout(filterStudents, 10);
    });
    
    statusFilter.addEventListener('change', filterStudents);
    
    // Initial filter
    filterStudents();
    
    console.log('Search and filter initialized successfully');
});
</script>
"""

# ----------------- MODIFIED reports_content_block -----------------
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
                <h4>الطالب: {{ student.full_name or student.username }}</h4>
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
                
                {# ================== START: DYNAMIC REPORTS MODIFICATION ================== #}
                <hr>
                <h5 class="card-title mt-4">الفيديوهات المنهجية والتقييمات</h5>
                {# جلب معايير المنهجي #}
                {% set manhaji_criteria = all_criteria.get('منهجي', []) %}
                {% if student.videos_manhaji %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover small">
                            <thead>
                                <tr>
                                    <th>عنوان الفيديو</th>
                                    <th>تاريخ الرفع</th>
                                    {# عرض أسماء المعايير بشكل ديناميكي #}
                                    {% for criterion in manhaji_criteria %}
                                        <th title="{{ criterion.name }}"><i class="fas fa-star"></i> {{ criterion.name }}</th>
                                    {% endfor %}
                                    <th>مجموع <i class="fas fa-star text-warning"></i></th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for video in student.videos_manhaji %}
                                <tr>
                                    <td>{{ video.title }}</td>
                                    <td>{{ video.timestamp | strftime('%Y-%m-%d') }}</td>
                                    {# عرض التقييم (صح/خطأ) لكل معيار #}
                                    {% set video_ratings = video.ratings %}
                                    {% for criterion in manhaji_criteria %}
                                        <td>
                                            {% if video_ratings.get(criterion.key, 0) == 1 %}
                                                <i class="fas fa-check-circle text-success fa-lg"></i>
                                            {% else %}
                                                <i class="fas fa-times-circle text-danger fa-lg"></i>
                                            {% endif %}
                                        </td>
                                    {% endfor %}
                                    <td class="fw-bold">{{ video.total_stars }} / {{ manhaji_criteria | length }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">لم يقم هذا الطالب برفع أي فيديوهات منهجية بعد.</p>
                {% endif %}

                <hr>
                <h5 class="card-title mt-4">تقرير الفيديوهات الإثرائية</h5>
                {# جلب معايير الاثرائي #}
                {% set ithrai_criteria = all_criteria.get('اثرائي', []) %}
                {% if student.videos_ithrai %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover small">
                            <thead>
                                <tr>
                                    <th>عنوان الفيديو</th>
                                    <th>التاريخ</th>
                                    {# عرض أسماء المعايير بشكل ديناميكي #}
                                    {% for criterion in ithrai_criteria %}
                                        <th title="{{ criterion.name }}"><i class="fas fa-star"></i> {{ criterion.name }}</th>
                                    {% endfor %}
                                    <th>المجموع <i class="fas fa-star text-warning"></i></th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for video in student.videos_ithrai %}
                                <tr>
                                    <td>{{ video.title }}</td>
                                    <td>{{ video.timestamp | strftime('%Y-%m-%d') }}</td>
                                    {# عرض التقييم (صح/خطأ) لكل معيار #}
                                    {% set video_ratings = video.ratings %}
                                    {% for criterion in ithrai_criteria %}
                                        <td>
                                            {% if video_ratings.get(criterion.key, 0) == 1 %}
                                                <i class="fas fa-check text-success"></i>
                                            {% else %}
                                                <i class="fas fa-times text-danger"></i>
                                            {% endif %}
                                        </td>
                                    {% endfor %}
                                    <td class="fw-bold">{{ video.total_stars }} / {{ ithrai_criteria | length }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">لم يقم هذا الطالب برفع أي فيديوهات إثرائية بعد.</p>
                {% endif %}
                {# ================== END: DYNAMIC REPORTS MODIFICATION ================== #}

            </div>
        </div>
        {% endfor %}
    {% else %}
        <p class="text-center text-muted mt-5">لا توجد بيانات لعرضها تطابق معايير البحث.</p>
    {% endif %}
</div>
"""

# ----------------- MODIFIED profile_content_block -----------------
profile_content_block = """
<div class="profile-header p-4 rounded mb-4 bg-white shadow-sm" style="background-color: rgba(255, 255, 255, 0.95);">
    <div class="d-flex align-items-center">
        <img src="{{ url_for('uploaded_file', filename=user.profile_image) }}" alt="Profile Image" class="rounded-circle" width="150" height="150" style="border: 4px solid #0d6efd;">
        <div class="profile-info ms-4">
            {% if user.role == 'admin' %}
                <h1 class="admin-username-gradient"><i class="fas fa-crown"></i> {{ user.full_name or user.username }}</h1>
            {% else %}
                <h1 class="text-primary">{{ user.full_name or user.username }}</h1>
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
<h2 class="mb-4 text-center">مقاطع الفيديو الخاصة بـ {{ user.full_name or user.username }}</h2>
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
    {% for video in videos %}
    <div class="col">
        <div class="card h-100 video-card shadow-sm">
            <video controls class="card-img-top" style="background-color:#000;">
                <source src="{{ url_for('uploaded_file', filename=video.filepath) }}" type="video/mp4">
            </video>
            
            {# START: Delete button for video owner and admin - directly under video #}
            {% if session['user_id'] == video.user_id or session['role'] == 'admin' %}
            <div class="text-center p-2">
                <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                    <button type="submit" class="btn btn-sm btn-danger"><i class="fas fa-trash me-1"></i>حذف الفيديو</button>
                </form>
            </div>
            {% endif %}
            {# END: Delete button #}

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
                        {# ================== DYNAMIC RATING MODIFICATION ================== #}
                        {% set rating_info = video_ratings.get(video.id) %}
                        {% set total_stars = rating_info.total_stars if rating_info else 0 %}
                        {% set max_stars = rating_info.max_stars if rating_info else (10 if video.video_type == 'اثرائي' else 4) %}
                        <span id="stars-display-{{ video.id }}">
                            {% if total_stars > 0 %}
                                <i class="fas fa-star"></i>
                                {{ total_stars }} / {{ max_stars }}
                            {% else %}
                                <small class="text-muted">لم يُقيّم</small>
                            {% endif %}
                        </span>
                        {# ================== END DYNAMIC RATING MODIFICATION ================== #}
                    </div>
                </div>
                
                {# ================== START: DYNAMIC RATING FORM MODIFICATION ================== #}
                {% if session.role == 'admin' %}
                <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
                     <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
                    
                    {% set current_video_ratings = video_ratings.get(video.id).ratings if video_ratings.get(video.id) else {} %}
                    {% set criteria_list = all_criteria.get(video.video_type, []) %}

                     <div class="mt-2">
                        <div class="row">
                            {% for criterion in criteria_list %}
                            <div class="col-md-6 col-12">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" 
                                           name="{{ criterion.key }}" 
                                           id="{{ criterion.key }}-{{video.id}}" 
                                           {% if current_video_ratings.get(criterion.key, 0) == 1 %}checked{% endif %}>
                                    <label class="form-check-label" for="{{ criterion.key }}-{{video.id}}">{{ criterion.name }}</label>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </form>
                {% endif %}
                {# ================== END: DYNAMIC RATING FORM MODIFICATION ================== #}
                
                <div class="comments-section mt-auto pt-3">
                     <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                        {% set comments = video_comments.get(video.id, {}).get('toplevel', []) %}
                        {% for comment in comments %}
                        <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                            <img src="{{ url_for('uploaded_file', filename=(comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                            <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                                <div class="d-flex justify-content-between">
                                    <p class="comment-author fw-bold mb-0">
                                        {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                        {% if comment.role == 'admin' %}
                                            <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.full_name or comment.username }}</span>
                                        {% else %}
                                            <span class="text-primary">{{ comment.full_name or comment.username }}</span>
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
    <p class="text-center text-muted">{{ user.full_name or user.username }} لم يقم بنشر أي مقاطع فيديو بعد.</p>
    {% endfor %}
</div>
"""

# ----------------- students_content_block (No Changes) -----------------
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
                <img src="{{ url_for('uploaded_file', filename=(student.profile_image or 'default.png')) }}" alt="Profile Image" class="rounded-circle mb-3" width="100" height="100" style="border: 3px solid #0d6efd; object-fit: cover;">
                <h5 class="card-title text-primary">{{ student.full_name or student.username }}</h5>
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
# ----------------- conversations_content_block (No Changes) -----------------
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

# ----------------- student_chat_content_block (No Changes) -----------------
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

# ----------------- MODIFIED video_review_content_block -----------------
video_review_content_block = """
<h1 class="mb-4 text-center">مراجعة الفيديوهات</h1>
<p class="text-center text-muted">هنا تظهر جميع الفيديوهات التي بانتظار الموافقة.</p>

<div class="row row-cols-1 row-cols-md-2 g-4">
    {% for video in videos %}
    <div class="col">
        <div class="card h-100 video-card shadow-sm">
            <div class="card-header bg-transparent border-0 pt-3">
                <div class="d-flex align-items-center">
                     <img src="{{ url_for('uploaded_file', filename=(video.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="50" height="50">
                    <div class="ms-3">
                        <a href="{{ url_for('profile', username=video.username) }}" class="text-decoration-none h5">
                            <span class="text-primary">{{ video.full_name or video.username }}</span>
                        </a>
                         <small class="d-block"><span class="badge bg-info">{{ video.video_type }}</span> <span class="text-muted ms-2">{{ video.timestamp | strftime }}</span></small>
                    </div>
                </div>
            </div>

            <video controls class="card-img-top" style="background-color:#000; border-radius: 0;">
                <source src="{{ url_for('uploaded_file', filename=video.filepath) }}" type="video/mp4">
            </video>

            {# START: Delete button for video owner and admin - directly under video #}
            {% if session['user_id'] == video.user_id or session['role'] == 'admin' %}
            <div class="text-center p-2">
                <form action="{{ url_for('delete_video', video_id=video.id) }}" method="post" class="d-inline" onsubmit="return confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا.');">
                    <button type="submit" class="btn btn-sm btn-danger"><i class="fas fa-trash me-1"></i>حذف الفيديو</button>
                </form>
            </div>
            {% endif %}
            {# END: Delete button #}

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
                        {# ================== DYNAMIC RATING MODIFICATION ================== #}
                        {% set rating_info = video_ratings.get(video.id) %}
                        {% set total_stars = rating_info.total_stars if rating_info else 0 %}
                        {% set max_stars = rating_info.max_stars if rating_info else (10 if video.video_type == 'اثرائي' else 4) %}
                        <span id="stars-display-{{ video.id }}">
                            {% if total_stars > 0 %}
                                <i class="fas fa-star"></i>
                                {{ total_stars }} / {{ max_stars }}
                            {% else %}
                                <small class="text-muted">لم يُقيّم</small>
                            {% endif %}
                        </span>
                        {# ================== END DYNAMIC RATING MODIFICATION ================== #}
                    </div>
                </div>

                {# ================== START: DYNAMIC RATING FORM MODIFICATION ================== #}
                <form class="rating-form p-3 mt-3 rounded bg-light" data-video-id="{{ video.id }}" data-video-type="{{ video.video_type }}">
                     <small class="form-text text-muted">تقييم المسؤول ({{video.video_type}}):</small>
                    
                    {% set current_video_ratings = video_ratings.get(video.id).ratings if video_ratings.get(video.id) else {} %}
                    {% set criteria_list = all_criteria.get(video.video_type, []) %}

                     <div class="mt-2">
                        <div class="row">
                            {% for criterion in criteria_list %}
                            <div class="col-md-6 col-12">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" 
                                           name="{{ criterion.key }}" 
                                           id="{{ criterion.key }}-{{video.id}}" 
                                           {% if current_video_ratings.get(criterion.key, 0) == 1 %}checked{% endif %}>
                                    <label class="form-check-label" for="{{ criterion.key }}-{{video.id}}">{{ criterion.name }}</label>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </form>
                {# ================== END: DYNAMIC RATING FORM MODIFICATION ================== #}

                <div class="comments-section mt-auto pt-3">
                     <ul class="list-unstyled" id="comments-list-{{ video.id }}">
                        {% set comments = video_comments.get(video.id, {}).get('toplevel', []) %}
                        {% for comment in comments %}
                        <li class="comment d-flex mb-2" id="comment-{{ comment.id }}">
                            <img src="{{ url_for('uploaded_file', filename=(comment.profile_image or 'default.png')) }}" alt="Avatar" class="rounded-circle" width="40" height="40">
                            <div class="comment-body ms-2 p-2 rounded w-100 {% if comment.is_pinned %}bg-warning bg-opacity-25{% else %}bg-light{% endif %}">
                                <div class="d-flex justify-content-between">
                                    <p class="comment-author fw-bold mb-0">
                                        {% if comment.is_pinned %}<i class="fas fa-thumbtack text-primary me-2" title="تعليق مثبت"></i>{% endif %}
                                        {% if comment.role == 'admin' %}
                                            <span class="admin-username-gradient"><i class="fas fa-crown"></i> {{ comment.full_name or comment.username }}</span>
                                        {% else %}
                                            <span class="text-primary">{{ comment.full_name or comment.username }}</span>
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

# ----------------- edit_user_html (No Changes) -----------------
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
                                {% if user.profile_image %}<img src="{{ url_for('uploaded_file', filename=user.profile_image) }}" alt="Profile Image" width="100" class="mt-2 rounded">{% endif %}
                            </div>

                            {# START: TELEGRAM SETTINGS (Admin Only) #}
                            {% if session['role'] == 'admin' and user.role == 'admin' %}
                            <h4 class="mt-4">إعدادات تليجرام</h4>
                            <hr>
                            <div class="mb-3">
                                <label for="telegram_bot_token" class="form-label">Telegram Bot Token</label>
                                <input type="text" class="form-control" id="telegram_bot_token" name="telegram_bot_token" value="{{ telegram_settings.bot_token if telegram_settings else '' }}" placeholder="أدخل Bot Token">
                                <small class="form-text text-muted">يمكنك الحصول على Bot Token من @BotFather في تليجرام</small>
                            </div>
                            <div class="mb-3">
                                <label for="telegram_chat_id" class="form-label">Telegram Chat ID</label>
                                <input type="text" class="form-control" id="telegram_chat_id" name="telegram_chat_id" value="{{ telegram_settings.chat_id if telegram_settings else '' }}" placeholder="أدخل Chat ID">
                                <small class="form-text text-muted">يمكنك الحصول على Chat ID من @userinfobot في تليجرام</small>
                            </div>
                            {% endif %}
                            {# END: TELEGRAM SETTINGS #}

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

# ----------------- conversations_script_block (No Changes) -----------------
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
                const displayName = user.full_name || user.username;
                userItem.dataset.displayName = displayName;
                userItem.innerHTML = `
                    <div class="d-flex align-items-center">
                        <img src="${ "{{ url_for('uploaded_file', filename='FILL_IN') }}".replace('FILL_IN', user.profile_image || 'default.png') }" class="rounded-circle me-2" width="40" height="40">
                        <div>
                            <div>${displayName}</div>
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
            const displayName = target.dataset.displayName || userName;
            currentConversation = { type: 'user', id: userId, name: userName, class: null, section: null };
            chatWithName.textContent = displayName;
            chatWithInfo.textContent = 'محادثة فردية';

            // إصلاح: منع التكرار اللانهائي - إضافة تنظيف عند تغيير المحادثة
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
            fetchMessages(userId);
            // إصلاح: إضافة معالجة أخطاء لمنع التكرار عند الفشل
            let errorCount = 0;
            pollingInterval = setInterval(() => {
                if (errorCount > 3) {
                    clearInterval(pollingInterval);
                    console.warn('Stopped polling due to repeated errors');
                    return;
                }
                fetchMessages(userId).catch(() => {
                    errorCount++;
                });
            }, 5000);

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

# ----------------- student_chat_script_block (No Changes) -----------------
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

    // إصلاح: منع التكرار اللانهائي - إضافة تنظيف ومعالجة أخطاء
    let messagePollingInterval = null;
    let errorCount = 0;
    
    function startMessagePolling() {
        // تنظيف أي polling سابق
        if (messagePollingInterval) {
            clearInterval(messagePollingInterval);
        }
        errorCount = 0;
        
        // جلب الرسائل فوراً
        fetchMessages();
        
        // بدء polling مع معالجة أخطاء
        messagePollingInterval = setInterval(() => {
            if (errorCount > 3) {
                clearInterval(messagePollingInterval);
                console.warn('Stopped message polling due to repeated errors');
                return;
            }
            fetchMessages().catch(() => {
                errorCount++;
            });
        }, 5000);
    }
    
    // بدء polling عند تحميل الصفحة
    startMessagePolling();
    
    // تنظيف عند إغلاق الصفحة
    window.addEventListener('beforeunload', () => {
        if (messagePollingInterval) {
            clearInterval(messagePollingInterval);
        }
    });
});
</script>
"""
# ----------------- NEW: admin_criteria_content_block -----------------
# (This is the new template for the criteria management page)
admin_criteria_content_block = """
<h1 class="mb-4">إدارة معايير التقييم</h1>
<p>هنا يمكنك إضافة أو حذف المعايير التي تظهر للمدير عند تقييم الفيديوهات.</p>

<div class="row">
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-header"><h4><i class="fas fa-plus-circle me-2"></i>إضافة معيار جديد</h4></div>
            <div class="card-body">
                <form action="{{ url_for('add_criterion') }}" method="post">
                    <div class="mb-3">
                        <label for="criterion_name" class="form-label">اسم المعيار (ما يراه المدير)</label>
                        <input type="text" name="name" class="form-control" id="criterion_name" placeholder="مثال: الإبداع" required>
                    </div>
                    <div class="mb-3">
                        <label for="criterion_key" class="form-label">المفتاح البرمجي (انجليزي بدون مسافات)</label>
                        <input type="text" name="key" class="form-control" id="criterion_key" placeholder="مثال: creativity" required>
                        <small class="form-text text-muted">يجب أن يكون فريداً (لا يتكرر).</small>
                    </div>
                    <div class="mb-3">
                        <label for="video_type" class="form-label">نوع الفيديو</label>
                        <select name="video_type" id="video_type" class="form-select" required>
                            <option value="" disabled selected>اختر النوع...</option>
                            <option value="منهجي">منهجي</option>
                            <option value="اثرائي">اثرائي</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">إضافة المعيار</button>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-8 mb-4">
        <div class="card shadow-sm">
            <div class="card-header"><h4><i class="fas fa-list-ul me-2"></i>المعايير الحالية</h4></div>
            <div class="card-body">
                
                <h5 class="text-primary">معايير "منهجي" (المجموع: {{ criteria.منهجي | length }})</h5>
                <ul class="list-group mb-4">
                    {% for c in criteria.منهجي %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong>{{ c.name }}</strong>
                            <br><small class="text-muted">المفتاح: {{ c.key }}</small>
                        </div>
                        <form action="{{ url_for('delete_criterion', criterion_id=c.id) }}" method="post" onsubmit="return confirm('هل أنت متأكد من حذف هذا المعيار؟');">
                            <button type="submit" class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                        </form>
                    </li>
                    {% else %}
                    <li class="list-group-item text-muted">لا توجد معايير حالياً.</li>
                    {% endfor %}
                </ul>

                <h5 class="text-info">معايير "اثرائي" (المجموع: {{ criteria.اثرائي | length }})</h5>
                <ul class="list-group">
                    {% for c in criteria.اثرائي %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong>{{ c.name }}</strong>
                            <br><small class="text-muted">المفتاح: {{ c.key }}</small>
                        </div>
                        <form action="{{ url_for('delete_criterion', criterion_id=c.id) }}" method="post" onsubmit="return confirm('هل أنت متأكد من حذف هذا المعيار؟');">
                            <button type="submit" class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                        </form>
                    </li>
                    {% else %}
                    <li class="list-group-item text-muted">لا توجد معايير حالياً.</li>
                    {% endfor %}
                </ul>

            </div>
        </div>
    </div>
</div>
"""


# ----------------- UPDATED content_blocks dictionary -----------------
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
    'video_review': video_review_content_block,
    'admin_criteria': admin_criteria_content_block # <--- السطر الجديد المضاف
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
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE_MB', '200')) * 1024 * 1024
app.config['JSON_SORT_KEYS'] = False

WAITRESS_LISTEN = os.getenv('WAITRESS_LISTEN', '0.0.0.0:10000')
WAITRESS_THREADS = int(os.getenv('WAITRESS_THREADS', '8'))
WAITRESS_CONNECTION_LIMIT = int(os.getenv('WAITRESS_CONNECTION_LIMIT', '100'))
WAITRESS_CHANNEL_TIMEOUT = int(os.getenv('WAITRESS_CHANNEL_TIMEOUT', '60'))
WAITRESS_BACKLOG = int(os.getenv('WAITRESS_BACKLOG', '128'))
WAITRESS_LOOP_TIMEOUT = float(os.getenv('WAITRESS_LOOP_TIMEOUT', '1'))

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
    """
    Get database connection with connection pooling
    إصلاح: تحسين إدارة الاتصالات لمنع تسريب الذاكرة
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            timeout=20.0,  # إصلاح: إضافة timeout لمنع التعليق
            check_same_thread=False  # للسماح بالاستخدام من threads متعددة
        )
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")  # تفعيل مفاتيح العلاقات الخارجية
        # إصلاح: تحسين الأداء
        db.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging للأداء الأفضل
        db.execute("PRAGMA synchronous = NORMAL")  # توازن بين الأداء والموثوقية
        db.execute("PRAGMA cache_size = -64000")  # 64MB cache
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
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE 
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, user_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL, parent_id INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE, 
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE
            )''') # إضافة ON DELETE CASCADE

        # ================== START: DYNAMIC RATING TABLES ==================
        # تم حذف جدول video_ratings القديم
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rating_criteria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                key TEXT UNIQUE NOT NULL,
                video_type TEXT NOT NULL CHECK(video_type IN ('منهجي', 'اثرائي'))
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dynamic_video_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                criterion_id INTEGER NOT NULL,
                is_awarded INTEGER DEFAULT 0,
                admin_id INTEGER NOT NULL,
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
                FOREIGN KEY (criterion_id) REFERENCES rating_criteria (id) ON DELETE CASCADE,
                FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(video_id, criterion_id)
            )''')
        # ================== END: DYNAMIC RATING TABLES ==================

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, video_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE, 
                UNIQUE(video_id, user_id)
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suspensions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                end_date DATETIME NOT NULL, reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS star_bank (
                user_id INTEGER PRIMARY KEY,
                banked_stars INTEGER NOT NULL DEFAULT 0,
                last_updated_week_start_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
            )''') # إضافة ON DELETE CASCADE

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_bindings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                device_fingerprint TEXT NOT NULL,
                auth_token TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )''')
        
        # ================== START: TELEGRAM SETTINGS TABLE ==================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_token TEXT,
                chat_id TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        # ================== END: TELEGRAM SETTINGS TABLE ==================
        
        # --- إضافة المعايير الافتراضية (القديمة) إلى الجدول الجديد ---
        cursor.execute("SELECT COUNT(id) FROM rating_criteria")
        if cursor.fetchone()[0] == 0:
            print("لم يتم العثور على معايير، سيتم إضافة المعايير الافتراضية...")
            # ملاحظة: تم تغيير المفاتيح لتكون فريدة
            default_criteria = [
                # معايير المنهجي
                ('المشاركة', 'participation_m', 'منهجي'),
                ('الحفظ', 'memorization_m', 'منهجي'),
                ('النطق', 'pronunciation_m', 'منهجي'),
                ('الوسائل', 'use_of_aids_m', 'منهجي'),
                
                # معايير الاثرائي
                ('المشاركة', 'participation_e', 'اثرائي'),
                ('الحفظ', 'memorization_e', 'اثرائي'),
                ('النطق', 'pronunciation_e', 'اثرائي'),
                ('الوسائل', 'use_of_aids_e', 'اثرائي'),
                ('التصوير والإضاءة', 'filming_lighting_e', 'اثرائي'),
                ('جودة الصوت', 'sound_quality_e', 'اثرائي'),
                ('السلوك', 'behavior_e', 'اثرائي'),
                ('النظافة', 'cleanliness_e', 'اثرائي'),
                ('موقع التصوير', 'location_e', 'اثرائي'),
                ('الثقة', 'confidence_e', 'اثرائي')
            ]
            cursor.executemany("INSERT INTO rating_criteria (name, key, video_type) VALUES (?, ?, ?)", default_criteria)
            print(f"تم إضافة {len(default_criteria)} معيار افتراضي بنجاح.")


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

        # --- تم حذف ترحيل جدول video_ratings القديم ---

        # --- End Schema Migration ---

        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        if cursor.fetchone() is None:
            hashed_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password, role, is_profile_complete) VALUES (?, ?, ?, 1)",
                           ('admin', hashed_password, 'admin'))

        db.commit()
        print("Database structure is ready.")

# ----------------- HELPER FUNCTIONS -----------------

_UPLOAD_DIR_LOCK = Lock()
_CRITERIA_CACHE_LOCK = Lock()
_CRITERIA_CACHE = {"expires": 0, "value": None}
CRITERIA_CACHE_TTL = int(os.getenv('CRITERIA_CACHE_TTL', '60'))

def safe_row_value(row, key, default=None):
    """Safely read a value from sqlite3.Row or dict without using .get()."""
    if row is None:
        return default
    try:
        if hasattr(row, 'keys'):
            row_keys = row.keys()
            if key in row_keys:
                return row[key]
        if isinstance(row, dict) and key in row:
            return row[key]
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default

def ensure_upload_directory():
    """Create uploads directory if missing and return its absolute path."""
    upload_dir = app.config['UPLOAD_FOLDER']
    with _UPLOAD_DIR_LOCK:
        os.makedirs(upload_dir, exist_ok=True)
    return os.path.abspath(upload_dir)

def resolve_upload_path(filename):
    """Build a safe absolute path for uploads, preventing traversal attacks."""
    if not filename:
        raise ValueError('اسم الملف غير صالح.')
    upload_dir = ensure_upload_directory()
    destination = os.path.abspath(os.path.join(upload_dir, filename))
    if not destination.startswith(upload_dir):
        raise ValueError('تم رفض المسار المطلوب.')
    return destination

def load_all_criteria(force_refresh=False):
    """Cache rating criteria to reduce repetitive reads under load."""
    now = time.time()
    with _CRITERIA_CACHE_LOCK:
        cached = _CRITERIA_CACHE['value']
        if not force_refresh and cached and now < _CRITERIA_CACHE['expires']:
            return cached

    db = get_db()
    rows = db.execute("SELECT id, name, key, video_type FROM rating_criteria").fetchall()
    criteria_by_type = defaultdict(list)
    criteria_key_map = {}
    for row in rows:
        row_dict = dict(row)
        criteria_by_type[row_dict['video_type']].append(row_dict)
        criteria_key_map[row_dict['key']] = row_dict

    # Ensure known keys always exist for templates
    for preset in ('منهجي', 'اثرائي'):
        criteria_by_type.setdefault(preset, [])

    cached_payload = {
        'by_type': {key: list(value) for key, value in criteria_by_type.items()},
        'by_key': criteria_key_map
    }
    with _CRITERIA_CACHE_LOCK:
        _CRITERIA_CACHE['value'] = cached_payload
        _CRITERIA_CACHE['expires'] = now + CRITERIA_CACHE_TTL
    return cached_payload

def invalidate_criteria_cache():
    """Reset cached criteria after writes."""
    with _CRITERIA_CACHE_LOCK:
        _CRITERIA_CACHE['value'] = None
        _CRITERIA_CACHE['expires'] = 0

# ================== START: DEVICE BINDING FUNCTIONS ==================
def generate_auth_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def hash_device_fingerprint(fingerprint):
    """Hash device fingerprint for storage"""
    return hashlib.sha256(fingerprint.encode()).hexdigest()

def verify_device_binding(user_id, device_fingerprint):
    """Verify if device fingerprint matches user's bound device"""
    db = get_db()
    # Get user role to check if admin
    user = db.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Admin can login from any device - skip device binding check
    if user and user['role'] == 'admin':
        # For admin, get or create a token but don't enforce device binding
        binding = db.execute(
            'SELECT auth_token FROM device_bindings WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        if binding:
            return True, binding['auth_token']
        # If no binding exists, return None to create one
        return None, None
    
    # For students, enforce device binding
    binding = db.execute(
        'SELECT device_fingerprint, auth_token FROM device_bindings WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    if not binding:
        return None, None
    
    hashed_fingerprint = hash_device_fingerprint(device_fingerprint)
    if binding['device_fingerprint'] == hashed_fingerprint:
        return True, binding['auth_token']
    return False, None

def bind_device_to_user(user_id, device_fingerprint):
    """Bind device to user account"""
    db = get_db()
    # Check if user is admin
    user = db.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    
    hashed_fingerprint = hash_device_fingerprint(device_fingerprint) if device_fingerprint != 'pending' else hash_device_fingerprint('pending')
    auth_token = generate_auth_token()
    
    # Check if user already has a binding
    existing = db.execute('SELECT id FROM device_bindings WHERE user_id = ?', (user_id,)).fetchone()
    
    if existing:
        if user and user['role'] == 'admin':
            # For admin, just update token and timestamp, keep device_fingerprint as is (allow multiple devices)
            db.execute(
                'UPDATE device_bindings SET auth_token = ?, last_used = CURRENT_TIMESTAMP WHERE user_id = ?',
                (auth_token, user_id)
            )
        else:
            # For students, update device fingerprint (one device only)
            db.execute(
                'UPDATE device_bindings SET device_fingerprint = ?, auth_token = ?, last_used = CURRENT_TIMESTAMP WHERE user_id = ?',
                (hashed_fingerprint, auth_token, user_id)
            )
    else:
        # Create new binding
        db.execute(
            'INSERT INTO device_bindings (user_id, device_fingerprint, auth_token) VALUES (?, ?, ?)',
            (user_id, hashed_fingerprint, auth_token)
        )
    
    db.commit()
    return auth_token

def unbind_device(user_id):
    """Unbind device from user account (admin only)"""
    db = get_db()
    db.execute('DELETE FROM device_bindings WHERE user_id = ?', (user_id,))
    db.commit()

def get_user_by_token(auth_token):
    """Get user by auth token"""
    db = get_db()
    binding = db.execute(
        'SELECT user_id FROM device_bindings WHERE auth_token = ?',
        (auth_token,)
    ).fetchone()
    
    if binding:
        user = db.execute('SELECT * FROM users WHERE id = ?', (binding['user_id'],)).fetchone()
        return user
    
    # For admin, also check if token matches any admin token (for multi-device support)
    # This allows admin to login even if device binding doesn't match
    return None

def update_token_last_used(auth_token):
    """Update last used timestamp for token"""
    db = get_db()
    db.execute(
        'UPDATE device_bindings SET last_used = CURRENT_TIMESTAMP WHERE auth_token = ?',
        (auth_token,)
    )
    db.commit()
# ================== END: DEVICE BINDING FUNCTIONS ==================

# ================== START: SAFE ROW ACCESS HELPER ==================
def safe_row_get(row, key, default=None):
    """
    الوصول الآمن للقيم من sqlite3.Row أو dict
    إصلاح: sqlite3.Row لا يدعم .get() لذلك نستخدم هذه الدالة
    """
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    # sqlite3.Row case
    try:
        if key in row.keys():
            return row[key]
        return default
    except (KeyError, TypeError, AttributeError):
        return default
# ================== END: SAFE ROW ACCESS HELPER ==================

# ================== START: SUMMARY OF FIXES ==================
"""
ملخص الإصلاحات المطبقة على الكود:

1️⃣ إصلاح خطأ sqlite3.Row:
   - استبدال جميع استخدامات .get() على sqlite3.Row بـ safe_row_value()
   - إضافة دالة safe_row_get() للوصول الآمن
   - إصلاح دالة /auto-login لاستخدام safe_row_value في جميع الأماكن
   - إصلاح دالة login() و before_request_handler() لاستخدام safe_row_value

2️⃣ منع التكرار اللانهائي (infinite loop):
   - إضافة حماية في attemptAutoLogin() لمنع المحاولات المتكررة
   - إصلاح setInterval في admin chat: إضافة تنظيف عند تغيير المحادثة + معالجة أخطاء
   - إصلاح setInterval في student chat: إضافة تنظيف + معالجة أخطاء + إيقاف عند 3 أخطاء
   - منع إعادة المحاولة التلقائية عند فشل auto-login

3️⃣ إصلاح مشكلة Waitress Task Queue:
   - تحسين إعدادات Waitress: cleanup_interval, recv_bytes, send_bytes
   - إضافة timeout للاتصالات (20 ثانية)
   - تحسين معالجة الملفات الكبيرة

4️⃣ تحسين /auto-login بالكامل:
   - إضافة try/except شامل لمعالجة جميع الأخطاء
   - التحقق من وجود البيانات قبل المعالجة
   - استخدام safe_row_value في جميع الأماكن
   - إضافة معالجة أخطاء لكل خطوة (device binding, suspension check, session creation)
   - منع سقوط السيرفر عند أي خطأ

5️⃣ تحسين الأداء:
   - تحسين إعدادات SQLite: WAL mode, cache_size, synchronous
   - إضافة timeout للاتصالات
   - تحسين إدارة الاتصالات لمنع تسريب الذاكرة
   - إضافة check_same_thread=False للسماح بالاستخدام من threads متعددة

6️⃣ إعادة كتابة الكود:
   - توحيد استخدام safe_row_value في جميع الأماكن الحرجة
   - إضافة تعليقات توضيحية بالعربية
   - تحسين معالجة الأخطاء
"""
# ================== END: SUMMARY OF FIXES ==================

# ================== START: MODIFIED get_champion_statuses ==================
def get_champion_statuses():
    db = get_db()
    today = date.today()
    statuses = {}
    
    # 1. جلب جميع المعايير الديناميكية
    criteria = db.execute("SELECT id, key, video_type FROM rating_criteria").fetchall()
    criteria_map = {c['key']: c['id'] for c in criteria}
    manhaji_criteria_count = db.execute("SELECT COUNT(id) FROM rating_criteria WHERE video_type = 'منهجي'").fetchone()[0]
    ithrai_criteria_count = db.execute("SELECT COUNT(id) FROM rating_criteria WHERE video_type = 'اثرائي'").fetchone()[0]

    if ithrai_criteria_count > 0:
        # 2. أبطال خارقون (الحاصلون على 10/10 أو Max/Max في فيديو إثرائي هذا الشهر)
        start_of_month = today.replace(day=1)
        superhero_query = """
            SELECT v.user_id, SUM(dr.is_awarded) as total_stars
            FROM dynamic_video_ratings dr
            JOIN videos v ON dr.video_id = v.id
            JOIN rating_criteria rc ON dr.criterion_id = rc.id
            WHERE rc.video_type = 'اثرائي' AND date(v.timestamp) >= ?
            GROUP BY v.user_id, v.id
            HAVING total_stars = ?
        """
        superhero_rows = db.execute(superhero_query, (start_of_month.strftime('%Y-%m-%d'), ithrai_criteria_count)).fetchall()
        for row in superhero_rows:
            statuses[row['user_id']] = 'بطل خارق'

        # 3. بطل الشهر (أعلى مجموع نجوم إثرائية هذا الشهر)
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1)) if start_of_month.month != 12 else date(start_of_month.year, 12, 31)
        monthly_champions_query = """
            SELECT v.user_id, SUM(dr.is_awarded) as total_stars
            FROM dynamic_video_ratings dr
            JOIN videos v ON dr.video_id = v.id
            JOIN rating_criteria rc ON dr.criterion_id = rc.id
            WHERE rc.video_type = 'اثرائي' AND date(v.timestamp) BETWEEN ? AND ?
            GROUP BY v.user_id ORDER BY total_stars DESC LIMIT 1;
        """
        monthly_champion_row = db.execute(monthly_champions_query, (start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d'))).fetchone()
        if monthly_champion_row and monthly_champion_row['total_stars'] and monthly_champion_row['total_stars'] > 0:
            monthly_champion_id = monthly_champion_row['user_id']
            if monthly_champion_id not in statuses:
                statuses[monthly_champion_id] = 'بطل الشهر'

    # 4. بطل الأسبوع (نظام النجوم المنهجية)
    if manhaji_criteria_count > 0:
        days_since_saturday = (today.weekday() + 2) % 7
        start_of_week = today - timedelta(days=days_since_saturday)
        start_of_previous_week = start_of_week - timedelta(days=7)
        
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
                SELECT SUM(dr.is_awarded) as stars
                FROM dynamic_video_ratings dr
                JOIN videos v ON dr.video_id = v.id
                JOIN rating_criteria rc ON dr.criterion_id = rc.id
                WHERE rc.video_type = 'منهجي' AND v.user_id = ? AND date(v.timestamp) >= ?
            """, (student_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
            
            new_stars = new_stars_row['stars'] if new_stars_row and new_stars_row['stars'] is not None else 0
            total_score_this_week = carried_stars + new_stars
            stars_to_bank_for_next_week = 0
            
            if total_score_this_week >= manhaji_criteria_count:
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
# ================== END: MODIFIED get_champion_statuses ==================

# ================== START: TELEGRAM FUNCTIONS ==================
def get_telegram_settings():
    """Get Telegram bot settings from database"""
    db = get_db()
    settings = db.execute("SELECT bot_token, chat_id FROM telegram_settings ORDER BY id DESC LIMIT 1").fetchone()
    if settings and settings['bot_token'] and settings['chat_id']:
        return {'bot_token': settings['bot_token'], 'chat_id': settings['chat_id']}
    return None

def save_telegram_settings(bot_token, chat_id):
    """Save Telegram bot settings to database"""
    db = get_db()
    # Check if settings exist
    existing = db.execute("SELECT id FROM telegram_settings ORDER BY id DESC LIMIT 1").fetchone()
    if existing:
        db.execute("UPDATE telegram_settings SET bot_token = ?, chat_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                   (bot_token, chat_id, existing['id']))
    else:
        db.execute("INSERT INTO telegram_settings (bot_token, chat_id) VALUES (?, ?)", (bot_token, chat_id))
    db.commit()

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to Telegram"""
    try:
        import urllib.request
        import urllib.parse
        import json
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message
        }
        
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get('ok', False)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def send_telegram_document(bot_token, chat_id, file_path, caption=""):
    """Send a document/file to Telegram"""
    try:
        import urllib.request
        import urllib.parse
        
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Create multipart form data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body_parts = []
        
        # Add chat_id
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="chat_id"')
        body_parts.append(b'')
        body_parts.append(str(chat_id).encode())
        
        # Add caption if provided
        if caption:
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="caption"')
            body_parts.append(b'')
            body_parts.append(caption.encode('utf-8'))
        
        # Add document file
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="document"; filename="{os.path.basename(file_path)}"'.encode())
        body_parts.append(b'Content-Type: application/pdf')
        body_parts.append(b'')
        body_parts.append(file_content)
        
        # End boundary
        body_parts.append(f'--{boundary}--'.encode())
        
        # Combine all parts
        body = b'\r\n'.join(body_parts)
        
        # Create request
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Content-Length', str(len(body)))
        
        # Send request
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get('ok', False)
    except Exception as e:
        print(f"Error sending Telegram document: {e}")
        return False

def create_champions_pdf(class_name, section_name, champions_list):
    """Create a PDF file for champions of a specific class and section"""
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#0d6efd',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor='#495057',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Champion name style
        champion_style = ParagraphStyle(
            'ChampionStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor='#212529',
            spaceAfter=15,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        
        # Add title
        title = Paragraph("🏆 أبطال الأسبوع", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Add class and section
        class_section_text = f"الصف: {class_name} - الشعبة: {section_name}"
        subtitle = Paragraph(class_section_text, subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 1*cm))
        
        # Add champions list
        if champions_list:
            for i, champion in enumerate(champions_list, 1):
                champion_text = f"{i}. {champion['name']}"
                champion_para = Paragraph(champion_text, champion_style)
                elements.append(champion_para)
        else:
            no_champions = Paragraph("لا يوجد أبطال هذا الأسبوع", champion_style)
            elements.append(no_champions)
        
        # Build PDF
        doc.build(elements)
        
        return temp_path
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None

def get_week_champions():
    """Get all current week champions with their details"""
    db = get_db()
    today = date.today()
    days_since_saturday = (today.weekday() + 2) % 7
    start_of_week = today - timedelta(days=days_since_saturday)
    
    manhaji_criteria_count = db.execute("SELECT COUNT(id) FROM rating_criteria WHERE video_type = 'منهجي'").fetchone()[0]
    if manhaji_criteria_count == 0:
        return []
    
    start_of_previous_week = start_of_week - timedelta(days=7)
    
    champions = []
    students = db.execute("SELECT id, username, full_name, class_name, section_name FROM users WHERE role = 'student'").fetchall()
    
    for student in students:
        student_id = student['id']
        carried_stars = 0
        bank_entry = db.execute(
            "SELECT banked_stars FROM star_bank WHERE user_id = ? AND last_updated_week_start_date = ?",
            (student_id, start_of_previous_week.strftime('%Y-%m-%d'))
        ).fetchone()
        if bank_entry:
            carried_stars = bank_entry['banked_stars']
        
        new_stars_row = db.execute("""
            SELECT SUM(dr.is_awarded) as stars
            FROM dynamic_video_ratings dr
            JOIN videos v ON dr.video_id = v.id
            JOIN rating_criteria rc ON dr.criterion_id = rc.id
            WHERE rc.video_type = 'منهجي' AND v.user_id = ? AND date(v.timestamp) >= ?
        """, (student_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
        
        new_stars = new_stars_row['stars'] if new_stars_row and new_stars_row['stars'] is not None else 0
        total_score_this_week = carried_stars + new_stars
        
        if total_score_this_week >= manhaji_criteria_count:
            champions.append({
                'id': student_id,
                'name': student['full_name'] or student['username'],
                'class': student['class_name'] or 'غير محدد',
                'section': student['section_name'] or 'غير محدد'
            })
    
    return champions

def send_week_champions_to_telegram():
    """Send week champions to Telegram automatically as PDF files grouped by class and section"""
    logging.info("Starting scheduled send_week_champions_to_telegram task")
    try:
        settings = get_telegram_settings()
        if not settings:
            logging.warning("Telegram settings not configured, skipping send")
            return  # No settings configured, silently skip
        
        champions = get_week_champions()
        if not champions:
            logging.info("No champions this week, skipping send")
            return  # No champions this week
        
        # Group champions by class and section
        champions_by_class_section = defaultdict(list)
        for champion in champions:
            class_name = champion['class'] or 'غير محدد'
            section_name = champion['section'] or 'غير محدد'
            key = (class_name, section_name)
            champions_by_class_section[key].append(champion)
        
        # Create and send PDF for each class-section group
        temp_files = []  # Track temporary files for cleanup
        for (class_name, section_name), champions_list in champions_by_class_section.items():
            # Create PDF file
            pdf_path = create_champions_pdf(class_name, section_name, champions_list)
            if pdf_path:
                temp_files.append(pdf_path)
                # Create caption for the file
                caption = f"🏆 أبطال الأسبوع\nالصف: {class_name}\nالشعبة: {section_name}"
                # Send PDF to Telegram
                success = send_telegram_document(
                    settings['bot_token'], 
                    settings['chat_id'], 
                    pdf_path, 
                    caption=caption
                )
                if success:
                    logging.info(f"Successfully sent champions PDF for {class_name} - {section_name}")
                else:
                    logging.error(f"Failed to send champions PDF for {class_name} - {section_name}")
        logging.info(f"Completed sending {len(temp_files)} champion PDFs to Telegram")
    except Exception as e:
        logging.error(f"Error in send_week_champions_to_telegram: {e}", exc_info=True)
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logging.error(f"Error deleting temporary file {temp_file}: {e}")

def scheduled_send_champions():
    """Wrapper function for scheduled task with proper error handling"""
    logging.info("Scheduled task triggered: send_week_champions_to_telegram")
    try:
        send_week_champions_to_telegram()
    except Exception as e:
        logging.error(f"Error in scheduled_send_champions: {e}", exc_info=True)

# Track last known champions to detect new ones (stored in memory)
_last_known_champions = None
_last_sent_date = None  # Track last date when champions were sent

def check_and_send_new_champions():
    """Check for new champions and send to Telegram only on Wednesday at 8 PM"""
    global _last_known_champions, _last_sent_date
    current_champions = get_week_champions()
    current_ids = {c['id'] for c in current_champions}
    
    # If this is the first run, initialize but don't send
    if _last_known_champions is None:
        _last_known_champions = current_ids
        return
    
    # Get current date and time
    now = datetime.now()
    current_weekday = now.weekday()  # 0=Monday, 1=Tuesday, 2=Wednesday, etc.
    current_hour = now.hour
    current_date = now.date()
    
    # Check if it's Wednesday (2) and 8 PM (20:00)
    is_wednesday_8pm = (current_weekday == 2 and current_hour == 20)
    
    # Only send if:
    # 1. It's Wednesday at 8 PM
    # 2. We haven't sent today yet (to avoid multiple sends on the same day)
    if is_wednesday_8pm and _last_sent_date != current_date:
        # Send all current champions (not just new ones) on Wednesday at 8 PM
        if current_champions:  # Only send if there are champions
            send_week_champions_to_telegram()
            _last_sent_date = current_date  # Mark that we sent today
    
    # Update last known champions
    _last_known_champions = current_ids
# ================== END: TELEGRAM FUNCTIONS ==================

# ================== START: NEW FUNCTION FOR SUPERHEROES ==================
def get_superhero_champions_details():
    """
    تجلب قائمة ببيانات المستخدمين الفريدة الذين فازوا بلقب "بطل خارق"
    (تقييم كامل لفيديو إثرائي) خلال هذا الشهر.
    """
    db = get_db()
    today = date.today()
    start_of_month = today.replace(day=1)

    # 1. جلب الحد الأقصى لنجوم "اثرائي"
    ithrai_criteria_count_row = db.execute("SELECT COUNT(id) FROM rating_criteria WHERE video_type = 'اثرائي'").fetchone()
    max_ithrai_stars = ithrai_criteria_count_row[0] if ithrai_criteria_count_row else 0

    if max_ithrai_stars == 0:
        return [], 0 # إرجاع قائمة فارغة إذا لم يتم تحديد معايير

    # 2. جلب المستخدمين الفريدين الذين لديهم فيديو واحد على الأقل بتقييم كامل
    superhero_query = """
        SELECT DISTINCT u.id, u.username, u.full_name, u.profile_image
        FROM users u
        WHERE u.id IN (
            -- Subquery to find user_ids who have a perfect 'اثرائي' video this month
            SELECT v.user_id
            FROM dynamic_video_ratings dr
            JOIN videos v ON dr.video_id = v.id
            JOIN rating_criteria rc ON dr.criterion_id = rc.id
            WHERE rc.video_type = 'اثرائي'
              AND date(v.timestamp) >= ?
              AND v.is_approved = 1
            GROUP BY v.id, v.user_id
            HAVING SUM(dr.is_awarded) = ?
        )
        ORDER BY u.username
    """
    
    superhero_users = db.execute(superhero_query, (start_of_month.strftime('%Y-%m-%d'), max_ithrai_stars)).fetchall()
    
    return superhero_users, max_ithrai_stars
# ================== END: NEW FUNCTION FOR SUPERHEROES ==================


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    if not value: return ""
    dt_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if isinstance(value, str) else value
    return dt_obj.strftime(format) if dt_obj else value

app.jinja_env.filters['strftime'] = format_datetime

@app.before_request
def before_request_handler():
    # Allow auto-login endpoint without session check
    if request.endpoint == 'auto_login':
        return None

    db = get_db()
    # Session revocation and profile completion check
    # إصلاح: استخدام safe_row_value للوصول الآمن
    if 'user_id' in session and 'token' in session:
        user = db.execute('SELECT session_revocation_token, is_profile_complete, role, profile_reset_required FROM users WHERE id = ?', (session['user_id'],)).fetchone()

        user_session_token = safe_row_value(user, 'session_revocation_token') if user else None
        if not user or user_session_token != session['token']:
            session.clear()
            flash('تم تسجيل خروجك بواسطة المسؤول.', 'warning')
            return redirect(url_for('login'))

        # --- تعديل: إضافة uploaded_file إلى القائمة المسموحة ---
        # --- تعديل: إضافة مسارات المعايير الجديدة ---
        allowed_endpoints = ['login', 'logout', 'edit_user', 'static', 
                             'my_messages', 'api_get_student_messages', 'api_send_student_message', 
                             'uploaded_file', 'admin_criteria', 'add_criterion', 'delete_criterion']

        user_role = safe_row_value(user, 'role')
        user_is_profile_complete = safe_row_value(user, 'is_profile_complete', 0)
        user_profile_reset_required = safe_row_value(user, 'profile_reset_required', 0)
        
        if user_role == 'student' and request.endpoint not in allowed_endpoints:
            if not user_is_profile_complete:
                flash('الرجاء إكمال ملفك الشخصي أولاً للمتابعة. الحقول إلزامية.', 'warning')
                return redirect(url_for('edit_user', user_id=session['user_id']))

            if user_profile_reset_required:
                flash('سنة دراسية جديدة! الرجاء تحديث الصف والشعبة للمتابعة.', 'info')
                return redirect(url_for('edit_user', user_id=session['user_id']))

    # Unread message count for students
    g.unread_count = 0
    if session.get('role') == 'student':
        count = db.execute(
            'SELECT COUNT(id) FROM messages WHERE receiver_id = ? AND is_read = 0',
            (session['user_id'],)
        ).fetchone()[0]
        g.unread_count = count

    # --- START: NEW CODE FOR VIDEO REVIEW COUNT ---
    g.unapproved_count = 0
    if session.get('role') == 'admin':
        count = db.execute(
            'SELECT COUNT(id) FROM videos WHERE is_approved = 0'
        ).fetchone()[0]
        g.unapproved_count = count
    # --- END: NEW CODE ---
    
    # ================== NEW: Load all criteria into g ==================
    criteria_payload = load_all_criteria()
    g.all_criteria = criteria_payload.get('by_type', {})
    g.criteria_key_map = criteria_payload.get('by_key', {})
    # ================== END: Load criteria ==================
    
    # Note: Telegram sending is now handled by background scheduler (APScheduler)
    # Scheduled to run every Wednesday at 8:00 PM automatically


# ----------------- AUTHENTICATION ROUTES -----------------
@app.route('/auto-login', methods=['POST'])
def auto_login():
    """
    Auto-login endpoint that checks device fingerprint and token
    إصلاح: استخدام safe_row_value للوصول الآمن + معالجة أخطاء شاملة
    """
    try:
        # التحقق من وجود البيانات
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Invalid request format'}), 400
        
        data = request.get_json(silent=True) or {}
        device_fingerprint = data.get('device_fingerprint')
        auth_token = data.get('auth_token')
        
        if not device_fingerprint or not auth_token:
            return jsonify({'status': 'error', 'message': 'Missing credentials'}), 400
        
        # Get user by token - إصلاح: استخدام safe_row_value
        user = get_user_by_token(auth_token)
        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # إصلاح: استخدام safe_row_value للوصول الآمن للقيم من sqlite3.Row
        user_role = safe_row_value(user, 'role')
        user_id = safe_row_value(user, 'id')
        user_username = safe_row_value(user, 'username')
        user_session_token = safe_row_value(user, 'session_revocation_token')
        user_is_profile_complete = safe_row_value(user, 'is_profile_complete', 0)
        user_profile_reset_required = safe_row_value(user, 'profile_reset_required', 0)
        
        if not user_id or not user_role:
            return jsonify({'status': 'error', 'message': 'Invalid user data'}), 401
        
        db = get_db()
        if user_role == 'admin':
            # Admin can login from any device
            binding = db.execute(
                'SELECT auth_token FROM device_bindings WHERE user_id = ? AND auth_token = ?',
                (user_id, auth_token)
            ).fetchone()
            if not binding:
                try:
                    auth_token = bind_device_to_user(user_id, device_fingerprint)
                except Exception as e:
                    return jsonify({'status': 'error', 'message': f'Error creating token: {str(e)}'}), 500
        else:
            # For students, verify device fingerprint strictly
            try:
                is_valid, stored_token = verify_device_binding(user_id, device_fingerprint)
                if not is_valid or stored_token != auth_token:
                    return jsonify({
                        'status': 'error', 
                        'message': 'هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه.'
                    }), 403
            except Exception as e:
                return jsonify({'status': 'error', 'message': f'Error verifying device: {str(e)}'}), 500
        
        # Check suspension - إصلاح: استخدام safe_row_value
        suspension = db.execute(
            'SELECT end_date, reason FROM suspensions WHERE user_id = ? AND end_date > ?', 
            (user_id, datetime.now())
        ).fetchone()
        if suspension:
            end_date_raw = safe_row_value(suspension, 'end_date', '')
            end_date_formatted = str(end_date_raw).split('.')[0] if end_date_raw else ''
            reason = safe_row_value(suspension, 'reason', 'لا يوجد سبب.')
            return jsonify({
                'status': 'error',
                'message': f'حسابك موقوف حتى {end_date_formatted}. السبب: {reason}'
            }), 403
        
        # Update token last used
        try:
            update_token_last_used(auth_token)
        except Exception as e:
            # Log error but don't fail the login
            print(f"Warning: Failed to update token last used: {e}")
        
        # Create session
        try:
            session.clear()
            session['user_id'] = user_id
            session['username'] = user_username
            session['role'] = user_role
            session['token'] = user_session_token
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error creating session: {str(e)}'}), 500
        
        # Determine redirect URL
        needs_profile = user_role == 'student' and not bool(user_is_profile_complete)
        needs_reset = user_role == 'student' and bool(user_profile_reset_required)
        redirect_url = url_for('index')
        if user_role == 'student' and (needs_profile or needs_reset):
            redirect_url = url_for('edit_user', user_id=user_id)
        
        response = jsonify({
            'status': 'success',
            'redirect': redirect_url,
            'needs_profile': needs_profile,
            'needs_reset': needs_reset,
            'auth_token': auth_token
        })
        response.set_cookie('auth_token', auth_token, max_age=31536000, httponly=True, samesite='Lax', secure=False)
        return response
    except Exception as e:
        # إصلاح: معالجة جميع الأخطاء بدون سقوط السيرفر
        print(f"Error in auto-login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'An error occurred during login'}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        device_fingerprint = request.form.get('device_fingerprint', '')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        # Debug: Check if user exists and password verification
        # إصلاح: استخدام safe_row_value للوصول الآمن
        if not user:
            flash('اسم المستخدم غير موجود!', 'danger')
            return render_page('login')
        
        user_password = safe_row_value(user, 'password')
        password_valid = check_password_hash(user_password, password) if user_password else False
        if not password_valid:
            flash('كلمة المرور غير صحيحة!', 'danger')
            return render_page('login')

        if user and password_valid:
            user_id = safe_row_value(user, 'id')
            suspension = db.execute('SELECT * FROM suspensions WHERE user_id = ? AND end_date > ?', (user_id, datetime.now())).fetchone()
            if suspension:
                end_date = safe_row_value(suspension, 'end_date', '')
                reason = safe_row_value(suspension, 'reason', '')
                end_date_formatted = str(end_date).split('.')[0] if end_date else ''
                flash(f'حسابك موقوف حتى {end_date_formatted}. السبب: {reason}', 'danger')
                return render_page('login')

            # Check device binding - Admin can login from any device, students are restricted
            # إصلاح: استخدام safe_row_value
            user_role = safe_row_value(user, 'role')
            if user_role == 'admin':
                # Admin: Allow login from any device, create/update token without device binding restriction
                # For admin, we don't enforce device binding - just ensure token exists
                binding = db.execute('SELECT auth_token FROM device_bindings WHERE user_id = ?', (user_id,)).fetchone()
                if binding:
                    auth_token = safe_row_value(binding, 'auth_token')
                    update_token_last_used(auth_token)
                else:
                    # Create token for admin (use device_fingerprint if provided, otherwise 'pending')
                    fingerprint = device_fingerprint if device_fingerprint else 'pending'
                    auth_token = bind_device_to_user(user_id, fingerprint)
            else:
                # Student: Enforce device binding (one device only)
                if device_fingerprint:
                    is_valid, stored_token = verify_device_binding(user_id, device_fingerprint)
                    
                    if is_valid is False:  # Device exists but doesn't match
                        flash('هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه.', 'danger')
                        return render_page('login')
                    
                    # If no binding exists (first login), create one
                    if is_valid is None:
                        auth_token = bind_device_to_user(user_id, device_fingerprint)
                    else:
                        auth_token = stored_token
                        update_token_last_used(auth_token)
                else:
                    # If no fingerprint provided, check if account is already bound
                    binding = db.execute('SELECT id, device_fingerprint FROM device_bindings WHERE user_id = ?', (user_id,)).fetchone()
                    if binding:
                        # Check if binding is pending (first login case)
                        binding_fingerprint = safe_row_value(binding, 'device_fingerprint')
                        if binding_fingerprint == hash_device_fingerprint('pending'):
                            # Update with actual fingerprint if provided later
                            if device_fingerprint:
                                bind_device_to_user(user_id, device_fingerprint)
                                auth_token_row = db.execute('SELECT auth_token FROM device_bindings WHERE user_id = ?', (user_id,)).fetchone()
                                auth_token = safe_row_value(auth_token_row, 'auth_token') if auth_token_row else None
                            else:
                                auth_token_row = db.execute('SELECT auth_token FROM device_bindings WHERE user_id = ?', (user_id,)).fetchone()
                                auth_token = safe_row_value(auth_token_row, 'auth_token') if auth_token_row else None
                        else:
                            flash('هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه.', 'danger')
                            return render_page('login')
                    else:
                        # First login without fingerprint - create binding with pending fingerprint
                        auth_token = bind_device_to_user(user_id, 'pending')

            # إصلاح: استخدام safe_row_value
            user_username = safe_row_value(user, 'username')
            user_session_token = safe_row_value(user, 'session_revocation_token')
            user_is_profile_complete = safe_row_value(user, 'is_profile_complete', 0)
            user_profile_reset_required = safe_row_value(user, 'profile_reset_required', 0)
            
            session.clear()
            session['user_id'] = user_id
            session['username'] = user_username
            session['role'] = user_role
            session['token'] = user_session_token
            
            # Store auth token in response cookie and pass to template for localStorage
            redirect_url = url_for('index')
            if user_role == 'student' and not user_is_profile_complete:
                flash('مرحباً بك! يرجى إكمال معلومات ملفك الشخصي للمتابعة.', 'info')
                redirect_url = url_for('edit_user', user_id=user_id)
            elif user_role == 'student' and user_profile_reset_required:
                flash('سنة دراسية جديدة! يرجى تحديث الصف والشعبة للمتابعة.', 'info')
                redirect_url = url_for('edit_user', user_id=user_id)
            
            # Create response with token storage script
            response_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>تسجيل الدخول...</title>
            </head>
            <body>
                <script>
                    // Store token in multiple places
                    const token = '{auth_token}';
                    localStorage.setItem('auth_token', token);
                    
                    // Store in IndexedDB
                    if ('indexedDB' in window) {{
                        const request = indexedDB.open('AuthDB', 1);
                        request.onupgradeneeded = function(event) {{
                            const db = event.target.result;
                            if (!db.objectStoreNames.contains('tokens')) {{
                                db.createObjectStore('tokens');
                            }}
                        }};
                        request.onsuccess = function(event) {{
                            const db = event.target.result;
                            const transaction = db.transaction(['tokens'], 'readwrite');
                            const store = transaction.objectStore('tokens');
                            store.put(token, 'auth_token');
                        }};
                    }}
                    
                    // Redirect
                    window.location.href = '{redirect_url}';
                </script>
            </body>
            </html>
            """
            response = make_response(response_html)
            response.set_cookie('auth_token', auth_token, max_age=31536000, httponly=True, samesite='Lax', secure=False)
            return response
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')

    return render_page('login')

@app.route('/reset_admin_password', methods=['GET', 'POST'])
def reset_admin_password():
    """Temporary route to reset admin password - REMOVE IN PRODUCTION"""
    if request.method == 'POST':
        db = get_db()
        # Reset admin password to 'admin123'
        hashed_password = generate_password_hash('admin123')
        admin = db.execute('SELECT id FROM users WHERE username = ? AND role = ?', ('admin', 'admin')).fetchone()
        if admin:
            db.execute('UPDATE users SET password = ? WHERE username = ? AND role = ?', 
                      (hashed_password, 'admin', 'admin'))
            db.commit()
            return jsonify({'status': 'success', 'message': 'تم إعادة تعيين كلمة مرور المدير إلى admin123'})
        else:
            return jsonify({'status': 'error', 'message': 'المدير غير موجود'})
    return '''
    <form method="POST">
        <button type="submit">إعادة تعيين كلمة مرور المدير إلى admin123</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    # Clear auth token from cookie and add script to clear all tokens and set manual logout flag
    response_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الخروج...</title>
    </head>
    <body>
        <script>
            // Clear all tokens
            localStorage.removeItem('auth_token');
            
            // Set manual logout flag to prevent auto-login
            localStorage.setItem('manual_logout', 'true');
            
            // Clear IndexedDB
            if ('indexedDB' in window) {
                const request = indexedDB.open('AuthDB', 1);
                request.onsuccess = function(event) {
                    const db = event.target.result;
                    if (db.objectStoreNames.contains('tokens')) {
                        const transaction = db.transaction(['tokens'], 'readwrite');
                        const store = transaction.objectStore('tokens');
                        store.delete('auth_token');
                    }
                };
            }
            
            // Redirect to login
            window.location.href = '/login';
        </script>
    </body>
    </html>
    """
    response = make_response(response_html)
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route('/admin/unbind_device/<int:user_id>', methods=['POST'])
def admin_unbind_device(user_id):
    """Admin route to unbind device from user account"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    unbind_device(user_id)
    flash('تم إلغاء ربط الجهاز بنجاح. يمكن للمستخدم الآن تسجيل الدخول من جهاز جديد.', 'success')
    return jsonify({"status": "success", "message": "تم إلغاء ربط الجهاز بنجاح"})
# ================== START: MODIFIED get_common_video_data ==================
def get_common_video_data(video_ids):
    db = get_db()
    video_ratings = {}
    video_likes = {}
    user_liked_videos = set()
    video_comments = defaultdict(lambda: defaultdict(list))

    # 1. جلب كل المعايير من g (تم تحميلها في before_request)
    all_criteria_by_type = g.all_criteria
    criteria_key_map = g.criteria_key_map
    
    # حساب الحد الأقصى للنجوم لكل نوع
    max_stars_manhaji = len(all_criteria_by_type.get('منهجي', []))
    max_stars_ithrai = len(all_criteria_by_type.get('اثرائي', []))

    if not video_ids:
        return video_ratings, video_likes, user_liked_videos, video_comments

    placeholders = ','.join('?' for _ in video_ids)

    # 2. جلب جميع التقييمات الديناميكية للفيديوهات المطلوبة
    ratings_data = db.execute(f'''
        SELECT dr.video_id, dr.is_awarded, rc.key, v.video_type
        FROM dynamic_video_ratings dr
        JOIN rating_criteria rc ON dr.criterion_id = rc.id
        JOIN videos v ON dr.video_id = v.id
        WHERE dr.video_id IN ({placeholders})
    ''', video_ids).fetchall()

    # 3. تجميع التقييمات في قاموس منظم
    # الهيكل الجديد:
    # video_ratings = {
    #   video_id_1: {
    #     'total_stars': 3,
    #     'max_stars': 4,
    #     'ratings': { 'participation_m': 1, 'memorization_m': 1, 'pronunciation_m': 0, 'use_of_aids_m': 1 }
    #   }
    # }
    temp_ratings = defaultdict(lambda: {'total_stars': 0, 'max_stars': 0, 'ratings': {}})
    
    for item in ratings_data:
        video_id = item['video_id']
        key = item['key']
        is_awarded = item['is_awarded']
        video_type = item['video_type']
        
        temp_ratings[video_id]['ratings'][key] = is_awarded
        if is_awarded:
            temp_ratings[video_id]['total_stars'] += 1
            
        if video_type == 'منهجي':
            temp_ratings[video_id]['max_stars'] = max_stars_manhaji
        else:
            temp_ratings[video_id]['max_stars'] = max_stars_ithrai

    video_ratings = dict(temp_ratings)

    # 4. جلب الإعجابات (نفس الكود القديم)
    likes_data = db.execute(f'SELECT video_id, COUNT(id) as count FROM video_likes WHERE video_id IN ({placeholders}) GROUP BY video_id', video_ids).fetchall()
    video_likes = {item['video_id']: item['count'] for item in likes_data}

    if 'user_id' in session:
        user_likes_rows = db.execute(f'SELECT video_id FROM video_likes WHERE user_id = ? AND video_id IN ({placeholders})', [session['user_id']] + video_ids).fetchall()
        user_liked_videos = {row['video_id'] for row in user_likes_rows}

    # 5. جلب التعليقات (نفس الكود القديم)
    comments_data = db.execute(f'''
        SELECT c.id, c.content, c.video_id, c.parent_id, c.timestamp, u.username, u.full_name, u.role, u.profile_image, c.user_id, c.is_pinned
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.video_id IN ({placeholders}) ORDER BY c.is_pinned DESC, c.timestamp ASC
    ''', video_ids).fetchall()

    for comment in comments_data:
        video_comments[comment['video_id']]['toplevel'].append(dict(comment))

    return video_ratings, video_likes, user_liked_videos, video_comments
# ================== END: MODIFIED get_common_video_data ==================


# ================== START: MODIFIED common_scripts_block ==================
common_scripts_block = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // دالة الإعجاب (لم تتغير)
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

    // دالة التعليق (لم تتغير)
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

    // ================== MODIFIED: دالة التقييم ==================
    document.querySelectorAll('.rating-form').forEach(form => {
        form.addEventListener('change', function() {
            const videoId = this.dataset.videoId;
            const videoType = this.dataset.videoType;
            const ratingData = {}; // سيحتوي على { 'key1': 1, 'key2': 0, ... }

            // تجميع بيانات المربعات المحددة
            this.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                ratingData[checkbox.name] = checkbox.checked ? 1 : 0;
            });

            // إرسال البيانات الديناميكية إلى الخادم
            fetch(`/video/${videoId}/rate`, {
                method: 'POST',
                body: JSON.stringify(ratingData), // إرسال القاموس الديناميكي
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const starsDisplay = document.getElementById(`stars-display-${videoId}`);
                    if (starsDisplay) {
                        if (data.total_stars > 0) {
                            // استخدام الحد الأقصى الديناميكي من الخادم
                            starsDisplay.innerHTML = `<i class="fas fa-star"></i> ${data.total_stars} / ${data.max_stars}`;
                        } else {
                            starsDisplay.innerHTML = `<small class="text-muted">لم يُقيّم بعد</small>`;
                        }
                    }
                    if (data.champion_message) {
                        location.reload(); // أعد تحميل الصفحة إذا أصبح بطلاً
                    }
                }
            }).catch(console.error);
        });
    });
    // ================== END: MODIFIED: دالة التقييم ==================


    // دوال إدارة التعليقات (لم تتغير)
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

    # --- START: NEW CODE TO GET SUPERHEROES ---
    superhero_champions, max_ithrai_stars = get_superhero_champions_details()
    # --- END: NEW CODE ---

    all_classes = []
    all_sections = []
    selected_class = request.args.get('class_name', '')
    selected_section = request.args.get('section_name', '')
    selected_video_type = request.args.get('video_type', '')

    if session.get('role') == 'admin':
        all_classes = db.execute("SELECT DISTINCT TRIM(class_name) as class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND TRIM(class_name) != '' ORDER BY class_name").fetchall()
        all_sections = db.execute("SELECT DISTINCT TRIM(section_name) as section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND TRIM(section_name) != '' ORDER BY section_name").fetchall()

    posts = db.execute('SELECT p.content, p.timestamp, u.username, u.full_name FROM posts p JOIN users u ON p.user_id = u.id WHERE u.role = "admin" ORDER BY p.timestamp DESC').fetchall()
    
    # --- START: MODIFICATION FOR AUTO ARCHIVING ---
    # عرض الفيديوهات غير المؤرشفة فقط في الصفحة الرئيسية
    # --- START: MODIFICATION FOR VIDEO APPROVAL ---
    video_query = '''
        SELECT v.id, v.title, v.filepath, v.timestamp, v.video_type, v.is_approved, v.is_archived, u.username, u.full_name, u.role, u.id as user_id, u.profile_image
        FROM videos v JOIN users u ON v.user_id = u.id
        WHERE v.is_archived = 0 AND v.is_approved = 1
    '''
    # --- END: MODIFICATION FOR VIDEO APPROVAL ---
    params = []

    if session.get('role') == 'admin' and selected_class:
        video_query += ' AND TRIM(u.class_name) = ?'
        params.append(selected_class.strip())
    if session.get('role') == 'admin' and selected_section:
        video_query += ' AND TRIM(u.section_name) = ?'
        params.append(selected_section.strip())

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
                       selected_video_type=selected_video_type,
                       all_criteria=g.all_criteria, # <--- تعديل: تمرير المعايير
                       
                       # --- START: NEW DATA FOR TEMPLATE ---
                       superhero_champions=superhero_champions,
                       max_ithrai_stars=max_ithrai_stars
                       # --- END: NEW DATA ---
                       )
@app.route('/archive')
def archive():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()

    selected_class = request.args.get('class_name', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    selected_video_type = request.args.get('video_type', '')

    all_classes = db.execute("SELECT DISTINCT TRIM(class_name) as class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND TRIM(class_name) != '' ORDER BY class_name").fetchall()

    # --- START: MODIFICATION FOR AUTO ARCHIVING ---
    # عرض الفيديوهات المؤرشفة فقط في صفحة الأرشيف
    # الأرشفة التلقائية تتم يوم الجمعة، لكن الأرشيف متاح للعرض في أي وقت
    # (خاصة للفيديوهات المؤرشفة يدوياً)

    # --- START: MODIFICATION FOR VIDEO APPROVAL ---
    query = '''
        SELECT v.id, v.title, v.filepath, v.timestamp, v.video_type, v.is_approved, v.is_archived, u.username, u.full_name, u.role, u.id as user_id, u.profile_image
        FROM videos v JOIN users u ON v.user_id = u.id
        WHERE v.is_archived = 1 AND v.is_approved = 1
    '''
    # --- END: MODIFICATION FOR VIDEO APPROVAL ---
    params = []

    if selected_class:
        query += ' AND TRIM(u.class_name) = ?'
        params.append(selected_class.strip())
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
                       selected_video_type=selected_video_type,
                       all_criteria=g.all_criteria # <--- تعديل: تمرير المعايير
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
                       video_comments=video_comments, scripts_block=common_scripts_block,
                       all_criteria=g.all_criteria # <--- تعديل: تمرير المعايير
                       )

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
                       scripts_block=common_scripts_block, # لإضافة وظائف التعليق والإعجاب...الخ
                       all_criteria=g.all_criteria # <--- تعديل: تمرير المعايير
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
                try:
                    filename = secure_filename(f"user_{user_id}_{file.filename}")
                    safe_destination = resolve_upload_path(filename)
                    file.save(safe_destination)
                    db.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, user_id))
                except ValueError as upload_error:
                    flash(str(upload_error), 'danger')
                    return redirect(url_for('edit_user', user_id=user_id))

        # ================== START: SAVE TELEGRAM SETTINGS (Admin Only) ==================
        if session['role'] == 'admin' and user_to_edit['role'] == 'admin':
            telegram_bot_token = request.form.get('telegram_bot_token', '').strip()
            telegram_chat_id = request.form.get('telegram_chat_id', '').strip()
            if telegram_bot_token or telegram_chat_id:
                save_telegram_settings(telegram_bot_token, telegram_chat_id)
        # ================== END: SAVE TELEGRAM SETTINGS ==================

        db.commit()

        if user_id == session.get('user_id') and new_username != session.get('username'):
             session['username'] = new_username

        flash('تم تحديث الحساب بنجاح!', 'success')
        if session['role'] == 'admin' or (not profile_reset_required and is_profile_complete):
             return redirect(url_for('profile', username=new_username))
        else:
            return redirect(url_for('edit_user', user_id=user_id))

    # ================== START: GET TELEGRAM SETTINGS FOR TEMPLATE ==================
    telegram_settings = None
    if session.get('role') == 'admin' and user_to_edit['role'] == 'admin':
        telegram_settings = get_telegram_settings()
    # ================== END: GET TELEGRAM SETTINGS ==================

    return render_template_string(edit_user_html, user=user_to_edit, telegram_settings=telegram_settings)
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

    temp_filename = secure_filename(f"temp_upload_{session['user_id']}_{video_file.filename}")
    try:
        temp_filepath = resolve_upload_path(temp_filename)
    except ValueError as upload_error:
        flash(str(upload_error), 'danger')
        return redirect(url_for('index'))

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

        # 3. تطبيق حد المدة (60 ثانية للمنهجي، 240 ثانية للإثرائي)
        
        # (هذا السطر موجود مسبقاً في الدالة، نحن فقط نستخدم المتغير)
        # video_type = request.form.get('video_type')
        
        max_duration = 0
        limit_message = ""

        if video_type == 'منهجي':
            max_duration = 60  # 1 دقيقة
            limit_message = "60 ثانية (دقيقة واحدة)"
        elif video_type == 'اثرائي':
            max_duration = 240 # 4 دقائق
            limit_message = "240 ثانية (4 دقائق)"
        else:
            # حالة احتياطية إذا كان نوع الفيديو غير معروف
            flash('خطأ: نوع الفيديو المحدد غير صحيح.', 'danger')
            return redirect(url_for('index'))

        if duration > max_duration:
            flash(f'خطأ: مدة الفيديو هي {int(duration)} ثانية. الحد الأقصى المسموح به لهذا النوع ({video_type}) هو {limit_message}.', 'danger')
            return redirect(url_for('index'))

        # 4. إذا كانت المدة مقبولة، أنشئ اسماً نهائياً وانقل الملف
        final_filename = secure_filename(f"vid_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.filename}")
        try:
            final_filepath = resolve_upload_path(final_filename)
        except ValueError as upload_error:
            flash(str(upload_error), 'danger')
            return redirect(url_for('index'))

        os.replace(temp_filepath, final_filepath)

        # --- نهاية: التحقق من مدة الفيديو ---

        is_approved = 1 if session.get('role') == 'admin' else 0

        db = get_db()
        db.execute('INSERT INTO videos (title, filepath, user_id, video_type, is_approved) VALUES (?, ?, ?, ?, ?)',
                   (title, final_filename, session['user_id'], video_type, is_approved))
        db.commit()

        if is_approved == 0:
            flash(f'تم رفع الفيديو بنجاح (مدته {int(duration)} ثانية)، وهو الآن بانتظار موافقة المدير.', 'success')
        else:
            flash(f'تم رفع الفيديو بنجاح (مدته {int(duration)} ثانية)!', 'success')

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

# ================== START: MODIFIED rate_video (Dynamic) ==================
@app.route('/video/<int:video_id>/rate', methods=['POST'])
def rate_video(video_id):
    if session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Admins only.'}), 403

    # 1. جلب البيانات المرسلة (قاموس بالمفاتيح والقيم 0 أو 1)
    data = request.get_json()
    db = get_db()

    # 2. التأكد من وجود الفيديو
    video = db.execute('SELECT video_type FROM videos WHERE id = ?', (video_id,)).fetchone()
    if not video:
        return jsonify({'status': 'error', 'message': 'Video not found.'}), 404

    # 3. جلب المعايير من g (التي تم تحميلها في before_request)
    admin_id = session['user_id']
    criteria_key_map = g.criteria_key_map # قاموس { 'key': {...} }
    all_criteria_by_type = g.all_criteria # قاموس { 'نوع الفيديو': [...] }
    
    video_type_criteria = all_criteria_by_type.get(video['video_type'], [])
    max_stars = len(video_type_criteria)
    total_stars = 0
    champion_message = None

    # 4. المرور على جميع المعايير الخاصة بنوع هذا الفيديو
    for criterion in video_type_criteria:
        criterion_key = criterion['key']
        criterion_id = criterion['id']
        
        # 5. تحديد القيمة (هل تم منح النجمة أم لا)
        is_awarded = data.get(criterion_key, 0)
        
        if is_awarded == 1:
            total_stars += 1

        # 6. تحديث قاعدة البيانات (INSERT أو UPDATE)
        db.execute(f'''
            INSERT INTO dynamic_video_ratings (video_id, criterion_id, is_awarded, admin_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(video_id, criterion_id) DO UPDATE SET
            is_awarded = excluded.is_awarded, admin_id = excluded.admin_id
        ''', (video_id, criterion_id, is_awarded, admin_id))

    db.commit()

    # 7. التحقق من حالة "البطل الخارق"
    if video['video_type'] == 'اثرائي' and total_stars == max_stars and max_stars > 0:
        champion_message = "أصبح هذا الطالب بطلاً خارقاً!"

    # Note: Telegram sending is now handled automatically in before_request_handler()
    # on Wednesday at 8 PM, so no need to check here

    # 8. إرجاع البيانات المحدثة إلى الواجهة
    return jsonify({
        'status': 'success',
        'total_stars': total_stars,
        'max_stars': max_stars,
        'champion_message': champion_message
    })
# ================== END: MODIFIED rate_video (Dynamic) ==================


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
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً.', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    # ابحث عن الفيديو أولاً لجلب اسم الملف ومعلومات المستخدم
    video = db.execute('SELECT filepath, user_id FROM videos WHERE id = ?', (video_id,)).fetchone()

    if not video:
        flash('الفيديو غير موجود.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # التحقق من الصلاحية: المدير يمكنه حذف أي فيديو، والطالب يمكنه حذف فيديوهاته فقط
    if session.get('role') != 'admin' and session.get('user_id') != video['user_id']:
        flash('ليس لديك الصلاحية لحذف هذا الفيديو.', 'danger')
        return redirect(request.referrer or url_for('index'))

    try:
        # 1. حذف جميع البيانات المرتبطة بالفيديو يدوياً (لضمان الحذف الصحيح)
        db.execute('DELETE FROM comments WHERE video_id = ?', (video_id,))
        db.execute('DELETE FROM video_likes WHERE video_id = ?', (video_id,))
        db.execute('DELETE FROM dynamic_video_ratings WHERE video_id = ?', (video_id,))
        
        # 2. حذف ملف الفيديو من المجلد
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filepath'])
        if os.path.exists(filepath):
            os.remove(filepath)

        # 3. حذف الفيديو من قاعدة البيانات
        db.execute('DELETE FROM videos WHERE id = ?', (video_id,))

        db.commit()
        flash('تم حذف الفيديو وجميع البيانات المتعلقة به بنجاح.', 'success')

    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء حذف الفيديو: {e}', 'danger')

    # أعد التوجيه إلى الصفحة السابقة
    return redirect(request.referrer or url_for('index'))

# --- START: MANUAL ARCHIVE ROUTES ---
@app.route('/video/<int:video_id>/archive', methods=['POST'])
def archive_video(video_id):
    """أرشفة فيديو يدوياً (للمسؤول فقط)"""
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    db = get_db()
    video = db.execute('SELECT id, is_approved FROM videos WHERE id = ?', (video_id,)).fetchone()
    
    if not video:
        flash('الفيديو غير موجود.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    if video['is_approved'] != 1:
        flash('لا يمكن أرشفة فيديو غير معتمد.', 'warning')
        return redirect(request.referrer or url_for('index'))
    
    try:
        now = datetime.now()
        db.execute('''
            UPDATE videos 
            SET is_archived = 1, archived_date = ?
            WHERE id = ?
        ''', (now, video_id))
        db.commit()
        flash('تم نقل الفيديو إلى الأرشيف بنجاح.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء أرشفة الفيديو: {e}', 'danger')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/video/<int:video_id>/unarchive', methods=['POST'])
def unarchive_video(video_id):
    """إرجاع فيديو من الأرشيف (للمسؤول فقط)"""
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    db = get_db()
    video = db.execute('SELECT id FROM videos WHERE id = ?', (video_id,)).fetchone()
    
    if not video:
        flash('الفيديو غير موجود.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    try:
        db.execute('''
            UPDATE videos 
            SET is_archived = 0, archived_date = NULL
            WHERE id = ?
        ''', (video_id,))
        db.commit()
        flash('تم إرجاع الفيديو من الأرشيف بنجاح.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء إرجاع الفيديو: {e}', 'danger')
    
    return redirect(request.referrer or url_for('index'))
# --- END: MANUAL ARCHIVE ROUTES ---

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

    all_classes = db.execute("SELECT DISTINCT TRIM(class_name) as class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND TRIM(class_name) != '' ORDER BY class_name").fetchall()
    all_sections = db.execute("SELECT DISTINCT TRIM(section_name) as section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND TRIM(section_name) != '' ORDER BY section_name").fetchall()

    query = "SELECT id, username, full_name, profile_image, class_name, section_name FROM users WHERE role = 'student'"
    params = []

    if selected_class:
        query += " AND TRIM(class_name) = ?"
        params.append(selected_class.strip())
    if selected_section:
        query += " AND TRIM(section_name) = ?"
        params.append(selected_section.strip())
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

# ================== START: MODIFIED reports (Dynamic) ==================
@app.route('/reports')
def reports():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    db = get_db()

    selected_class = request.args.get('class_name', '')
    all_classes = db.execute("SELECT DISTINCT TRIM(class_name) as class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND TRIM(class_name) != '' ORDER BY class_name").fetchall()

    # 1. جلب الطلاب
    student_query = "SELECT id, username, class_name, section_name FROM users WHERE role = 'student'"
    params = []
    if selected_class:
        student_query += " AND TRIM(class_name) = ?"
        params.append(selected_class.strip())
    student_query += " ORDER BY username"
    students = db.execute(student_query, tuple(params)).fetchall()

    # 2. جلب جميع المعايير (من g)
    all_criteria = g.all_criteria

    # 3. جلب جميع فيديوهات الطلاب المفلترة
    video_params = []
    if selected_class:
        video_params.append(selected_class.strip())
    
    all_student_videos = db.execute(f"""
        SELECT v.id, v.title, v.timestamp, v.user_id, v.video_type
        FROM videos v
        JOIN users u ON v.user_id = u.id
        WHERE v.is_approved = 1 AND u.role = 'student'
        {'AND TRIM(u.class_name) = ?' if selected_class else ''}
    """, tuple(video_params)).fetchall()

    all_video_ids = [v['id'] for v in all_student_videos]
    videos_by_student = defaultdict(lambda: defaultdict(list))
    for v in all_student_videos:
        videos_by_student[v['user_id']][v['video_type']].append(dict(v))

    # 4. جلب جميع تقييمات هذه الفيديوهات مرة واحدة
    all_ratings = {}
    if all_video_ids:
        placeholders = ','.join('?' for _ in all_video_ids)
        ratings_rows = db.execute(f"""
            SELECT dr.video_id, dr.is_awarded, rc.key
            FROM dynamic_video_ratings dr
            JOIN rating_criteria rc ON dr.criterion_id = rc.id
            WHERE dr.video_id IN ({placeholders})
        """, all_video_ids).fetchall()
        
        # تنظيم التقييمات حسب الفيديو
        for r in ratings_rows:
            video_id = r['video_id']
            if video_id not in all_ratings:
                all_ratings[video_id] = {'total_stars': 0, 'ratings': {}}
            
            all_ratings[video_id]['ratings'][r['key']] = r['is_awarded']
            if r['is_awarded']:
                all_ratings[video_id]['total_stars'] += 1

    # 5. إعداد بيانات التقرير النهائية
    report_data = []
    champion_statuses = get_champion_statuses()
    start_of_week_dt = datetime.combine(date.today() - timedelta(days=date.today().weekday()), datetime.min.time())

    for student in students:
        student_info = dict(student)
        student_id = student['id']

        # إضافة الفيديوهات المنهجية مع تقييماتها
        student_info['videos_manhaji'] = []
        for video in videos_by_student[student_id]['منهجي']:
            video_data = dict(video)
            video_ratings = all_ratings.get(video['id'], {'total_stars': 0, 'ratings': {}})
            video_data.update(video_ratings)
            student_info['videos_manhaji'].append(video_data)

        # إضافة الفيديوهات الإثرائية مع تقييماتها
        student_info['videos_ithrai'] = []
        for video in videos_by_student[student_id]['اثرائي']:
            video_data = dict(video)
            video_ratings = all_ratings.get(video['id'], {'total_stars': 0, 'ratings': {}})
            video_data.update(video_ratings)
            student_info['videos_ithrai'].append(video_data)

        # إضافة ملخص النشاط الأسبوعي
        student_info['weekly_activity'] = {
            'uploads': db.execute("SELECT COUNT(id) as count FROM videos WHERE user_id = ? AND timestamp >= ?", (student['id'], start_of_week_dt)).fetchone()['count'],
            'comments': db.execute("SELECT COUNT(id) as count FROM comments WHERE user_id = ? AND timestamp >= ?", (student['id'], start_of_week_dt)).fetchone()['count'],
            'is_champion': champion_statuses.get(student['id']) == 'بطل الأسبوع'
        }
        report_data.append(student_info)

    return render_page('reports',
                       report_data=report_data,
                       all_classes=all_classes,
                       selected_class=selected_class,
                       all_criteria=all_criteria # <--- تعديل: تمرير المعايير
                       )
# ================== END: MODIFIED reports (Dynamic) ==================


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

# ================== START: NEW CRITERIA MANAGEMENT ROUTES ==================
@app.route('/admin/criteria')
def admin_criteria():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    db = get_db()
    # جلب المعايير من g (تم تحميلها في before_request)
    criteria_data = g.all_criteria
    
    return render_page('admin_criteria', criteria=criteria_data)

@app.route('/admin/criteria/add', methods=['POST'])
def add_criterion():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    key = request.form.get('key')
    video_type = request.form.get('video_type')

    if not name or not key or not video_type:
        flash('جميع الحقول مطلوبة.', 'danger')
        return redirect(url_for('admin_criteria'))

    db = get_db()
    try:
        db.execute("INSERT INTO rating_criteria (name, key, video_type) VALUES (?, ?, ?)", (name, key, video_type))
        db.commit()
        invalidate_criteria_cache()
        flash('تم إضافة المعيار بنجاح!', 'success')
    except sqlite3.IntegrityError:
        flash('خطأ: المفتاح البرمجي (key) يجب أن يكون فريداً (غير مكرر).', 'danger')
    
    return redirect(url_for('admin_criteria'))

@app.route('/admin/criteria/<int:criterion_id>/delete', methods=['POST'])
def delete_criterion(criterion_id):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    db = get_db()
    # الحذف من جدول المعايير (وسيتم الحذف من dynamic_video_ratings تلقائياً بفضل ON DELETE CASCADE)
    db.execute("DELETE FROM rating_criteria WHERE id = ?", (criterion_id,))
    db.commit()
    invalidate_criteria_cache()
    
    flash('تم حذف المعيار وأي تقييمات مرتبطة به.', 'success')
    return redirect(url_for('admin_criteria'))
# ================== END: NEW CRITERIA MANAGEMENT ROUTES ==================
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

@app.route('/admin/send_champions_telegram', methods=['POST'])
def send_champions_telegram_manual():
    """إرسال تقرير أبطال الأسبوع إلى تيليجرام يدوياً (للمسؤول فقط)"""
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "error": "غير مصرح"}), 403
    
    try:
        logging.info("Manual send champions report triggered by admin")
        send_week_champions_to_telegram()
        return jsonify({"status": "success", "message": "تم إرسال تقرير الأبطال إلى تيليجرام بنجاح"})
    except Exception as e:
        logging.error(f"Error in manual send champions: {e}", exc_info=True)
        return jsonify({"status": "error", "error": f"حدث خطأ أثناء الإرسال: {str(e)}"}), 500

@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """حذف حساب طالب مع جميع البيانات المرتبطة"""
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "error": "غير مصرح"}), 403
    
    db = get_db()
    
    # التحقق من وجود الطالب
    student = db.execute('SELECT id, username, profile_image FROM users WHERE id = ? AND role = ?', (student_id, 'student')).fetchone()
    if not student:
        return jsonify({"status": "error", "error": "الطالب غير موجود"}), 404
    
    try:
        # 1. حذف جميع الفيديوهات المرتبطة بالطالب (مع ملفاتها)
        videos = db.execute('SELECT id, filepath FROM videos WHERE user_id = ?', (student_id,)).fetchall()
        for video in videos:
            # حذف التعليقات المرتبطة بالفيديو
            db.execute('DELETE FROM comments WHERE video_id = ?', (video['id'],))
            # حذف الإعجابات المرتبطة بالفيديو
            db.execute('DELETE FROM video_likes WHERE video_id = ?', (video['id'],))
            # حذف التقييمات المرتبطة بالفيديو
            db.execute('DELETE FROM dynamic_video_ratings WHERE video_id = ?', (video['id'],))
            # حذف ملف الفيديو
            if video['filepath']:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filepath'])
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Error deleting video file {video['filepath']}: {e}")
        
        # حذف الفيديوهات من قاعدة البيانات
        db.execute('DELETE FROM videos WHERE user_id = ?', (student_id,))
        
        # 2. حذف التعليقات التي كتبها الطالب (في فيديوهات أخرى)
        db.execute('DELETE FROM comments WHERE user_id = ?', (student_id,))
        
        # 3. حذف الإعجابات التي أعجب بها الطالب
        db.execute('DELETE FROM video_likes WHERE user_id = ?', (student_id,))
        
        # 4. حذف الرسائل المرتبطة بالطالب
        db.execute('DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?', (student_id, student_id))
        
        # 5. حذف الإيقافات
        db.execute('DELETE FROM suspensions WHERE user_id = ?', (student_id,))
        
        # 6. حذف ربط الأجهزة
        db.execute('DELETE FROM device_bindings WHERE user_id = ?', (student_id,))
        
        # 7. حذف المنشورات (إن وجدت)
        db.execute('DELETE FROM posts WHERE user_id = ?', (student_id,))
        
        # 8. حذف صورة الملف الشخصي (إن لم تكن الصورة الافتراضية)
        if student['profile_image'] and student['profile_image'] != 'default.png':
            try:
                profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], student['profile_image'])
                if os.path.exists(profile_image_path):
                    os.remove(profile_image_path)
            except Exception as e:
                print(f"Error deleting profile image {student['profile_image']}: {e}")
        
        # 9. حذف حساب الطالب نفسه
        db.execute('DELETE FROM users WHERE id = ?', (student_id,))
        
        db.commit()
        return jsonify({"status": "success", "message": "تم حذف حساب الطالب بنجاح"})
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting student: {e}")
        return jsonify({"status": "error", "error": f"حدث خطأ أثناء حذف الحساب: {str(e)}"}), 500

# ================== START: MODIFIED start_new_year ==================
@app.route('/admin/start_new_year', methods=['POST'])
def start_new_year():
    if session.get('role') != 'admin':
        flash('ليس لديك الصلاحية للقيام بهذا الإجراء.', 'danger')
        return redirect(url_for('index'))

    db = get_db()
    try:
        # --- START: MODIFICATION ---
        # حذف ملفات الفيديوهات والصور المرفوعة (باستثناء default.png)
        files_to_delete = db.execute("SELECT profile_image FROM users WHERE profile_image IS NOT NULL AND profile_image != 'default.png'").fetchall()
        videos_to_delete = db.execute("SELECT filepath FROM videos").fetchall()

        for user_file in files_to_delete:
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], user_file['profile_image'])
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error deleting user file {user_file['profile_image']}: {e}")

        for video in videos_to_delete:
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filepath'])
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error deleting video file {video['filepath']}: {e}")
        # --- END: MODIFICATION ---

        # حذف البيانات من الجداول
        # بفضل ON DELETE CASCADE، سيتم حذف البيانات المرتبطة تلقائياً
        # (مثل التعليقات، الإعجابات، التقييمات عند حذف الفيديوهات)
        db.execute('DELETE FROM videos') 
        db.execute('DELETE FROM posts')
        db.execute('DELETE FROM star_bank')
        db.execute('DELETE FROM suspensions')
        db.execute('DELETE FROM messages')
        


        db.execute("""
            UPDATE users
            SET class_name = NULL, section_name = NULL, profile_reset_required = 1, profile_image = 'default.png'
            WHERE role = 'student'
        """)

        db.commit()
        flash('تم بدء سنة دراسية جديدة بنجاح! تم مسح جميع البيانات وتجهيز النظام للعام الجديد.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'حدث خطأ أثناء بدء السنة الجديدة: {e}', 'danger')

    return redirect(url_for('admin_dashboard'))
# ================== END: MODIFIED start_new_year ==================
# ----------------- CONVERSATION ROUTES (Main Pages + APIs) -----------------
@app.route('/conversations')
def conversations():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    db = get_db()
    all_classes = db.execute("SELECT DISTINCT TRIM(class_name) as class_name FROM users WHERE role = 'student' AND class_name IS NOT NULL AND TRIM(class_name) != '' ORDER BY class_name").fetchall()
    all_sections = db.execute("SELECT DISTINCT TRIM(section_name) as section_name FROM users WHERE role = 'student' AND section_name IS NOT NULL AND TRIM(section_name) != '' ORDER BY section_name").fetchall()

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

    query = "SELECT id, username, full_name, profile_image, class_name, section_name FROM users WHERE role = 'student'"
    params = []

    if class_name:
        query += " AND TRIM(class_name) = ?"
        params.append(class_name.strip())
    if section_name:
        query += " AND TRIM(section_name) = ?"
        params.append(section_name.strip())
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

        student_query = "SELECT id FROM users WHERE role = 'student' AND TRIM(class_name) = ?"
        params = [class_name.strip()]
        if section_name:
            student_query += " AND TRIM(section_name) = ?"
            params.append(section_name.strip())

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

# --- تعديل 2: إضافة مسار خدمة الملفات الجديد ---
@app.route('/data/uploads/<filename>')
def uploaded_file(filename):
    try:
        # Security check to prevent accessing files outside the intended folder
        safe_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if not safe_path.startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
             abort(404) # Not Found if path is suspicious

        # Check if file exists, otherwise serve default image
        if not os.path.exists(safe_path):
             default_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default.png')
             if os.path.exists(default_image_path):
                 return send_from_directory(app.config['UPLOAD_FOLDER'], 'default.png')
             else:
                  abort(404) # Return 404 if even default is missing

        # Serve the requested file
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
         abort(404)
    except Exception as e:
         print(f"Error serving file {filename}: {e}") # Log error for debugging
         abort(500) # Internal Server Error


def run_waitress_server():
    """
    Start the application with waitress using optimized settings
    إصلاح: تحسين إعدادات Waitress لمنع ضغط السيرفر
    """
    from waitress import serve
    app.logger.info(
        "Starting waitress on %s (threads=%s, connection_limit=%s, channel_timeout=%s)",
        WAITRESS_LISTEN,
        WAITRESS_THREADS,
        WAITRESS_CONNECTION_LIMIT,
        WAITRESS_CHANNEL_TIMEOUT
    )
    # إصلاح: إعدادات محسّنة لمنع ضغط السيرفر
    serve(
        app,
        listen=WAITRESS_LISTEN,
        threads=WAITRESS_THREADS,
        connection_limit=WAITRESS_CONNECTION_LIMIT,
        channel_timeout=WAITRESS_CHANNEL_TIMEOUT,
        backlog=WAITRESS_BACKLOG,
        asyncore_loop_timeout=WAITRESS_LOOP_TIMEOUT,
        # إصلاح: إضافة timeout للطلبات لمنع التعليق
        cleanup_interval=30,
        # إصلاح: تحسين معالجة الملفات الكبيرة
        recv_bytes=8192,
        send_bytes=8192
    )


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# Schedule weekly champions report to Telegram every Wednesday at 8 PM
scheduler.add_job(
    scheduled_send_champions,
    trigger=CronTrigger(day_of_week='wed', hour=20, minute=0),
    id='weekly_champions_telegram',
    name='Send weekly champions to Telegram',
    replace_existing=True
)
logging.info("Scheduled task configured: Send champions to Telegram every Wednesday at 8:00 PM")

init_db()
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    if debug_mode:
        print("--- STARTING IN DEBUG MODE (FOR LOCAL TESTING) ---")
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '10000')), debug=True, threaded=True)
    else:
        run_waitress_server()