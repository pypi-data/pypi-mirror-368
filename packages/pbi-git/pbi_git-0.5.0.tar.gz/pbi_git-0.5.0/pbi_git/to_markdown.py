from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

from .change_classes import ChangeType

if TYPE_CHECKING:
    from pbi_git.change_classes import DiffReport


TEMPLATES = {
    p.stem: jinja2.Template(p.read_text()) for p in (Path(__file__).parent / "templates" / "markdown").iterdir()
}


def name_formatter(name: str) -> str:
    """Format names for display in markdown."""
    return name.replace("_", " ").title()


def to_markdown(diff_report: "DiffReport") -> str:
    summary = TEMPLATES["summary"].render(diff_report=diff_report)
    tables_without_changes = ", ".join(table for table, changes in diff_report.ssas_changes.items() if not changes)
    tables_with_changes = {table: changes for table, changes in diff_report.ssas_changes.items() if changes}
    ssas = TEMPLATES["ssas"].render(
        ssas_changes=diff_report.ssas_changes,
        tables_with_changes=tables_with_changes,
        tables_without_changes=tables_without_changes,
        name_formatter=name_formatter,
    )
    layout = TEMPLATES["layout"].render(
        layout_changes=diff_report.layout_changes,
        ChangeType=ChangeType,
    )
    return TEMPLATES["main"].render(summary=summary, ssas=ssas, layout=layout)
