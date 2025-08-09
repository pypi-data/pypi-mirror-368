"""
Reporting module for document processing results.
Handles console and file report generation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Union

from .processor import ProcessingResults


class ProcessingReporter:
    """Handle processing reports"""

    def __init__(self):
        self.timestamp = datetime.now()

    def generate_report(
        self,
        results: ProcessingResults,
        format: str = "console",
        update_existing: bool = False,
        output_dir: Union[str, Path] = None,
    ) -> None:
        """Generate processing report

        Args:
            results: Processing results object
            format: Output format ('console' or 'file')
            update_existing: Update existing report file instead of creating new one
            output_dir: Directory to save report file (defaults to current directory)
        """
        if format == "console":
            self._print_console_report(results)
        elif format == "file":
            self._save_file_report(results, update_existing, output_dir)
        else:
            raise ValueError(f"Unknown report format: {format}")

    def _print_console_report(self, results: ProcessingResults) -> None:
        """Print report to console"""
        print("\n" + "=" * 60)
        print("📋 ОТЧЕТ О ПОСТОБРАБОТКЕ ДОКУМЕНТОВ")
        print("=" * 60)
        print(f"⏰ Время обработки: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Всего файлов: {results.total}")
        print(f"✅ Обработано: {results.processed}")
        print(f"⏭️ Пропущено: {results.skipped}")
        print(f"❌ Ошибок: {results.errors}")

        # Success rate
        if results.total > 0:
            success_rate = (results.processed / results.total) * 100
            print(f"📊 Процент успеха: {success_rate:.1f}%")

        # Quality statistics
        if any(results.quality_stats.values()):
            print("\n📈 СТАТИСТИКА КАЧЕСТВА:")
            print(f"  🟢 Высокое качество: {results.quality_stats['high']} файлов")
            print(f"  🟡 Среднее качество: {results.quality_stats['medium']} файлов")
            print(f"  🔴 Низкое качество: {results.quality_stats['low']} файлов")

        # Error details
        if results.files_errored:
            print(f"\n❌ ОШИБКИ ({len(results.files_errored)}):")
            for error in results.files_errored[:10]:  # Show max 10 errors
                print(f"  • {error}")
            if len(results.files_errored) > 10:
                print(f"  ... и еще {len(results.files_errored) - 10} ошибок")

        # Status summary
        print("\n🎯 ОБЩИЙ СТАТУС: ", end="")
        if results.errors == 0:
            print("✅ Задача выполнена успешно")
        elif results.processed > 0:
            print("⚠️ Выполнено с предупреждениями")
        else:
            print("❌ Выполнение не удалось")

        print("=" * 60)

    def _save_file_report(
        self,
        results: ProcessingResults,
        update_existing: bool = False,
        output_dir: Union[str, Path] = None,
    ) -> None:
        """Save report to file"""
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)

        # Determine report file path
        base_name = "processing_report.md"
        report_path = output_dir / base_name

        if report_path.exists() and not update_existing:
            # Create versioned file with timestamp
            timestamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
            report_path = output_dir / f"processing_report_{timestamp}.md"

        # Generate report content
        report_content = self._generate_markdown_report(results, update_existing)

        # Write report
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)

            print(f"📄 Отчет сохранен в: {report_path}")

        except Exception as e:
            print(f"❌ Ошибка при сохранении отчета: {e}")

    def _generate_markdown_report(
        self, results: ProcessingResults, is_update: bool = False
    ) -> str:
        """Generate markdown report content"""
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Header
        if is_update:
            content = "# Отчет о постобработке документов (обновлен)\n\n"
        else:
            content = "# Отчет о постобработке документов\n\n"

        content += f"**Дата создания:** {timestamp_str}\n"
        content += "**Генератор:** DocxMD Converter v0.1.0\n\n"

        # Executive Summary
        content += "## Краткое резюме\n\n"
        content += f"✅ **Успешно обработано:** {results.processed} документов\n"
        content += f"⏭️ **Пропущено:** {results.skipped} документов\n"
        content += f"❌ **Ошибок:** {results.errors}\n"
        content += f"📁 **Всего файлов:** {results.total}\n\n"

        # Status
        if results.errors == 0:
            status = "✅ Задача выполнена успешно"
        elif results.processed > 0:
            status = "⚠️ Выполнено с предупреждениями"
        else:
            status = "❌ Выполнение не удалось"

        content += f"**Общий статус:** {status}\n\n"

        # Success rate
        if results.total > 0:
            success_rate = (results.processed / results.total) * 100
            content += f"**Процент успеха:** {success_rate:.1f}%\n\n"

        content += "---\n\n"

        # Quality Statistics
        if any(results.quality_stats.values()):
            content += "## Статистика качества обработки\n\n"
            total_processed = sum(results.quality_stats.values())

            if total_processed > 0:
                high_pct = (results.quality_stats["high"] / total_processed) * 100
                medium_pct = (results.quality_stats["medium"] / total_processed) * 100
                low_pct = (results.quality_stats["low"] / total_processed) * 100

                content += "| Качество | Количество файлов | Процент | Описание |\n"
                content += "|----------|-------------------|---------|----------|\n"
                high_desc = "Все разделы заполнены структурированным содержимым"
                medium_desc = "Большинство разделов заполнено"
                low_desc = "Только структура, минимум содержимого"

                content += f"| **🟢 Высокое** | {results.quality_stats['high']} | {high_pct:.1f}% | {high_desc} |\n"
                content += f"| **🟡 Среднее** | {results.quality_stats['medium']} | {medium_pct:.1f}% | {medium_desc} |\n"
                content += f"| **🔴 Низкое** | {results.quality_stats['low']} | {low_pct:.1f}% | {low_desc} |\n\n"

        # Processing Details
        if results.processed > 0:
            content += "## Детали обработки\n\n"
            content += "### ✅ Успешно обработанные файлы\n\n"

            if len(results.files_processed) <= 20:
                # Show all files if not too many
                for i, file_path in enumerate(results.files_processed, 1):
                    content += f"{i}. `{Path(file_path).name}`\n"
            else:
                # Show first 10 and last 10
                for i, file_path in enumerate(results.files_processed[:10], 1):
                    content += f"{i}. `{Path(file_path).name}`\n"
                content += (
                    f"... (пропущено {len(results.files_processed) - 20} файлов) ...\n"
                )
                for i, file_path in enumerate(
                    results.files_processed[-10:], len(results.files_processed) - 9
                ):
                    content += f"{i}. `{Path(file_path).name}`\n"

            content += "\n"

        # Skipped files
        if results.files_skipped:
            content += "### ⏭️ Пропущенные файлы\n\n"
            content += "Следующие файлы были пропущены (уже обработаны ранее):\n\n"

            for file_path in results.files_skipped[:10]:  # Show max 10
                content += f"- `{Path(file_path).name}`\n"

            if len(results.files_skipped) > 10:
                content += f"- ... и еще {len(results.files_skipped) - 10} файлов\n"

            content += "\n"

        # Errors
        if results.files_errored:
            content += "### ❌ Ошибки обработки\n\n"
            content += "Следующие файлы не удалось обработать:\n\n"

            for error in results.files_errored[:10]:  # Show max 10
                content += f"- {error}\n"

            if len(results.files_errored) > 10:
                content += f"- ... и еще {len(results.files_errored) - 10} ошибок\n"

            content += "\n"

        # Recommendations
        content += "---\n\n"
        content += "## Рекомендации\n\n"

        if results.quality_stats["low"] > 0:
            low_count = results.quality_stats['low']
            content += f"### 📝 Документы с низким качеством ({low_count} шт.)\n\n"
            recommendation = "Рекомендуется ручная доработка документов с низким качеством обработки:"
            content += f"{recommendation}\n\n"
            content += (
                '1. Найдите документы с `"processing_quality": "low"` в метаданных\n'
            )
            content += "2. Дополните содержимое разделов вручную\n"
            content += "3. Обновите метаданные после доработки\n\n"

        if results.files_errored:
            content += (
                f"### 🔧 Устранение ошибок ({len(results.files_errored)} шт.)\n\n"
            )
            content += "Для исправления ошибок:\n\n"
            content += "1. Проверьте права доступа к файлам\n"
            content += "2. Убедитесь в корректности кодировки файлов (UTF-8)\n"
            content += "3. Проверьте структуру исходных документов\n"
            content += (
                "4. Попробуйте повторную обработку с флагом `--force-process`\n\n"
            )

        # Next steps
        content += "### 🚀 Дальнейшие действия\n\n"
        content += (
            "1. **Проверка качества:** Просмотрите документы с низким качеством\n"
        )
        content += "2. **Ручная доработка:** Дополните содержимое при необходимости\n"
        content += "3. **Повторная обработка:** Используйте улучшенный алгоритм\n"
        content += "4. **Интеграция:** Внедрите обработку в процесс CI/CD\n\n"

        # Technical Information
        content += "---\n\n"
        content += "## Техническая информация\n\n"
        content += f"**Время выполнения:** {timestamp_str}\n"
        content += "**Версия обработчика:** DocxMD Converter v0.1.0\n"
        content += "**Формат данных:** Markdown с JSON метаданными\n\n"

        # Metadata
        metadata = {
            "report_type": "processing_report",
            "generated_at": timestamp_str,
            "generator": "docxmd_converter",
            "version": "0.1.0",
            "statistics": results.to_dict(),
        }

        content += "<!-- REPORT METADATA\n"
        content += json.dumps(metadata, indent=2, ensure_ascii=False)
        content += "\n-->\n"

        return content

    def generate_summary_report(self, results: ProcessingResults) -> str:
        """Generate brief summary report"""
        if results.total == 0:
            return "📋 Нет файлов для обработки"

        status_emoji = (
            "✅" if results.errors == 0 else ("⚠️" if results.processed > 0 else "❌")
        )

        summary = (
            f"{status_emoji} Обработка завершена: "
            f"{results.processed}/{results.total} файлов"
        )

        if results.skipped > 0:
            summary += f", пропущено: {results.skipped}"

        if results.errors > 0:
            summary += f", ошибок: {results.errors}"

        return summary


# Convenience functions for quick reporting
def print_processing_summary(results: ProcessingResults) -> None:
    """Print quick processing summary"""
    reporter = ProcessingReporter()
    print(reporter.generate_summary_report(results))


def save_processing_report(
    results: ProcessingResults,
    output_dir: Union[str, Path] = None,
    update_existing: bool = False,
) -> None:
    """Save processing report to file"""
    reporter = ProcessingReporter()
    reporter.generate_report(
        results, format="file", update_existing=update_existing, output_dir=output_dir
    )
