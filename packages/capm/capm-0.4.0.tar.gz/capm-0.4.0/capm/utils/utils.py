from rich.console import Console  # type: ignore

console = Console()


def info(text: str):
    console.print(f'[bold]ℹ︎[/bold] {text}', soft_wrap=True)


def succeed(text: str):
    console.print(f'[green]✔[/green] {text}', soft_wrap=True)


def fail(text: str):
    console.print(f'[red]⨯[/red] {text}', soft_wrap=True)
