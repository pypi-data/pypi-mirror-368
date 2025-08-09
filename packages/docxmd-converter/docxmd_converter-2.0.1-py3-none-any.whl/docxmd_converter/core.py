"""
Core functionality for document conversion between .docx and .md formats.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import pypandoc


class ConversionError(Exception):
    """Custom exception for conversion errors."""

    pass


class DocxMdConverter:
    """Main converter class for .docx ⇄ .md conversion."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = self._setup_logging(log_level)
        self._check_pandoc()

    def _setup_logging(self, level: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, level.upper()))

        # Create console handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _check_pandoc(self) -> None:
        """Check if pandoc is available."""
        try:
            version = pypandoc.get_pandoc_version()
            self.logger.info(f"Pandoc version: {version}")
        except OSError:
            raise ConversionError(
                "Pandoc is not installed. Please install pandoc first.\n"
                "Visit: https://pandoc.org/installing.html"
            )

    def convert_file(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        format: str,
        template_path: Optional[Union[str, Path]] = None,
    ) -> bool:
        """Convert a single file.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            format: Conversion format ('docx2md' or 'md2docx')
            template_path: Path to .docx template (for md2docx only)

        Returns:
            True if conversion successful, False otherwise
        """
        input_file = Path(input_file)
        output_file = Path(output_file)

        if not input_file.exists():
            self.logger.error(f"Input file does not exist: {input_file}")
            return False

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "docx2md":
                self._convert_docx_to_md(input_file, output_file)
            elif format == "md2docx":
                self._convert_md_to_docx(
                    input_file,
                    output_file,
                    Path(template_path) if template_path else None,
                )
            else:
                raise ConversionError(f"Invalid format: {format}")

            self.logger.info(f"Successfully converted: {input_file} -> {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to convert {input_file}: {str(e)}")
            return False

    def _convert_docx_to_md(self, input_file: Path, output_file: Path) -> None:
        """Convert .docx to .md using pandoc."""
        extra_args = [
            "--extract-media",
            str(output_file.parent / "media"),
            "--wrap=none",
        ]

        pypandoc.convert_file(
            str(input_file), "md", outputfile=str(output_file), extra_args=extra_args
        )

    def _convert_md_to_docx(
        self, input_file: Path, output_file: Path, template_path: Optional[Path] = None
    ) -> None:
        """Convert .md to .docx using pandoc."""
        extra_args = []

        if template_path:
            template_path = Path(template_path)
            if template_path.exists():
                extra_args.extend(["--reference-doc", str(template_path)])
            else:
                self.logger.warning(f"Template not found: {template_path}")

        pypandoc.convert_file(
            str(input_file), "docx", outputfile=str(output_file), extra_args=extra_args
        )

    def convert_directory(
        self,
        src_dir: Union[str, Path],
        dst_dir: Union[str, Path],
        format: str,
        template_path: Optional[Union[str, Path]] = None,
        post_process: bool = False,
        processor_type: str = "basic",
        force_process: bool = False,
        dry_run_process: bool = False,
        report_format: str = "console",
        report_update: bool = False,
    ) -> Tuple[int, int, Optional[dict]]:
        """Convert all files in directory recursively with optional post-processing.

        Args:
            src_dir: Source directory path
            dst_dir: Destination directory path
            format: Conversion format ('docx2md' or 'md2docx')
            template_path: Path to .docx template (for md2docx only)
            post_process: Apply document processing after conversion
            processor_type: Type of processor to use ('basic' or 'advanced')
            force_process: Force processing of already processed files
            dry_run_process: Show what would be processed without making changes
            report_format: Report output format ('console' or 'file')
            report_update: Update existing report file instead of creating new one

        Returns:
            Tuple of (successful_conversions, total_files, processing_results)
        """
        src_dir = Path(src_dir)
        dst_dir = Path(dst_dir)

        if not src_dir.exists():
            raise ConversionError(f"Source directory does not exist: {src_dir}")

        # Determine file extension to search for
        if format == "docx2md":
            file_pattern = "*.docx"
            output_ext = ".md"
        elif format == "md2docx":
            file_pattern = "*.md"
            output_ext = ".docx"
        else:
            raise ConversionError(f"Invalid format: {format}")

        # Find all files to convert
        files_to_convert = list(src_dir.rglob(file_pattern))

        if not files_to_convert:
            self.logger.warning(f"No {file_pattern} files found in {src_dir}")

            # Still apply post-processing if requested, even without conversion
            processing_results = None
            if post_process:
                processing_results = self._apply_post_processing(
                    dst_dir if format == "docx2md" else src_dir,
                    processor_type,
                    force_process,
                    dry_run_process,
                    report_format,
                    report_update,
                )

            return 0, 0, processing_results

        successful_conversions = 0
        total_files = len(files_to_convert)

        self.logger.info(f"Found {total_files} files to convert")

        for input_file in files_to_convert:
            # Calculate relative path to preserve directory structure
            relative_path = input_file.relative_to(src_dir)
            output_file = dst_dir / relative_path.with_suffix(output_ext)

            if self.convert_file(input_file, output_file, format, template_path):
                successful_conversions += 1

        self.logger.info(
            f"Conversion completed: {successful_conversions}/{total_files} files"
        )

        # Apply post-processing if requested
        processing_results = None
        if post_process:
            processing_results = self._apply_post_processing(
                dst_dir if format == "docx2md" else src_dir,
                processor_type,
                force_process,
                dry_run_process,
                report_format,
                report_update,
            )

        return successful_conversions, total_files, processing_results

    def _apply_post_processing(
        self,
        process_dir: Union[str, Path],
        processor_type: str,
        force_process: bool,
        dry_run_process: bool,
        report_format: str,
        report_update: bool,
    ) -> dict:
        """Apply post-processing to converted files"""
        try:
            from .processor import DocumentProcessor
            from .reporting import ProcessingReporter

            self.logger.info(
                f"Starting post-processing with {processor_type} processor..."
            )

            # Initialize processor
            processor_kwargs = {}
            if processor_type == "advanced":
                processor_kwargs = {
                    "force_reprocess": force_process,
                    "dry_run": dry_run_process,
                }

            processor = DocumentProcessor(processor_type, **processor_kwargs)

            # Process files
            results = processor.process_directory(
                process_dir,
                force=force_process,
                dry_run=dry_run_process,
                pattern="*.md",
            )

            # Generate report
            reporter = ProcessingReporter()
            reporter.generate_report(
                results,
                format=report_format,
                update_existing=report_update,
                output_dir=process_dir,
            )

            processed_count = results.processed
            total_count = results.total
            msg = f"Post-processing completed: {processed_count}/{total_count} files processed"
            self.logger.info(msg)

            return results.to_dict()

        except Exception as e:
            self.logger.error(f"Post-processing failed: {str(e)}")
            return {"error": str(e), "processed": 0, "total": 0}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported conversion formats."""
        return ["docx2md", "md2docx"]

    def validate_template(self, template_path: Union[str, Path]) -> bool:
        """Validate if template file is a valid .docx file.

        Args:
            template_path: Path to template file

        Returns:
            True if valid, False otherwise
        """
        template_path = Path(template_path)

        if not template_path.exists():
            self.logger.error(f"Template file does not exist: {template_path}")
            return False

        if template_path.suffix.lower() != ".docx":
            self.logger.error(f"Template must be a .docx file: {template_path}")
            return False

        return True
