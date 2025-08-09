"""
Document processor module for post-processing converted markdown files.
Integrates functionality from scripts/document_processor.py and
advanced_document_processor.py
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Union


class ProcessingResults:
    """Container for processing results"""

    def __init__(self):
        self.processed = 0
        self.skipped = 0
        self.errors = 0
        self.total = 0
        self.files_processed = []
        self.files_skipped = []
        self.files_errored = []
        self.quality_stats = {"high": 0, "medium": 0, "low": 0}

    def to_dict(self) -> Dict:
        return {
            "processed": self.processed,
            "skipped": self.skipped,
            "errors": self.errors,
            "total": self.total,
            "files_processed": self.files_processed,
            "files_skipped": self.files_skipped,
            "files_errored": self.files_errored,
            "quality_stats": self.quality_stats,
        }


class BaseDocumentProcessor:
    """Base class for document processors"""

    def __init__(self):
        self.results = ProcessingResults()

    def clean_line_breaks(self, text: str) -> str:
        """Clean unnecessary line breaks and backslash breaks"""
        text = re.sub(r"\\\n", " ", text)
        text = re.sub(r"\\\r\n", " ", text)
        text = re.sub(r" +", " ", text)
        return text.strip()

    def remove_consultant_plus_elements(self, content: str) -> str:
        """Remove formatting artifacts"""
        # Remove separator blocks
        content = re.sub(r"-{20,}.*?-{20,}", "", content, flags=re.DOTALL)

        # Remove images and media file links
        content = re.sub(r"!\[.*?\]\(.*?media/.*?\).*?\n", "", content)

        # Remove external system links
        content = re.sub(
            r"Документ предоставлен.*?www\.consultant\.ru.*?\n",
            "",
            content,
            flags=re.DOTALL,
        )

        # Remove save date information
        content = re.sub(r"Дата сохранения:.*?\n", "", content)

        # Remove "Актуально на" blocks
        content = re.sub(r"\*\*Актуально на.*?\*\*", "", content)

        # Remove tables with information
        content = re.sub(r"\+.*?\+.*?\n", "", content)
        content = re.sub(r"\|.*?\|.*?\n", "", content)

        # Remove "См.:" blocks
        content = re.sub(r"См\.:.*?Путеводитель.*?\n", "", content, flags=re.DOTALL)

        return content

    def remove_formatting_artifacts(self, content: str) -> str:
        """Remove formatting artifacts from Word"""
        # Remove service separators
        content = re.sub(r"_{10,}", "", content)
        content = re.sub(r"─{10,}", "", content)
        content = re.sub(r"--+ --+.*?--+", "", content, flags=re.DOTALL)

        # Clean extra spaces and indents at line beginnings
        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            line = re.sub(r"^ +", "", line)
            if line.strip():
                cleaned_lines.append(line)

        content = "\n".join(cleaned_lines)

        # Remove multiple empty lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        return content

    def is_already_processed(self, content: str) -> bool:
        """Check if file was already processed"""
        return (
            "<!-- METADATA" in content
            and '"document_type": "структурированный_документ"' in content
        )

    def add_metadata(
        self,
        content: str,
        position: str,
        department: str,
        processing_quality: str = "medium",
    ) -> str:
        """Add metadata to document end"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = {
            "created_at": now,
            "updated_at": now,
            "author": "docxmd_processor",
            "version": "1.0.0",
            "document_type": "структурированный_документ",
            "position": self.normalize_position_name(position),
            "department": self.normalize_department_name(department),
            "processing_quality": processing_quality,
        }

        metadata_str = (
            f"<!-- METADATA\n{json.dumps(metadata, indent=2, ensure_ascii=False)}\n-->"
        )
        return content + "\n\n" + metadata_str

    def normalize_position_name(self, name: str) -> str:
        """Normalize position name for metadata"""
        return re.sub(r"[^а-яА-Яa-zA-Z0-9\s]", "", name).lower().replace(" ", "_")

    def normalize_department_name(self, path: str) -> str:
        """Extract and normalize department name from path"""
        parts = path.split("/")
        for part in parts:
            if part.isupper() and len(part) > 5:
                return part.lower().replace(" ", "_").replace("_и_", "_")
        return "неопределен"

    def extract_position_from_filename(self, filename: str) -> str:
        """Extract position name from filename"""
        name = os.path.splitext(filename)[0]
        name = re.sub(r"^ПР\s+", "", name)
        return name.strip()

    def assess_processing_quality(self, content: str) -> str:
        """Assess the quality of processed content"""
        sections = [
            "Общие положения",
            "Функции",
            "Должностные обязанности",
            "Права",
            "Ответственность",
        ]
        filled_sections = 0

        for section in sections:
            if (
                section in content
                and len(re.findall(f"{section}.*?(?=##|$)", content, re.DOTALL)) > 0
            ):
                section_content = re.findall(
                    f"{section}.*?(?=##|$)", content, re.DOTALL
                )[0]
                if len(section_content.strip()) > 50:  # Non-trivial content
                    filled_sections += 1

        if filled_sections >= 4:
            return "high"
        elif filled_sections >= 2:
            return "medium"
        else:
            return "low"


class BasicDocumentProcessor(BaseDocumentProcessor):
    """Basic document processor (v1.0)"""

    def process_file(self, file_path: Union[str, Path], force: bool = False) -> bool:
        """Process a single file"""
        file_path = Path(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if already processed
            if self.is_already_processed(content) and not force:
                self.results.skipped += 1
                self.results.files_skipped.append(str(file_path))
                return True

            # Clean content
            content = self.remove_consultant_plus_elements(content)
            content = self.remove_formatting_artifacts(content)

            # Structure content
            structured_content = self.structure_content(content, file_path.name)

            # Assess quality
            quality = self.assess_processing_quality(structured_content)
            self.results.quality_stats[quality] += 1

            # Add metadata
            position = self.extract_position_from_filename(file_path.name)
            department = self.normalize_department_name(str(file_path))
            final_content = self.add_metadata(
                structured_content, position, department, quality
            )

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            self.results.processed += 1
            self.results.files_processed.append(str(file_path))
            return True

        except Exception as e:
            self.results.errors += 1
            self.results.files_errored.append(f"{file_path}: {str(e)}")
            return False

    def structure_content(self, content: str, filename: str) -> str:
        """Structure content according to style guide"""
        position_name = self.extract_position_from_filename(filename)

        # Start with clean template
        structured_content = f"# Должностная инструкция: {position_name}\n\n"
        structured_content += "## Информация о документе\n\n"
        structured_content += "**Организация:** _(наименование организации)_\n\n"
        structured_content += (
            "**Утверждено:** _(подпись, инициалы, фамилия руководителя)_\n\n"
        )
        structured_content += "**Дата утверждения:** _(дата)_\n\n"

        # Extract and structure sections
        sections = self.extract_sections(content)

        # General provisions
        if sections.get("general"):
            structured_content += "## 1. Общие положения\n\n"
            structured_content += self.format_general_section(sections["general"])
        else:
            structured_content += (
                "## 1. Общие положения\n\n_(Общие положения должности)_\n\n"
            )

        # Functions
        if sections.get("functions"):
            structured_content += "## 2. Функции\n\n"
            structured_content += self.format_functions_section(sections["functions"])
        else:
            structured_content += "## 2. Функции\n\n_(Функции должности)_\n\n"

        # Duties
        if sections.get("duties"):
            structured_content += "## 3. Должностные обязанности\n\n"
            structured_content += self.format_duties_section(sections["duties"])
        else:
            structured_content += (
                "## 3. Должностные обязанности\n\n_(Должностные обязанности)_\n\n"
            )

        # Rights
        if sections.get("rights"):
            structured_content += "## 4. Права\n\n"
            structured_content += self.format_rights_section(sections["rights"])
        else:
            structured_content += "## 4. Права\n\n_(Права сотрудника)_\n\n"

        # Responsibility
        if sections.get("responsibility"):
            structured_content += "## 5. Ответственность\n\n"
            structured_content += self.format_responsibility_section(
                sections["responsibility"]
            )
        else:
            structured_content += (
                "## 5. Ответственность\n\n_(Виды ответственности)_\n\n"
            )

        # Signatures
        structured_content += "## 6. Согласование и утверждение\n\n"
        structured_content += "### Подписи\n\n"
        structured_content += "**Руководитель структурного подразделения:** _________________ _(инициалы, фамилия)_\n\n"
        structured_content += "**Дата:** _(дата)_\n\n"
        structured_content += "### Ознакомление сотрудника\n\n"
        employee_text = "С документом ознакомлен(а), один экземпляр получил(а) на руки и обязуюсь хранить его на рабочем месте.\n\n"
        structured_content += employee_text
        employee_sig = "**Подпись сотрудника:** _________________ _(инициалы, фамилия)_\n\n"
        structured_content += employee_sig
        structured_content += "**Дата:** _(дата)_\n\n"

        return structured_content

    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from content"""
        sections = {}

        # General provisions
        general_match = re.search(
            r"1\.\s*Общие положения(.*?)(?=\d+\.|$)", content, re.DOTALL | re.IGNORECASE
        )
        if general_match:
            sections["general"] = general_match.group(1).strip()

        # Functions
        functions_match = re.search(
            r"2\.\s*Функции(.*?)(?=\d+\.|$)", content, re.DOTALL | re.IGNORECASE
        )
        if functions_match:
            sections["functions"] = functions_match.group(1).strip()

        # Duties
        duties_match = re.search(
            r"3\.\s*Должностные обязанности(.*?)(?=\d+\.|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if duties_match:
            sections["duties"] = duties_match.group(1).strip()

        # Rights
        rights_match = re.search(
            r"4\.\s*Права(.*?)(?=\d+\.|$)", content, re.DOTALL | re.IGNORECASE
        )
        if rights_match:
            sections["rights"] = rights_match.group(1).strip()

        # Responsibility
        resp_match = re.search(
            r"5\.\s*Ответственность(.*?)(?=\d+\.|─|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if resp_match:
            sections["responsibility"] = resp_match.group(1).strip()

        return sections

    def format_general_section(self, content: str) -> str:
        """Format general provisions section"""
        return self.clean_line_breaks(content) + "\n\n"

    def format_functions_section(self, content: str) -> str:
        """Format functions section"""
        result = "Основные функции:\n\n"
        functions = re.findall(r"2\.\d+\.\s*(.*?)(?=2\.\d+\.|$)", content, re.DOTALL)
        for func in functions:
            func = self.clean_line_breaks(func).strip()
            if func:
                result += f"- {func}\n"
        return result + "\n"

    def format_duties_section(self, content: str) -> str:
        """Format duties section"""
        result = "Сотрудник исполняет следующие обязанности:\n\n"
        duties = re.findall(r"3\.\d+\.\s*(.*?)(?=3\.\d+\.|$)", content, re.DOTALL)
        for i, duty in enumerate(duties, 1):
            duty = self.clean_line_breaks(duty).strip()
            if duty and not re.match(r"_{5,}", duty):
                result += f"{i}. {duty}\n\n"
        return result

    def format_rights_section(self, content: str) -> str:
        """Format rights section"""
        result = "Сотрудник имеет право:\n\n"
        rights = re.findall(r"4\.\d+\.\s*(.*?)(?=4\.\d+\.|$)", content, re.DOTALL)
        for i, right in enumerate(rights, 1):
            right = self.clean_line_breaks(right).strip()
            if right and not re.match(r"_{5,}", right):
                result += f"{i}. {right}\n\n"
        return result

    def format_responsibility_section(self, content: str) -> str:
        """Format responsibility section"""
        result = "### 5.1. Виды ответственности\n\n"
        result += "Сотрудник привлекается к ответственности:\n\n"

        resp_items = re.split(r"[-–]\s*", content)
        for item in resp_items:
            item = self.clean_line_breaks(item).strip()
            if item and len(item) > 10 and not re.match(r"5\.\d", item):
                result += f"- {item}\n\n"

        return result


class AdvancedDocumentProcessor(BaseDocumentProcessor):
    """Advanced document processor (v2.0) with enhanced capabilities"""

    def __init__(self, force_reprocess: bool = False, dry_run: bool = False):
        super().__init__()
        self.force_reprocess = force_reprocess
        self.dry_run = dry_run

    def process_file(self, file_path: Union[str, Path], force: bool = False) -> bool:
        """Process a single file with advanced features"""
        file_path = Path(file_path)

        if self.dry_run:
            self.results.processed += 1
            self.results.files_processed.append(f"{file_path} (dry-run)")
            return True

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if already processed
            if self.is_already_processed(content) and not (
                force or self.force_reprocess
            ):
                self.results.skipped += 1
                self.results.files_skipped.append(str(file_path))
                return True

            # Advanced cleaning
            content = self.clean_consultant_plus_artifacts_advanced(content)
            content = self.remove_formatting_artifacts(content)

            # Advanced structuring
            structured_content = self.advanced_structure_content(
                content, file_path.name
            )

            # Assess quality
            quality = self.assess_processing_quality(structured_content)
            self.results.quality_stats[quality] += 1

            # Add metadata
            position = self.extract_position_from_filename(file_path.name)
            department = self.normalize_department_name(str(file_path))
            final_content = self.add_metadata(
                structured_content, position, department, quality
            )

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            self.results.processed += 1
            self.results.files_processed.append(str(file_path))
            return True

        except Exception as e:
            self.results.errors += 1
            self.results.files_errored.append(f"{file_path}: {str(e)}")
            return False

    def clean_consultant_plus_artifacts_advanced(self, content: str) -> str:
        """Advanced cleaning of formatting artifacts"""
        # Remove separator blocks
        content = re.sub(r"-{15,}.*?-{15,}", "", content, flags=re.DOTALL)
        content = re.sub(r"_{15,}", "", content)
        content = re.sub(r"─{15,}", "", content)

        # Remove images and media links
        content = re.sub(r"!\[.*?\]\(.*?media.*?\).*?\n", "", content)
        content = re.sub(r"!\[.*?\]\(.*?\){[^}]*}", "", content)

        # Remove external system information
        content = re.sub(r"Форма:.*?\n", "", content)
        content = re.sub(r"\(Подготовлен для системы.*?\)", "", content)
        content = re.sub(
            r"Документ предоставлен.*?www\.consultant\.ru.*?\n",
            "",
            content,
            flags=re.DOTALL,
        )
        content = re.sub(r"Дата сохранения:.*?\n", "", content)
        content = re.sub(r"\*\*Актуально на.*?\*\*", "", content)

        # Remove tables
        content = re.sub(r"\+[-+]+\+.*?\n", "", content)
        content = re.sub(r"\|.*?\|.*?\n", "", content)

        # Remove links
        content = re.sub(r"См\.:.*?Путеводитель.*?\n", "", content, flags=re.DOTALL)

        # Remove service blocks
        content = re.sub(r"-- -- -+ --.*?-- -- -+ --", "", content, flags=re.DOTALL)

        return content

    def advanced_structure_content(self, content: str, filename: str) -> str:
        """Advanced content structuring"""
        position_name = self.extract_position_from_filename(filename)

        # Start with template
        result = f"# Должностная инструкция: {position_name}\n\n"
        result += "## Информация о документе\n\n"
        result += "**Организация:** _(наименование организации)_\n\n"
        result += "**Утверждено:** _(подпись, инициалы, фамилия руководителя)_\n\n"
        result += "**Дата утверждения:** _(дата)_\n\n"

        # Extract main sections
        sections = self.improved_extract_sections(content)

        # Build structure
        if sections["general"]:
            result += self.format_general_section_advanced(sections["general"])
        else:
            result += self.create_default_general_section(position_name)

        if sections["functions"]:
            result += "## 2. Функции\n\n" + self.format_functions_advanced(
                sections["functions"]
            )
        else:
            result += "## 2. Функции\n\n_(Функции должности указываются отдельно)_\n\n"

        if sections["duties"]:
            result += "## 3. Должностные обязанности\n\n" + self.format_duties_advanced(
                sections["duties"]
            )
        else:
            duties_placeholder = "_(Обязанности указываются отдельно)_"
            result += f"## 3. Должностные обязанности\n\n{duties_placeholder}\n\n"

        if sections["rights"]:
            result += "## 4. Права\n\n" + self.format_rights_advanced(
                sections["rights"]
            )
        else:
            result += "## 4. Права\n\n_(Права указываются отдельно)_\n\n"

        if sections["responsibility"]:
            result += "## 5. Ответственность\n\n" + self.format_responsibility_advanced(
                sections["responsibility"]
            )
        else:
            resp_placeholder = "_(Виды ответственности указываются отдельно)_"
            result += f"## 5. Ответственность\n\n{resp_placeholder}\n\n"

        # Signatures
        result += self.get_signatures_section()

        return result

    def improved_extract_sections(self, content: str) -> Dict[str, str]:
        """Advanced section extraction"""
        sections = {
            "general": "",
            "functions": "",
            "duties": "",
            "rights": "",
            "responsibility": "",
        }

        # Clean content from service information
        content = self.clean_consultant_plus_artifacts_advanced(content)

        # General provisions - extended search
        general_patterns = [
            r"1\.\s*Общие положения(.*?)(?=\d+\.|$)",
            r"\*\*1\.\s*Общие положения\*\*(.*?)(?=\*\*\d+\.|$)",
            r"Общие положения(.*?)(?=Функции|Обязанности|$)",
        ]

        for pattern in general_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                sections["general"] = match.group(1).strip()
                break

        # Functions
        functions_patterns = [
            r"2\.\s*Функции(.*?)(?=\d+\.|$)",
            r"\*\*2\.\s*Функции\*\*(.*?)(?=\*\*\d+\.|$)",
        ]

        for pattern in functions_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                sections["functions"] = match.group(1).strip()
                break

        # Duties
        duties_patterns = [
            r"3\.\s*Должностные обязанности(.*?)(?=\d+\.|$)",
            r"\*\*3\.\s*Должностные обязанности\*\*(.*?)(?=\*\*\d+\.|$)",
            r"обязанности.*?исполняет следующие обязанности:(.*?)(?=\d+\.|$)",
        ]

        for pattern in duties_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                sections["duties"] = match.group(1).strip()
                break

        # Rights
        rights_patterns = [
            r"4\.\s*Права(.*?)(?=\d+\.|$)",
            r"\*\*4\.\s*Права\*\*(.*?)(?=\*\*\d+\.|$)",
            r"имеет право:(.*?)(?=\d+\.|$)",
        ]

        for pattern in rights_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                sections["rights"] = match.group(1).strip()
                break

        # Responsibility
        resp_patterns = [
            r"5\.\s*Ответственность(.*?)(?=\d+\.|─|С документом|$)",
            r"\*\*5\.\s*Ответственность\*\*(.*?)(?=\*\*\d+\.|─|С документом|$)",
            r"привлекается к ответственности:(.*?)(?=\d+\.|─|С документом|$)",
        ]

        for pattern in resp_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                sections["responsibility"] = match.group(1).strip()
                break

        return sections

    def format_general_section_advanced(self, content: str) -> str:
        """Advanced formatting of general provisions"""
        result = "## 1. Общие положения\n\n"

        # Try to extract subsections
        subsections = re.split(r"(\d+\.\d+\.)", content)

        current_subsection = ""
        subsection_map = {
            "1.1.": ("### 1.1. Категория должности\n\n", self.format_category),
            "1.2.": (
                "### 1.2. Требования к образованию и опыту\n\n",
                self.format_requirements,
            ),
            "1.3.": ("### 1.3. Знания и навыки\n\n", self.format_knowledge),
            "1.4.": ("### 1.4. Руководящие документы\n\n", self.format_documents),
            "1.5.": ("### 1.5. Подчиненность\n\n", self.format_subordination),
            "1.6.": ("### 1.6. Замещение\n\n", self.format_replacement),
        }

        for i, part in enumerate(subsections):
            if re.match(r"\d+\.\d+\.", part):
                current_subsection = part
            elif current_subsection and part.strip():
                if current_subsection in subsection_map:
                    header, formatter = subsection_map[current_subsection]
                    result += header + formatter(part) + "\n\n"

        return result

    def format_category(self, text: str) -> str:
        """Format position category"""
        text = self.clean_text(text)
        if "относится к категории" in text.lower():
            return text
        else:
            return "_(Информация о категории должности)_"

    def format_requirements(self, text: str) -> str:
        """Format requirements"""
        text = self.clean_text(text)
        if any(
            word in text.lower()
            for word in ["образование", "принимается лицо", "требования"]
        ):
            return text
        else:
            return "_(Требования к образованию и опыту работы)_"

    def format_knowledge(self, text: str) -> str:
        """Format knowledge and skills"""
        text = self.clean_text(text)

        if "должен знать" in text.lower():
            # Try to extract knowledge list
            knowledge_items = re.split(r"[-–]\s*", text)
            if len(knowledge_items) > 1:
                result = "Сотрудник должен знать:\n\n"
                for item in knowledge_items[1:]:  # Skip first element
                    item = item.strip().rstrip(";.,")
                    if item and len(item) > 3:
                        result += f"- {item}\n"
                return result
            else:
                return text
        else:
            return "_(Перечень необходимых знаний и навыков)_"

    def format_documents(self, text: str) -> str:
        """Format governing documents"""
        text = self.clean_text(text)
        if "руководствуется" in text.lower():
            return f"Сотрудник в своей деятельности руководствуется:\n\n{text}"
        else:
            return "_(Перечень руководящих документов)_"

    def format_subordination(self, text: str) -> str:
        """Format subordination"""
        text = self.clean_text(text)
        if "подчиняется" in text.lower():
            return text
        else:
            return "_(Информация о подчиненности)_"

    def format_replacement(self, text: str) -> str:
        """Format replacement"""
        text = self.clean_text(text)
        if any(word in text.lower() for word in ["замещ", "отсутств", "отпуск"]):
            return text
        else:
            return "_(Порядок замещения при отсутствии)_"

    def clean_text(self, text: str) -> str:
        """Clean text"""
        text = re.sub(r"\s+", " ", text.strip())
        text = re.sub(r"_{3,}", "", text)
        return text

    def create_default_general_section(self, position: str) -> str:
        """Create default general provisions template"""
        return f"""## 1. Общие положения

### 1.1. Категория должности

_(Укажите категорию должности {position})_

### 1.2. Требования к образованию и опыту

_(Укажите требования к образованию и опыту для должности {position})_

### 1.3. Знания и навыки

Сотрудник должен знать:

- _(перечень необходимых знаний)_
- основы трудового законодательства
- правила внутреннего трудового распорядка
- правила охраны труда и техники безопасности

### 1.4. Руководящие документы

Сотрудник в своей деятельности руководствуется:

- настоящим документом
- положением о структурном подразделении
- _(иные документы)_

### 1.5. Подчиненность

_(Укажите, кому подчиняется сотрудник)_

### 1.6. Замещение

_(Порядок замещения при отсутствии сотрудника)_

"""

    def format_functions_advanced(self, content: str) -> str:
        """Advanced functions formatting"""
        result = "Основные функции:\n\n"

        # Look for functions in various formats
        functions = re.findall(r"2\.\d+\.\s*(.*?)(?=2\.\d+\.|$)", content, re.DOTALL)
        if functions:
            for func in functions:
                func = self.clean_text(func)
                if func:
                    result += f"- {func}\n"
        else:
            # Try to find other patterns
            lines = content.split("\n")
            for line in lines:
                line = self.clean_text(line)
                if line and len(line) > 5:
                    result += f"- {line}\n"

        return result + "\n"

    def format_duties_advanced(self, content: str) -> str:
        """Advanced duties formatting"""
        result = "Сотрудник исполняет следующие обязанности:\n\n"

        duties = re.findall(r"3\.\d+\.\s*(.*?)(?=3\.\d+\.|$)", content, re.DOTALL)
        counter = 1

        if duties:
            for duty in duties:
                duty = self.clean_text(duty)
                if duty and not re.match(r"_{3,}", duty):
                    result += f"{counter}. {duty}\n\n"
                    counter += 1
        else:
            # Alternative search
            lines = content.split("\n")
            for line in lines:
                line = self.clean_text(line)
                if line and len(line) > 10 and not re.match(r"\d+\.\d+\.", line):
                    result += f"{counter}. {line}\n\n"
                    counter += 1

        return result

    def format_rights_advanced(self, content: str) -> str:
        """Advanced rights formatting"""
        result = "Сотрудник имеет право:\n\n"

        rights = re.findall(r"4\.\d+\.\s*(.*?)(?=4\.\d+\.|$)", content, re.DOTALL)
        counter = 1

        if rights:
            for right in rights:
                right = self.clean_text(right)
                if right and not re.match(r"_{3,}", right):
                    result += f"{counter}. {right}\n\n"
                    counter += 1
        else:
            # Alternative search
            lines = content.split("\n")
            for line in lines:
                line = self.clean_text(line)
                if line and len(line) > 10 and not re.match(r"\d+\.\d+\.", line):
                    result += f"{counter}. {line}\n\n"
                    counter += 1

        return result

    def format_responsibility_advanced(self, content: str) -> str:
        """Advanced responsibility formatting"""
        result = "Сотрудник привлекается к ответственности:\n\n"

        resp_items = re.split(r"[-–]\s*", content)
        for item in resp_items:
            item = self.clean_text(item)
            if item and len(item) > 10 and not re.match(r"5\.\d", item):
                result += f"- {item}\n\n"

        return result

    def get_signatures_section(self) -> str:
        """Get signatures section"""
        employee_ack = "С документом ознакомлен(а), один экземпляр получил(а) на руки и обязуюсь хранить его на рабочем месте."
        return f"""## 6. Согласование и утверждение

### Подписи

**Руководитель структурного подразделения:** _________________ _(инициалы, фамилия)_

**Дата:** _(дата)_

### Ознакомление сотрудника

{employee_ack}

**Подпись сотрудника:** _________________ _(инициалы, фамилия)_

**Дата:** _(дата)_

"""


class DocumentProcessor:
    """Unified interface for document processing"""

    def __init__(self, processor_type: str = "basic", **kwargs):
        """Initialize processor based on type"""
        if processor_type == "basic":
            self.processor = BasicDocumentProcessor()
        elif processor_type == "advanced":
            self.processor = AdvancedDocumentProcessor(**kwargs)
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")

    def process_directory(
        self,
        directory: Union[str, Path],
        force: bool = False,
        dry_run: bool = False,
        pattern: str = "*.md",
    ) -> ProcessingResults:
        """Process all markdown files in directory"""
        directory = Path(directory)

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        # Find all files matching pattern
        files_to_process = list(directory.rglob(pattern))

        self.processor.results.total = len(files_to_process)

        for file_path in files_to_process:
            if file_path.suffix.lower() == ".md":
                self.processor.process_file(file_path, force=force)

        return self.processor.results
