"""
# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Command-line interface for geneinfo package using typer and rich
# Version: 0.1

Command-line interface for geneinfo package.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .core import GeneInfo

# Initialize typer app and rich console
app = typer.Typer(
    name="geneinfo",
    help="Get comprehensive gene information from multiple public databases",
    epilog="Example: geneinfo --gene TP53 --output tp53_info.json",
)
console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"geneinfo {__version__}")
        raise typer.Exit()


def setup_logging(verbose: bool = False):
    """Setup logging configuration with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO

    # Configure rich logging handler
    rich_handler = RichHandler(
        console=console, show_time=True, show_path=verbose, rich_tracebacks=True
    )

    logging.basicConfig(
        level=level, format="%(message)s", handlers=[rich_handler]
    )


def read_gene_list(file_path: Path) -> List[str]:
    """Read gene list from file."""
    try:
        genes = []
        with file_path.open("r") as f:
            for line in f:
                gene = line.strip()
                if gene and not gene.startswith("#"):
                    genes.append(gene)
        return genes
    except Exception as e:
        console.print(f"[red]Error reading gene file: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def main(
    genes_input: Optional[List[str]] = typer.Argument(
        None,
        help="Gene symbol(s) or Ensembl ID(s) (e.g., TP53 BRCA1 or ENSG00000141510)",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    gene: Optional[str] = typer.Option(
        None,
        "--gene",
        "-g",
        help="Single gene symbol or Ensembl ID (e.g., TP53 or ENSG00000141510)",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="File containing list of gene symbols/IDs (one per line)",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (CSV for summary, JSON for detailed)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Output directory for batch processing (creates individual files + summary.csv)",
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Export detailed information in JSON format",
    ),
    species: str = typer.Option(
        "human", "--species", "-s", help="Target species (default: human)"
    ),
    workers: int = typer.Option(
        5,
        "--workers",
        "-w",
        help="Number of concurrent workers for batch processing (default: 5)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Email address for NCBI Entrez API (can also be set via ENTREZ_EMAIL env var)",
    ),
    entrez_api_key: Optional[str] = typer.Option(
        None,
        "--entrez-api-key",
        help="NCBI Entrez API key (can also be set via ENTREZ_API_KEY env var)",
    ),
    omim_api_key: Optional[str] = typer.Option(
        None,
        "--omim-api-key",
        help="OMIM API key (can also be set via OMIM_API_KEY env var)",
    ),
    biogrid_api_key: Optional[str] = typer.Option(
        None,
        "--biogrid-api-key",
        help="BioGRID API key for protein interactions (can also be set via BIOGRID_API_KEY env var)",
    ),
):
    """
    Get comprehensive gene information based on gene symbol or Ensembl ID.

    Examples:

    # Get info for a single gene
    geneinfo --gene TP53 --output tp53_info.json

    # Process multiple genes from file
    geneinfo --file genes.txt --output results.csv

    # Batch process to directory with individual files
    geneinfo --file genes.txt --output-dir results/

    # Get detailed info with verbose logging and API keys
    geneinfo --gene BRCA1 --detailed --verbose --entrez-api-key YOUR_KEY --omim-api-key YOUR_KEY --biogrid-api-key YOUR_KEY

    # Use environment variables for API keys (create .env file with ENTREZ_API_KEY, OMIM_API_KEY, and BIOGRID_API_KEY)
    geneinfo --gene TP53 --detailed
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    # Handle positional arguments
    if genes_input and gene:
        console.print(
            "[red]Error: Cannot use both positional arguments and --gene option[/red]"
        )
        raise typer.Exit(1)

    if genes_input:
        # Convert positional arguments to gene
        if len(genes_input) == 1:
            gene = genes_input[0]
        else:
            # Multiple genes provided as positional arguments - treat as batch
            genes = genes_input
            gene = None

    # Validate input
    if not gene and not file and not genes_input:
        console.print(
            "[red]Error: Must provide either gene name(s), --gene, or --file[/red]"
        )
        raise typer.Exit(1)

    if gene and file:
        console.print(
            "[red]Error: Cannot use both --gene and --file options[/red]"
        )
        raise typer.Exit(1)

    if output and output_dir:
        console.print(
            "[red]Error: Cannot use both --output and --output-dir options[/red]"
        )
        raise typer.Exit(1)

    # Initialize GeneInfo
    try:
        with console.status("[bold green]Initializing GeneInfo..."):
            gene_info = GeneInfo(
                species=species,
                email=email,
                entrez_api_key=entrez_api_key,
                omim_api_key=omim_api_key,
                biogrid_api_key=biogrid_api_key,
            )
    except Exception as e:
        console.print(f"[red]Error initializing GeneInfo: {str(e)}[/red]")
        raise typer.Exit(1)

    # Get gene list
    if gene:
        genes = [gene]
        console.print(f"[blue]Processing single gene: {gene}[/blue]")
    elif genes_input and len(genes_input) > 1:
        # Multiple positional arguments provided
        console.print(
            f"[blue]Processing {len(genes_input)} genes from arguments[/blue]"
        )
    else:
        try:
            genes = read_gene_list(file)
            console.print(f"[blue]Read {len(genes)} genes from {file}[/blue]")
        except Exception as e:
            console.print(f"[red]Error reading gene file: {str(e)}[/red]")
            raise typer.Exit(1)

    if not genes:
        console.print("[red]No genes to process[/red]")
        raise typer.Exit(1)

    # Process genes
    try:
        if output_dir:
            # Batch processing to directory with individual files and summary
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Processing {len(genes)} genes to directory...", total=None
                )
                gene_info.export_batch_to_directory(
                    genes, str(output_dir), max_workers=workers
                )
                progress.remove_task(task)

        elif len(genes) == 1 and not detailed:
            # Single gene, simple output
            with console.status(
                f"[bold green]Fetching information for {genes[0]}..."
            ):
                result = gene_info.get_gene_info(genes[0])

            if output:
                with output.open("w") as f:
                    json.dump(result, f, indent=2, default=str)
                console.print(f"[green]Results saved to {output}[/green]")
            else:
                # Display results in a nice table format
                display_gene_summary(result)

        elif detailed:
            # Detailed JSON output
            if not output:
                output = Path("gene_info_detailed.json")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Fetching detailed information...", total=None
                )
                gene_info.export_detailed_info(genes, str(output))
                progress.remove_task(task)

            console.print(f"[green]Detailed results saved to {output}[/green]")

        else:
            # Batch processing with CSV summary
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Processing {len(genes)} genes...", total=None
                )
                df = gene_info.get_batch_info(genes, max_workers=workers)
                progress.remove_task(task)

            if output:
                df.to_csv(output, index=False)
                console.print(f"[green]Results saved to {output}[/green]")
            else:
                display_batch_summary(df)

    except Exception as e:
        logger.error(f"Error processing genes: {str(e)}")
        console.print(f"[red]Error processing genes: {str(e)}[/red]")
        raise typer.Exit(1)

    console.print("[green]✅ Processing completed successfully[/green]")


def display_gene_summary(result: dict):
    """Display gene information in a formatted table."""
    table = Table(title=f"Gene Information: {result.get('query', 'Unknown')}")

    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Basic info
    basic_info = result.get("basic_info", {})
    table.add_row("Gene Symbol", basic_info.get("display_name", "N/A"))
    table.add_row("Ensembl ID", basic_info.get("id", "N/A"))
    table.add_row("Description", basic_info.get("description", "N/A"))
    table.add_row("Chromosome", str(basic_info.get("seq_region_name", "N/A")))
    table.add_row("Start", str(basic_info.get("start", "N/A")))
    table.add_row("End", str(basic_info.get("end", "N/A")))
    table.add_row("Strand", str(basic_info.get("strand", "N/A")))

    # Counts
    table.add_row("Transcripts", str(len(result.get("transcripts", []))))
    table.add_row("GO Terms", str(len(result.get("gene_ontology", []))))
    table.add_row("Pathways", str(len(result.get("pathways", []))))
    table.add_row(
        "Protein Domains", str(len(result.get("protein_domains", [])))
    )
    table.add_row(
        "Interactions", str(len(result.get("protein_interactions", [])))
    )
    table.add_row("Paralogs", str(len(result.get("paralogs", []))))
    table.add_row("Orthologs", str(len(result.get("orthologs", []))))

    console.print(table)


def display_batch_summary(df):
    """Display batch processing results in a formatted table."""
    table = Table(title="Batch Processing Summary")

    # Add columns dynamically based on DataFrame
    for col in df.columns:
        table.add_column(col, style="cyan")

    # Add rows (limit to first 20 for display)
    for idx, row in df.head(20).iterrows():
        table.add_row(*[str(val) for val in row])

    console.print(table)

    if len(df) > 20:
        console.print(f"[yellow]... and {len(df) - 20} more rows[/yellow]")


if __name__ == "__main__":
    app()
