"""Enhanced response wrapper for ReqNinja."""

import json
from typing import Any, Dict
import requests
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


class ReqNinjaResponse:
    """Enhanced response wrapper with additional features."""
    
    def __init__(
        self,
        response: requests.Response,
        start_time: float,
        end_time: float
    ):
        self._response = response
        self.start_time = start_time
        self.end_time = end_time
        self._console = Console()
    
    @property
    def elapsed_seconds(self) -> float:
        """Get the elapsed time in seconds."""
        return self.end_time - self.start_time
    
    @property
    def elapsed_ms(self) -> float:
        """Get the elapsed time in milliseconds."""
        return (self.end_time - self.start_time) * 1000
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying response."""
        return getattr(self._response, name)
    
    def json(self, **kwargs) -> Any:
        """Get JSON data with enhanced error handling."""
        try:
            return self._response.json(**kwargs)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def pretty_print(
        self,
        show_headers: bool = False,
        max_width: int = 120
    ) -> None:
        """Pretty print the response with syntax highlighting."""
        # Status line
        if 200 <= self.status_code < 300:
            status_color = "green"
        elif self.status_code >= 400:
            status_color = "red"
        else:
            status_color = "yellow"

        status_text = Text(
            f"HTTP {self.status_code} {self.reason}",
            style=status_color
        )
        self._console.print(status_text)

        # Timing info
        timing_text = Text(f"⏱️  {self.elapsed_ms:.2f}ms", style="blue")
        self._console.print(timing_text)
        self._console.print()

        # Headers
        if show_headers:
            headers_table = Table(title="Response Headers", show_header=True)
            headers_table.add_column("Header", style="cyan")
            headers_table.add_column("Value", style="white")

            for key, value in self.headers.items():
                headers_table.add_row(key, value)

            self._console.print(headers_table)
            self._console.print()

        # Body
        content_type = self.headers.get('content-type', '').lower()

        if 'application/json' in content_type:
            try:
                json_data = self.json()
                json_str = json.dumps(
                    json_data, indent=2, ensure_ascii=False
                )
                syntax = Syntax(
                    json_str, "json", theme="monokai", line_numbers=False
                )
                self._console.print(syntax)
            except (ValueError, json.JSONDecodeError):
                self._console.print(Text(self.text, style="white"))
        elif content_type.startswith('text/'):
            # Try to detect if it's HTML, XML, etc.
            text_content = self.text
            if (text_content.strip().startswith('<?xml') or
                    text_content.strip().startswith('<')):
                syntax = Syntax(
                    text_content, "xml", theme="monokai",
                    line_numbers=False, word_wrap=True
                )
                self._console.print(syntax)
            elif (text_content.strip().startswith('<!DOCTYPE') or
                  '<html' in text_content.lower()):
                syntax = Syntax(
                    text_content, "html", theme="monokai",
                    line_numbers=False, word_wrap=True
                )
                self._console.print(syntax)
            else:
                self._console.print(Text(text_content, style="white"))
        else:
            # Binary or unknown content
            size_kb = len(self.content) / 1024
            self._console.print(
                f"[dim]Binary content ({size_kb:.1f} KB)[/dim]"
            )
    
    def save(self, filepath: str, format: str = "auto") -> None:
        """Save response to a file."""
        import os
        
        if format == "auto":
            format = "json" if filepath.endswith('.json') else "text"
        
        # Only create directories if there's a directory path
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        if format == "json":
            try:
                data = self.json()
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except (ValueError, json.JSONDecodeError):
                # Fallback to text if not valid JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.text)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.text)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to a dictionary for analysis."""
        return {
            "status_code": self.status_code,
            "reason": self.reason,
            "headers": dict(self.headers),
            "elapsed_ms": self.elapsed_ms,
            "url": self.url,
            "size_bytes": len(self.content),
            "content_type": self.headers.get('content-type', ''),
        }
    
    def __repr__(self) -> str:
        return (
            f"<ReqNinjaResponse [{self.status_code}] "
            f"{self.elapsed_ms:.2f}ms>"
        )
