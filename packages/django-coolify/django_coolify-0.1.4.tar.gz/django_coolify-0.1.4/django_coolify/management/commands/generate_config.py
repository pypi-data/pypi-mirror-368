"""
Django management command to generate coolify.json configuration
"""
from django.core.management.base import BaseCommand, CommandError

from django_coolify.config import CoolifyConfig
from django_coolify.utils import ensure_docker_files, auto_configure_django_settings, auto_configure_django_urls, ensure_gitignore_entries


class Command(BaseCommand):
    help = 'Generate coolify.json configuration file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--coolify-url',
            type=str,
            help='Coolify instance URL (e.g., https://coolify.example.com)'
        )
        parser.add_argument(
            '--api-token',
            type=str,
            help='Coolify API token'
        )
        parser.add_argument(
            '--project-name',
            type=str,
            help='Project name in Coolify'
        )
        parser.add_argument(
            '--app-name',
            type=str,
            help='Application name in Coolify'
        )
        parser.add_argument(
            '--git-repository',
            type=str,
            help='Git repository URL'
        )
        parser.add_argument(
            '--git-branch',
            type=str,
            default='main',
            help='Git branch to deploy (default: main)'
        )
        parser.add_argument(
            '--build-pack',
            type=str,
            default='dockerfile',
            choices=['dockerfile', 'nixpacks'],
            help='Build pack to use (default: dockerfile)'
        )
        parser.add_argument(
            '--domains',
            type=str,
            help='Domains for the application (comma-separated)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing configuration file'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive configuration mode'
        )
        parser.add_argument(
            '--skip-docker',
            action='store_true',
            help='Skip Docker file generation'
        )
    
    def handle(self, *args, **options):
        # Auto-configure Django settings first
        self.stdout.write("Auto-configuring Django settings...")
        settings_modified = auto_configure_django_settings()
        if settings_modified:
            self.stdout.write(
                self.style.SUCCESS("✓ Django settings updated for Coolify deployment")
            )
        else:
            self.stdout.write("✓ Django settings already configured")
        
        # Auto-configure Django URLs for health endpoint
        self.stdout.write("Auto-configuring Django URLs...")
        urls_modified = auto_configure_django_urls()
        if urls_modified:
            self.stdout.write(
                self.style.SUCCESS("✓ Django URLs updated to include health endpoint")
            )
        else:
            self.stdout.write("✓ Django URLs already configured")
        
        config_manager = CoolifyConfig()
        
        # Check if config already exists
        if config_manager.exists() and not options['force']:
            if options['interactive']:
                overwrite = input(
                    f"Configuration file already exists at {config_manager.config_path}. "
                    "Overwrite? (y/N): "
                ).lower().strip()
                if overwrite != 'y':
                    self.stdout.write(
                        self.style.WARNING('Configuration generation cancelled.')
                    )
                    return
            else:
                raise CommandError(
                    f"Configuration file already exists at {config_manager.config_path}. "
                    "Use --force to overwrite or --interactive for prompt."
                )
        
        # Start with default config
        config = config_manager.generate_default_config()
        
        # Interactive mode
        if options['interactive']:
            config = self._interactive_config(config)
        else:
            # Update config with provided options
            if options['coolify_url']:
                config['coolify_url'] = options['coolify_url'].rstrip('/')
            if options['api_token']:
                config['api_token'] = options['api_token']
            if options['project_name']:
                config['project_name'] = options['project_name']
            if options['app_name']:
                config['app_name'] = options['app_name']
            if options['git_repository']:
                config['git_repository'] = options['git_repository']
            if options['git_branch']:
                config['git_branch'] = options['git_branch']
            if options['build_pack']:
                config['build_pack'] = options['build_pack']
            if options['domains']:
                config['domains'] = options['domains']
        
        # Validate required fields
        required_fields = ['coolify_url', 'api_token']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields and not options['interactive']:
            raise CommandError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Provide them as arguments or use --interactive mode."
            )
        
        # Save configuration
        try:
            config_manager.save(config)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Configuration saved to {config_manager.config_path}"
                )
            )
            
            # Check if API token was provided and inform about .env file
            if config.get('api_token'):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"API token saved securely to {config_manager.env_path}"
                    )
                )
            
        except ValueError as e:
            raise CommandError(f"Error saving configuration: {e}")
        
        # Update .gitignore to ensure .env is ignored
        self.stdout.write("Updating .gitignore...")
        gitignore_updated = ensure_gitignore_entries()
        if gitignore_updated:
            self.stdout.write(
                self.style.SUCCESS("✓ .gitignore updated to exclude .env files")
            )
        else:
            self.stdout.write("✓ .gitignore already configured")
        
        # Generate Docker files unless skipped
        if not options['skip_docker']:
            self._setup_docker_files()
        
        # Display next steps
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Review and edit the configuration file if needed")
        if config.get('api_token'):
            self.stdout.write("2. ⚠️  Your Coolify API token is stored in .env (keep this file secure!)")
        else:
            self.stdout.write("2. Add your Coolify API token to .env file: COOLIFY_API_TOKEN=your_token_here")
        if not options['skip_docker']:
            self.stdout.write("3. Review the generated Docker files")
            self.stdout.write("4. Run 'python manage.py setup-infra' to create project and application")
            self.stdout.write("4. Commit your changes to git")
            self.stdout.write("5. Run 'python manage.py deploy' to deploy your application")
        else:
            self.stdout.write("2. Run 'python manage.py setup-infra' to create project and application")
            self.stdout.write("3. Setup Docker files manually or run 'python manage.py setup-docker'")
            self.stdout.write("4. Commit your changes to git")
            self.stdout.write("5. Run 'python manage.py deploy' to deploy your application")
    
    def _interactive_config(self, config):
        """Interactive configuration mode"""
        self.stdout.write(self.style.SUCCESS("Interactive Coolify Configuration"))
        self.stdout.write("Press Enter to keep the current value in brackets\n")
        
        # Coolify URL
        coolify_url = input(
            f"Coolify instance URL [{config.get('coolify_url', '')}]: "
        ).strip()
        if coolify_url:
            config['coolify_url'] = coolify_url.rstrip('/')
        
        # API Token
        api_token = input(
            f"Coolify API token [{config.get('api_token', '')[:10]}{'...' if config.get('api_token') else ''}]: "
        ).strip()
        if api_token:
            config['api_token'] = api_token
        
        # Project name
        project_name = input(
            f"Project name [{config.get('project_name', '')}]: "
        ).strip()
        if project_name:
            config['project_name'] = project_name
        
        # App name
        app_name = input(
            f"Application name [{config.get('app_name', '')}]: "
        ).strip()
        if app_name:
            config['app_name'] = app_name
        
        # Git repository
        git_repository = input(
            f"Git repository URL [{config.get('git_repository', '')}]: "
        ).strip()
        if git_repository:
            config['git_repository'] = git_repository
        
        # Git branch
        git_branch = input(
            f"Git branch [{config.get('git_branch', 'main')}]: "
        ).strip()
        if git_branch:
            config['git_branch'] = git_branch
        
        # Build pack
        build_pack = input(
            f"Build pack (dockerfile/nixpacks) [{config.get('build_pack', 'dockerfile')}]: "
        ).strip()
        if build_pack and build_pack in ['dockerfile', 'nixpacks']:
            config['build_pack'] = build_pack
        
        # Domains
        domains = input(
            f"Domains (comma-separated) [{config.get('domains', '')}]: "
        ).strip()
        if domains:
            config['domains'] = domains
        
        return config
    
    def _setup_docker_files(self):
        """Setup Docker files and health check"""
        self.stdout.write("\nSetting up Docker files...")
        
        # Create Docker files
        try:
            created_files = ensure_docker_files()
            
            for file_type, file_path in created_files.items():
                if file_type == 'dockerfile':
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Dockerfile created: {file_path}")
                    )
                elif file_type == 'dockerignore':
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ .dockerignore created: {file_path}")
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Could not create Docker files: {e}")
            )
