import json
import requests
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

def run(args):
    if not args or len(args) != 1:
        console.print("[red]Usage: cf-cli log <contestId>/<problemLetter>[/red]")
        return
    
    contestAndProblem = args[0]
    
    try:
        contestId, problemLetter = contestAndProblem.split("/")
        contestId = int(contestId)
        problemLetter = problemLetter.upper()
    except ValueError:
        console.print("[red]Usage cf-cli log <contestId>/<problemLetter>.[/red] Refer to documentation for more information")
        return
    
    try:
        res = requests.get("https://codeforces.com/api/problemset.problems", timeout=10)
        data = res.json()
        
        if data["status"] != "OK":
            console.print("[red]Failed to fetch problemset from Codeforces. Try again later.[/red]")
            return
        
        problems = data["result"]["problems"]
        foundProblem = next(
            (p for p in problems if p["contestId"] == contestId and p["index"] == problemLetter),
            None
        )
        
        if not foundProblem:
            console.print(f"[red]Problem {contestId}/{problemLetter} not found in problemset. Please ensure this exists.[/red]")
            return
        
        dataDir = Path.home() / ".cfcli" / "data"
        dataDir.mkdir(parents=True, exist_ok=True)
        solvedPath = dataDir / "solved.json"
        
        if not solvedPath.exists(): #if the solved dir doesnt exists (ie this is the first time to the user ran this command)
            solvedList = []
        else:
            solvedList = json.loads(solvedPath.read_text())
            
        entry = {
            "contestId": contestId,
            "index": problemLetter,
            "name": foundProblem["name"],
            "tags": foundProblem.get("tags", []),
            "rating": foundProblem.get("rating", None),
            "timestamp": datetime.now().isoformat()
        }
        
        solvedList.append(entry)
        solvedPath.write_text(json.dumps(solvedList, indent=1))
        
        console.print(f"[green]Logged solved problem: {contestId}/{problemLetter} - {foundProblem['name']}[/green]")
    
    except Exception as e:
        console.print(f"[red]Failed to log solved problem: {e}[/red]")