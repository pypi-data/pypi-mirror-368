"""Batch processing utilities for handling large datasets efficiently"""

import os
import json
import time
from pathlib import Path
from typing import Iterator, Callable, Any, Optional, Dict, List
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from ..errors import DatasetError

console = Console()

class BatchProcessor:
    """Process large files in memory-efficient batches"""
    
    def __init__(self, batch_size: int = 10000, max_workers: int = 4):
        """
        Initialize batch processor
        
        Args:
            batch_size: Number of rows per batch
            max_workers: Maximum number of parallel workers
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.stats = {
            'total_processed': 0,
            'total_flagged': 0,
            'processing_time': 0,
            'errors': 0
        }
    
    def process_dataset(
        self,
        filepath: Path,
        process_func: Callable[[pd.DataFrame], Dict[str, Any]],
        output_file: Optional[Path] = None,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Process a large dataset in batches
        
        Args:
            filepath: Path to the dataset
            process_func: Function to process each batch
            output_file: Optional output file for results
            show_progress: Show progress bar
        
        Returns:
            Processing statistics
        """
        from ..utils.file_handlers import read_dataset_streaming
        
        start_time = time.time()
        results = []
        
        # Count total rows for progress bar (approximate for large files)
        total_rows = self._estimate_rows(filepath)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            if show_progress:
                task = progress.add_task(
                    f"Processing {filepath.name}",
                    total=total_rows
                )
            
            # Process in chunks
            for batch_num, chunk in enumerate(read_dataset_streaming(filepath, self.batch_size)):
                try:
                    # Process batch
                    batch_result = process_func(chunk)
                    results.append(batch_result)
                    
                    # Update statistics
                    self.stats['total_processed'] += len(chunk)
                    if 'flagged' in batch_result:
                        self.stats['total_flagged'] += batch_result['flagged']
                    
                    if show_progress:
                        progress.update(task, advance=len(chunk))
                    
                    # Save intermediate results if output file specified
                    if output_file and batch_num % 10 == 0:
                        self._save_intermediate_results(output_file, results)
                        
                except Exception as e:
                    console.print(f"[yellow]Warning: Error in batch {batch_num}: {e}[/yellow]")
                    self.stats['errors'] += 1
                    continue
        
        # Calculate final statistics
        self.stats['processing_time'] = time.time() - start_time
        self.stats['rows_per_second'] = self.stats['total_processed'] / self.stats['processing_time']
        
        # Save final results
        if output_file:
            self._save_final_results(output_file, results, self.stats)
        
        # Display summary
        self._display_summary()
        
        return self.stats
    
    def process_multiple_files(
        self,
        filepaths: List[Path],
        process_func: Callable[[pd.DataFrame], Dict[str, Any]],
        output_dir: Optional[Path] = None,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Process multiple files with optional parallelization
        
        Args:
            filepaths: List of file paths to process
            process_func: Function to process each batch
            output_dir: Optional output directory for results
            parallel: Process files in parallel
        
        Returns:
            Aggregated statistics
        """
        console.print(f"\n[cyan]Processing {len(filepaths)} files[/cyan]")
        
        aggregate_stats = {
            'files_processed': 0,
            'total_rows': 0,
            'total_flagged': 0,
            'total_time': 0,
            'file_results': {}
        }
        
        if parallel and len(filepaths) > 1:
            # Process files in parallel using multiprocessing
            from concurrent.futures import ProcessPoolExecutor, as_completed
            
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(
                        self.process_dataset,
                        filepath,
                        process_func,
                        output_dir / f"{filepath.stem}_results.json" if output_dir else None,
                        False  # Disable progress for parallel processing
                    ): filepath
                    for filepath in filepaths
                }
                
                with Progress(console=console) as progress:
                    task = progress.add_task("Processing files", total=len(filepaths))
                    
                    for future in as_completed(futures):
                        filepath = futures[future]
                        try:
                            stats = future.result()
                            aggregate_stats['file_results'][str(filepath)] = stats
                            aggregate_stats['files_processed'] += 1
                            aggregate_stats['total_rows'] += stats['total_processed']
                            aggregate_stats['total_flagged'] += stats.get('total_flagged', 0)
                            progress.update(task, advance=1)
                        except Exception as e:
                            console.print(f"[red]Error processing {filepath}: {e}[/red]")
        else:
            # Process files sequentially
            for filepath in filepaths:
                console.print(f"\nProcessing: [cyan]{filepath.name}[/cyan]")
                stats = self.process_dataset(
                    filepath,
                    process_func,
                    output_dir / f"{filepath.stem}_results.json" if output_dir else None
                )
                aggregate_stats['file_results'][str(filepath)] = stats
                aggregate_stats['files_processed'] += 1
                aggregate_stats['total_rows'] += stats['total_processed']
                aggregate_stats['total_flagged'] += stats.get('total_flagged', 0)
                aggregate_stats['total_time'] += stats['processing_time']
        
        # Display aggregate summary
        self._display_aggregate_summary(aggregate_stats)
        
        return aggregate_stats
    
    def _estimate_rows(self, filepath: Path) -> int:
        """Estimate number of rows in file for progress bar"""
        file_size = filepath.stat().st_size
        
        # Sample first few lines to estimate average row size
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample_lines = []
            for i, line in enumerate(f):
                if i >= 100:
                    break
                sample_lines.append(line)
        
        if not sample_lines:
            return 0
        
        avg_line_size = sum(len(line) for line in sample_lines) / len(sample_lines)
        estimated_rows = int(file_size / avg_line_size)
        
        return estimated_rows
    
    def _save_intermediate_results(self, output_file: Path, results: List[Dict]):
        """Save intermediate results to prevent data loss"""
        temp_file = output_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump({
                'intermediate': True,
                'timestamp': time.time(),
                'results': results,
                'stats': self.stats
            }, f)
    
    def _save_final_results(self, output_file: Path, results: List[Dict], stats: Dict):
        """Save final results to output file"""
        output_data = {
            'complete': True,
            'timestamp': time.time(),
            'results': results,
            'statistics': stats
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Remove temporary file if exists
        temp_file = output_file.with_suffix('.tmp')
        if temp_file.exists():
            temp_file.unlink()
        
        console.print(f"\n[green]✓[/green] Results saved to: {output_file}")
    
    def _display_summary(self):
        """Display processing summary"""
        table = Table(title="Processing Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Processed", f"{self.stats['total_processed']:,}")
        table.add_row("Total Flagged", f"{self.stats['total_flagged']:,}")
        table.add_row("Processing Time", f"{self.stats['processing_time']:.2f} seconds")
        table.add_row("Throughput", f"{self.stats['rows_per_second']:.0f} rows/second")
        
        if self.stats['errors'] > 0:
            table.add_row("Errors", f"{self.stats['errors']}", style="yellow")
        
        console.print(table)
    
    def _display_aggregate_summary(self, stats: Dict):
        """Display aggregate summary for multiple files"""
        table = Table(title="Aggregate Processing Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files Processed", f"{stats['files_processed']}")
        table.add_row("Total Rows", f"{stats['total_rows']:,}")
        table.add_row("Total Flagged", f"{stats['total_flagged']:,}")
        table.add_row("Total Time", f"{stats['total_time']:.2f} seconds")
        
        if stats['total_time'] > 0:
            avg_throughput = stats['total_rows'] / stats['total_time']
            table.add_row("Average Throughput", f"{avg_throughput:.0f} rows/second")
        
        console.print(table)


class CheckpointManager:
    """Manage checkpoints for resumable processing"""
    
    def __init__(self, job_id: str):
        """
        Initialize checkpoint manager
        
        Args:
            job_id: Unique identifier for the job
        """
        self.job_id = job_id
        self.checkpoint_dir = Path.home() / '.darkfield' / 'checkpoints'
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{job_id}.checkpoint"
    
    def save(self, state: Dict[str, Any]):
        """Save current job state"""
        import pickle
        from datetime import datetime
        
        checkpoint = {
            'job_id': self.job_id,
            'timestamp': datetime.now().isoformat(),
            'state': state
        }
        
        with open(self.checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint, f)
        
        console.print(f"[dim]Checkpoint saved: {self.job_id}[/dim]")
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load saved job state"""
        import pickle
        
        if not self.checkpoint_file.exists():
            return None
        
        try:
            with open(self.checkpoint_file, 'rb') as f:
                checkpoint = pickle.load(f)
            
            console.print(f"[green]✓[/green] Resuming from checkpoint: {checkpoint['timestamp']}")
            return checkpoint['state']
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load checkpoint: {e}[/yellow]")
            return None
    
    def cleanup(self):
        """Remove checkpoint after successful completion"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            console.print(f"[dim]Checkpoint cleaned up: {self.job_id}[/dim]")
    
    @classmethod
    def list_checkpoints(cls) -> List[Dict[str, str]]:
        """List all saved checkpoints"""
        import pickle
        
        checkpoint_dir = Path.home() / '.darkfield' / 'checkpoints'
        if not checkpoint_dir.exists():
            return []
        
        checkpoints = []
        for file in checkpoint_dir.glob('*.checkpoint'):
            try:
                with open(file, 'rb') as f:
                    cp = pickle.load(f)
                    checkpoints.append({
                        'job_id': cp['job_id'],
                        'timestamp': cp['timestamp'],
                        'file': str(file)
                    })
            except:
                continue
        
        return checkpoints