"""CloudStack Orchestrator CLI."""

import asyncio
from typing import Optional
import sys
import subprocess
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .core import Orchestrator, Config, CloudProvider
from .core.config import GitHubConfig, KeycloakConfig
from .auth import GitHubDeviceFlow
from .auth.keycloak_idp import KeycloakIdentityProviderManager, IdentityProviderType
from .commands import module as module_commands

# Enable UTF-8 encoding for Windows to support emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"CloudStack Orchestrator v{__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="cso",
    help=f"CloudStack Orchestrator CLI v{__version__} - Manage your Kubernetes platform with ease",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """CloudStack Orchestrator CLI - Enterprise GitOps platform management."""
    if ctx.invoked_subcommand is None:
        # No command provided, show status (which includes everything)
        status(validate_only=False)


@app.command()
def setup(
    provider: CloudProvider = typer.Option(
        CloudProvider.LOCAL,
        "--provider", "-p",
        help="Cloud provider"
    ),
    cluster_name: str = typer.Option(
        "cso-cluster",
        "--cluster", "-c",
        help="Kubernetes cluster name"
    ),
    domain: str = typer.Option(
        None,
        "--domain", "-d",
        help="Platform domain (e.g., platform.example.com)"
    ),
    github_org: str = typer.Option(
        None,
        "--github-org", "-g",
        help="GitHub organization"
    ),
    github_token: Optional[str] = typer.Option(
        None,
        "--github-token",
        envvar="GITHUB_TOKEN",
        help="GitHub personal access token"
    ),
    region: Optional[str] = typer.Option(
        "us-east-1",
        "--region", "-r",
        help="Cloud region (for AWS/GCP/Azure)"
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive", "-n",
        help="Run without prompts"
    ),
    auth_interactive: bool = typer.Option(
        False,
        "--auth-interactive", "-a",
        help="Use interactive OAuth authentication"
    ),
):
    """Set up a new CloudStack Orchestrator instance."""
    console.print("[bold cyan]🚀 CloudStack Orchestrator Setup[/bold cyan]\n")
    
    # Interactive mode
    if not non_interactive:
        if not domain:
            domain = typer.prompt(
                "Platform domain",
                default="platform.local" if provider == CloudProvider.LOCAL else "platform.example.com"
            )
        
        if not github_org:
            github_org = typer.prompt("GitHub organization")
        
        # Check if repository is private
        repo_url = f"https://github.com/{github_org}/cloudstack-orchestrator"
        console.print(f"\n[dim]Checking repository: {repo_url}[/dim]")
        
        # GitHub authentication is required for private repositories
        if not github_token:
            console.print("\n[red]⚠️  GitHub authentication is required[/red]")
            console.print("[yellow]ArgoCD needs access to the cloudstack-orchestrator repository[/yellow]")
            console.print("\nAuthentication options:")
            console.print("  1. OAuth Device Flow (recommended - secure & easy)")
            console.print("  2. Personal Access Token (manual setup)")
            
            auth_choice = typer.prompt(
                "\nChoose authentication method",
                type=int,
                default=1,
                show_default=True,
                show_choices=False
            )
            
            if auth_choice not in [1, 2]:
                console.print("[red]Invalid choice. Please select 1 or 2.[/red]")
                raise typer.Exit(1)
            
            if auth_choice == 1:  # OAuth Device Flow
                console.print("\n[cyan]Starting GitHub OAuth device flow authentication...[/cyan]")
                
                # Ask for client ID
                console.print("[dim]Note: OAuth App must have device flow enabled[/dim]")
                oauth_client_id = typer.prompt(
                    "GitHub OAuth App Client ID", 
                    default="",
                    show_default=False
                )
                
                if not oauth_client_id:
                    console.print("[red]OAuth App Client ID is required for device flow[/red]")
                    raise typer.Exit(1)
                
                # Perform OAuth authentication
                github_auth = GitHubDeviceFlow(console, client_id=oauth_client_id)
                auth_result = github_auth.authenticate(scopes="repo")
                
                if auth_result:
                    github_token = auth_result.access_token
                    console.print(f"[green]✅ Authenticated successfully with '{auth_result.scope}' scope[/green]")
                else:
                    console.print("[red]❌ Authentication failed or was cancelled[/red]")
                    raise typer.Exit(1)
                        
            else:  # auth_choice == 2 - Personal Access Token
                console.print("\n[cyan]To create a Personal Access Token:[/cyan]")
                console.print("1. Go to https://github.com/settings/tokens/new")
                console.print("2. Select scope: 'repo' (Full control of private repositories)")
                console.print("3. Generate token and copy it\n")
                
                github_token = typer.prompt("GitHub personal access token", hide_input=True)
                
                if not github_token:
                    console.print("[red]❌ GitHub token is required[/red]")
                    raise typer.Exit(1)
                
                # Validate the token silently
                github_auth = GitHubDeviceFlow(console)
                github_auth.validate_token(github_token)
    
    # Validate required fields (only domain and github_org are truly required)
    if not all([domain, github_org]):
        console.print("[red]Error: Missing required configuration (domain and GitHub org)[/red]")
        raise typer.Exit(1)
    
    # Create configuration
    config = Config(
        provider=provider,
        region=region if provider != CloudProvider.LOCAL else None,
        cluster_name=cluster_name,
        domain=domain,
        github=GitHubConfig(
            org=github_org,
            token=github_token
        ),
        keycloak=KeycloakConfig()
    )
    
    # Show configuration
    console.print("\n[yellow]Configuration Summary:[/yellow]")
    table = Table(show_header=False, box=None)
    table.add_row("Provider:", config.provider.value)
    if config.region:
        table.add_row("Region:", config.region)
    table.add_row("Cluster:", config.cluster_name)
    table.add_row("Domain:", config.domain)
    table.add_row("GitHub Org:", config.github.org)
    console.print(table)
    
    if not non_interactive:
        if not typer.confirm("\nProceed with setup?", default=True):
            console.print("[yellow]⚠️ Setup cancelled[/yellow]")
            raise typer.Exit(0)
    
    # Run setup
    orchestrator = Orchestrator(config, console)
    
    try:
        results = asyncio.run(orchestrator.setup())
        
        console.print("\n[green]✅ Setup completed successfully![/green]")
        
        # Show access information
        if config.provider == CloudProvider.LOCAL:
            console.print("\n[cyan]🎯 Access your platform:[/cyan]")
            console.print(f"   ArgoCD:      http://localhost:30080  (GitOps Dashboard)")
            console.print(f"   Keycloak:    http://localhost:30081  (Identity Management)")
            console.print(f"   Platform:    http://localhost:30082  (OAuth2 Entry Point)")
            
            if results.get("local_access", {}).get("services"):
                console.print(f"\n[cyan]📱 Module UIs (behind Keycloak auth):[/cyan]")
                console.print(f"   VoiceFuse:   http://localhost:30083")
                console.print(f"   Langfuse:    http://localhost:30084")
            
            if "argocd" in results and results["argocd"].get("admin_password"):
                console.print(f"\n[dim]   ArgoCD login: admin / {results['argocd']['admin_password']}[/dim]")
                
            # Check if GitHub repo was configured
            if config.github.token:
                console.print("\n[green]✅ GitHub repository access configured[/green]")
            else:
                console.print("\n[yellow]⚠️  GitHub repository not configured[/yellow]")
                console.print("[dim]   ArgoCD won't be able to sync from private repos[/dim]")
                console.print("[dim]   Run 'cso auth' after setup to configure[/dim]")
        else:
            console.print("\n[cyan]Access Information:[/cyan]")
            info_table = Table(show_header=False, box=None)
            info_table.add_row("ArgoCD URL:", f"https://argocd.{config.domain}")
            info_table.add_row("Keycloak URL:", f"https://keycloak.{config.domain}")
            if "argocd" in results and results["argocd"].get("admin_password"):
                info_table.add_row("ArgoCD Password:", results["argocd"]["admin_password"])
            console.print(info_table)
            
            console.print("\n[blue]📌 Next steps:[/blue]")
            console.print("1. Configure DNS for your domain")
            console.print("2. Access ArgoCD to monitor deployments")
            console.print("3. Set up GitHub/Google OAuth in Keycloak (optional)")
        
    except Exception as e:
        console.print(f"\n[red]❌ Setup failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    validate_only: bool = typer.Option(
        False,
        "--validate",
        "-v",
        help="Only validate prerequisites without checking deployment status"
    ),
):
    """Check CloudStack Orchestrator status and validate prerequisites."""
    console.print(f"[bold cyan]📊 CloudStack Orchestrator v{__version__}[/bold cyan]\n")
    
    if validate_only:
        return validate_prerequisites()
    
    # Try to load existing config
    # For now, we'll need to pass config or load from a file
    # This is a simplified version
    try:
        # Create a minimal config for status check
        config = Config(
            provider=CloudProvider.LOCAL,
            cluster_name="unknown",
            domain="unknown",
            github=GitHubConfig(org="unknown")
        )
        
        orchestrator = Orchestrator(config, console)
        status = asyncio.run(orchestrator.get_status())
        
        # Kubernetes status
        k8s_status = "[green]Connected[/green]" if status["kubernetes"]["connected"] else "[red]Not connected[/red]"
        k8s_context = status["kubernetes"].get("context", "Unknown")
        console.print(f"☸️  Kubernetes: {k8s_status}")
        console.print(f"   Context: [cyan]{k8s_context}[/cyan]")
        
        # ArgoCD status
        argo_status = "[green]Installed[/green]" if status["argocd"]["installed"] else "[red]Not installed[/red]"
        argo_url = "http://localhost:30080" if status["argocd"]["installed"] else ""
        console.print(f"\n🚀 ArgoCD: {argo_status}")
        if argo_url:
            console.print(f"   URL: [link={argo_url}]{argo_url}[/link]")
            # Get ArgoCD password if available
            argo_password = status.get("argocd", {}).get("admin_password")
            if argo_password:
                console.print(f"   Login: admin / {argo_password}")
        
        # Platform status
        platform_status = "[green]Deployed[/green]" if status["platform"]["deployed"] else "[red]Not deployed[/red]"
        console.print(f"\n📦 Platform: {platform_status}")
        
        # Keycloak status if platform is deployed
        keycloak_info = status.get("keycloak", {})
        if keycloak_info.get("installed"):
            console.print(f"\n🔐 Keycloak: [green]Running[/green]")
            keycloak_url = "http://localhost:30081" if config.provider == CloudProvider.LOCAL else f"https://keycloak.{config.domain}"
            console.print(f"   URL: [link={keycloak_url}]{keycloak_url}[/link]")
            keycloak_password = keycloak_info.get("admin_password")
            if keycloak_password:
                console.print(f"   Login: admin / {keycloak_password}")
        
        # Repository status (local vs remote)
        repo_type = "Local" if config.provider == CloudProvider.LOCAL else "Remote"
        repo_connected = status.get("github", {}).get("connected")
        if repo_type == "Local":
            console.print(f"\n📁 Repository: [cyan]Local Development[/cyan]")
            console.print(f"   [dim]No external repository authentication needed[/dim]")
        else:
            repo_status = "[green]Connected[/green]" if repo_connected else "[yellow]Not connected[/yellow]"
            console.print(f"\n🔗 Repository: {repo_status}")
            if not repo_connected:
                console.print(f"   [dim]Run 'cso auth' to connect to private repositories[/dim]")
        
        # Check ArgoCD sync status if available
        if status.get("argocd_apps"):
            console.print("\n[yellow]ArgoCD Applications:[/yellow]")
            for app_name, app_status in status["argocd_apps"].items():
                sync = app_status.get("sync", "Unknown")
                health = app_status.get("health", "Unknown")
                
                # Color code the statuses
                if sync == "Synced":
                    sync_display = f"[green]{sync}[/green]"
                elif sync == "OutOfSync":
                    sync_display = f"[yellow]{sync}[/yellow]"
                else:
                    sync_display = f"[red]{sync}[/red]"
                    
                if health == "Healthy":
                    health_display = f"[green]{health}[/green]"
                elif health == "Progressing":
                    health_display = f"[yellow]{health}[/yellow]"
                else:
                    health_display = f"[red]{health}[/red]"
                
                console.print(f"  {app_name}: Sync: {sync_display}, Health: {health_display}")
        
    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def teardown(
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Force teardown without confirmation"
    ),
):
    """Teardown CloudStack Orchestrator platform."""
    console.print("[bold red]⚠️  CloudStack Orchestrator Teardown[/bold red]\n")
    console.print("[yellow]This will remove all CSO components from your cluster:[/yellow]")
    console.print("  • ArgoCD and all applications")
    console.print("  • Istio service mesh")
    console.print("  • Keycloak authentication")
    console.print("  • All platform namespaces")
    console.print("  • Custom Resource Definitions (CRDs)\n")
    
    if not force:
        console.print("[red]This action cannot be undone![/red]")
        console.print("Use --force to skip this confirmation.\n")
        raise typer.Exit(1)
    
    # Create config for orchestrator
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name="unknown",
        domain="unknown",
        github=GitHubConfig(org="unknown")
    )
    
    orchestrator = Orchestrator(config, console)
    
    try:
        result = asyncio.run(orchestrator.teardown())
        
        if result["success"]:
            console.print("\n[green]✅ Teardown completed successfully![/green]")
            console.print("[dim]All CSO components have been removed from the cluster.[/dim]")
        else:
            console.print(f"\n[red]❌ Teardown failed: {result.get('error')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"\n[red]❌ Teardown error: {e}[/red]")
        raise typer.Exit(1)


def validate_prerequisites():
    """Validate prerequisites for CloudStack Orchestrator."""
    console.print("[bold cyan]🔍 Validating Prerequisites[/bold cyan]\n")
    
    # Check for required commands
    commands = ["kubectl", "helm", "git"]
    all_good = True
    
    for cmd in commands:
        import shutil
        if shutil.which(cmd):
            console.print(f"✅ {cmd}")
        else:
            console.print(f"❌ {cmd} not found")
            all_good = False
    
    # Check Kubernetes connection
    try:
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("✅ Kubernetes cluster connected")
        else:
            console.print("❌ Cannot connect to Kubernetes cluster")
            all_good = False
    except:
        console.print("❌ kubectl command failed")
        all_good = False
    
    if all_good:
        console.print("\n[green]All prerequisites satisfied! ✨[/green]")
    else:
        console.print("\n[red]❌ Some prerequisites are missing. Please install them first.[/red]")
        raise typer.Exit(1)


# Secrets management commands
secrets_app = typer.Typer(help="Manage CloudStack secrets")
app.add_typer(secrets_app, name="secrets")


@secrets_app.command("list")
def secrets_list():
    """List all managed secrets."""
    console.print("[yellow]Secret management coming soon![/yellow]")


@secrets_app.command("rotate")
def secrets_rotate(
    secret_name: str = typer.Argument(..., help="Secret to rotate")
):
    """Rotate a specific secret."""
    console.print(f"[yellow]Rotating {secret_name} coming soon![/yellow]")


@app.command()
def auth(
    github_org: str = typer.Option(
        None,
        "--github-org", "-g",
        help="GitHub organization"
    ),
    token: str = typer.Option(
        None,
        "--token", "-t",
        help="GitHub personal access token"
    ),
):
    """Configure GitHub authentication for ArgoCD repository access."""
    console.print("[bold cyan]🔐 GitHub Authentication[/bold cyan]\n")
    
    # First check if ArgoCD is installed
    console.print("[yellow]Checking platform status...[/yellow]")
    try:
        result = subprocess.run(
            ["kubectl", "get", "namespace", "argocd"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            console.print("\n[red]❌ ArgoCD is not installed![/red]")
            console.print("[yellow]Please run 'cso setup' first to install the platform.[/yellow]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error checking platform status: {e}[/red]")
        raise typer.Exit(1)
    
    console.print("[green]✅ ArgoCD found[/green]\n")
    
    # Get GitHub org if not provided
    if not github_org:
        github_org = typer.prompt("GitHub organization", default="killerapp")
    
    # Get token if not provided
    if not token:
        console.print("[cyan]To create a Personal Access Token:[/cyan]")
        console.print("1. Go to https://github.com/settings/tokens/new")
        console.print("2. Select scope: 'repo' (Full control of private repositories)")
        console.print("3. Generate token and copy it\n")
        
        token = typer.prompt("GitHub personal access token", hide_input=True)
        
        if not token:
            console.print("[red]❌ Token is required[/red]")
            raise typer.Exit(1)
    
    # Validate token silently
    github_auth = GitHubDeviceFlow(console)
    if not github_auth.validate_token(token):
        console.print("[yellow]⚠️  Could not validate token[/yellow]")
    
    # Create minimal config
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name="unknown",
        domain="unknown",
        github=GitHubConfig(
            org=github_org,
            token=token
        )
    )
    
    # Configure ArgoCD
    orchestrator = Orchestrator(config, console)
    
    try:
        result = asyncio.run(orchestrator.configure_argocd_repo())
        if result.get("created") or result.get("updated"):
            # Trigger ArgoCD refresh
            subprocess.run([
                "kubectl", "-n", "argocd", "patch", "app", 
                "cloudstack-platform", "--type", "merge", 
                "-p", '{"metadata": {"annotations": {"argocd.argoproj.io/refresh": "normal"}}}'
            ], capture_output=True)
            
            console.print(f"\n[green]✅ Repository configured for {result.get('url')}[/green]")
            console.print("[cyan]Check ArgoCD UI at http://localhost:30080[/cyan]")
        else:
            console.print(f"\n[red]❌ Failed: {result.get('error')}[/red]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")


@app.command("repos")
def configure_repositories():
    """Configure ArgoCD Helm repositories for platform dependencies."""
    console.print("[bold cyan]🔧 Configuring ArgoCD Repositories[/bold cyan]\n")
    
    # Create minimal config for orchestrator
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name="unknown",
        domain="unknown",
        github=GitHubConfig(org="killerapp")
    )
    
    orchestrator = Orchestrator(config, console)
    
    try:
        result = asyncio.run(orchestrator.configure_argocd_helm_repos())
        
        console.print(f"\n[green]✅ Repository configuration complete![/green]")
        console.print(f"Configured {len(result['configured_repositories'])} of {result['total_repositories']} repositories")
        
        if result['configured_repositories']:
            console.print("\n[cyan]Configured repositories:[/cyan]")
            for repo in result['configured_repositories']:
                console.print(f"  • {repo}")
                
            console.print("\n[yellow]Note:[/yellow] ArgoCD repo server was restarted to pick up new repositories")
            console.print("[cyan]Refresh your platform applications in ArgoCD UI[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Repository configuration failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="idp")
def identity_provider(
    provider: IdentityProviderType = typer.Argument(
        ...,
        help="Identity provider to configure (github, google, microsoft)"
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive", "-n",
        help="Use existing secret configuration without prompting"
    ),
):
    """Configure identity providers for Keycloak SSO."""
    console.print(f"[bold cyan]🔐 Identity Provider Configuration[/bold cyan]\n")
    
    # Check if platform is installed
    console.print("[yellow]Checking platform status...[/yellow]")
    try:
        result = subprocess.run(
            ["kubectl", "get", "namespace", "platform"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            console.print("\n[red]❌ Platform namespace not found![/red]")
            console.print("[yellow]Please run 'cso setup' first to install the platform.[/yellow]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error checking platform status: {e}[/red]")
        raise typer.Exit(1)
    
    # Configure the identity provider
    manager = KeycloakIdentityProviderManager(console)
    success = manager.configure_provider(provider, interactive=not non_interactive)
    
    if success:
        console.print(f"\n[green]✅ {provider.value.title()} identity provider configured successfully![/green]")
        
        # Additional instructions for making users admins
        console.print(f"\n[cyan]📝 To grant admin access to a {provider.value} user:[/cyan]")
        console.print(f"1. Have the user log in via {provider.value.title()} first")
        console.print(f"2. Access Keycloak Admin Console: http://localhost:30081")
        console.print(f"3. Login as admin/admin123")
        console.print(f"4. Select 'platform' realm (top-left dropdown)")
        console.print(f"5. Go to Users → View all users")
        console.print(f"6. Click on the {provider.value} user")
        console.print(f"7. Go to 'Role Mappings' tab")
        console.print(f"8. Assign 'platform-admin' role")
    else:
        console.print(f"\n[red]❌ Failed to configure {provider.value} identity provider[/red]")
        raise typer.Exit(1)


# Module management commands - imported from cli.module
# The module commands are now in a separate file for better organization
# They provide full module management capabilities:
# - list: Show all deployed modules
# - deploy: Deploy a new module
# - status: Check module status
# - logs: View module logs
# - scale: Scale module replicas
# - rollback: Rollback to previous version
# - delete: Remove a module
# Register module commands
app.add_typer(module_commands.app, name="module")


if __name__ == "__main__":
    app()