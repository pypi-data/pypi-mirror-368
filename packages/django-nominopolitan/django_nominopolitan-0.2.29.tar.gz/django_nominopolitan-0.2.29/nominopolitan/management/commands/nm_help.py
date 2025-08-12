from django.core.management.base import BaseCommand
import webbrowser

class Command(BaseCommand):
    help = "Opens the Nominopolitan documentation in your default browser"

    def handle(self, *args, **options):
        docs_url = "https://doctor-cornelius.github.io/django-nominopolitan/"
        
        try:
            webbrowser.open(docs_url)
            self.stdout.write(
                self.style.SUCCESS(f"Opening Nominopolitan documentation at {docs_url}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to open browser: {str(e)}")
            )
            self.stdout.write(
                self.style.WARNING(f"Please manually visit: {docs_url}")
            )
