from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404

from django.contrib import messages
from django.contrib.auth import login
from .forms import SignupForm
from .models import (
    Course, Module, Lesson, Resource, Enrollment,
    LessonCompletion, UserProfile, Quiz, QuizAttempt, Question, Choice, ContactMessage
)

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model, update_session_auth_hash
import json

from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.db.models import Count, Q

# ----- Pages kept from your UI -----
def index(request):
    """Homepage shows courses that actually exist in DB (admin-created)."""
    courses = Course.objects.filter(is_active=True).order_by("title")
    # Keep your current template; we’ll only wire the Enroll links.
    return render(request, "index.html", {"courses": courses})

@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    obj, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={"status": Enrollment.STATUS_ACTIVE},
    )
    # 🔥 remove this broken call:
    # Enrollment.objects.get_or_create()

    if created:
        messages.success(request, f"You’re enrolled in {course.title}.")
    else:
        messages.info(request, f"You’re already enrolled in {course.title}.")
    return redirect("dashboard")

@require_POST
def contact_submit(request):
    """Store contact requests; show a friendly flash message."""
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    message = request.POST.get("message", "").strip()

    if not (name and email and message):
        messages.error(request, "Please fill in all contact fields.")
        return redirect("index")  # simple UX

    ContactMessage.objects.create(name=name, email=email, message=message)
    messages.success(request, "Thanks! We’ll get back to you within 1 business day.")
    return redirect("index")

def _ensure_static_quiz(num: int) -> int:
    """
    Make sure there's a Course/Module/Lesson/Quiz for the given quiz number.
    Returns the Quiz.id so the template can POST to /api/quiz/<id>/attempt/.
    """
    # A dedicated container so it won't clash with your real courses
    course, _ = Course.objects.get_or_create(
        slug="web-dev-static",
        defaults={
            "title": "Web Development (Static Quizzes)",
            "category": "Web Dev",
            "short_desc": "Container course for static quiz pages 1–8.",
            "is_active": True,
        },
    )
    module, _ = Module.objects.get_or_create(
        course=course,
        index=1,
        defaults={"title": "Module (Static Quizzes)", "intro": "Auto-provisioned"},
    )
    lesson, _ = Lesson.objects.get_or_create(
        module=module,
        index=num,
        defaults={"title": f"Static Quiz {num}", "summary": "Auto-provisioned"},
    )
    quiz, _ = Quiz.objects.get_or_create(
        lesson=lesson, defaults={"title": f"Quiz {num}", "pass_mark": 60}
    )
    return quiz.id

# --- your existing view, replace it with this version ---
def quiz_static(request, num: int):
    # Allow only 1..8
    if not (1 <= num <= 8):
        raise Http404("Quiz not found")
    quiz_id = _ensure_static_quiz(num)
    api_url = reverse("api_quiz_attempt", args=[quiz_id])
    # render the right static file and inject context for JS
    return render(
        request,
        f"quiz/quiz{num}.html",
        {
            "quiz_id": quiz_id,
            "api_url": api_url,
            "can_post_results": request.user.is_authenticated,
        },
    )


def course_player(request):
    return render(request, "course_player.html")

@login_required
def settings_view(request):
    return render(request, "setting.html")

# ----- Auth / Register -----
def register(request):
    # If already logged in, don’t show register
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Ensure profile exists even if signal didn’t fire for any reason
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.country = form.cleaned_data.get("country", "")
            profile.timezone = form.cleaned_data.get("timezone", "")
            profile.save()

            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("settings")  # or dashboard
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignupForm()

    return render(request, "register.html", {"form": form})

# ----- Dashboard -----
@login_required
def dashboard(request):
    enrollments = (
    Enrollment.objects.select_related("course")
    .filter(user=request.user, course__is_active=True)
    .order_by("course__title")
    )

    items = []
    for e in enrollments:
        c = e.course
        items.append({
            "id": c.slug,
            "title": c.title,
            "category": c.category or "General",
            "status": e.status or "In Progress",
            "desc": c.short_desc or "",
            "progress": 0,
            "tags": ["Enrolled"],
            "badge": "NEW" if c.slug == "full-stack-web-dev" else ""
        })

    return render(request, "dashboard.html", {
        "courses_json": json.dumps(items),
        "is_staff": request.user.is_staff,
    })


# ----- Dynamic Course Page (optional) -----
@login_required
def course_detail(request, slug):
    """
    Authenticated course player. Only enrolled users can access.
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Gate: must be enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, "Please enroll to access the course player.")
        return redirect("course_enroll", slug=course.slug)

    # Curriculum
    modules = (
        course.modules.all()
        .prefetch_related("lessons__resources")
        .order_by("index")
    )

    # Completed lesson IDs for this user
    completed_ids = set(
        LessonCompletion.objects.filter(
            user=request.user,
            lesson__module__course=course,
            completed=True,
        ).values_list("lesson_id", flat=True)
    )

    # For JS to mark module badges as completed when all lessons done
    module_lessons = [
        {"anchor": f"module{m.index}", "lesson_ids": [l.id for l in m.lessons.all()]}
        for m in modules
    ]

    counts = course.modules.aggregate(
        n_modules=Count("id", distinct=True),
        n_lessons=Count("lessons", distinct=True),
    )

    return render(request, "course_player.html", {
        "course": course,
        "modules": modules,
        "completed_ids": completed_ids,
        "module_lessons_json": json.dumps(module_lessons),
        "n_modules": counts.get("n_modules") or 0,
        "n_lessons": counts.get("n_lessons") or 0,
    })

# ===========================
# JSON API (fetch/AJAX)
# ===========================

@login_required
@require_http_methods(["GET", "POST", "PUT", "PATCH"])
def api_profile(request):
    """
    GET  -> Return current user's profile data
    POST/PUT/PATCH -> Update user + profile (supports multipart for avatar)
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # ---------- GET ----------
    if request.method == "GET":
        return JsonResponse({
            "first_name": request.user.first_name or "",
            "last_name": request.user.last_name or "",
            "email": request.user.email or "",
            "phone": profile.phone or "",
            "country": profile.country or "",
            "timezone": profile.timezone or "",
            "bio": profile.bio or "",
            "avatar_url": profile.avatar.url if profile.avatar else "",
        })

    # ---------- POST / PUT / PATCH ----------
    data = request.POST or {}

    # --- Update core user fields ---
    request.user.first_name = data.get("first_name", request.user.first_name)
    request.user.last_name = data.get("last_name", request.user.last_name)
    email = data.get("email")
    if email:
        request.user.email = email.strip().lower()
        request.user.username = email.strip().lower()  # keep username=email pattern
    request.user.save()

    # --- Update profile fields ---
    profile.phone = data.get("phone", profile.phone)
    profile.country = data.get("country", profile.country)
    profile.timezone = data.get("timezone", profile.timezone)
    profile.bio = data.get("bio", profile.bio)

    # Handle avatar upload
    if request.FILES.get("avatar"):
        profile.avatar = request.FILES["avatar"]

    profile.save()

    return JsonResponse({"ok": True, "message": "Profile updated successfully"})

@login_required
@require_http_methods(["GET","POST","PUT","PATCH"])
def api_preferences(request):
    profile = request.user.userprofile
    if request.method == "GET":
        return JsonResponse(profile.prefs or {})

    prefs = {
        "theme": request.POST.get("theme", (profile.prefs or {}).get("theme","light")),
        "nAnnouncements": request.POST.get("nAnnouncements","true") in ("true","1","on"),
        "nReminders": request.POST.get("nReminders","true") in ("true","1","on"),
        "nMarketing": request.POST.get("nMarketing","false") in ("true","1","on"),
    }
    profile.prefs = prefs
    profile.save()
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def api_toggle_lesson_completion(request):
    """Body: lesson_id, completed=true/false"""
    lesson_id = request.POST.get("lesson_id")
    completed = str(request.POST.get("completed","false")).lower() in ("true","1","yes")
    lesson = get_object_or_404(Lesson, id=lesson_id)
    obj, _ = LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    obj.completed = completed
    obj.completed_at = timezone.now() if completed else None
    obj.save()
    return JsonResponse({"ok": True, "completed": obj.completed})

@login_required
@require_http_methods(["POST"])
def api_submit_quiz_attempt(request, quiz_id: int):
    """
    Accepts either:
      - answers[question_id]=choice_id for real DB-backed questions
      - OR static pages can send {score, total, label_*}
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)

    raw_answers = {}
    score_param = request.POST.get("score")

    if score_param is None:
        # DB-backed scoring
        answers = {k.split("_", 1)[1]: v for k, v in request.POST.items() if k.startswith("q_")}
        total = quiz.questions.count()
        correct = 0
        for q in quiz.questions.all().prefetch_related("choices"):
            chosen_id = str(answers.get(str(q.id), ""))
            raw_answers[str(q.id)] = chosen_id
            if q.choices.filter(id=chosen_id, is_correct=True).exists():
                correct += 1
        score = int(round((correct * 100) / max(total, 1)))
    else:
        # Static page payload
        try:
            score = int(score_param)
        except ValueError:
            score = 0
        try:
            total = int(request.POST.get("total", 10))
        except ValueError:
            total = 10
        # collect labels (optional)
        for k, v in request.POST.items():
            if k.startswith("label_"):
                raw_answers[k] = v

    passed = score >= getattr(quiz, "pass_mark", 70)
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        total=total,
        passed=passed,
        raw_answers=raw_answers,
    )
    return JsonResponse({"ok": True, "score": score, "total": total, "passed": passed, "attempt_id": attempt.id})

@login_required
@require_POST
def api_delete_account(request):
    u = request.user
    from django.contrib.auth import logout
    logout(request)
    u.delete()
    return JsonResponse({"ok": True})

User = get_user_model()

@user_passes_test(lambda u: u.is_staff)
def enroll_user(request, user_id, slug):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Course, slug=slug, is_active=True)
    Enrollment.objects.get_or_create(user=user, course=course, defaults={"status": "In Progress"})
    messages.success(request, f"Enrolled {user.email or user.username} in {course.title}.")
    # go back to dashboard if it's you; otherwise back to admin list
    return redirect("dashboard" if user == request.user else "/admin/pages/enrollment/")

@user_passes_test(lambda u: u.is_staff)
def unenroll_user(request, user_id, slug):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Course, slug=slug, is_active=True)
    Enrollment.objects.filter(user=user, course=course).delete()
    messages.success(request, f"Removed {user.email or user.username} from {course.title}.")
    return redirect("dashboard" if user == request.user else "/admin/pages/enrollment/")

def courses_list(request):
    q = request.GET.get("q", "").strip()
    qs = Course.objects.filter(is_active=True).annotate(
        n_modules=Count("modules", distinct=True),
        n_lessons=Count("modules__lessons", distinct=True),
    ).order_by("title")

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(category__icontains=q))

    enrolled_slugs = set()
    if request.user.is_authenticated:
        enrolled_slugs = set(
            Enrollment.objects.filter(user=request.user).values_list("course__slug", flat=True)
        )

    return render(request, "courses_list.html", {
        "courses": qs,
        "enrolled_slugs": enrolled_slugs,
    })

def course_enroll(request, slug):
    """
    Public landing page for a course with curriculum preview and Enroll/Continue CTA.
    Context used by your template:
      course, modules, n_modules, n_lessons, is_enrolled, enroll_link, continue_link
    """
    course = get_object_or_404(Course.objects.filter(is_active=True), slug=slug)

    # Prefetch curriculum
    modules = (
        course.modules
        .prefetch_related("lessons")
        .order_by("index")
    )

    # Fast counts (single query)
    counts = course.modules.aggregate(
        n_modules=Count("id", distinct=True),
        n_lessons=Count("lessons", distinct=True),
    )
    n_modules = counts.get("n_modules") or 0
    n_lessons = counts.get("n_lessons") or 0

    # Determine correct CTA
    is_enrolled = False
    enroll_link = None
    continue_link = None

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        if is_enrolled:
            continue_link = reverse("course_detail", args=[course.slug])
        else:
            enroll_link = reverse("enroll", args=[course.slug])
    else:
        # send through login, then bounce back to enroll endpoint
        enroll_link = reverse("login") + "?next=" + reverse("enroll", args=[course.slug])

    return render(request, "course_enroll.html", {
        "course": course,
        "modules": modules,
        "n_modules": n_modules,
        "n_lessons": n_lessons,
        "is_enrolled": is_enrolled,
        "enroll_link": enroll_link,
        "continue_link": continue_link,
    })