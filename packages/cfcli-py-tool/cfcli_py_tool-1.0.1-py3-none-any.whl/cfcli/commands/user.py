import requests
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.table import Table
from rich.progress import Progress
from rich import box
import typing

console = Console()

RANK_COLOURS = {
    "newbie": "grey54",
    "pupil": "green",
    "specialist": "cyan",
    "expert": "blue",
    "candidate master": "magenta",
    "master": "yellow",
    "international master": "bright_yellow",
    "grandmaster": "red",
    "international grandmaster": "bright_red",
    "legendary grandmaster": "bold red",
}

def getColour(rank) -> str:
    """Displays the colour of the user based on the ranking table

    Args:
        rank (str): The rank of the user fetched from Codeforces Data

    Returns:
        str: The colour value of their given ranking
    """
    return RANK_COLOURS.get(rank.lower(), "white")

def run(args) -> None:
    if len(args) < 1:
        console.print("[red]Usage: cfcli user <handle>[/red]")
        return
    
    handle = args[0]
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        if data["status"] != "OK":
            console.print(f"[red]Error: {data.get('comment', 'Unknown error')}[/red]")
            return
        
        user = data["result"][0]
        
        handleText = Text(user["handle"], style=getColour(user.get("rank", "")))
        
        #make the table for the user display
        infoTable = Table(show_header=False, box=None, padding=(0, 1))
        
        #add the stuff
        infoTable.add_row("Username", handleText)
        infoTable.add_row("Country", user.get("country", "N/A"))
        infoTable.add_row("Name", f"{user.get('firstName', '')} {user.get('lastName', '')}".strip())
        infoTable.add_row("Max Rating", str(user.get("maxRating", "N/A")))
        infoTable.add_row("Contribution", str(user.get("contribution", 0)))
        
        photoUrl = user.get("titlePhoto")
        photoText = f"[link={photoUrl}][dim]View Title Photo[/dim][/link]"
        
        photoPanel = Panel(
            Align.center(photoText, vertical="middle"),
            title="Title Photo",
            padding=(1, 2),
            width=30
        )
        
        console.print(Columns([infoTable, photoPanel]))
        
    except requests.RequestException as e:
        console.print(f"[red]Request failed: [/red] {e}")