import json
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel

console = Console()

def run(args):
    dataPath = Path.home() / ".cfcli" / "data" / "solved.json"
    
    if not dataPath.exists():
        console.print("[red]No solved problems logged yet. Please log them with `cf-cli log <contestId>/<problemLetter>[/red]")
        return
    
    try:
        solvedList = json.loads(dataPath.read_text())
        if not solvedList:
            console.print("[yellow]No problems found in log yet.[/yellow]") #this might be the same action as line 12-14 since they both dont have the logs
            return
        
        dates = sorted(set(
            datetime.fromisoformat(entry["timestamp"]).date()
            for entry in solvedList
        ))
        
        # streak stuff
        maxStreak = 0
        currentStreak = 0
        streak = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + timedelta(days=1):
                streak += 1
            elif dates[i] != dates[i-1]:
                streak = 1
                
            maxStreak = max(maxStreak, streak)
            
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        if dates[-1] == today: # latest
            currentStreak = 1
            for i in range(len(dates)-2, -1, -1):
                if dates[i] == yesterday - timedelta(days=len(dates)-2 - i):
                    currentStreak = 1
                else:
                    break
                
        console.print(
            Panel.fit(
                f"[bold cyan]Streak Stats[/bold cyan]\n"
                f"[green]Current Streak[/green]: {currentStreak}\n"
                f"[yellow]Max Streak[/yellow]: {maxStreak}\n"
                f"[blue]Days Logged[/blue]: {len(dates)}"
            )
        )
        
    except Exception as e:
        console.print("[red]Error reading streak data: {e}[/red]")