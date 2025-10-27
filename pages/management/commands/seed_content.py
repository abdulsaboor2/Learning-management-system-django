from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from pages.models import Course, Module, Lesson, Quiz, Question, Choice, Resource

from django.core.files.base import ContentFile


FULLSTACK = {
    "slug": "full-stack-web-dev",
    "title": "Full Stack Web Development",
    "category": "Web Dev",
    "short_desc": "From HTML/CSS/JS to Django, databases, and deployment.",
    "is_active": True,
    "modules": [
        {
            "index": 1,
            "title": "Frontend Fundamentals",
            "intro": "HTML, CSS, JavaScript basics and modern tooling.",
            "lessons": [
                {
                    "index": 1,
                    "title": "HTML & Semantic Structure",
                    "youtube_url": "https://www.youtube.com/watch?v=UB1O30fR-EE",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which tag best represents the main content of a page?",
                                "choices": [
                                    ("<div>", False),
                                    ("<main>", True),
                                    ("<section>", False),
                                    ("<span>", False),
                                ],
                            },
                            {
                                "text": "Which tag is best for a navigation region?",
                                "choices": [
                                    ("<nav>", True),
                                    ("<aside>", False),
                                    ("<article>", False),
                                    ("<ul>", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "index": 2,
                    "title": "CSS Layout Essentials",
                    "youtube_url": "https://www.youtube.com/watch?v=1Rs2ND1ryYc",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which CSS module provides two-dimensional layout?",
                                "choices": [
                                    ("Flexbox", False),
                                    ("Grid", True),
                                    ("Floats", False),
                                    ("Positioning", False),
                                ],
                            },
                            {
                                "text": "Which property sets a flex container?",
                                "choices": [
                                    ("display: flex", True),
                                    ("position: flex", False),
                                    ("flex: container", False),
                                    ("layout: flex", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "index": 3,
                    "title": "JavaScript Fundamentals",
                    "youtube_url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which keyword declares a block-scoped variable?",
                                "choices": [
                                    ("var", False),
                                    ("let", True),
                                    ("def", False),
                                    ("static", False),
                                ],
                            },
                            {
                                "text": "Which method converts JSON string to an object?",
                                "choices": [
                                    ("JSON.parse()", True),
                                    ("JSON.encode()", False),
                                    ("Object.fromJSON()", False),
                                    ("String.toJSON()", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            "index": 2,
            "title": "Backend with Django",
            "intro": "Django MVC (MTV), routing, views, templates, forms.",
            "lessons": [
                {
                    "index": 1,
                    "title": "Django Project Structure",
                    "youtube_url": "https://www.youtube.com/watch?v=F5mRW0jo-U4",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "What does MTV stand for in Django?",
                                "choices": [
                                    ("Model-Template-View", True),
                                    ("Model-Tool-View", False),
                                    ("Module-Template-Variable", False),
                                    ("Model-Template-Variable", False),
                                ],
                            },
                            {
                                "text": "Which file maps URL patterns?",
                                "choices": [
                                    ("urls.py", True),
                                    ("views.py", False),
                                    ("models.py", False),
                                    ("settings.py", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "index": 2,
                    "title": "Django ORM Basics",
                    "youtube_url": "https://www.youtube.com/watch?v=F5mRW0jo-U4&t=3600s",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which method creates and saves a new model instance?",
                                "choices": [
                                    ("Model.objects.create()", True),
                                    ("Model.save_new()", False),
                                    ("Model.add()", False),
                                    ("Model.insert()", False),
                                ],
                            },
                            {
                                "text": "Which QuerySet method returns a single object or raises DoesNotExist?",
                                "choices": [
                                    ("get()", True),
                                    ("filter()", False),
                                    ("all()", False),
                                    ("values()", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            "index": 3,
            "title": "Databases & Persistence",
            "intro": "Relational modeling, migrations, and relationships.",
            "lessons": [
                {
                    "index": 1,
                    "title": "Modeling Relationships",
                    "youtube_url": "https://www.youtube.com/watch?v=IojkpS7QwW0",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which field creates a many-to-one relation in Django?",
                                "choices": [
                                    ("ForeignKey", True),
                                    ("OneToOneField", False),
                                    ("ManyToManyField", False),
                                    ("RelationField", False),
                                ],
                            },
                            {
                                "text": "Which command creates new migration files?",
                                "choices": [
                                    ("python manage.py makemigrations", True),
                                    ("python manage.py migrate", False),
                                    ("python manage.py collectstatic", False),
                                    ("python manage.py runserver", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            "index": 4,
            "title": "Deployment & Ops",
            "intro": "Static/media, environment variables, basic hosting.",
            "lessons": [
                {
                    "index": 1,
                    "title": "Preparing for Deployment",
                    "youtube_url": "https://www.youtube.com/watch?v=4r6WDaY3SOA",
                    "quiz": {
                        "pass_mark": 60,
                        "questions": [
                            {
                                "text": "Which setting must be False in production?",
                                "choices": [
                                    ("DEBUG", True),
                                    ("USE_TZ", False),
                                    ("USE_I18N", False),
                                    ("LANGUAGE_CODE", False),
                                ],
                            },
                            {
                                "text": "Which command collects static files?",
                                "choices": [
                                    ("python manage.py collectstatic", True),
                                    ("python manage.py static", False),
                                    ("python manage.py gatherstatic", False),
                                    ("python manage.py buildstatic", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Seeds the Full Stack Web Development course, modules, lessons, and quizzes."

    @transaction.atomic
    def handle(self, *args, **options):
        c, created = Course.objects.get_or_create(
            slug=FULLSTACK["slug"],
            defaults={
                "title": FULLSTACK["title"],
                "category": FULLSTACK["category"],
                "short_desc": FULLSTACK["short_desc"],
                "is_active": FULLSTACK["is_active"],
            },
        )
        if not created:
            # keep title/category/desc in sync if changed in dict
            c.title = FULLSTACK["title"]
            c.category = FULLSTACK["category"]
            c.short_desc = FULLSTACK["short_desc"]
            c.is_active = FULLSTACK["is_active"]
            c.save()

        self.stdout.write(self.style.SUCCESS(f"Course: {c.title} ({c.slug})"))

        for mdef in FULLSTACK["modules"]:
            m, _ = Module.objects.get_or_create(
                course=c,
                index=mdef["index"],
                defaults={"title": mdef["title"], "intro": mdef.get("intro", "")},
            )
            # keep title/intro synced
            m.title = mdef["title"]
            m.intro = mdef.get("intro", "")
            m.save()
            self.stdout.write(f"  Module {m.index}: {m.title}")

            for ldef in mdef["lessons"]:
                l, _ = Lesson.objects.get_or_create(
                    module=m,
                    index=ldef["index"],
                    defaults={
                        "title": ldef["title"],
                        "youtube_url": ldef.get("youtube_url", ""),
                        "summary": ldef.get("summary", ""),
                    },
                )
                # sync fields
                l.title = ldef["title"]
                l.youtube_url = ldef.get("youtube_url", "")
                l.summary = ldef.get("summary", "")
                l.save()
                self.stdout.write(f"    Lesson {l.index}: {l.title}")

                # Create a quiz per lesson (OneToOne)
                q, _ = Quiz.objects.get_or_create(
                    lesson=l,
                    defaults={
                        "title": f"{l.title} Quiz",
                        "is_active": True,
                        "pass_mark": ldef.get("quiz", {}).get("pass_mark", 60),
                    },
                )
                # update pass_mark if changed
                q.title = f"{l.title} Quiz"
                q.is_active = True
                q.pass_mark = ldef.get("quiz", {}).get("pass_mark", 60)
                q.save()

                # Clear and re-add questions for simplicity (or make this smarter)
                existing_qs = list(q.questions.all())
                if existing_qs:
                    # Keep if you prefer incremental; here we replace to match spec
                    for eq in existing_qs:
                        eq.delete()

                order = 1
                for qdef in ldef.get("quiz", {}).get("questions", []):
                    qq = Question.objects.create(
                        quiz=q,
                        text=qdef["text"],
                        order=order,
                    )
                    order += 1
                    for text, is_correct in qdef["choices"]:
                        Choice.objects.create(question=qq, text=text, is_correct=is_correct)

                # (Optional) create a tiny placeholder resource file per lesson
                # Comment out if you don't want resources
                # content = ContentFile(f"Notes for: {l.title}\n".encode("utf-8"))
                # r = Resource(lesson=l, name=f"{l.title} Notes.txt")
                # r.file.save(f"{slugify(l.title)}-notes.txt", content, save=True)

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
