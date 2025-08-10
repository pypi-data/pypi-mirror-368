"""Custom exceptions with helpful error messages for darkfield CLI"""

from rich.console import Console
from typing import Optional

console = Console()

class DarkfieldError(Exception):
    """Base exception with helpful error messages"""
    
    def __init__(
        self,
        message: str,
        fix_hint: Optional[str] = None,
        doc_link: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.fix_hint = fix_hint
        self.doc_link = doc_link
        self.error_code = error_code or "ERR_UNKNOWN"
        super().__init__(self.message)
    
    def display(self):
        """Display formatted error to user"""
        console.print(f"\n[red]✗ Error:[/red] {self.message}")
        
        if self.fix_hint:
            console.print(f"[yellow]💡 Hint:[/yellow] {self.fix_hint}")
        
        if self.doc_link:
            console.print(f"[blue]📚 Docs:[/blue] {self.doc_link}")
        
        console.print(f"[dim]Error Code: {self.error_code}[/dim]\n")

class AuthenticationError(DarkfieldError):
    """Authentication related errors"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message or "Authentication failed",
            fix_hint="Run 'darkfield auth login' or set DARKFIELD_API_KEY environment variable",
            doc_link="https://darkfield.ai/docs/authentication",
            error_code="ERR_AUTH_001"
        )

class APIKeyError(DarkfieldError):
    """API key related errors"""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message or "Invalid or missing API key",
            fix_hint="Get an API key at https://darkfield.ai/auth or use 'darkfield auth login --api-key YOUR_KEY'",
            doc_link="https://darkfield.ai/docs/api-keys",
            error_code="ERR_AUTH_002"
        )

class DatasetError(DarkfieldError):
    """Dataset processing errors"""
    
    def __init__(self, filepath: str, original_error: Optional[Exception] = None):
        error_details = f": {str(original_error)}" if original_error else ""
        super().__init__(
            f"Failed to process dataset: {filepath}{error_details}",
            fix_hint="Check file encoding or try converting to UTF-8. Supported formats: CSV, JSON, JSONL, Parquet",
            doc_link="https://darkfield.ai/docs/datasets",
            error_code="ERR_DATA_001"
        )

class EncodingError(DarkfieldError):
    """File encoding errors"""
    
    def __init__(self, filepath: str, encoding: Optional[str] = None):
        super().__init__(
            f"Cannot read file {filepath} - encoding issues detected",
            fix_hint=f"Try converting the file to UTF-8 or use a different format. Detected encoding: {encoding or 'unknown'}",
            doc_link="https://darkfield.ai/docs/file-formats",
            error_code="ERR_DATA_002"
        )

class NetworkError(DarkfieldError):
    """Network and API connection errors"""
    
    def __init__(self, endpoint: Optional[str] = None, original_error: Optional[Exception] = None):
        error_details = f" to {endpoint}" if endpoint else ""
        super().__init__(
            f"Network connection failed{error_details}",
            fix_hint="Check your internet connection and firewall settings. You can also use offline mode for development.",
            doc_link="https://darkfield.ai/docs/troubleshooting#network",
            error_code="ERR_NET_001"
        )

class RateLimitError(DarkfieldError):
    """Rate limiting errors"""
    
    def __init__(self, retry_after: Optional[int] = None):
        retry_msg = f" Retry after {retry_after} seconds." if retry_after else ""
        super().__init__(
            f"Rate limit exceeded.{retry_msg}",
            fix_hint="Consider upgrading your plan for higher limits or batch your requests",
            doc_link="https://darkfield.ai/docs/rate-limits",
            error_code="ERR_RATE_001"
        )

class ConfigurationError(DarkfieldError):
    """Configuration and setup errors"""
    
    def __init__(self, config_item: str, message: Optional[str] = None):
        super().__init__(
            message or f"Configuration error: {config_item}",
            fix_hint=f"Check your configuration file or environment variables for {config_item}",
            doc_link="https://darkfield.ai/docs/configuration",
            error_code="ERR_CONFIG_001"
        )

class ModelError(DarkfieldError):
    """Model-related errors"""
    
    def __init__(self, model_name: str, message: Optional[str] = None):
        super().__init__(
            message or f"Model '{model_name}' not available",
            fix_hint="Check available models with 'darkfield models list' or use the default model",
            doc_link="https://darkfield.ai/docs/models",
            error_code="ERR_MODEL_001"
        )

class QuotaError(DarkfieldError):
    """Usage quota errors"""
    
    def __init__(self, resource: str, limit: Optional[int] = None):
        limit_msg = f" (limit: {limit})" if limit else ""
        super().__init__(
            f"Quota exceeded for {resource}{limit_msg}",
            fix_hint="Check your usage with 'darkfield billing usage' or upgrade your plan",
            doc_link="https://darkfield.ai/pricing",
            error_code="ERR_QUOTA_001"
        )

def handle_error(error: Exception, exit_code: int = 1):
    """
    Handle and display errors appropriately
    
    Args:
        error: The exception to handle
        exit_code: Exit code for the program (default: 1)
    """
    if isinstance(error, DarkfieldError):
        error.display()
    else:
        # Generic error handling
        console.print(f"\n[red]✗ Unexpected Error:[/red] {str(error)}")
        console.print("[yellow]💡 Hint:[/yellow] Try running with --debug flag for more details")
        console.print("[dim]If this persists, please report at https://github.com/darkfield-ai/cli/issues[/dim]\n")
    
    if exit_code:
        import sys
        sys.exit(exit_code)