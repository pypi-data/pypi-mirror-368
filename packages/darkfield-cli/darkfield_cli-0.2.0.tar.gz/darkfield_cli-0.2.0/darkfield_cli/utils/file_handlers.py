"""File handling utilities with encoding detection and format support"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Union, Optional, Any, Iterator
import chardet
from rich.console import Console

console = Console()

def detect_encoding(file_path: Union[str, Path], sample_size: int = 100000) -> str:
    """
    Detect file encoding by reading a sample
    
    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample for detection
    
    Returns:
        Detected encoding string
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        if confidence < 0.7:
            console.print(f"[yellow]Warning: Low confidence ({confidence:.0%}) in encoding detection. Trying {encoding}[/yellow]")
        
        return encoding

def read_dataset_with_encoding_detection(
    file_path: Union[str, Path],
    file_format: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Read dataset with automatic encoding detection and format support
    
    Args:
        file_path: Path to the dataset file
        file_format: Optional format override (csv, json, jsonl, parquet, etc.)
        **kwargs: Additional arguments to pass to pandas read functions
    
    Returns:
        DataFrame containing the dataset
    
    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file format
    if file_format is None:
        file_format = file_path.suffix.lower().lstrip('.')
    
    # Handle different file formats
    if file_format in ['csv', 'tsv', 'txt']:
        return read_csv_robust(file_path, **kwargs)
    elif file_format in ['json']:
        return pd.read_json(file_path, **kwargs)
    elif file_format in ['jsonl', 'ndjson']:
        return read_jsonlines(file_path, **kwargs)
    elif file_format in ['parquet', 'pq']:
        return pd.read_parquet(file_path, **kwargs)
    elif file_format in ['xlsx', 'xls']:
        return pd.read_excel(file_path, **kwargs)
    elif file_format in ['feather', 'ftr']:
        return pd.read_feather(file_path, **kwargs)
    elif file_format in ['h5', 'hdf5', 'hdf']:
        return pd.read_hdf(file_path, **kwargs)
    else:
        # Try to infer from content
        return read_csv_robust(file_path, **kwargs)

def read_csv_robust(
    file_path: Union[str, Path],
    encoding: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Read CSV with robust encoding handling
    
    Args:
        file_path: Path to CSV file
        encoding: Optional encoding override
        **kwargs: Additional pandas read_csv arguments
    
    Returns:
        DataFrame containing the CSV data
    """
    file_path = Path(file_path)
    
    # Detect encoding if not provided
    if encoding is None:
        encoding = detect_encoding(file_path)
    
    # List of encodings to try in order
    encodings = [encoding] if encoding else []
    encodings.extend(['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-32'])
    
    # Remove duplicates while preserving order
    encodings = list(dict.fromkeys(encodings))
    
    last_error = None
    for enc in encodings:
        try:
            # Try reading with current encoding
            df = pd.read_csv(
                file_path,
                encoding=enc,
                on_bad_lines='skip',  # Skip bad lines instead of failing
                engine='python',  # More robust but slower
                **kwargs
            )
            
            # Check if we got meaningful data
            if len(df) > 0:
                if enc != encodings[0]:
                    console.print(f"[green]✓[/green] Successfully read file with {enc} encoding")
                return df
                
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            last_error = e
            continue
    
    # Last resort: try with error handling
    console.print("[yellow]Warning: Using error-ignoring mode for file reading[/yellow]")
    try:
        return pd.read_csv(
            file_path,
            encoding='utf-8',
            encoding_errors='ignore',  # Ignore encoding errors
            on_bad_lines='skip',
            engine='python',
            **kwargs
        )
    except Exception as e:
        raise ValueError(f"Failed to read file {file_path} with any encoding. Last error: {last_error}")

def read_jsonlines(
    file_path: Union[str, Path],
    **kwargs
) -> pd.DataFrame:
    """
    Read JSON Lines format file
    
    Args:
        file_path: Path to JSONL file
        **kwargs: Additional arguments
    
    Returns:
        DataFrame containing the JSONL data
    """
    file_path = Path(file_path)
    
    records = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            try:
                if line.strip():  # Skip empty lines
                    records.append(json.loads(line))
            except json.JSONDecodeError as e:
                console.print(f"[yellow]Warning: Skipping invalid JSON at line {line_num}: {e}[/yellow]")
                continue
    
    if not records:
        raise ValueError(f"No valid JSON records found in {file_path}")
    
    return pd.DataFrame(records)

def read_dataset_streaming(
    file_path: Union[str, Path],
    chunk_size: int = 10000,
    file_format: Optional[str] = None,
    **kwargs
) -> Iterator[pd.DataFrame]:
    """
    Read large datasets in chunks for memory-efficient processing
    
    Args:
        file_path: Path to the dataset file
        chunk_size: Number of rows per chunk
        file_format: Optional format override
        **kwargs: Additional arguments
    
    Yields:
        DataFrame chunks
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file format
    if file_format is None:
        file_format = file_path.suffix.lower().lstrip('.')
    
    if file_format in ['csv', 'tsv', 'txt']:
        # Detect encoding first
        encoding = detect_encoding(file_path)
        
        # Use pandas chunked reader
        reader = pd.read_csv(
            file_path,
            encoding=encoding,
            chunksize=chunk_size,
            on_bad_lines='skip',
            engine='python',
            **kwargs
        )
        
        for chunk in reader:
            yield chunk
            
    elif file_format in ['jsonl', 'ndjson']:
        # Read JSONL in batches
        batch = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    if line.strip():
                        batch.append(json.loads(line))
                        if len(batch) >= chunk_size:
                            yield pd.DataFrame(batch)
                            batch = []
                except json.JSONDecodeError:
                    continue
            
            # Yield remaining batch
            if batch:
                yield pd.DataFrame(batch)
    else:
        # For other formats, read entire file (no streaming support)
        df = read_dataset_with_encoding_detection(file_path, file_format, **kwargs)
        
        # Split into chunks
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]