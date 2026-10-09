"""Command-line entry point for salesreport.

This is the *only* file that should know about argv, click, or how a
human invokes this tool. Everything it does is delegate to report.py -
that's the whole point of separating the two.
"""

from pathlib import Path

import click

from salesreport.report import read_sales_rows, total_revenue_by_store


@click.group()
def cli() -> None:
    """salesreport - daily store revenue reporting."""


@cli.command()
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to a sales CSV file.",
)
def generate(input_path: Path) -> None:
    """Print total revenue per store from a sales CSV."""
    rows = read_sales_rows(input_path)
    totals = total_revenue_by_store(rows)
    click.echo("Revenue by store:")
    for store, total in sorted(totals.items()):
        click.echo(f"  {store}: ${total:.2f}")


if __name__ == "__main__":
    cli()
