"""
Django management command to setup Docker files for deployment
"""
from django.core.management.base import BaseCommand, CommandError

from django_coolify.utils import ensure_docker_files, add_health_check_url


class Command(BaseCommand):
    help = 'Setup Docker files for deployment (Dockerfile using uv, .dockerignore, health check)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-health-check',
            action='store_true',
            help='Skip adding health check URL to Django project'
        )
    
    def handle(self, *args, **options):
        # Create Docker files
        try:
            created_files = ensure_docker_files()
            
            for file_type, file_path in created_files.items():
                if file_type == 'dockerfile':
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Dockerfile created/verified: {file_path}")
                    )
                elif file_type == 'dockerignore':
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ .dockerignore created/verified: {file_path}")
                    )
            
        except Exception as e:
            raise CommandError(f"Error creating Docker files: {e}")
        
        # Add health check URL
        if not options['skip_health_check']:
            try:
                added = add_health_check_url()
                if added:
                    self.stdout.write(
                        self.style.SUCCESS("✓ Health check URL added to Django project")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("Health check URL already exists or could not be added")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Could not add health check URL: {e}")
                )
        
        self.stdout.write("\nDocker setup completed!")
        self.stdout.write("Next steps:")
        self.stdout.write("1. Review the generated Dockerfile (uses uv for dependency management)")
        self.stdout.write("2. Test your application locally: docker build -t myapp . && docker run -p 8000:8000 myapp")
        self.stdout.write("3. Run 'python manage.py deploy' to deploy to Coolify")
