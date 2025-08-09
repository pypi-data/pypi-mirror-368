import re
import sys
import typer
import simplesam
from flexiformatter import __version__ 

app = typer.Typer(add_completion=False)

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context, 
    infile: str = typer.Argument(None),
    version: bool = typer.Option(
        None, "--version", "-v", help="Prints the version of the tool.", is_eager=True
    ),
):
    """
    A simple tool for processing BAM/SAM files.
    """
    if version:
        typer.echo(f"flexi_formatter version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None and infile is not None:
        # If no subcommand is invoked and 'infile' is given, call 'main' directly
        main(infile)

@app.command()
def main(infile: str):
    """Process BAM/SAM file."""
    with simplesam.Reader(open(infile)) as in_bam:
        with simplesam.Writer(sys.stdout, in_bam.header) as out_sam:
            for read in in_bam:
            
                # Get header name and split by "_#" or "#"
                match = re.match(r'^([ACGT]+)(?:_([ACGT]+))?#', read.qname)
                bc = match.group(1) if match else None
                umi = match.group(2) if match and len(match.groups()) > 1 else None
                
                if bc:
                    read.tags['CB'] = bc
                if umi:
                    read.tags['UR'] = umi
                
                # Write new reads
                out_sam.write(read)

if __name__ == "__main__":
    app()
