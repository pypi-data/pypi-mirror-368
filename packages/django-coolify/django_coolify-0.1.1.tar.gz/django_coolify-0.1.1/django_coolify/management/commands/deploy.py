"""
Django management command to deploy application to Coolify
"""
import subprocess
import sys

from django.core.management.base import BaseCommand, CommandError

from django_coolify.client import CoolifyClient, CoolifyAPIError
from django_coolify.config import CoolifyConfig


class Command(BaseCommand):
    help = 'Deploy application to Coolify (requires committed code)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force rebuild without cache'
        )
        parser.add_argument(
            '--skip-git-check',
            action='store_true',
            help='Skip git status checks (not recommended)'
        )
        parser.add_argument(
            '--tag',
            type=str,
            help='Deploy specific tag instead of branch'
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
        except ValueError as e:
            raise CommandError(f"Error loading configuration: {e}")
        
        # Validate configuration
        required_fields = ['coolify_url', 'api_token', 'app_uuid']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise CommandError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Run 'python manage.py setup-infra' first."
            )
        
        # Check Git status before deployment
        if not options['skip_git_check'] and not options['tag']:
            self._check_git_status_and_require_clean_state()
        
        # Initialize Coolify client
        try:
            client = CoolifyClient(config['coolify_url'], config['api_token'])
        except Exception as e:
            raise CommandError(f"Error initializing Coolify client: {e}")
        
        # Deploy application
        try:
            self._deploy_application(client, config, options)
        except CoolifyAPIError as e:
            raise CommandError(f"Coolify API error: {e}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")
    
    def _deploy_application(self, client, config, options):
        """Deploy the application"""
        
        # Trigger deployment (no auto-push, code should already be committed)
        app_uuid = config['app_uuid']
        
        if options['tag']:
            self.stdout.write(f"Deploying tag: {options['tag']}")
            deployment = client.deploy_application(options['tag'], force=options['force'])
        else:
            self.stdout.write(f"Deploying application: {app_uuid}")
            deployment = client.deploy_application(app_uuid, force=options['force'])
        
        # Display deployment information
        deployments = deployment.get('deployments', [])
        if deployments:
            for deploy in deployments:
                self.stdout.write(self.style.SUCCESS(f"Deployment started!"))
                self.stdout.write(f"  Message: {deploy.get('message', 'N/A')}")
                self.stdout.write(f"  Resource UUID: {deploy.get('resource_uuid', 'N/A')}")
                self.stdout.write(f"  Deployment UUID: {deploy.get('deployment_uuid', 'N/A')}")
        else:
            self.stdout.write(self.style.SUCCESS("Deployment triggered successfully!"))
        
        # Show next steps
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Monitor deployment progress in Coolify dashboard")
        self.stdout.write(f"2. Visit: {config['coolify_url']}/project/{config.get('project_uuid', '')}")
        
        if config.get('domains'):
            domains = config['domains'].split(',')
            self.stdout.write("3. Access your application at:")
            for domain in domains:
                domain = domain.strip()
                if domain:
                    if not domain.startswith('http'):
                        domain = f"https://{domain}"
                    self.stdout.write(f"   {domain}")
    
    def _check_git_status_and_require_clean_state(self):
        """Check git repository status and require clean state"""
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            
            # Check if there are uncommitted changes
            if repo.is_dirty():
                raise CommandError(
                    "You have uncommitted changes in your repository.\n"
                    "Please review and commit your changes before deploying:\n"
                    "1. Run 'git status' to see changes\n"
                    "2. Run 'git add .' to stage changes\n"
                    "3. Run 'git commit -m \"Your commit message\"' to commit\n"
                    "4. Run 'git push' to push to remote\n"
                    "5. Then run deploy again"
                )
            
            # Check if there are untracked files
            untracked_files = repo.untracked_files
            if untracked_files:
                # Filter out common files that don't need to be committed
                important_untracked = [
                    f for f in untracked_files 
                    if not f.startswith('.') and not f.endswith('.pyc') 
                    and f not in ['coolify.json', '__pycache__']
                ]
                
                if important_untracked:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warning: Untracked files detected: {', '.join(important_untracked[:5])}\n"
                            "Consider adding them to git if they're important for deployment."
                        )
                    )
            
            # Check if local branch is ahead of remote
            try:
                origin = repo.remotes.origin
                origin.fetch()  # Fetch latest from remote
                
                local_commit = repo.head.commit
                try:
                    remote_commit = origin.refs[repo.active_branch.name].commit
                    
                    if local_commit != remote_commit:
                        # Check if local is ahead
                        commits_ahead = list(repo.iter_commits(f'origin/{repo.active_branch.name}..HEAD'))
                        if commits_ahead:
                            raise CommandError(
                                f"Your local branch is {len(commits_ahead)} commit(s) ahead of remote.\n"
                                "Please push your changes before deploying:\n"
                                f"Run 'git push origin {repo.active_branch.name}'"
                            )
                        else:
                            # Local is behind remote
                            self.stdout.write(
                                self.style.WARNING(
                                    "Your local branch is behind remote. Consider pulling latest changes."
                                )
                            )
                except:
                    # Remote branch doesn't exist, probably first push
                    self.stdout.write(
                        self.style.WARNING(
                            f"Remote branch '{repo.active_branch.name}' doesn't exist. "
                            "You may need to push this branch first."
                        )
                    )
            except:
                # No remote or fetch failed, continue anyway
                pass
                
        except ImportError:
            # Fallback to subprocess if GitPython is not available
            self._check_git_status_subprocess()
        except git.exc.GitCommandError as e:
            raise CommandError(f"Git error: {e}")
        except Exception as e:
            # Not a git repository or other git error
            raise CommandError(
                f"Could not check git status: {e}. "
                "Make sure your code is committed and pushed to the remote repository."
            )
    
    def _check_git_status_subprocess(self):
        """Check git status using subprocess (fallback method)"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                raise CommandError(
                    "You have uncommitted changes in your repository.\n"
                    "Please review and commit your changes before deploying:\n"
                    "1. Run 'git status' to see changes\n"
                    "2. Run 'git add .' to stage changes\n"
                    "3. Run 'git commit -m \"Your commit message\"' to commit\n"
                    "4. Run 'git push' to push to remote\n"
                    "5. Then run deploy again"
                )
                
        except subprocess.CalledProcessError as e:
            if 'not a git repository' in e.stderr:
                raise CommandError(
                    "Not a git repository. Make sure your code is in a git repository "
                    "and pushed to the remote before deploying."
                )
            else:
                raise CommandError(f"Git command failed: {e}")
        except FileNotFoundError:
            raise CommandError(
                "Git command not found. Make sure git is installed and your code "
                "is committed and pushed to the remote repository."
            )
