from django.db import migrations

def seed(apps, schema_editor):
    Course = apps.get_model("pages", "Course")
    if not Course.objects.filter(slug="full-stack-web-dev").exists():
        Course.objects.create(
            slug="full-stack-web-dev",
            title="Full Stack Web Development",
            category="Web",
            short_desc="HTML, CSS, JavaScript, and back-end fundamentals.",
            is_active=True,
        )

def unseed(apps, schema_editor):
    apps.get_model("pages", "Course").objects.filter(slug="full-stack-web-dev").delete()

class Migration(migrations.Migration):
    dependencies = [("pages", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
