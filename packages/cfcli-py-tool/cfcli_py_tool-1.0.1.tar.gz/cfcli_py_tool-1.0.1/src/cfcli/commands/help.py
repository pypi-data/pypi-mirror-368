from rich.console import Console

console = Console()

def run(args) -> None:
    console.print(
        """
[bold underline cyan]cfcli - Codeforces CLI Tool[/bold underline cyan]

[bold]Usage:[/bold]
    cfcli [command] [options]

[bold]Commands:[/bold]
    help            Show this help message
    contests        List upcoming contests
    user <handle>   Get info about a Codeforces user
    problems        Search or explore problems
    submissions     Check submission results
    tracker         Manage your problem tracker
""")