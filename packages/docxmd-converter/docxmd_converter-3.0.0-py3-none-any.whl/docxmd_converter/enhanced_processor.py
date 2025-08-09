"""
Enhanced document processor with integrated formatting cleanup.
Final unified version combining all improvements from scripts/ directory.
Includes advanced document structuring and comprehensive artifact cleanup.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

from .processor import BaseDocumentProcessor, ProcessingResults


class EnhancedDocumentProcessor(BaseDocumentProcessor):
    """
    Enhanced document processor with comprehensive formatting cleanup.

    Features:
    - Complete КонсультантПлюс artifact removal
    - Advanced document structuring
    - Intelligent position name extraction
    - Comprehensive section formatting
    - Quality assessment and metadata
    - Safe document processing with skip logic
    """

    def __init__(self):
        """Initialize the enhanced processor."""
        super().__init__()
        self.version = "2.1.0"

    def clean_and_structure_document(self, content: str) -> str:
        """
        Comprehensive document cleaning and structuring.
        Combines all advanced formatting improvements.
        """
        # 1. Remove all formatting artifacts
        content = self._remove_all_artifacts(content)

        # 2. Extract position name
        position_name = self._extract_position_name(content)

        # 3. Structure document
        structured_content = self._structure_document(content, position_name)

        return structured_content

    def _remove_all_artifacts(self, content: str) -> str:
        """
        Advanced comprehensive artifact removal.
        Combines all cleaning techniques from various processors.
        """
        # Remove service blocks and separators (extended)
        content = re.sub(r'-{15,}.*?-{15,}', '', content, flags=re.DOTALL)
        content = re.sub(r'_{15,}', '', content)
        content = re.sub(r'─{15,}', '', content)
        content = re.sub(r'-- -- --', '', content)
        content = re.sub(r'-- -- -+ --.*?-- -- -+ --', '', content, flags=re.DOTALL)

        # Advanced КонсультантПлюс artifact removal
        content = re.sub(r'\+[-+\|]*\+.*?\+[-+\|]*\+', '', content, flags=re.DOTALL)
        content = re.sub(r'!\[.*?\]\(.*?media.*?\).*?\n', '', content)
        content = re.sub(r'!\[.*?\]\(.*?\){[^}]*}', '', content)
        content = re.sub(r'Форма:.*?\n', '', content)
        content = re.sub(r'\(Подготовлен для системы КонсультантПлюс.*?\)', '', content)
        content = re.sub(r'Документ предоставлен.*?www\.consultant\.ru.*?\n', '', content, flags=re.DOTALL)
        content = re.sub(r'Дата сохранения:.*?\n', '', content)
        content = re.sub(r'\*\*Актуально на.*?\*\*', '', content)
        content = re.sub(r'См\.:.*?Путеводитель.*?\n', '', content, flags=re.DOTALL)

        # Remove tables and structured data
        content = re.sub(r'\+[-+]+\+.*?\n', '', content)
        content = re.sub(r'\|.*?\|.*?\n', '', content)

        # Advanced backslash and formatting cleanup
        content = re.sub(r'\\\n', ' ', content)
        content = re.sub(r'\\\r\n', ' ', content)
        content = re.sub(r'\\-', '-', content)
        content = re.sub(r'\\', '', content)

        # Clean excessive whitespace
        content = re.sub(r' +', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content

    def _extract_position_name(self, content: str) -> str:
        """
        Advanced position name extraction.
        Combines filename parsing and content analysis.
        """
        # Check if already has title
        if content.startswith('# Должностная инструкция:'):
            match = re.search(r'# Должностная инструкция: (.+)', content)
            if match:
                return match.group(1).strip()

        # Extended search patterns for position names
        patterns = [
            # Specific professions
            r'\*\*(.+?граф.*?)\*\*',
            r'\*\*(.+?ист.*?)\*\*',
            r'\*\*(.+?лог.*?)\*\*',
            r'\*\*(.+?тор.*?)\*\*',
            r'\*\*(.+?нт.*?)\*\*',
            # General patterns
            r'\*\*([А-ЯЁ][а-яё]+(?:\s+[а-яё]+){0,2})\*\*',
            # Content-based extraction
            r'должность\s+([А-ЯЁ][а-яё]+(?:\s+[а-яё]+){0,2})',
            r'инструкция\s+([А-ЯЁ][а-яё]+(?:\s+[а-яё]+){0,2})'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                # Skip non-position words
                if position not in ['ДОЛЖНОСТНАЯ ИНСТРУКЦИЯ', 'УТВЕРЖДАЮ', 'СОГЛАСОВАНО', 'ОРГАНИЗАЦИЯ']:
                    return self.normalize_position_name(position)

        return "Специалист"

    def _structure_document(self, content: str, position_name: str) -> str:
        """Structure document with proper formatting."""
        # Extract sections from source content
        sections = self._extract_document_sections(content)

        # Build structured document
        doc = []

        # Header
        doc.append(f"# Должностная инструкция: {position_name}")
        doc.append("")

        # Document information
        doc.append("## Информация о документе")
        doc.append("")
        doc.append("**Организация:** `____________________________`")
        doc.append("")
        doc.append("**Должность руководителя:** `____________________________`")
        doc.append("")
        doc.append("**ФИО руководителя:** `____________________________`")
        doc.append("")
        doc.append("**Дата утверждения:** `____________________________`")
        doc.append("")
        doc.append("**Номер приказа:** `____________________________`")
        doc.append("")

        # 1. General provisions
        doc.append("## 1. Общие положения")
        doc.append("")
        if sections.get('general'):
            doc.extend(self._format_general_section(sections['general'], position_name))
        else:
            doc.append(f"1.1. {position_name} относится к категории специалистов.")
            doc.append("")
            doc.append("1.2. На должность принимается лицо, имеющее `____________________________`.")
            doc.append("")
            doc.append(f"1.3. {position_name} должен знать:")
            doc.append("- `____________________________`;")
            doc.append("- `____________________________`.")
            doc.append("")
            doc.append(f"1.4. {position_name} подчиняется непосредственно `____________________________`.")
            doc.append("")

        # 2. Functions
        doc.append("## 2. Функции")
        doc.append("")
        if sections.get('functions'):
            doc.extend(self._format_functions_section(sections['functions']))
        else:
            doc.append("Основные функции:")
            doc.append("- `____________________________`;")
            doc.append("- `____________________________`.")
            doc.append("")

        # 3. Duties
        doc.append("## 3. Должностные обязанности")
        doc.append("")
        doc.append(f"{position_name} исполняет следующие обязанности:")
        doc.append("")
        if sections.get('duties'):
            doc.extend(self._format_duties_section(sections['duties']))
        else:
            doc.append("3.1. `____________________________`.")
            doc.append("")
            doc.append("3.2. `____________________________`.")
            doc.append("")

        # 4. Rights
        doc.append("## 4. Права")
        doc.append("")
        doc.append(f"{position_name} имеет право:")
        doc.append("")
        if sections.get('rights'):
            doc.extend(self._format_rights_section(sections['rights']))
        else:
            doc.append("4.1. Участвовать в обсуждении проектов решений руководства организации.")
            doc.append("")
            doc.append("4.2. Запрашивать и получать необходимую информацию и документы.")
            doc.append("")

        # 5. Responsibility
        doc.append("## 5. Ответственность")
        doc.append("")
        if sections.get('responsibility'):
            doc.extend(self._format_responsibility_section(sections['responsibility'], position_name))
        else:
            doc.append(f"5.1. {position_name} привлекается к ответственности:")
            doc.append("")
            doc.append("- за ненадлежащее исполнение должностных обязанностей - в порядке, установленном трудовым законодательством РФ;")
            doc.append("- за правонарушения - в порядке, установленном действующим законодательством РФ;")
            doc.append("- за причинение ущерба организации - в порядке, установленном трудовым законодательством РФ.")
            doc.append("")

        # 6. Final provisions
        if sections.get('conclusion'):
            doc.append("## 6. Заключительные положения")
            doc.append("")
            doc.extend(self._format_conclusion_section(sections['conclusion']))

        # 7. Signatures
        doc.append("## 7. Согласование и утверждение")
        doc.append("")
        doc.append("### Подписи")
        doc.append("")
        doc.append("**Руководитель подразделения:**")
        doc.append("")
        doc.append("`____________________` / `____________________` / `____________________`")
        doc.append("*(подпись)* / *(И.О.Ф)* / *(дата)*")
        doc.append("")
        doc.append("### Ознакомление сотрудника")
        doc.append("")
        doc.append("С должностной инструкцией ознакомлен(а), экземпляр получил(а):")
        doc.append("")
        doc.append("`____________________` / `____________________` / `____________________`")
        doc.append("*(подпись сотрудника)* / *(И.О.Ф)* / *(дата)*")
        doc.append("")

        # Final cleanup
        result = '\n'.join(doc)
        result = self._final_cleanup(result)

        return result

    def _extract_document_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from document."""
        sections = {}

        # General provisions
        general_match = re.search(r'\*\*1\.\s*Общие положения\*\*(.*?)(?=\*\*\d+\.|$)', content, re.DOTALL)
        if general_match:
            sections['general'] = self._clean_section_text(general_match.group(1))

        # Functions
        functions_match = re.search(r'\*\*2\.\s*Функции\*\*(.*?)(?=\*\*\d+\.|$)', content, re.DOTALL)
        if functions_match:
            sections['functions'] = self._clean_section_text(functions_match.group(1))

        # Duties
        duties_match = re.search(r'\*\*3\.\s*Должностные обязанности\*\*(.*?)(?=\*\*\d+\.|$)', content, re.DOTALL)
        if duties_match:
            sections['duties'] = self._clean_section_text(duties_match.group(1))

        # Rights
        rights_match = re.search(r'\*\*4\.\s*Права\*\*(.*?)(?=\*\*\d+\.|$)', content, re.DOTALL)
        if rights_match:
            sections['rights'] = self._clean_section_text(rights_match.group(1))

        # Responsibility
        resp_match = re.search(r'\*\*5\.\s*Ответственность\*\*(.*?)(?=\*\*\d+\.|$)', content, re.DOTALL)
        if resp_match:
            sections['responsibility'] = self._clean_section_text(resp_match.group(1))

        # Conclusion
        concl_match = re.search(r'\*\*6\.\s*Заключительные положения\*\*(.*?)$', content, re.DOTALL)
        if concl_match:
            sections['conclusion'] = self._clean_section_text(concl_match.group(1))

        return sections

    def _clean_section_text(self, text: str) -> str:
        """Clean section text."""
        text = re.sub(r'\n+', '\n', text.strip())
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'[_.]{2,}', '`____________________________`', text)
        text = re.sub(r'\s+\.\s*$', ' `____________________________`.', text, flags=re.MULTILINE)
        text = re.sub(r'\s+;\s*$', ' `____________________________`;', text, flags=re.MULTILINE)
        return text

    def _format_general_section(self, text: str, position_name: str) -> list:
        """Format general provisions section."""
        lines = []
        paragraphs = text.split('\n')

        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('('):
                lines.append(para)
                lines.append("")

        return lines

    def _format_functions_section(self, text: str) -> list:
        """Format functions section."""
        lines = ["Основные функции:", ""]

        # Find numbered functions
        functions = re.findall(r'2\.\d+\.\s*(.*?)(?=2\.\d+\.|$)', text, re.DOTALL)
        for func in functions:
            func = func.strip().replace('\n', ' ')
            if func:
                lines.append(f"- {func}")

        if len(lines) == 2:  # No functions found
            lines.append("- `____________________________`;")
            lines.append("- `____________________________`.")

        lines.append("")
        return lines

    def _format_duties_section(self, text: str) -> list:
        """Format duties section."""
        lines = []

        # Find numbered duties
        duties = re.findall(r'3\.\d+\.\s*(.*?)(?=3\.\d+\.|$)', text, re.DOTALL)
        for i, duty in enumerate(duties, 1):
            duty = duty.strip().replace('\n', ' ')
            if duty and not duty.startswith('('):
                lines.append(f"3.{i}. {duty}")
                lines.append("")

        if not lines:
            lines.extend(["3.1. `____________________________`.", ""])

        return lines

    def _format_rights_section(self, text: str) -> list:
        """Format rights section."""
        lines = []

        # Find numbered rights
        rights = re.findall(r'4\.\d+\.\s*(.*?)(?=4\.\d+\.|$)', text, re.DOTALL)
        for i, right in enumerate(rights, 1):
            right = right.strip().replace('\n', ' ')
            if right and not right.startswith('('):
                lines.append(f"4.{i}. {right}")
                lines.append("")

        if not lines:
            lines.extend([
                "4.1. Участвовать в обсуждении проектов решений руководства организации.",
                "",
                "4.2. Запрашивать и получать необходимую информацию и документы.",
                ""
            ])

        return lines

    def _format_responsibility_section(self, text: str, position_name: str) -> list:
        """Format responsibility section."""
        lines = [f"5.1. {position_name} привлекается к ответственности:", ""]

        # Find responsibility items
        resp_items = re.findall(r'-\s*(за.*?)(?=-\s*за|$)', text, re.DOTALL)
        for item in resp_items:
            item = item.strip().replace('\n', ' ')
            if item:
                lines.append(f"- {item};")

        if len(lines) == 2:  # No items found
            lines.extend([
                "- за ненадлежащее исполнение должностных обязанностей - в порядке, установленном трудовым законодательством РФ;",
                "- за правонарушения - в порядке, установленном действующим законодательством РФ;",
                "- за причинение ущерба организации - в порядке, установленном трудовым законодательством РФ."
            ])

        lines.append("")
        lines.append("5.2. `____________________________`.")
        lines.append("")
        return lines

    def _format_conclusion_section(self, text: str) -> list:
        """Format conclusion section."""
        lines = []
        paragraphs = text.split('\n')

        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('('):
                lines.append(para)
                lines.append("")

        return lines

    def _final_cleanup(self, content: str) -> str:
        """Final document cleanup."""
        lines = content.split('\n')
        cleaned_lines = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                cleaned_lines.append('')
                i += 1
                continue

            # Remove remaining explanatory notes
            if re.match(r'^\(.*\)$', line) and len(line) < 50:
                i += 1
                continue

            # Remove specific leftover lines
            if line in ['функцией археографа)', 'функцией архивиста)', 'руководителя)', '(иные обязанности)', '(иные права)']:
                i += 1
                continue

            # Remove standalone ##
            if line == '##':
                i += 1
                continue

            # Clean trailing ## from headers
            if line.startswith('##') and line.endswith('##') and line != '##':
                line = line.rstrip('#').strip()

            # Fix position names - capitalize first letter
            if line.startswith(('археограф', 'архивист', 'специалист')):
                line = line[0].upper() + line[1:]

            # Fix double semicolons
            line = re.sub(r';;+', ';', line)

            # Remove artifacts with КонсультантПлюс
            if any(artifact in line for artifact in ['КонсультантПлюс', 'www.consultant.ru', 'Дата сохранения:']):
                i += 1
                continue

            # Fix merged sentences - separate 5.2 correctly
            if 'Российской Федерации. 5.2.' in line:
                parts = line.split('5.2.')
                if len(parts) >= 2:
                    cleaned_lines.append(parts[0].strip())
                    cleaned_lines.append('')
                    # Continue with 5.2 section
                    line = f"5.2.{parts[1]}" if parts[1].strip() else "5.2. `____________________________`."

            # Fix broken lines with artifacts
            if '---' in line and any(word in line for word in ['ознакомлен', 'подпись', 'дата']):
                i += 1
                continue

            line = re.sub(r';\s*$', '.', line)

            # Fix fill-in fields
            line = re.sub(r'`____________________________`\.\s*\(.*?\)', '`____________________________`', line)

            # Remove bold artifacts
            line = re.sub(r'\*\*\*\*.*?\*\*\*\*', '', line)

            cleaned_lines.append(line)
            i += 1

        # Join and final cleanup
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 newlines
        result = re.sub(r'\.{2,}', '.', result)     # Remove multiple dots
        result = re.sub(r'\n##\n', '\n', result)    # Remove standalone ##
        result = re.sub(r'^##$', '', result, flags=re.MULTILINE)  # Remove lines with only ##

        return result.strip()

    def process_file(self, file_path: Union[str, Path], force: bool = False) -> bool:
        """
        Process a single file with comprehensive safety checks.
        Includes advanced filtering to protect documentation.
        """
        file_path = Path(file_path)

        # Enhanced documentation protection
        protected_paths = [
            'documentation_management',
            'docs/documentation_management',
            '.git',
            '.zencoder',
            '__pycache__',
            'venv',
            'node_modules'
        ]

        protected_patterns = [
            r'README.*\.md$',
            r'CHANGELOG.*\.md$',
            r'LICENSE.*',
            r'.*\.py$',
            r'.*\.json$',
            r'.*\.yml$',
            r'.*\.yaml$',
        ]

        # Check protected paths
        if any(protected in str(file_path) for protected in protected_paths):
            self.results.skipped += 1
            self.results.files_skipped.append(str(file_path))
            return True

        # Check protected patterns
        if any(re.search(pattern, file_path.name, re.IGNORECASE) for pattern in protected_patterns):
            self.results.skipped += 1
            self.results.files_skipped.append(str(file_path))
            return True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip non-job-description files based on content
            if not self._is_job_description(content):
                self.results.skipped += 1
                self.results.files_skipped.append(str(file_path))
                return True

            # Check if already processed by enhanced processor
            if 'Информация о документе' in content and not force:
                self.results.skipped += 1
                self.results.files_skipped.append(str(file_path))
                return True

            # Clean and structure document
            processed_content = self.clean_and_structure_document(content)

            # Assess quality
            quality = self.assess_processing_quality(processed_content)
            self.results.quality_stats[quality] += 1

            # Add enhanced metadata
            position = self._extract_position_name(content)
            department = self.normalize_department_name(str(file_path))
            final_content = self.add_enhanced_metadata(
                processed_content, position, department, quality
            )

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            self.results.processed += 1
            self.results.files_processed.append(str(file_path))
            return True

        except Exception as e:
            self.results.errors += 1
            self.results.files_errored.append(f"{file_path}: {str(e)}")
            return False

    def add_enhanced_metadata(
        self,
        content: str,
        position: str,
        department: str,
        processing_quality: str = "high"
    ) -> str:
        """Add enhanced metadata to document."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = {
            "created_at": now,
            "updated_at": now,
            "author": "Enhanced docxmd_processor v2.0",
            "version": "2.0.0",
            "document_type": "должностная_инструкция",
            "position": self.normalize_position_name(position),
            "department": self.normalize_department_name(department),
            "processing_quality": processing_quality,
            "processor_version": "enhanced_v2.0.0",
            "formatting": "fully_structured"
        }

        metadata_str = f"<!-- METADATA\n{json.dumps(metadata, indent=2, ensure_ascii=False)}\n-->"
        return content + "\n\n" + metadata_str

    def normalize_position_name(self, name: str) -> str:
        """Normalize position name for metadata."""
        if not name:
            return "специалист"

        name = re.sub(r'\s+', '_', name.lower().strip())
        name = re.sub(r'[^\w\-_]', '', name)
        return name

    def normalize_department_name(self, path: str) -> str:
        """Extract and normalize department name from file path."""
        path_parts = Path(path).parts

        # Skip standard directories
        skip_dirs = {'docs', 'documents', 'markdown', 'converted', 'src', 'dst'}

        for part in reversed(path_parts):
            if part not in skip_dirs and not part.endswith('.md'):
                return re.sub(r'[^\w\s\-]', '', part).strip()

        return "общий_отдел"

    def _is_job_description(self, content: str) -> bool:
        """
        Advanced job description detection.
        Uses multiple criteria to identify if document is a job description.
        """
        if not content or len(content) < 100:
            return False

        # Strong indicators
        strong_indicators = [
            r'должностн\w+\s+инструкци\w+',
            r'общие положения',
            r'должностные обязанности',
            r'функции.*должности',
            r'права.*работника',
            r'ответственность.*работника'
        ]

        strong_count = sum(1 for pattern in strong_indicators
        if re.search(pattern, content, re.IGNORECASE))

        if strong_count >= 3:
            return True

        # Weak indicators (need more to confirm)
        weak_indicators = [
            r'подчиняется',
            r'имеет право',
            r'несет ответственность',
            r'трудовой договор',
            r'рабочее место',
            r'квалификационные требования'
        ]

        weak_count = sum(1 for pattern in weak_indicators
                        if re.search(pattern, content, re.IGNORECASE))

        return strong_count >= 1 and weak_count >= 2

    def process_directory(self, directory: Union[str, Path], force: bool = False) -> ProcessingResults:
        """
        Process all markdown files in directory with enhanced safety.
        Only processes files in docs/Conversion/ to avoid damaging documentation.
        """
        directory = Path(directory)

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        # Safety check: only allow processing in safe directories
        safe_dirs = ['Conversion', 'converted', 'documents', 'markdown', 'temp', 'test']
        is_safe_directory = any(safe_dir in str(directory) for safe_dir in safe_dirs)

        if not is_safe_directory and not force:
            print(f"⚠️  Warning: Processing directory {directory} may affect documentation.")
            print("   Use docs/Conversion/ for safe testing or add --force-process flag.")
            return self.results

        md_files = list(directory.rglob('*.md'))
        self.results.total = len(md_files)

        for md_file in md_files:
            self.process_file(md_file, force)

        return self.results

