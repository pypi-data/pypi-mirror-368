import click
from pathlib import Path
from .core import create_project, build_project, run_project

@click.group()
def cli():
    """Nexagen - Next-Generation Multi-Agent System Builder"""
    pass

@cli.command()
@click.argument("project_name")
def create(project_name):
    """Create a new Nexagen project"""
    project_path = Path.cwd() / project_name
    create_project(project_path)
    click.echo(f"Project '{project_name}' created successfully at {project_path}")

@cli.command()
def build():
    """Build the Nexagen multi-agent system"""
    project_path = Path.cwd()
    build_project(project_path)
    click.echo("Nexagen system built successfully")

@cli.command()
def run():
    """Run the Nexagen system"""
    project_path = Path.cwd()
    run_project(project_path)
    click.echo("Nexagen system running")

if __name__ == "__main__":
    cli()