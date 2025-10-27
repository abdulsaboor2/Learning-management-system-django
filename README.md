# Learning Management System (LMS)

A Django-based LMS with courses → modules → lessons, downloadable resources, enrollments, progress tracking, and quizzes. Modern Bootstrap UI for landing pages, catalog, dashboard, and an authenticated course player.

## ✨ Features

- **Auth & Profiles:** Sign up/login/logout, profile with avatar, bio, country & timezone, and preference storage.
- **Courses & Curriculum:** Courses contain modules and ordered lessons; lessons can embed YouTube videos and attach PDF resources.
- **Enrollments & Dashboard:** Users enroll and continue learning from a personalized dashboard.
- **Lesson Progress:** Toggle completion per lesson and track progress.
- **Quizzes:** One quiz per lesson (DB-backed) + static quiz pages (1–8) with scoring and pass/fail.
- **Contact:** Simple contact form posting to the backend.
- **Admin:** Rich Django admin with inlines for Resources, Lessons, Questions/Choices and helpful list displays.

## 🖼 UI Pages

- **Home / Marketing:** modern hero + value prop.
- **Courses catalog:** searchable list of active courses.
- **Course landing page:** enroll/continue CTA with curriculum preview.
- **Course player (auth & enrolled):** sticky module steps, video panel, resources, and mark-complete.
- **Dashboard:** enrolled courses grid with progress & quick actions.
- **Auth:** login & register.
- **Static quizzes:** `/quiz/1 … /quiz/8` (auto-provisions a container course/module/lesson/quiz on first visit).

## 🗂 Project Structure
- learning_management_system/ # Django project
- settings.py, urls.py, wsgi.py
- pages/ # App: models, views, admin, forms, templates, static
- media/ # Uploaded lesson resources & avatars (dev)
- manage.py
