from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    help = "Starts Django's development server without requiring a database preflight."

    def check_migrations(self):
        self.stdout.write(
            self.style.WARNING(
                "Skipping migration check for dev server startup. "
                "Use `manage.py migrate` to verify database migrations."
            )
        )
