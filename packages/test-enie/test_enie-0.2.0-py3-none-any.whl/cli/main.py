#!/usr/bin/env python3
import click
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from commands.generate import generate
from cli.auth import login, logout, status

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """TestGenie CLI - Generate test cases for your Python/C++ code"""
    pass

# Add subcommands
cli.add_command(generate)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(status)

if __name__ == "__main__":
    cli() 