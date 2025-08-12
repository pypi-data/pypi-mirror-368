"""
Command-line interface for HTTP Proxy CLI.
"""

import sys
import uvicorn
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .proxy import SimpleProxy
from .logger import ProxyLogger

console = Console()


@click.command()
@click.option(
    "--target",
    "-t",
    required=True,
    help="Target URL to proxy requests to",
    type=str,
)
@click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    help="Host to bind the proxy server to",
    type=str,
)
@click.option(
    "--port",
    "-p",
    default=8000,
    help="Port to bind the proxy server to",
    type=int,
)
@click.option(
    "--log-file",
    "-l",
    default="logs/proxy_requests.log",
    help="Log file path for requests and responses",
    type=str,
)
@click.option(
    "--log-level",
    "-v",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
@click.option(
    "--log-format",
    "-f",
    default="json",
    help="Log format (json or plain, default: json)",
    type=click.Choice(["json", "plain"]),
)
@click.option(
    "--no-console",
    is_flag=True,
    help="Disable console logging output",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
@click.option(
    "--workers",
    "-w",
    default=1,
    help="Number of worker processes",
    type=int,
)
@click.version_option(version="0.1.0", prog_name="http-proxy")
def main(target, host, port, log_file, log_level, log_format, no_console, reload, workers):
    """
    HTTP Proxy CLI - A simple HTTP proxy for intercepting and logging requests.

    Examples:
        http-proxy --target https://api.example.com
        http-proxy -t https://httpbin.org -p 8080 -l my_logs.json
        http-proxy --target https://jsonplaceholder.typicode.com --log-level DEBUG
    """
    
    # Validate target URL
    if not target.startswith(("http://", "https://")):
        console.print(f"[red]Error: Target URL must start with http:// or https://[/red]")
        sys.exit(1)

    # Create logger
    logger = ProxyLogger(
        log_file=log_file,
        log_level=log_level,
        log_format=log_format,
        console_output=not no_console,
    )

    # Create proxy
    proxy = SimpleProxy(target, logger)
    app = proxy.create_app()

    # Display startup info
    console.print(Panel.fit(
        f"[bold green]HTTP Proxy CLI v0.1.0[/bold green]\n\n"
        f"[blue]Target:[/blue] {target}\n"
        f"[blue]Proxy:[/blue] http://{host}:{port}\n"
        f"[blue]Logs:[/blue] {log_file}\n"
        f"[blue]Format:[/blue] {log_format}\n"
        f"[blue]Level:[/blue] {log_level}",
        title="Configuration",
        border_style="green"
    ))

    # Display usage examples
    console.print("\n[bold yellow]Usage Examples:[/bold yellow]")
    examples = Table(show_header=False, box=None)
    examples.add_row("GET Request:", f"curl http://{host}:{port}/api/users")
    examples.add_row("POST Request:", f'curl -X POST http://{host}:{port}/api/users -d \'{{"name": "John"}}\'')
    examples.add_row("Query Params:", f"curl http://{host}:{port}/api/search?q=test\u0026limit=10")
    examples.add_row("File Upload:", f"curl -X POST http://{host}:{port}/upload -F 'file=@document.pdf'")
    console.print(examples)

    console.print(f"\n[green]Starting proxy server...[/green]")
    console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        # Start server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level.lower(),
            reload=reload,
            workers=workers if not reload else 1,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Proxy server stopped.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


@click.group()
def cli():
    """HTTP Proxy CLI commands."""
    pass


@cli.command()
@click.option("--log-file", default="logs/proxy_requests.log", help="Log file to analyze")
def stats(log_file):
    """Display statistics about logged requests."""
    from .logger import ProxyLogger
    
    logger = ProxyLogger(log_file=log_file, console_output=False)
    stats = logger.get_stats()
    
    console.print(Panel.fit(
        f"[bold blue]Proxy Statistics[/bold blue]\n\n"
        f"[green]Requests:[/green] {stats['requests']}\n"
        f"[green]Responses:[/green] {stats['responses']}\n"
        f"[red]Errors:[/red] {stats['errors']}\n"
        f"[yellow]Log Size:[/yellow] {stats['file_size']} bytes",
        title="Statistics",
        border_style="blue"
    ))


@cli.command()
@click.option("--target", required=True, help="Target URL to test")
@click.option("--path", default="/", help="Path to test")
def test(target, path):
    """Test connectivity to target URL."""
    import httpx
    
    url = f"{target.rstrip('/')}{path}"
    
    try:
        response = httpx.get(url, timeout=10)
        console.print(Panel.fit(
            f"[green]✓ Connection successful[/green]\n\n"
            f"[blue]URL:[/blue] {url}\n"
            f"[blue]Status:[/blue] {response.status_code}\n"
            f"[blue]Size:[/blue] {len(response.content)} bytes",
            title="Connection Test",
            border_style="green"
        ))
    except Exception as e:
        console.print(Panel.fit(
            f"[red]✗ Connection failed[/red]\n\n"
            f"[blue]URL:[/blue] {url}\n"
            f"[red]Error:[/red] {str(e)}",
            title="Connection Test",
            border_style="red"
        ))


if __name__ == "__main__":
    main()