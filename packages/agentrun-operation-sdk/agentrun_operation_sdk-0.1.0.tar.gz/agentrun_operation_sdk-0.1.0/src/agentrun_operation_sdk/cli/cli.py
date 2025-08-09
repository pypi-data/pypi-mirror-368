import typer
from ..utils.logging_config import setup_toolkit_logging
from .runtime.commands import launch, configure

app = typer.Typer(name="agentrun", help="HWAgentRun CLI", add_completion=False, rich_markup_mode="rich")

setup_toolkit_logging(mode="cli")

app.command("launch")(launch)
app.command("configure")(configure)


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
