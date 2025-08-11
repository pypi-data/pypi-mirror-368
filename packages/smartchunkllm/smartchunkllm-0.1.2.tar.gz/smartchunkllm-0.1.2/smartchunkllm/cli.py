#!/usr/bin/env python3
"""Command Line Interface for SmartChunkLLM."""

import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from rich import print as rprint

from .processor import SmartChunkLLM, ProcessingOptions
from .core.types import ChunkingStrategy, QualityLevel
from .core.exceptions import SmartChunkLLMError
from . import get_version, get_package_info

console = Console()


@click.group()
@click.version_option(version=get_version(), prog_name="SmartChunkLLM")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.pass_context
def cli(ctx, verbose: bool, quiet: bool):
    """SmartChunkLLM - Advanced Legal Document Semantic Chunking System.
    
    A powerful tool for processing legal documents with AI-powered semantic chunking,
    supporting multiple LLM providers including Ollama for offline processing.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    
    if not quiet:
        console.print(Panel.fit(
            "[bold blue]SmartChunkLLM[/bold blue] - Legal Document Semantic Chunking",
            border_style="blue"
        ))


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file path (JSON format)')
@click.option('--strategy', '-s', 
              type=click.Choice(['semantic', 'hybrid', 'hierarchical']),
              default='semantic', help='Chunking strategy')
@click.option('--quality', '-q', 
              type=click.Choice(['fast', 'balanced', 'high', 'maximum']),
              default='balanced', help='Quality level')
@click.option('--chunk-size', type=int, default=512, 
              help='Target chunk size in tokens')
@click.option('--overlap', type=int, default=50, 
              help='Overlap between chunks in tokens')
@click.option('--use-ollama', is_flag=True, 
              help='Use Ollama for offline processing')
@click.option('--ollama-model', default='llama3.1', 
              help='Ollama model to use')
@click.option('--ollama-url', default='http://localhost:11434', 
              help='Ollama server URL')
@click.option('--openai-key', envvar='OPENAI_API_KEY', 
              help='OpenAI API key')
@click.option('--anthropic-key', envvar='ANTHROPIC_API_KEY', 
              help='Anthropic API key')
@click.option('--enable-ocr', is_flag=True, 
              help='Enable OCR for scanned documents')
@click.option('--enable-layout', is_flag=True, 
              help='Enable advanced layout detection')
@click.option('--batch-size', type=int, default=10, 
              help='Batch size for processing')
@click.option('--max-workers', type=int, default=4, 
              help='Maximum number of worker threads')
@click.option('--save-intermediate', is_flag=True, 
              help='Save intermediate processing results')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'yaml', 'txt', 'markdown']),
              default='json', help='Output format')
@click.pass_context
def process(ctx, input_file: Path, output: Optional[Path], strategy: str, 
           quality: str, chunk_size: int, overlap: int, use_ollama: bool,
           ollama_model: str, ollama_url: str, openai_key: Optional[str],
           anthropic_key: Optional[str], enable_ocr: bool, enable_layout: bool,
           batch_size: int, max_workers: int, save_intermediate: bool,
           output_format: str):
    """Process a legal document and generate semantic chunks.
    
    INPUT_FILE: Path to the PDF document to process
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        # Validate input file
        if not input_file.exists():
            raise click.ClickException(f"Input file not found: {input_file}")
        
        if input_file.suffix.lower() != '.pdf':
            raise click.ClickException("Only PDF files are supported")
        
        # Set up processing options
        options = ProcessingOptions(
            chunking_strategy=ChunkingStrategy(strategy.upper()),
            quality_level=QualityLevel(quality.upper()),
            chunk_size=chunk_size,
            overlap_size=overlap,
            enable_ocr=enable_ocr,
            enable_layout_detection=enable_layout,
            batch_size=batch_size,
            max_workers=max_workers,
            save_intermediate_results=save_intermediate
        )
        
        # Initialize processor
        processor_config = {
            'use_ollama': use_ollama,
            'ollama_model': ollama_model,
            'ollama_base_url': ollama_url,
        }
        
        if openai_key:
            processor_config['openai_api_key'] = openai_key
        if anthropic_key:
            processor_config['anthropic_api_key'] = anthropic_key
            
        processor = SmartChunkLLM(**processor_config)
        
        # Process document with progress tracking
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing document...", total=None)
                result = processor.process_pdf(str(input_file), options)
                progress.update(task, description="✅ Processing completed")
        else:
            result = processor.process_pdf(str(input_file), options)
        
        # Display results
        if not quiet:
            _display_results(result, verbose)
        
        # Save output
        if output:
            _save_output(result, output, output_format)
            if not quiet:
                console.print(f"\n✅ Results saved to: [green]{output}[/green]")
        
    except SmartChunkLLMError as e:
        raise click.ClickException(f"Processing error: {e}")
    except Exception as e:
        if verbose:
            console.print_exception()
        raise click.ClickException(f"Unexpected error: {e}")


@cli.command()
@click.argument('text', type=str)
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file path (JSON format)')
@click.option('--strategy', '-s', 
              type=click.Choice(['semantic', 'hybrid', 'hierarchical']),
              default='semantic', help='Chunking strategy')
@click.option('--quality', '-q', 
              type=click.Choice(['fast', 'balanced', 'high', 'maximum']),
              default='balanced', help='Quality level')
@click.option('--chunk-size', type=int, default=512, 
              help='Target chunk size in tokens')
@click.option('--overlap', type=int, default=50, 
              help='Overlap between chunks in tokens')
@click.option('--use-ollama', is_flag=True, 
              help='Use Ollama for offline processing')
@click.option('--ollama-model', default='llama3.1', 
              help='Ollama model to use')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'yaml', 'txt', 'markdown']),
              default='json', help='Output format')
@click.pass_context
def chunk_text(ctx, text: str, output: Optional[Path], strategy: str, 
              quality: str, chunk_size: int, overlap: int, use_ollama: bool,
              ollama_model: str, output_format: str):
    """Process raw text and generate semantic chunks.
    
    TEXT: Text content to process
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        # Set up processing options
        options = ProcessingOptions(
            chunking_strategy=ChunkingStrategy(strategy.upper()),
            quality_level=QualityLevel(quality.upper()),
            chunk_size=chunk_size,
            overlap_size=overlap
        )
        
        # Initialize processor
        processor = SmartChunkLLM(
            use_ollama=use_ollama,
            ollama_model=ollama_model
        )
        
        # Process text
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing text...", total=None)
                result = processor.process_text(text, options)
                progress.update(task, description="✅ Processing completed")
        else:
            result = processor.process_text(text, options)
        
        # Display results
        if not quiet:
            _display_results(result, verbose)
        
        # Save output
        if output:
            _save_output(result, output, output_format)
            if not quiet:
                console.print(f"\n✅ Results saved to: [green]{output}[/green]")
        
    except SmartChunkLLMError as e:
        raise click.ClickException(f"Processing error: {e}")
    except Exception as e:
        if verbose:
            console.print_exception()
        raise click.ClickException(f"Unexpected error: {e}")


@cli.command()
@click.option('--check-ollama', is_flag=True, help='Check Ollama availability')
@click.option('--check-openai', is_flag=True, help='Check OpenAI API')
@click.option('--check-anthropic', is_flag=True, help='Check Anthropic API')
@click.option('--list-models', is_flag=True, help='List available models')
def info(check_ollama: bool, check_openai: bool, check_anthropic: bool, list_models: bool):
    """Display system information and check provider availability."""
    
    # Package information
    package_info = get_package_info()
    
    info_table = Table(title="SmartChunkLLM System Information")
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Status", style="green")
    info_table.add_column("Details")
    
    info_table.add_row("Version", "✅", package_info['version'])
    info_table.add_row("Python", "✅", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check providers if requested
    if check_ollama:
        try:
            from .llm.providers import OllamaProvider
            provider = OllamaProvider()
            if provider.is_available():
                info_table.add_row("Ollama", "✅", "Available")
            else:
                info_table.add_row("Ollama", "❌", "Not available")
        except Exception as e:
            info_table.add_row("Ollama", "❌", f"Error: {e}")
    
    if check_openai:
        try:
            from .llm.providers import OpenAIProvider
            provider = OpenAIProvider()
            if provider.is_available():
                info_table.add_row("OpenAI", "✅", "Available")
            else:
                info_table.add_row("OpenAI", "❌", "API key required")
        except Exception as e:
            info_table.add_row("OpenAI", "❌", f"Error: {e}")
    
    if check_anthropic:
        try:
            from .llm.providers import AnthropicProvider
            provider = AnthropicProvider()
            if provider.is_available():
                info_table.add_row("Anthropic", "✅", "Available")
            else:
                info_table.add_row("Anthropic", "❌", "API key required")
        except Exception as e:
            info_table.add_row("Anthropic", "❌", f"Error: {e}")
    
    console.print(info_table)
    
    # List models if requested
    if list_models:
        console.print("\n[bold]Available Models:[/bold]")
        
        if check_ollama:
            try:
                from .llm.providers import OllamaProvider
                provider = OllamaProvider()
                models = provider.list_models()
                if models:
                    tree = Tree("🦙 Ollama Models")
                    for model in models:
                        tree.add(model)
                    console.print(tree)
                else:
                    console.print("No Ollama models found")
            except Exception:
                console.print("Could not list Ollama models")


@cli.command()
def examples():
    """Show usage examples."""
    from . import show_examples
    show_examples()


def _display_results(result, verbose: bool = False):
    """Display processing results in a formatted way."""
    
    # Summary table
    summary_table = Table(title="Processing Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Chunks", str(len(result.chunks)))
    summary_table.add_row("Processing Time", f"{result.stats.total_time:.2f}s")
    summary_table.add_row("Average Quality Score", f"{result.stats.average_quality_score:.2f}")
    summary_table.add_row("Total Tokens", str(result.stats.total_tokens))
    
    console.print(summary_table)
    
    if verbose and result.chunks:
        console.print("\n[bold]Sample Chunks:[/bold]")
        
        # Show first few chunks
        for i, chunk in enumerate(result.chunks[:3]):
            panel_title = f"Chunk {i+1} - {chunk.metadata.get('content_type', 'Unknown')}"
            content = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            
            panel_content = f"[bold]Content:[/bold]\n{content}\n\n"
            panel_content += f"[bold]Quality Score:[/bold] {chunk.quality_score:.2f}\n"
            panel_content += f"[bold]Tokens:[/bold] {chunk.token_count}\n"
            
            if chunk.metadata.get('legal_concepts'):
                concepts = ", ".join(chunk.metadata['legal_concepts'][:3])
                panel_content += f"[bold]Legal Concepts:[/bold] {concepts}"
            
            console.print(Panel(panel_content, title=panel_title, border_style="blue"))


def _save_output(result, output_path: Path, format_type: str):
    """Save processing results to file."""
    
    if format_type == 'json':
        data = {
            'chunks': [chunk.to_dict() for chunk in result.chunks],
            'stats': result.stats.to_dict(),
            'metadata': result.metadata
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format_type == 'yaml':
        import yaml
        data = {
            'chunks': [chunk.to_dict() for chunk in result.chunks],
            'stats': result.stats.to_dict(),
            'metadata': result.metadata
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    elif format_type == 'txt':
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"SmartChunkLLM Processing Results\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Total Chunks: {len(result.chunks)}\n")
            f.write(f"Processing Time: {result.stats.total_time:.2f}s\n")
            f.write(f"Average Quality: {result.stats.average_quality_score:.2f}\n\n")
            
            for i, chunk in enumerate(result.chunks):
                f.write(f"Chunk {i+1}\n")
                f.write(f"{'-'*20}\n")
                f.write(f"Content: {chunk.content}\n")
                f.write(f"Quality: {chunk.quality_score:.2f}\n")
                f.write(f"Tokens: {chunk.token_count}\n\n")
    
    elif format_type == 'markdown':
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# SmartChunkLLM Processing Results\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Chunks:** {len(result.chunks)}\n")
            f.write(f"- **Processing Time:** {result.stats.total_time:.2f}s\n")
            f.write(f"- **Average Quality:** {result.stats.average_quality_score:.2f}\n\n")
            
            f.write("## Chunks\n\n")
            for i, chunk in enumerate(result.chunks):
                f.write(f"### Chunk {i+1}\n\n")
                f.write(f"**Quality Score:** {chunk.quality_score:.2f}  \n")
                f.write(f"**Token Count:** {chunk.token_count}  \n\n")
                f.write(f"{chunk.content}\n\n")
                f.write("---\n\n")


def main():
    """Main entry point for CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()