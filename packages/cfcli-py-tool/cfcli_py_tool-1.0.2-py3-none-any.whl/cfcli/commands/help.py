from rich.console import Console

console = Console()

def run(args) -> None:
    console.print(
        """
[bold underline cyan]cfcli - Codeforces CLI Tool[/bold underline cyan]

[bold]Usage:[/bold]
    cf-cli [command] [options]

[bold]Commands:[/bold]
    help            Show this help message
    contests        List upcoming contests
    user <handle>   Get info about a Codeforces user
    problemset      Search or explore problems
    streak          Display the current streak
    rating          Check their rating changes
    log             Log solved problems to add to streak
""")