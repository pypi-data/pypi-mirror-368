"""
Django management command to setup infrastructure in Coolify
"""
from django.core.management.base import BaseCommand, CommandError

from django_coolify.client import CoolifyClient, CoolifyAPIError
from django_coolify.config import CoolifyConfig


class Command(BaseCommand):
    help = 'Setup infrastructure in Coolify (create project and application)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--server-uuid',
            type=str,
            help='Specific server UUID to deploy to'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing resources'
        )
        parser.add_argument(
            '--list-servers',
            action='store_true',
            help='List available servers and exit'
        )
    
    def handle(self, *args, **options):
        config_manager = CoolifyConfig()
        
        # Check if config exists
        if not config_manager.exists():
            raise CommandError(
                "Configuration file not found. Run 'python manage.py generate-config' first."
            )
        
        # Load configuration
        try:
            config = config_manager.load()
            self.stdout.write(f"Loaded config: {config}")
        except ValueError as e:
            raise CommandError(f"Error loading configuration: {e}")
        
        # Validate required configuration
        required_fields = ['coolify_url', 'api_token', 'project_name', 'app_name']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise CommandError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Update your coolify.json file or regenerate it."
            )
        
        # Initialize Coolify client
        try:
            client = CoolifyClient(config['coolify_url'], config['api_token'])
        except Exception as e:
            raise CommandError(f"Error initializing Coolify client: {e}")
        
        # List servers if requested
        if options['list_servers']:
            self._list_servers(client)
            return
        
        # Setup infrastructure
        try:
            self._setup_infrastructure(client, config, config_manager, options)
        except CoolifyAPIError as e:
            raise CommandError(f"Coolify API error: {e}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")
    
    def _list_servers(self, client):
        """List available servers"""
        try:
            servers = client.list_servers()
            
            if not servers:
                self.stdout.write(self.style.WARNING("No servers found."))
                return
            
            self.stdout.write(self.style.SUCCESS("Available servers:"))
            for server in servers:
                self.stdout.write(f"  UUID: {server.get('uuid', 'N/A')}")
                self.stdout.write(f"  Name: {server.get('name', 'N/A')}")
                self.stdout.write(f"  IP: {server.get('ip', 'N/A')}")
                self.stdout.write("")
                
        except CoolifyAPIError as e:
            raise CommandError(f"Error listing servers: {e}")
    
    def _setup_infrastructure(self, client, config, config_manager, options):
        """Setup project and application in Coolify"""
        
        # Step 1: Create or find project
        project_uuid = self._setup_project(client, config, options['force'])
        config['project_uuid'] = project_uuid
        
        # Step 1.5: Check environments in the project
        try:
            environments = client.list_environments(project_uuid)
            self.stdout.write(f"Available environments: {environments}")
        except Exception as e:
            self.stdout.write(f"Could not list environments: {e}")
        
        # Step 2: Get server UUID
        server_uuid = self._get_server_uuid(client, config, options.get('server_uuid'))
        config['server_uuid'] = server_uuid
        
        # Step 3: Create application
        app_uuid = self._setup_application(client, config, options['force'])
        config['app_uuid'] = app_uuid
        
        # Step 4: Save updated configuration
        config_manager.save(config)
        
        self.stdout.write(self.style.SUCCESS("Infrastructure setup completed!"))
        self.stdout.write(f"Project UUID: {project_uuid}")
        self.stdout.write(f"Application UUID: {app_uuid}")
        self.stdout.write(f"Server UUID: {server_uuid}")
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Review the application settings in Coolify dashboard")
        self.stdout.write("2. Run 'python manage.py deploy' to deploy your application")
    
    def _setup_project(self, client, config, force):
        """Create or find project"""
        project_name = config['project_name']
        
        # Check if project UUID is already in config
        if config.get('project_uuid') and not force:
            try:
                project = client.get_project(config['project_uuid'])
                self.stdout.write(f"Using existing project: {project.get('name', 'N/A')}")
                return config['project_uuid']
            except CoolifyAPIError:
                # Project doesn't exist, create new one
                pass
        
        # Look for existing project by name
        if not force:
            try:
                projects = client.list_projects()
                for project in projects:
                    if project.get('name') == project_name:
                        self.stdout.write(f"Found existing project: {project_name}")
                        return project['uuid']
            except CoolifyAPIError:
                pass
        
        # Create new project
        self.stdout.write(f"Creating project: {project_name}")
        try:
            project = client.create_project(
                name=project_name,
                description=f"Django project: {project_name}"
            )
            self.stdout.write(self.style.SUCCESS(f"Project created with UUID: {project['uuid']}"))
            return project['uuid']
        except CoolifyAPIError as e:
            raise CommandError(f"Error creating project: {e}")
    
    def _get_server_uuid(self, client, config, server_uuid_arg):
        """Get server UUID"""
        # Use provided server UUID
        if server_uuid_arg:
            return server_uuid_arg
        
        # Use server UUID from config
        if config.get('server_uuid'):
            return config['server_uuid']
        
        # Auto-select first available server
        try:
            servers = client.list_servers()
            if not servers:
                raise CommandError("No servers available. Please add a server to your Coolify instance.")
            
            server = servers[0]
            server_uuid = server['uuid']
            self.stdout.write(f"Auto-selected server: {server.get('name', 'N/A')} ({server_uuid})")
            return server_uuid
            
        except CoolifyAPIError as e:
            raise CommandError(f"Error getting servers: {e}")
    
    def _setup_application(self, client, config, force):
        """Create application"""
        app_name = config['app_name']
        
        # Check if app UUID is already in config
        if config.get('app_uuid') and not force:
            try:
                app = client.get_application(config['app_uuid'])
                self.stdout.write(f"Using existing application: {app.get('name', 'N/A')}")
                return config['app_uuid']
            except CoolifyAPIError:
                # App doesn't exist, create new one
                pass
        
        # Validate git repository
        if not config.get('git_repository'):
            raise CommandError("Git repository URL is required. Update your configuration.")
        
        # Create application
        self.stdout.write(f"Creating application: {app_name}")
        
        app_data = {
            "project_uuid": config['project_uuid'],
            "server_uuid": config['server_uuid'],
            "name": app_name,
            "git_repository": config['git_repository'],
            "git_branch": config.get('git_branch', 'main'),
            "build_pack": config.get('build_pack', 'dockerfile'),
            "environment_name": config.get('environment_name', 'production'),
            "ports_exposes": "8000",  # Default Django port
        }
        
        # Debug output
        self.stdout.write(f"App data: {app_data}")
        
        # Add optional configurations
        if config.get('domains'):
            app_data['domains'] = config['domains']
        
        if config.get('health_check_enabled'):
            app_data['health_check_enabled'] = True
            if config.get('health_check_path'):
                app_data['health_check_path'] = config['health_check_path']
        
        try:
            app = client.create_public_application(**app_data)
            self.stdout.write(self.style.SUCCESS(f"Application created with UUID: {app['uuid']}"))
            return app['uuid']
        except CoolifyAPIError as e:
            raise CommandError(f"Error creating application: {e}")
