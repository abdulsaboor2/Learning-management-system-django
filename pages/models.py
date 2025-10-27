from django.conf import settings
from django.db import models
from django.utils.text import slugify

# Create your models here.

# ----- User Profile -----

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = models.CharField(max_length=64, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    prefs = models.JSONField(default=dict, blank=True)  # ✅ correct
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.username})"


# ----- Courses -----
class Course(models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=64, blank=True)  # Web/Data/Design/Security...
    short_desc = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def save(self, *a, **kw):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*a, **kw)
    def __str__(self): return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    index = models.PositiveIntegerField(default=1)  # Module order
    title = models.CharField(max_length=200)
    intro = models.TextField(blank=True)
    
    class Meta:
        ordering = ["index"]
        indexes = [models.Index(fields=["course", "index"])]
        
    def __str__(self): return f"{self.course.title} • Module {self.index}"

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    index = models.PositiveIntegerField(default=1)
    youtube_url = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True)
    module = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="lessons")
    
    class Meta:
        ordering = ["index"]
        indexes = [models.Index(fields=["module", "index"])]
    
    def __str__(self): 
        return f"{self.module} • L{self.index}: {self.title}"

class Resource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="lesson_resources/")
    def __str__(self): return f"{self.lesson}: {self.name}"

# Enrollment & progress
class Enrollment(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_NOT_STARTED = "not_started"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_NOT_STARTED, "Not started"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment")
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} ↔ {self.course}"

class LessonCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_completions")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="completions")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lesson"], name="unique_completion")]
        indexes = [models.Index(fields=["user", "lesson"])]
        
    def __str__(self): return f"{self.user} • {self.lesson} : {self.completed}"

# ----- Quizzes -----
class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=200, default="Lesson Quiz")
    is_active = models.BooleanField(default=True)
    pass_mark = models.PositiveIntegerField(default=70)  # percent ✅

    def __str__(self):
        return f"Quiz: {self.lesson}"

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # ADD THESE:
    passed = models.BooleanField(default=False)
    raw_answers = models.JSONField(default=dict, blank=True)

    @property
    def passed_property(self):
        # keep a computed view if you still want it
        if self.total == 0:
            return False
        return (self.score * 100 / self.total) >= getattr(self.quiz, "pass_mark", 70)
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:60]

    class Meta:
        ordering = ("order", "id")   # ✅ use existing field


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:60]

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email}> • {self.created_at:%Y-%m-%d}"
