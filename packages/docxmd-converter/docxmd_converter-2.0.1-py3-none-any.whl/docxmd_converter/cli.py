"""
Command-line interface for DocxMD Converter.
"""

import argparse
import sys
from pathlib import Path

from .core import ConversionError, DocxMdConverter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="docxmd",
        description="Convert between .docx and .md files with template support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all .docx files to .md
  docxmd --src ./documents --dst ./markdown --format docx2md

  # Convert all .md files to .docx with template
  docxmd --src ./markdown --dst ./documents --format md2docx \\
         --template ./template.docx

  # Convert and apply post-processing
  docxmd --src ./documents --dst ./markdown --format docx2md \\
         --post-process --processor advanced --report file

  # Enable debug logging
  docxmd --src ./input --dst ./output --format docx2md --verbose
        """,
    )

    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="Source directory containing files to convert",
    )

    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help="Destination directory for converted files",
    )

    parser.add_argument(
        "--format",
        type=str,
        required=True,
        choices=["docx2md", "md2docx"],
        help="Conversion format: docx2md or md2docx",
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Path to .docx template file (only for md2docx direction)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    # Post-processing options
    parser.add_argument(
        "--post-process",
        action="store_true",
        help="Apply document processing after conversion",
    )

    parser.add_argument(
        "--processor",
        type=str,
        choices=["basic", "advanced"],
        default="basic",
        help="Document processor type (default: basic)",
    )

    parser.add_argument(
        "--report",
        type=str,
        choices=["console", "file"],
        default="console",
        help="Report output format (default: console)",
    )

    parser.add_argument(
        "--report-update",
        action="store_true",
        help="Update existing report file instead of creating dated version",
    )

    parser.add_argument(
        "--force-process",
        action="store_true",
        help="Force processing of already processed files",
    )

    parser.add_argument(
        "--dry-run-process",
        action="store_true",
        help="Show what would be processed without actual changes",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    src_path = Path(args.src)
    if not src_path.exists():
        raise ConversionError(f"Source directory does not exist: {args.src}")

    if not src_path.is_dir():
        raise ConversionError(f"Source path is not a directory: {args.src}")

    # Validate template if provided
    if args.template:
        if args.format != "md2docx":
            raise ConversionError("Template can only be used with md2docx format")

        template_path = Path(args.template)
        if not template_path.exists():
            raise ConversionError(f"Template file does not exist: {args.template}")

        if template_path.suffix.lower() != ".docx":
            raise ConversionError(f"Template must be a .docx file: {args.template}")


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Validate arguments
        validate_args(args)

        # Setup converter
        log_level = "DEBUG" if args.verbose else "INFO"
        converter = DocxMdConverter(log_level=log_level)

        # Convert files
        successful, total, processing_results = converter.convert_directory(
            src_dir=args.src,
            dst_dir=args.dst,
            format=args.format,
            template_path=args.template,
            post_process=args.post_process,
            processor_type=args.processor,
            force_process=args.force_process,
            dry_run_process=args.dry_run_process,
            report_format=args.report,
            report_update=args.report_update,
        )

        if successful == total:
            if args.post_process and processing_results:
                print(f"✅ Successfully converted all {total} files")
                if args.report == "console":
                    proc = processing_results['processed']
                    total = processing_results['total']
                    print(f"📋 Post-processing: {proc}/{total} files processed")
            else:
                print(f"✅ Successfully converted all {total} files")
            return 0
        else:
            print(f"⚠️  Converted {successful}/{total} files (some errors occurred)")
            if args.post_process and processing_results:
                processed = processing_results["processed"]
                total_proc = processing_results["total"]
                print(f"📋 Post-processing: {processed}/{total_proc} files processed")
            return 1

    except ConversionError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n❌ Conversion cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
