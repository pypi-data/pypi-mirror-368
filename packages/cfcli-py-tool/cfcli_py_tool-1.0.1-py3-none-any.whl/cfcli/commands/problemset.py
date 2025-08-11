import argparse
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def run(args) -> None:
    parser = argparse.ArgumentParser(prog="cf-cli problemset", add_help=False)
    parser.add_argument("-count", type=int, default=1000, help="Number of problems to display (default: 1000)")
    
    try:
        parsedArgs = parser.parse_args(args)
        count = parsedArgs.count
    except SystemExit:
        console.print("[red]Invalid arguments. Use:[/red] [yellow]cf-cli problemset -count <number>[/yellow]")
        return
    
    url = "https://codeforces.com/api/problemset.problems"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "OK":
            console.print(f"[red]API Error:[/red] {data.get('comment', 'Unknown Error')}")
            return
        
        problems = data["result"]["problems"][:count]
        
        table = Table(title=f"First {len(problems)} Codeforces Problems", show_lines=False)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="bold")
        table.add_column("Points", style="yellow", justify="right")
        table.add_column("Tags", style="dim")
        
        for problem in problems:
            problemId = f"{problem['contestId']}{problem['index']}"
            name = problem["name"]
            points = str(problem.get('points', problem.get('rating', 'N/A')))
            tags = ", ".join(problem.get("tags", []))
            table.add_row(problemId, name, points, tags)
            
        console.print(table)
        
    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch problems: [/red] {e}")