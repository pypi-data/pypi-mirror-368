# Examples

Real-world examples showing how to use Highlander Enum in various scenarios.

## Table of Contents

1. [Command-Line Tools](#command-line-tools)
2. [Game Configuration](#game-configuration)
3. [Network Protocols](#network-protocols)
4. [File Processing](#file-processing)
5. [Web Server Settings](#web-server-settings)
6. [Advanced Patterns](#advanced-patterns)

## Command-Line Tools

### Basic CLI Tool

```python
import argparse
from highlander import OptionsFlag

class CLIFlags(OptionsFlag):
    # Verbosity levels (mutually exclusive)
    QUIET = 1, ["q", "quiet"], "Suppress all output"
    NORMAL = 2, ["n", "normal"], "Normal output level"
    VERBOSE = 4, ["v", "verbose"], "Verbose output"
    DEBUG = 8, ["d", "debug"], "Debug output", (QUIET, NORMAL, VERBOSE)

    # Output formats (mutually exclusive)
    TEXT = 16, ["t", "text"], "Plain text output"
    JSON = 32, ["j", "json"], "JSON formatted output"
    XML = 64, ["x", "xml"], "XML formatted output", (TEXT, JSON)

    # Independent options
    FORCE = 128, ["f", "force"], "Force operation without confirmation"
    DRY_RUN = 256, ["dry-run"], "Show what would be done without executing"

def create_cli_parser():
    """Create argument parser from OptionsFlag definition."""
    parser = argparse.ArgumentParser(description="Example CLI tool")

    # Add arguments based on flag definitions
    for flag in CLIFlags:
        # Create argument name
        arg_name = f"--{flag.name.lower().replace('_', '-')}"
        aliases = [f"--{alias}" for alias in flag.aliases if len(alias) > 1]
        short_aliases = [f"-{alias}" for alias in flag.aliases if len(alias) == 1]

        parser.add_argument(
            arg_name, *(aliases + short_aliases),
            action='store_true',
            help=flag.help
        )

    return parser

def parse_cli_flags(args) -> CLIFlags:
    """Convert parsed arguments to CLIFlags."""
    flags = CLIFlags(0)

    if args.quiet: flags |= CLIFlags.QUIET
    if args.normal: flags |= CLIFlags.NORMAL
    if args.verbose: flags |= CLIFlags.VERBOSE
    if args.debug: flags |= CLIFlags.DEBUG
    if args.text: flags |= CLIFlags.TEXT
    if args.json: flags |= CLIFlags.JSON
    if args.xml: flags |= CLIFlags.XML
    if args.force: flags |= CLIFlags.FORCE
    if args.dry_run: flags |= CLIFlags.DRY_RUN

    return flags

def main():
    parser = create_cli_parser()
    args = parser.parse_args()
    flags = parse_cli_flags(args)

    # Use the flags to control behavior
    if flags & CLIFlags.DEBUG:
        print("Debug mode enabled")
        print(f"Active flags: {flags}")
    elif flags & CLIFlags.VERBOSE:
        print("Verbose mode enabled")
    elif flags & CLIFlags.QUIET:
        pass  # Suppress output
    else:
        print("Normal operation")

    if flags & CLIFlags.DRY_RUN:
        print("DRY RUN: Would process files...")
    else:
        print("Processing files...")

if __name__ == "__main__":
    main()
```

### Advanced CLI with Configuration

```python
import argparse
import json
from enum import auto
from pathlib import Path

from highlander import OptionsFlag

class AppConfig(OptionsFlag):
    # Log levels (mutually exclusive)
    LOG_ERROR = auto(), ["log-error"], "Log errors only"
    LOG_WARN = auto(), ["log-warn"], "Log warnings and errors"
    LOG_INFO = auto(), ["log-info"], "Log info, warnings, and errors"
    LOG_DEBUG = auto(), ["log-debug"], "Log everything", (LOG_ERROR, LOG_WARN, LOG_INFO)

    # Performance modes (mutually exclusive)
    FAST = auto(), ["fast"], "Prioritize speed over accuracy"
    BALANCED = auto(), ["balanced"], "Balance speed and accuracy"
    ACCURATE = auto(), ["accurate"], "Prioritize accuracy over speed", (FAST, BALANCED)

    # Output options (mutually exclusive)
    STDOUT = auto(), ["stdout"], "Output to standard output"
    FILE = auto(), ["file"], "Output to file"
    BOTH = auto(), ["both"], "Output to both stdout and file", (STDOUT, FILE)

    # Feature flags (independent)
    COLORS = auto(), ["colors"], "Enable colored output"
    PROGRESS = auto(), ["progress"], "Show progress bars"
    TIMESTAMPS = auto(), ["timestamps"], "Include timestamps in output"

class ConfigManager:
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path("app.json")
        self.flags = AppConfig(0)

    def load_from_file(self) -> AppConfig:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            return AppConfig(0)

        with open(self.config_file) as f:
            data = json.load(f)

        flags = AppConfig(0)
        for flag_name, enabled in data.get("flags", {}).items():
            if enabled and hasattr(AppConfig, flag_name):
                flags |= getattr(AppConfig, flag_name)

        return flags

    def save_to_file(self, flags: AppConfig) -> None:
        """Save configuration to JSON file."""
        data = {
            "flags": {
                flag.name: bool(flags & flag)
                for flag in AppConfig
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def merge_cli_args(self, cli_flags: AppConfig) -> AppConfig:
        """Merge CLI arguments with file configuration."""
        # CLI arguments override file configuration
        return self.flags | cli_flags

# Usage example
def main():
    config_manager = ConfigManager()
    file_config = config_manager.load_from_file()

    # Parse CLI arguments (simplified)
    cli_config = AppConfig.LOG_INFO | AppConfig.FAST | AppConfig.COLORS

    # Merge configurations
    final_config = config_manager.merge_cli_args(cli_config)

    print(f"Final configuration: {final_config}")

    # Save the final configuration
    config_manager.save_to_file(final_config)
```

## Game Configuration

### Graphics Settings Manager

```python
from enum import auto

from highlander import ExFlag

class GraphicsSettings(ExFlag):
    # Quality presets (mutually exclusive)
    QUALITY_LOW = auto()
    QUALITY_MEDIUM = auto()
    QUALITY_HIGH = auto()
    QUALITY_ULTRA = auto(), (QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH)

    # Resolution scaling (mutually exclusive)
    SCALE_50 = auto()
    SCALE_75 = auto()
    SCALE_100 = auto()
    SCALE_125 = auto()
    SCALE_150 = auto(), (SCALE_50, SCALE_75, SCALE_100, SCALE_125)

    # Anti-aliasing (mutually exclusive)
    AA_OFF = auto()
    AA_FXAA = auto()
    AA_MSAA_2X = auto()
    AA_MSAA_4X = auto()
    AA_MSAA_8X = auto(), (AA_OFF, AA_FXAA, AA_MSAA_2X, AA_MSAA_4X)

    # Independent features
    VSYNC = auto()
    HDR = auto()
    RAY_TRACING = auto()
    MOTION_BLUR = auto()

class GameConfig:
    def __init__(self):
        # Default to medium quality, 100% scale, FXAA, no extras
        self.graphics = (GraphicsSettings.QUALITY_MEDIUM |
                        GraphicsSettings.SCALE_100 |
                        GraphicsSettings.AA_FXAA)

        self.performance_profile = "balanced"

    def apply_preset(self, preset: str) -> None:
        """Apply a graphics preset."""
        presets = {
            "low": (GraphicsSettings.QUALITY_LOW |
                   GraphicsSettings.SCALE_75 |
                   GraphicsSettings.AA_OFF),

            "medium": (GraphicsSettings.QUALITY_MEDIUM |
                      GraphicsSettings.SCALE_100 |
                      GraphicsSettings.AA_FXAA),

            "high": (GraphicsSettings.QUALITY_HIGH |
                    GraphicsSettings.SCALE_100 |
                    GraphicsSettings.AA_MSAA_4X |
                    GraphicsSettings.VSYNC),

            "ultra": (GraphicsSettings.QUALITY_ULTRA |
                     GraphicsSettings.SCALE_125 |
                     GraphicsSettings.AA_MSAA_8X |
                     GraphicsSettings.VSYNC |
                     GraphicsSettings.HDR |
                     GraphicsSettings.RAY_TRACING)
        }

        if preset in presets:
            self.graphics = presets[preset]
            self.performance_profile = preset

    def toggle_feature(self, feature: GraphicsSettings) -> None:
        """Toggle an independent feature on/off."""
        independent_features = {
            GraphicsSettings.VSYNC,
            GraphicsSettings.HDR,
            GraphicsSettings.RAY_TRACING,
            GraphicsSettings.MOTION_BLUR
        }

        if feature in independent_features:
            self.graphics ^= feature

    def get_performance_impact(self) -> str:
        """Estimate performance impact of current settings."""
        impact_score = 0

        # Quality impact
        if self.graphics & GraphicsSettings.QUALITY_ULTRA:
            impact_score += 4
        elif self.graphics & GraphicsSettings.QUALITY_HIGH:
            impact_score += 3
        elif self.graphics & GraphicsSettings.QUALITY_MEDIUM:
            impact_score += 2
        else:
            impact_score += 1

        # Anti-aliasing impact
        if self.graphics & GraphicsSettings.AA_MSAA_8X:
            impact_score += 4
        elif self.graphics & GraphicsSettings.AA_MSAA_4X:
            impact_score += 3
        elif self.graphics & GraphicsSettings.AA_MSAA_2X:
            impact_score += 2
        elif self.graphics & GraphicsSettings.AA_FXAA:
            impact_score += 1

        # Feature impact
        if self.graphics & GraphicsSettings.RAY_TRACING:
            impact_score += 3
        if self.graphics & GraphicsSettings.HDR:
            impact_score += 1
        if self.graphics & GraphicsSettings.MOTION_BLUR:
            impact_score += 1

        if impact_score <= 3:
            return "Low"
        elif impact_score <= 6:
            return "Medium"
        elif impact_score <= 9:
            return "High"
        else:
            return "Very High"

    def get_summary(self) -> dict:
        """Get a summary of current settings."""
        settings = {}

        # Determine quality level
        for quality in [GraphicsSettings.QUALITY_LOW, GraphicsSettings.QUALITY_MEDIUM,
                       GraphicsSettings.QUALITY_HIGH, GraphicsSettings.QUALITY_ULTRA]:
            if self.graphics & quality:
                settings["quality"] = quality.name.split("_")[1].lower()
                break

        # Determine scale
        for scale in [GraphicsSettings.SCALE_50, GraphicsSettings.SCALE_75,
                     GraphicsSettings.SCALE_100, GraphicsSettings.SCALE_125,
                     GraphicsSettings.SCALE_150]:
            if self.graphics & scale:
                settings["scale"] = scale.name.split("_")[1] + "%"
                break

        # Determine anti-aliasing
        for aa in [GraphicsSettings.AA_OFF, GraphicsSettings.AA_FXAA,
                  GraphicsSettings.AA_MSAA_2X, GraphicsSettings.AA_MSAA_4X,
                  GraphicsSettings.AA_MSAA_8X]:
            if self.graphics & aa:
                settings["antialiasing"] = aa.name.replace("AA_", "").replace("_", " ")
                break

        # Check features
        features = []
        if self.graphics & GraphicsSettings.VSYNC:
            features.append("V-Sync")
        if self.graphics & GraphicsSettings.HDR:
            features.append("HDR")
        if self.graphics & GraphicsSettings.RAY_TRACING:
            features.append("Ray Tracing")
        if self.graphics & GraphicsSettings.MOTION_BLUR:
            features.append("Motion Blur")

        settings["features"] = features
        settings["performance_impact"] = self.get_performance_impact()

        return settings

# Usage example
def main():
    config = GameConfig()

    print("Default settings:")
    print(config.get_summary())

    print("\nApplying ultra preset:")
    config.apply_preset("ultra")
    print(config.get_summary())

    print("\nToggling ray tracing off:")
    config.toggle_feature(GraphicsSettings.RAY_TRACING)
    print(config.get_summary())

if __name__ == "__main__":
    main()
```

## Network Protocols

### Connection Manager

```python
import socket
import ssl
from enum import auto

from highlander import ExFlag

class ConnectionFlags(ExFlag):
    # Protocol versions (mutually exclusive)
    IPV4 = auto()
    IPV6 = auto()
    DUAL_STACK = auto(), (IPV4, IPV6)

    # Security levels (mutually exclusive)
    PLAINTEXT = auto()
    TLS_1_2 = auto()
    TLS_1_3 = auto(), (PLAINTEXT, TLS_1_2)

    # Connection modes (mutually exclusive)
    BLOCKING = auto()
    NON_BLOCKING = auto()
    ASYNC = auto(), (BLOCKING, NON_BLOCKING)

    # Features (independent)
    COMPRESSION = auto()
    KEEPALIVE = auto()
    NAGLE_DISABLED = auto()
    BUFFER_OPTIMIZATION = auto()

class NetworkConnection:
    def __init__(self, host: str, port: int, flags: ConnectionFlags = None):
        self.host = host
        self.port = port
        self.flags = flags or (ConnectionFlags.IPV4 |
                              ConnectionFlags.TLS_1_3 |
                              ConnectionFlags.NON_BLOCKING)
        self.socket = None
        self.ssl_context = None

    def _create_socket(self) -> socket.socket:
        """Create socket based on flags."""
        if self.flags & ConnectionFlags.IPV6:
            family = socket.AF_INET6
        elif self.flags & ConnectionFlags.DUAL_STACK:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        sock = socket.socket(family, socket.SOCK_STREAM)

        # Apply socket options based on flags
        if self.flags & ConnectionFlags.KEEPALIVE:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        if self.flags & ConnectionFlags.NAGLE_DISABLED:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if self.flags & ConnectionFlags.NON_BLOCKING:
            sock.setblocking(False)

        return sock

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context based on flags."""
        if self.flags & ConnectionFlags.PLAINTEXT:
            return None

        if self.flags & ConnectionFlags.TLS_1_3:
            context = ssl.create_default_context()
            context.minimum_version = ssl.TLSVersion.TLSv1_3
        elif self.flags & ConnectionFlags.TLS_1_2:
            context = ssl.create_default_context()
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            context = ssl.create_default_context()

        return context

    def connect(self) -> bool:
        """Establish connection with configured flags."""
        try:
            self.socket = self._create_socket()

            # Connect to remote host
            if self.flags & ConnectionFlags.DUAL_STACK:
                # Try IPv6 first, fallback to IPv4
                try:
                    self.socket.connect((self.host, self.port))
                except (socket.gaierror, ConnectionRefusedError):
                    self.socket.close()
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((self.host, self.port))
            else:
                self.socket.connect((self.host, self.port))

            # Wrap with SSL if needed
            if not (self.flags & ConnectionFlags.PLAINTEXT):
                self.ssl_context = self._create_ssl_context()
                self.socket = self.ssl_context.wrap_socket(
                    self.socket, server_hostname=self.host
                )

            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            if self.socket:
                self.socket.close()
            return False

    def get_connection_info(self) -> dict:
        """Get information about the current connection."""
        info = {
            "host": self.host,
            "port": self.port,
            "protocol": "IPv6" if self.flags & ConnectionFlags.IPV6 else "IPv4",
            "security": "TLS 1.3" if self.flags & ConnectionFlags.TLS_1_3 else
                       "TLS 1.2" if self.flags & ConnectionFlags.TLS_1_2 else "Plaintext",
            "mode": "Async" if self.flags & ConnectionFlags.ASYNC else
                   "Non-blocking" if self.flags & ConnectionFlags.NON_BLOCKING else "Blocking",
            "features": []
        }

        if self.flags & ConnectionFlags.COMPRESSION:
            info["features"].append("Compression")
        if self.flags & ConnectionFlags.KEEPALIVE:
            info["features"].append("Keep-Alive")
        if self.flags & ConnectionFlags.NAGLE_DISABLED:
            info["features"].append("Nagle Disabled")
        if self.flags & ConnectionFlags.BUFFER_OPTIMIZATION:
            info["features"].append("Buffer Optimization")

        return info

# Usage example
def main():
    # Create secure connection with compression
    flags = (ConnectionFlags.IPV4 |
             ConnectionFlags.TLS_1_3 |
             ConnectionFlags.NON_BLOCKING |
             ConnectionFlags.COMPRESSION |
             ConnectionFlags.KEEPALIVE)

    conn = NetworkConnection("example.com", 443, flags)

    print("Connection configuration:")
    print(conn.get_connection_info())

    # Connection will be resolved automatically - TLS_1_3 wins over conflicting options
    print(f"Active flags: {conn.flags}")

if __name__ == "__main__":
    main()
```

## File Processing

### File Processor with Multiple Modes

```python
import gzip
import json
import os
from pathlib import Path
from typing import List, Dict, Any

from highlander import OptionsFlag

class ProcessorOptions(OptionsFlag):
    # Verbosity (mutually exclusive)
    SILENT = 1, ["s", "silent"], "No output except errors"
    NORMAL = 2, ["n", "normal"], "Standard output"
    VERBOSE = 4, ["v", "verbose"], "Detailed output"
    DEBUG = 8, ["d", "debug"], "Debug output", (SILENT, NORMAL, VERBOSE)

    # Processing modes (mutually exclusive)
    FAST = 16, ["f", "fast"], "Fast processing (may skip some optimizations)"
    BALANCED = 32, ["b", "balanced"], "Balanced speed/quality"
    THOROUGH = 64, ["t", "thorough"], "Thorough processing", (FAST, BALANCED)

    # Output formats (mutually exclusive)
    JSON_OUTPUT = 128, ["json"], "Output in JSON format"
    XML_OUTPUT = 256, ["xml"], "Output in XML format"
    CSV_OUTPUT = 512, ["csv"], "Output in CSV format"
    PLAIN_OUTPUT = 1024, ["plain"], "Plain text output", (JSON_OUTPUT, XML_OUTPUT, CSV_OUTPUT)

    # Features (independent)
    BACKUP = 2048, ["backup"], "Create backup files"
    COMPRESS = 4096, ["compress"], "Compress output files"
    VALIDATE = 8192, ["validate"], "Validate input files"
    PARALLEL = 16384, ["parallel"], "Use parallel processing"

class FileProcessor:
    def __init__(self, options: ProcessorOptions = None):
        self.options = options or (ProcessorOptions.NORMAL |
                                  ProcessorOptions.BALANCED |
                                  ProcessorOptions.JSON_OUTPUT)
        self.processed_files: List[Path] = []
        self.errors: List[str] = []
        self.stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "total_size": 0,
            "processing_time": 0
        }

    def _log(self, message: str, level: str = "info") -> None:
        """Log message based on verbosity settings."""
        if self.options & ProcessorOptions.SILENT and level != "error":
            return

        if level == "debug" and not (self.options & ProcessorOptions.DEBUG):
            return

        if level == "verbose" and not (self.options & (ProcessorOptions.VERBOSE | ProcessorOptions.DEBUG)):
            return

        prefix = {
            "error": "ERROR: ",
            "debug": "DEBUG: ",
            "verbose": "VERBOSE: ",
            "info": ""
        }.get(level, "")

        print(f"{prefix}{message}")

    def _create_backup(self, file_path: Path) -> bool:
        """Create backup file if backup option is enabled."""
        if not (self.options & ProcessorOptions.BACKUP):
            return True

        try:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
            backup_path.write_bytes(file_path.read_bytes())
            self._log(f"Created backup: {backup_path}", "verbose")
            return True
        except Exception as e:
            self._log(f"Failed to create backup for {file_path}: {e}", "error")
            return False

    def _validate_file(self, file_path: Path) -> bool:
        """Validate input file if validation is enabled."""
        if not (self.options & ProcessorOptions.VALIDATE):
            return True

        try:
            # Simple validation - check if file is readable and not empty
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if file_path.stat().st_size == 0:
                raise ValueError(f"File is empty: {file_path}")

            # Try to read first few bytes
            with open(file_path, 'rb') as f:
                f.read(1024)

            self._log(f"Validated: {file_path}", "debug")
            return True

        except Exception as e:
            self._log(f"Validation failed for {file_path}: {e}", "error")
            return False

    def _process_file_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Process file content based on processing mode."""
        result = {
            "file": str(file_path),
            "size": len(content),
            "lines": len(content.splitlines())
        }

        if self.options & ProcessorOptions.FAST:
            # Fast processing - minimal analysis
            result["word_count"] = len(content.split())

        elif self.options & ProcessorOptions.BALANCED:
            # Balanced processing - moderate analysis
            lines = content.splitlines()
            result.update({
                "word_count": len(content.split()),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "average_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0
            })

        elif self.options & ProcessorOptions.THOROUGH:
            # Thorough processing - detailed analysis
            lines = content.splitlines()
            words = content.split()

            result.update({
                "word_count": len(words),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "average_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0,
                "unique_words": len(set(word.lower().strip('.,!?";') for word in words)),
                "character_frequency": dict(sorted(
                    {char: content.lower().count(char) for char in set(content.lower())}.items(),
                    key=lambda x: x[1], reverse=True
                )[:10])  # Top 10 characters
            })

        return result

    def _format_output(self, results: List[Dict[str, Any]]) -> str:
        """Format results based on output format option."""
        if self.options & ProcessorOptions.JSON_OUTPUT:
            return json.dumps(results, indent=2)

        elif self.options & ProcessorOptions.XML_OUTPUT:
            xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<results>']
            for result in results:
                xml_lines.append('  <file>')
                for key, value in result.items():
                    if isinstance(value, dict):
                        xml_lines.append(f'    <{key}>')
                        for k, v in value.items():
                            xml_lines.append(f'      <{k}>{v}</{k}>')
                        xml_lines.append(f'    </{key}>')
                    else:
                        xml_lines.append(f'    <{key}>{value}</{key}>')
                xml_lines.append('  </file>')
            xml_lines.append('</results>')
            return '\n'.join(xml_lines)

        elif self.options & ProcessorOptions.CSV_OUTPUT:
            if not results:
                return ""

            # Get all possible keys
            all_keys = set()
            for result in results:
                all_keys.update(result.keys())

            # Filter out nested dictionaries for CSV
            simple_keys = [k for k in all_keys if not isinstance(results[0].get(k), dict)]

            csv_lines = [','.join(simple_keys)]
            for result in results:
                values = [str(result.get(k, '')) for k in simple_keys]
                csv_lines.append(','.join(values))
            return '\n'.join(csv_lines)

        else:  # PLAIN_OUTPUT
            output_lines = []
            for result in results:
                output_lines.append(f"File: {result['file']}")
                for key, value in result.items():
                    if key != 'file' and not isinstance(value, dict):
                        output_lines.append(f"  {key}: {value}")
                output_lines.append("")  # Empty line between files
            return '\n'.join(output_lines)

    def _write_output(self, content: str, output_path: Path) -> None:
        """Write output content, optionally compressed."""
        try:
            if self.options & ProcessorOptions.COMPRESS:
                # Write compressed output
                compressed_path = output_path.with_suffix(f"{output_path.suffix}.gz")
                with gzip.open(compressed_path, 'wt', encoding='utf-8') as f:
                    f.write(content)
                self._log(f"Compressed output written to: {compressed_path}", "verbose")
            else:
                # Write regular output
                output_path.write_text(content, encoding='utf-8')
                self._log(f"Output written to: {output_path}", "verbose")

        except Exception as e:
            self._log(f"Failed to write output: {e}", "error")

    def process_files(self, input_files: List[Path], output_path: Path = None) -> Dict[str, Any]:
        """Process a list of input files."""
        import time

        start_time = time.time()
        results = []

        self._log(f"Processing {len(input_files)} files with options: {self.options}")

        for file_path in input_files:
            try:
                self._log(f"Processing: {file_path}", "verbose")

                # Validate file if enabled
                if not self._validate_file(file_path):
                    self.stats["files_skipped"] += 1
                    continue

                # Create backup if enabled
                if not self._create_backup(file_path):
                    self.stats["files_skipped"] += 1
                    continue

                # Read and process file content
                content = file_path.read_text(encoding='utf-8')
                result = self._process_file_content(content, file_path)
                results.append(result)

                self.stats["files_processed"] += 1
                self.stats["total_size"] += len(content)
                self.processed_files.append(file_path)

                self._log(f"Completed: {file_path} ({len(content)} bytes)", "debug")

            except Exception as e:
                error_msg = f"Failed to process {file_path}: {e}"
                self._log(error_msg, "error")
                self.errors.append(error_msg)
                self.stats["files_skipped"] += 1

        # Write output if specified
        if output_path and results:
            formatted_output = self._format_output(results)
            self._write_output(formatted_output, output_path)

        self.stats["processing_time"] = time.time() - start_time

        # Print summary
        self._log(f"Processing complete:", "info")
        self._log(f"  Files processed: {self.stats['files_processed']}", "info")
        self._log(f"  Files skipped: {self.stats['files_skipped']}", "info")
        self._log(f"  Total size: {self.stats['total_size']} bytes", "info")
        self._log(f"  Processing time: {self.stats['processing_time']:.2f} seconds", "info")

        return {
            "results": results,
            "stats": self.stats,
            "errors": self.errors
        }

# Usage example
def main():
    # Create some test files
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    test_files = []
    for i in range(3):
        test_file = test_dir / f"test_{i}.txt"
        test_file.write_text(f"This is test file {i}\n" * (10 + i * 5))
        test_files.append(test_file)

    # Configure processor with thorough processing, validation, backup, and JSON output
    options = (ProcessorOptions.VERBOSE |
              ProcessorOptions.THOROUGH |
              ProcessorOptions.JSON_OUTPUT |
              ProcessorOptions.VALIDATE |
              ProcessorOptions.BACKUP |
              ProcessorOptions.COMPRESS)

    processor = FileProcessor(options)

    # Process files
    output_path = Path("results.json")
    result = processor.process_files(test_files, output_path)

    print(f"\nProcessing results:")
    print(f"Successfully processed: {len(result['results'])} files")
    print(f"Errors: {len(result['errors'])}")

    # Clean up test files
    import shutil
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    main()
```

## Web Server Settings

### HTTP Server Configuration

```python
from highlander import ExFlag
from typing import Dict, Any
import ssl

class ServerFlags(ExFlag):
    # HTTP versions (mutually exclusive)
    HTTP_1_0 = 1
    HTTP_1_1 = 2
    HTTP_2 = 4
    HTTP_3 = 8, (HTTP_1_0, HTTP_1_1, HTTP_2)

    # SSL/TLS versions (mutually exclusive)
    NO_SSL = 16
    TLS_1_2 = 32
    TLS_1_3 = 64, (NO_SSL, TLS_1_2)

    # Compression (mutually exclusive)
    NO_COMPRESSION = 128
    GZIP = 256
    BROTLI = 512, (NO_COMPRESSION, GZIP)

    # Security features (independent)
    HSTS = 1024
    CSP = 2048
    CORS = 4096
    RATE_LIMITING = 8192

    # Performance features (independent)
    CACHING = 16384
    CONNECTION_POOLING = 32768
    LOAD_BALANCING = 65536

class WebServer:
    def __init__(self, name: str, port: int, flags: ServerFlags = None):
        self.name = name
        self.port = port
        self.flags = flags or (ServerFlags.HTTP_1_1 |
                              ServerFlags.TLS_1_3 |
                              ServerFlags.GZIP |
                              ServerFlags.CACHING)

    def get_configuration(self) -> Dict[str, Any]:
        """Get server configuration based on flags."""
        config = {
            "server_name": self.name,
            "port": self.port,
            "protocols": [],
            "security": {},
            "compression": "none",
            "features": []
        }

        # Determine HTTP version
        if self.flags & ServerFlags.HTTP_3:
            config["protocols"] = ["HTTP/3", "HTTP/2", "HTTP/1.1"]
        elif self.flags & ServerFlags.HTTP_2:
            config["protocols"] = ["HTTP/2", "HTTP/1.1"]
        elif self.flags & ServerFlags.HTTP_1_1:
            config["protocols"] = ["HTTP/1.1"]
        elif self.flags & ServerFlags.HTTP_1_0:
            config["protocols"] = ["HTTP/1.0"]

        # Determine SSL/TLS
        if self.flags & ServerFlags.TLS_1_3:
            config["security"]["tls_version"] = "1.3"
            config["security"]["ssl_enabled"] = True
        elif self.flags & ServerFlags.TLS_1_2:
            config["security"]["tls_version"] = "1.2"
            config["security"]["ssl_enabled"] = True
        else:
            config["security"]["ssl_enabled"] = False

        # Security features
        if self.flags & ServerFlags.HSTS:
            config["security"]["hsts"] = True
        if self.flags & ServerFlags.CSP:
            config["security"]["csp"] = True
        if self.flags & ServerFlags.CORS:
            config["security"]["cors"] = True
        if self.flags & ServerFlags.RATE_LIMITING:
            config["security"]["rate_limiting"] = True

        # Compression
        if self.flags & ServerFlags.BROTLI:
            config["compression"] = "brotli"
        elif self.flags & ServerFlags.GZIP:
            config["compression"] = "gzip"

        # Performance features
        if self.flags & ServerFlags.CACHING:
            config["features"].append("caching")
        if self.flags & ServerFlags.CONNECTION_POOLING:
            config["features"].append("connection_pooling")
        if self.flags & ServerFlags.LOAD_BALANCING:
            config["features"].append("load_balancing")

        return config

    def generate_nginx_config(self) -> str:
        """Generate nginx configuration based on flags."""
        config_lines = [
            "server {",
            f"    listen {self.port};",
            f"    server_name {self.name};",
            ""
        ]

        # SSL configuration
        if self.flags & (ServerFlags.TLS_1_2 | ServerFlags.TLS_1_3):
            config_lines.extend([
                f"    listen {self.port} ssl;",
                "    ssl_certificate /path/to/cert.pem;",
                "    ssl_certificate_key /path/to/key.pem;",
            ])

            if self.flags & ServerFlags.TLS_1_3:
                config_lines.append("    ssl_protocols TLSv1.3;")
            elif self.flags & ServerFlags.TLS_1_2:
                config_lines.append("    ssl_protocols TLSv1.2 TLSv1.3;")

        # HTTP version support
        if self.flags & ServerFlags.HTTP_2:
            config_lines.append("    http2 on;")

        # Compression
        if self.flags & ServerFlags.GZIP:
            config_lines.extend([
                "    gzip on;",
                "    gzip_types text/plain application/json text/css;",
            ])
        elif self.flags & ServerFlags.BROTLI:
            config_lines.extend([
                "    brotli on;",
                "    brotli_types text/plain application/json text/css;",
            ])

        # Security headers
        if self.flags & ServerFlags.HSTS:
            config_lines.append("    add_header Strict-Transport-Security \"max-age=31536000\";")

        if self.flags & ServerFlags.CSP:
            config_lines.append("    add_header Content-Security-Policy \"default-src 'self'\";")

        if self.flags & ServerFlags.CORS:
            config_lines.append("    add_header Access-Control-Allow-Origin \"*\";")

        # Rate limiting
        if self.flags & ServerFlags.RATE_LIMITING:
            config_lines.append("    limit_req zone=api burst=20 nodelay;")

        # Caching
        if self.flags & ServerFlags.CACHING:
            config_lines.extend([
                "    location ~* \\.(jpg|jpeg|png|gif|ico|css|js)$ {",
                "        expires 1y;",
                "        add_header Cache-Control \"public\";",
                "    }",
            ])

        config_lines.append("}")
        return "\n".join(config_lines)

    def get_performance_score(self) -> int:
        """Calculate performance score based on configuration."""
        score = 0

        # HTTP version benefits
        if self.flags & ServerFlags.HTTP_3:
            score += 40
        elif self.flags & ServerFlags.HTTP_2:
            score += 30
        elif self.flags & ServerFlags.HTTP_1_1:
            score += 20
        else:
            score += 10

        # Compression benefits
        if self.flags & ServerFlags.BROTLI:
            score += 25
        elif self.flags & ServerFlags.GZIP:
            score += 15

        # Caching benefit
        if self.flags & ServerFlags.CACHING:
            score += 20

        # Connection pooling benefit
        if self.flags & ServerFlags.CONNECTION_POOLING:
            score += 10

        # Load balancing benefit
        if self.flags & ServerFlags.LOAD_BALANCING:
            score += 15

        return min(score, 100)  # Cap at 100

# Usage example
def main():
    # Create a high-performance secure server
    server = WebServer(
        "api.example.com",
        443,
        ServerFlags.HTTP_2 |
        ServerFlags.TLS_1_3 |
        ServerFlags.BROTLI |
        ServerFlags.HSTS |
        ServerFlags.CSP |
        ServerFlags.RATE_LIMITING |
        ServerFlags.CACHING |
        ServerFlags.CONNECTION_POOLING
    )

    print("Server Configuration:")
    config = server.get_configuration()
    for key, value in config.items():
        print(f"  {key}: {value}")

    print(f"\nPerformance Score: {server.get_performance_score()}/100")

    print(f"\nNginx Configuration:")
    print(server.generate_nginx_config())

if __name__ == "__main__":
    main()
```

## Advanced Patterns

### State Machine with Exclusions

```python
from typing import Set, Dict, Callable

from highlander import ExFlag, STRICT

class WorkflowState(ExFlag, conflict=STRICT):
    # Initial states (mutually exclusive)
    CREATED = 1
    INITIALIZED = 2, (CREATED,)

    # Processing states (mutually exclusive with initial and final)
    PROCESSING = 4
    PAUSED = 8
    RETRYING = 16, (CREATED, INITIALIZED, PROCESSING, PAUSED)

    # Final states (mutually exclusive with all others)
    COMPLETED = 32
    FAILED = 64
    CANCELLED = 128, (CREATED, INITIALIZED, PROCESSING, PAUSED, RETRYING, COMPLETED, FAILED)
WorkflowState

class WorkflowStateMachine:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.current_state = WorkflowState.CREATED
        self.state_history: List[WorkflowState] = [self.current_state]

        # Define valid transitions
        self.valid_transitions: Dict[WorkflowState, Set[WorkflowState]] = {
            WorkflowState.CREATED: {WorkflowState.INITIALIZED, WorkflowState.CANCELLED},
            WorkflowState.INITIALIZED: {WorkflowState.PROCESSING, WorkflowState.CANCELLED},
            WorkflowState.PROCESSING: {WorkflowState.COMPLETED, WorkflowState.FAILED,
                                     WorkflowState.PAUSED, WorkflowState.CANCELLED},
            WorkflowState.PAUSED: {WorkflowState.PROCESSING, WorkflowState.CANCELLED},
            WorkflowState.RETRYING: {WorkflowState.PROCESSING, WorkflowState.FAILED,
                                   WorkflowState.CANCELLED},
            WorkflowState.COMPLETED: set(),  # Terminal state
            WorkflowState.FAILED: {WorkflowState.RETRYING, WorkflowState.CANCELLED},
            WorkflowState.CANCELLED: set()   # Terminal state
        }

        # State handlers
        self.state_handlers: Dict[WorkflowState, Callable] = {
            WorkflowState.INITIALIZED: self._on_initialized,
            WorkflowState.PROCESSING: self._on_processing,
            WorkflowState.PAUSED: self._on_paused,
            WorkflowState.RETRYING: self._on_retrying,
            WorkflowState.COMPLETED: self._on_completed,
            WorkflowState.FAILED: self._on_failed,
            WorkflowState.CANCELLED: self._on_cancelled
        }

    def transition_to(self, new_state: WorkflowState) -> bool:
        """Attempt to transition to a new state."""
        try:
            # Check if transition is valid
            if new_state not in self.valid_transitions[self.current_state]:
                raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")

            # Attempt the state change (will raise if exclusions conflict)
            test_state = self.current_state | new_state

            # If we get here, transition is valid
            old_state = self.current_state
            self.current_state = new_state
            self.state_history.append(new_state)

            print(f"Workflow {self.workflow_id}: {old_state} → {new_state}")

            # Execute state handler
            if new_state in self.state_handlers:
                self.state_handlers[new_state]()

            return True

        except (ValueError, TypeError) as e:
            print(f"Transition failed: {e}")
            return False

    def _on_initialized(self):
        print(f"  Workflow {self.workflow_id} initialized and ready for processing")

    def _on_processing(self):
        print(f"  Workflow {self.workflow_id} is now processing")

    def _on_paused(self):
        print(f"  Workflow {self.workflow_id} has been paused")

    def _on_retrying(self):
        print(f"  Workflow {self.workflow_id} is retrying after failure")

    def _on_completed(self):
        print(f"  Workflow {self.workflow_id} completed successfully")

    def _on_failed(self):
        print(f"  Workflow {self.workflow_id} failed")

    def _on_cancelled(self):
        print(f"  Workflow {self.workflow_id} was cancelled")

    def get_available_transitions(self) -> Set[WorkflowState]:
        """Get states that can be transitioned to from current state."""
        return self.valid_transitions[self.current_state]

    def is_terminal(self) -> bool:
        """Check if current state is terminal."""
        return len(self.valid_transitions[self.current_state]) == 0

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state machine."""
        return {
            "workflow_id": self.workflow_id,
            "current_state": self.current_state.name,
            "is_terminal": self.is_terminal(),
            "available_transitions": [state.name for state in self.get_available_transitions()],
            "state_history": [state.name for state in self.state_history]
        }

# Usage example
def main():
    # Create a workflow
    workflow = WorkflowStateMachine("WF-001")

    print("Initial state:")
    print(workflow.get_state_summary())
    print()

    # Execute a typical workflow
    transitions = [
        WorkflowState.INITIALIZED,
        WorkflowState.PROCESSING,
        WorkflowState.PAUSED,
        WorkflowState.PROCESSING,
        WorkflowState.COMPLETED
    ]

    for next_state in transitions:
        success = workflow.transition_to(next_state)
        if not success:
            print("Workflow execution stopped due to invalid transition")
            break
        print(f"Available next states: {[s.name for s in workflow.get_available_transitions()]}")
        print()

    print("Final state:")
    print(workflow.get_state_summary())

    # Demonstrate invalid transition attempt
    print("\nAttempting invalid transition from terminal state:")
    workflow.transition_to(WorkflowState.PROCESSING)

if __name__ == "__main__":
    main()
```

These examples demonstrate the power and flexibility of Highlander Enum across various domains. Each example shows different aspects:

1. **Mutual exclusion** ensuring only one option from conflicting groups can be active
2. **Conflict resolution** handling what happens when conflicts occur
3. **Rich metadata** with `OptionsFlag` for building user interfaces
4. **Complex state management** with multiple exclusion groups
5. **Integration patterns** with existing libraries and frameworks
6. **Type safety** and IDE support throughout

The key takeaway is that Highlander Enum provides a robust foundation for managing complex flag relationships while maintaining clean, readable code.
