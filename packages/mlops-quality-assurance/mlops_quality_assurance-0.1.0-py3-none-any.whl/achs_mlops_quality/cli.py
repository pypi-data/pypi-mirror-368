import typer
from rich.console import Console
from rich.table import Table
from achs_mlops_quality.models import LibraryChecker

app = typer.Typer()
console = Console()

@app.command()
def hello():
    console.print("[bold cyan]  Hello desde MLOPS Library checker [/bold cyan]")

@app.command()
def run(path : str = ".",  formal: bool = False):
    console.rule("[bold cyan] 📂 Starting Notebook Analysis [/bold cyan]")
    model = LibraryChecker(path)
    model.analize_notebooks()
    if model.issues_detected > 0:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="yellow")
        table.add_column("Issue", style="red")
        for n in model.issues_files:
            table.add_row(n, "Unpinned libraries detected")
        console.print(table)
        console.print("[bold yellow] ⚠ Please fix these libraries by specifying their versions. [/bold yellow]")
        console.print(f"[bold yellow] ⚠ Files with issues {model.issues_detected}, Files analized {model.analized_files}. [/bold yellow]")
        raise typer.Exit(1)
    else:
        console.print(f"[bold green] No se detectaron librerias sin versionamiento: Files with issues {model.issues_detected}, Files analized {model.analized_files}. [/bold green]")

if __name__ == "__main__":
    app()