from django.contrib import admin 
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, Course, Module, Lesson, Resource,
    Enrollment, LessonCompletion, Quiz, Question, Choice, QuizAttempt, ContactMessage
)

admin.site.site_header = "Rabbani CiC Admin"
admin.site.site_title = "Rabbani CiC Admin"
admin.site.index_title = "Learning Management System"

# ----- Inlines -----
class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ("name", "file")
    show_change_link = True

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("index", "title", "youtube_url")  # (you removed is_published, good)
    ordering = ("index",)
    show_change_link = True

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    fields = ("text", "is_correct")
    show_change_link = True

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ("order", "text")          # ✅ was index
    ordering = ("order",)               # ✅ was index
    show_change_link = True

# ----- UserProfile -----
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "timezone", "updated_at")
    search_fields = ("user__username", "user__email", "country", "timezone")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

# ----- Course -----
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "slug")
    list_filter = ("category", "is_active")
    search_fields = ("title", "slug", "category")
    prepopulated_fields = {"slug": ("title",)}
    actions = ("activate_selected", "deactivate_selected")

    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} course(s).")
    activate_selected.short_description = "Activate selected courses"

    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} course(s).")
    deactivate_selected.short_description = "Deactivate selected courses"

# ----- Module -----
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("course", "index", "title")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "index")
    autocomplete_fields = ("course",)
    inlines = [LessonInline]

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("course"))

# ----- Lesson -----
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("module", "index", "title", "youtube_preview")
    list_filter = ("module__course", "module")
    search_fields = ("title", "module__title", "module__course__title")
    ordering = ("module", "index")
    autocomplete_fields = ("module",)
    inlines = [ResourceInline]

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("module", "module__course"))

    @admin.display(description="YouTube")
    def youtube_preview(self, obj: Lesson):
        if not obj.youtube_url:
            return "-"
        url = obj.youtube_url
        vid = None
        if "youtu.be/" in url:
            vid = url.rsplit("/", 1)[-1]
        elif "watch?v=" in url:
            vid = url.split("watch?v=", 1)[-1].split("&", 1)[0]
        if vid:
            thumb = f"https://img.youtube.com/vi/{vid}/default.jpg"
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" alt="thumb" style="height:38px;border-radius:6px"></a>',
                url, thumb
            )
        return mark_safe('<span style="color:#94a3b8">n/a</span>')

# ----- Quiz -----
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("lesson", "title", "is_active")  # ✅ removed pass_mark
    list_filter = ("lesson__module__course", "lesson__module")
    search_fields = ("title", "lesson__title", "lesson__module__title", "lesson__module__course__title")
    ordering = ("lesson",)
    autocomplete_fields = ("lesson",)
    inlines = [QuestionInline]

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("lesson", "lesson__module", "lesson__module__course"))

# ----- Question -----
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "text")   # ✅ was index
    list_filter = ("quiz__lesson__module__course", "quiz")
    search_fields = ("text", "quiz__title", "quiz__lesson__title")
    ordering = ("quiz", "order")               # ✅ was index
    autocomplete_fields = ("quiz",)
    inlines = [ChoiceInline]

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("quiz", "quiz__lesson", "quiz__lesson__module", "quiz__lesson__module__course"))

# ----- Choice -----
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "is_correct", "text")
    list_filter = ("is_correct", "question__quiz")
    search_fields = ("text", "question__text", "question__quiz__title")
    ordering = ("question", "id")
    autocomplete_fields = ("question",)

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("question", "question__quiz"))

# ----- Enrollment -----
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "created_at")
    list_filter = ("status", "course")
    search_fields = ("user__username", "user__email", "course__title")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "course")
    date_hierarchy = "created_at"
    actions = ("mark_active", "mark_completed")

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("user", "course"))

    def mark_active(self, request, queryset):
        updated = queryset.update(status="active")
        self.message_user(request, f"Marked {updated} enrollment(s) as active.")
    mark_active.short_description = "Mark selected as Active"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"Marked {updated} enrollment(s) as completed.")
    mark_completed.short_description = "Mark selected as Completed"

# ----- LessonCompletion -----
@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "completed_at")
    list_filter = ("completed", "lesson__module__course")
    search_fields = ("user__username", "user__email", "lesson__title", "lesson__module__course__title")
    ordering = ("-completed_at",)
    autocomplete_fields = ("user", "lesson")
    date_hierarchy = "completed_at"

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("user", "lesson", "lesson__module", "lesson__module__course"))

# ----- QuizAttempt -----
@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "total", "created_at")   # ✅ removed passed/submitted_at
    list_filter = ("quiz__lesson__module__course",)                   # ✅ removed passed
    search_fields = ("user__username", "user__email", "quiz__title", "quiz__lesson__title")
    ordering = ("-created_at",)                                       # ✅ was -submitted_at
    autocomplete_fields = ("user", "quiz")
    date_hierarchy = "created_at"                                     # ✅

    def get_queryset(self, request):
        return (super()
                .get_queryset(request)
                .select_related("user", "quiz", "quiz__lesson", "quiz__lesson__module", "quiz__lesson__module__course"))

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)