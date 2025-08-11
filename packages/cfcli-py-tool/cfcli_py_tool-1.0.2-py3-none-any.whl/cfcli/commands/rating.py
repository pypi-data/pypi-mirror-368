import requests
from rich.table import Table
from rich.console import Console
from matplotlib import pyplot as plt
from datetime import datetime

console = Console()


def run(args) -> None:
    if len(args) < 1:
        console.print("[red]Error: Please provide a Codeforces username.[/red]")
        return

    handle = args[0]
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = requests.get(url)

    if response.status_code != 200:
        console.print(f"[red]Failed to fetch data. Status code: {response.status_code}[/red]")
        return

    data = response.json()
    if data["status"] != "OK":
        console.print(f"[red]Error: {data['comment']}[/red]")
        return

    ratingChanges = data["result"]

    if not ratingChanges:
        console.print(f"[yellow]{handle} has no rating history.[/yellow]")
        return

    table = Table(title=f"{handle}'s Rating History")

    table.add_column("Contest Name", style="bold")
    table.add_column("Rank", justify="right")
    table.add_column("Old Rating", justify="right")
    table.add_column("New Rating", justify="right")
    table.add_column("Delta", justify="right")

    x = []
    y = []

    for change in ratingChanges:
        contestName = change["contestName"]
        rank = str(change["rank"])
        oldRating = change["oldRating"]
        newRating = change["newRating"]
        delta = newRating - oldRating
        deltaStr = f"[green]+{delta}[/green]" if delta >= 0 else f"[red]{delta}[/red]"

        table.add_row(contestName, rank, str(oldRating), str(newRating), deltaStr)

        x.append(datetime.fromtimestamp(change["ratingUpdateTimeSeconds"]))
        y.append(newRating)

    console.print(table)

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')
    plt.title(f'{handle} Rating History')
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.grid(True)
    plt.tight_layout()
    plt.show()