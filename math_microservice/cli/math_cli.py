#!/usr/bin/env python
import click
import requests

API_BASE = "http://localhost:8000"

@click.group()
def cli():
    """Math Microservice CLI Client"""
    pass

@cli.command()
@click.argument("operation", type=click.Choice(["pow", "fibonacci", "factorial"]))
@click.argument("operand", type=int)
def compute(operation, operand):
    """Compute a math operation and print the result"""
    try:
        res = requests.post(f"{API_BASE}/compute", json={"operation": operation, "operand": operand})
        res.raise_for_status()
        data = res.json()
        click.echo(f"Result: {data['result']}")
        click.echo(f"Timestamp: {data['timestamp']}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Request failed: {e}", err=True)

@cli.command()
def history():
    """Show history of all operations"""
    try:
        res = requests.get(f"{API_BASE}/history")
        res.raise_for_status()
        data = res.json()
        if not data:
            click.echo("No operation history yet.")
        for op in data:
            click.echo(f"{op['operation']}({op['operand']}) = {op['result']} @ {op['timestamp']}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Request failed: {e}", err=True)

if __name__ == "__main__":
    cli()
