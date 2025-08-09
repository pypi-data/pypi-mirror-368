import textwrap
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import jinja2

from .utils import get_git_name


def name_formatter(name: str) -> str:
    """Format names for display in markdown."""
    return name.replace("_", " ").title()


FIELD_CHANGES_TABLE = jinja2.Template("""
| Field | From | To |
| ----- | ---- | -- |
{% for field, (from_val, to_val) in changes.items() -%}
| {{name_formatter(field)}} | <code>{{ from_val or "*No Value*" }}</code> | <code>{{ to_val or "*No Value*" }}</code> |
{% endfor %}
""")


def get_field_changes_table(changes: dict[str, tuple[Any, Any]]) -> str:
    parsed_data = {k: (get_git_name(a), get_git_name(b)) for k, (a, b) in changes.items()}
    return FIELD_CHANGES_TABLE.render(
        changes=parsed_data,
        name_formatter=name_formatter,
    )


class ChangeType(Enum):
    ADDED = "ADDED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    NO_CHANGE = "NO_CHANGE"  # used when only changes in children are present


@dataclass
class Change:
    id: str
    change_type: ChangeType
    entity: Any  # The entity itself, e.g., a table or measure object
    field_changes: dict[str, tuple[Any, Any]] = field(default_factory=dict)  # field name to [old_value, new_value]


@dataclass
class FilterChange(Change):
    def to_markdown(self) -> str:
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"""
Filter: {self.entity.get_display_name()}

**Filter {self.change_type.value.title()}**
"""

        filter_change_table = get_field_changes_table(self.field_changes)
        return f"""

Filter: {self.entity.get_display_name()}

{filter_change_table}
"""


@dataclass
class VisualChange(Change):
    filters: list[FilterChange] = field(default_factory=list)
    data_changes: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert the visual change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"**Visual {self.change_type.value.title()}**"

        ret = ""
        if self.field_changes:
            ret += get_field_changes_table(self.field_changes)

        if self.filters:
            filter_section = "#### *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)
            ret += "\n"
        if self.data_changes:
            data_section = "#### *Updated Data Queries*\n"
            data_section += "| Section | Source | Action |\n"
            data_section += "| ------- | ------ | ------ |\n"
            for field, changes in self.data_changes.items():
                for change_type in ["added", "removed"]:
                    for item in changes.get(change_type, []):
                        data_section += f"| {field} | {item} | {change_type.title()} |\n"
            ret += textwrap.indent(data_section, "> ", predicate=lambda _line: True)
        return ret


@dataclass
class SectionChange(Change):
    filters: list[FilterChange] = field(default_factory=list)
    visuals: list[VisualChange] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert the section change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"**Section {self.change_type.value.title()}**"

        ret = ""
        if self.field_changes:
            ret += get_field_changes_table(self.field_changes)

        if self.filters:
            filter_section = "### *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)

        return ret


@dataclass
class LayoutChange(Change):
    filters: list[FilterChange] = field(default_factory=list)
    sections: list[SectionChange] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert the layout change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return "No changes in report layout."

        ret = ""

        if self.filters:
            filter_section = "## *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)

        return ret


@dataclass
class SsasChange(Change):
    entity_type: str = "--undefined--"  # e.g., "table", "measure", "column"


@dataclass
class DiffReport:
    layout_changes: LayoutChange
    ssas_changes: dict[str, list[SsasChange]]

    def to_markdown(self) -> str:
        """Convert the diff report to a markdown string."""
        from .to_markdown import to_markdown  # noqa: PLC0415

        return to_markdown(self)

    def to_pdf(self, file_path: str) -> None:
        def add_ids(line: str) -> str:
            if not line.lstrip().startswith("#"):
                return line

            # we're relying on the fact that the string in lstrip is actually a set
            title = line.lstrip(" #")
            title_id = title.lower().replace(" ", "-")
            heading_prefix = line[0 : line.index(title)]
            return f"{heading_prefix} <a id='{title_id}'></a>{title}"

        """Summary here

        Note:
            markdown_pdf doesn't handle temporary files well, that's why we save directly to a file path.

        """
        from markdown_pdf import MarkdownPdf, Section  # noqa: PLC0415

        # mode gfm-like requires linkify-it-py
        css = (Path(__file__).parent / "templates" / "github-dark.css").read_text()

        markdown_content = self.to_markdown()
        markdown_content = "\n".join(add_ids(x) for x in markdown_content.splitlines())
        pdf = MarkdownPdf(mode="gfm-like")
        pdf.add_section(Section(markdown_content), user_css=css)
        pdf.save(file_path)

    def layout_updates(self) -> int:
        """Count the number of layout updates."""
        return len(self.layout_changes.field_changes) + len(self.layout_changes.filters)

    def section_updates(self) -> int:
        """Count the number of section updates."""
        return sum(len(section.field_changes) + len(section.filters) for section in self.layout_changes.sections)

    def visual_updates(self) -> int:
        """Count the number of visual updates."""
        return sum(
            len(visual.field_changes) + len(visual.filters)
            for section in self.layout_changes.sections
            for visual in section.visuals
        )
