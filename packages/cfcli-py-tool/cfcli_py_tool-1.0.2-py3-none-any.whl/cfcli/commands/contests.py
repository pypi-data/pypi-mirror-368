from rich.console import Console
from rich.table import Table
import requests
from datetime import datetime

console = Console()

def run(args) -> None:
    try:
        response = requests.get("https://codeforces.com/api/contest.list", timeout=10)
        if response.status_code != 200 or not response.text:
            console.print("[red]Response error — status 404 or empty body.[/red]")
            return
        
        data = response.json()
        if data["status"] != "OK":
            console.print("[red]Invalid API status.[/red]")
            return
        
        contests = data["result"]
        table = Table(title="Upcoming Codeforces Contests")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Start in (sec)", style="magenta")
        
        for contest in contests:
            if contest["phase"] != "BEFORE":
                break
            table.add_row(str(contest["id"]), contest["name"], str(-contest["relativeTimeSeconds"]))

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error fetching or processing contests: {e}[/red]")