"""
Django management command to set domain for Coolify application
"""
from django.core.management.base import BaseCommand, CommandError

from django_coolify.client import CoolifyClient, CoolifyAPIError
from django_coolify.config import CoolifyConfig
from django_coolify.utils import generate_domain_name


class Command(BaseCommand):
    help = 'Set domain for Coolify application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain to set (if not provided, will auto-generate)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if domain already exists'
        )
    
    def handle(self, *args, **options):
        config_manager = CoolifyConfig()
        
        # Check if config exists
        if not config_manager.exists():
            raise CommandError(
                "Configuration file not found. Run 'python manage.py generate_config' first."
            )
        
        # Load configuration
        try:
            config = config_manager.load()
        except ValueError as e:
            raise CommandError(f"Error loading configuration: {e}")
        
        # Validate required configuration
        required_fields = ['coolify_url', 'api_token', 'app_uuid']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise CommandError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Run 'python manage.py setup_infra' first."
            )
        
        # Initialize client
        client = CoolifyClient(config['coolify_url'], config['api_token'])
        
        # Determine domain to set
        if options['domain']:
            domain = options['domain']
            # Ensure https:// prefix for Coolify API
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"
            self.stdout.write(f"Using provided domain: {domain}")
        elif not config.get('domains') or options['force']:
            # Get the port from config, default to 8000 for Django
            port = int(config.get('ports_exposes', 8000))
            domain = generate_domain_name(config['app_name'], config['coolify_url'], port)
            self.stdout.write(f"Generated domain: {domain}")
        else:
            domain = config['domains']
            # Ensure https:// prefix for existing config
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"
            self.stdout.write(f"Using existing domain from config: {domain}")
        
        # Set domain on the application
        app_uuid = config['app_uuid']
        
        try:
            # Method 1: Update application settings
            settings = {"domains": domain}
            client.update_application_settings(app_uuid, settings)
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully set domain: {domain}")
            )
            
        except CoolifyAPIError as e:
            self.stdout.write(
                self.style.WARNING(f"Method 1 failed: {e}")
            )
            
            # Method 2: Try domain-specific endpoint
            try:
                client.set_application_domain(app_uuid, domain)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Successfully set domain (method 2): {domain}")
                )
            except CoolifyAPIError as e2:
                raise CommandError(f"Failed to set domain: {e2}")
        
        # Also set as environment variable for Django (without https:// and port)
        try:
            # Remove protocol and port for ALLOWED_HOSTS
            domain_for_django = domain.replace('https://', '').replace('http://', '')
            # Remove port if present (e.g., "example.com:8000" -> "example.com")
            if ':' in domain_for_django:
                domain_for_django = domain_for_django.split(':')[0]
            
            # Include localhost and 0.0.0.0 for Docker and local development
            allowed_hosts = f"{domain_for_django},localhost,0.0.0.0"
            
            client.set_environment_variable(app_uuid, 'ALLOWED_HOSTS', allowed_hosts)
            self.stdout.write(f"✓ Set ALLOWED_HOSTS environment variable: {allowed_hosts}")
        except CoolifyAPIError as e:
            self.stdout.write(
                self.style.WARNING(f"Warning: Could not set ALLOWED_HOSTS env var: {e}")
            )
        
        # Update config
        config['domains'] = domain
        config_manager.save(config)
        
        self.stdout.write(
            self.style.SUCCESS(f"\nDomain configuration completed!")
        )
        self.stdout.write(f"Your application will be available at: {domain}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("NOTE: You may need to manually set the domain in the Coolify UI:"))
        self.stdout.write(f"1. Go to your Coolify dashboard")
        self.stdout.write(f"2. Navigate to your application: {config['app_name']}")
        self.stdout.write(f"3. Go to Configuration > General > Domains")
        self.stdout.write(f"4. Set the domain to: {domain}")
        self.stdout.write(f"5. Click 'Set Direction' if needed")
        self.stdout.write(f"6. Save the configuration")
