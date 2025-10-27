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

System Interface
<img width="1351" height="3618" alt="127 0 0 1_8000_ (1)" src="https://github.com/user-attachments/assets/5de0f7b9-4c46-468e-aaa0-6995d577054b" />

<img width="1351" height="646" alt="127 0 0 1_8000_register_" src="https://github.com/user-attachments/assets/ae3a8c8b-0ddb-445c-b006-9c10ee3ce58a" />

<img width="1366" height="641" alt="127 0 0 1_8000_login_" src="https://github.com/user-attachments/assets/39d1ce33-ce9a-4367-a56a-e6487330423f" />

<img width="1351" height="945" alt="127 0 0 1_8000_courses_" src="https://github.com/user-attachments/assets/5a7c441b-fae4-452a-97d5-b6c2c21d2b2f" />

<img width="1351" height="1238" alt="127 0 0 1_8000_courses_full-stack-web-dev_" src="https://github.com/user-attachments/assets/9a22adef-70ab-461e-9cf3-c758dca493c8" />

<img width="1366" height="641" alt="127 0 0 1_8000_dashboard_" src="https://github.com/user-attachments/assets/6675d8e4-55af-45fd-9888-7cc5cfd9a48a" />

<img width="1351" height="4427" alt="127 0 0 1_8000_course_full-stack-web-dev_" src="https://github.com/user-attachments/assets/0c92d9b2-5ee0-408b-b664-5770f355457f" />

<img width="1366" height="641" alt="_C__Users_ZAIIIN_Downloads_Learning_Management_System_Pages_templates_quiz_quiz1 html" src="https://github.com/user-attachments/assets/1cc207fd-8c43-4754-896f-eac488c59821" />







