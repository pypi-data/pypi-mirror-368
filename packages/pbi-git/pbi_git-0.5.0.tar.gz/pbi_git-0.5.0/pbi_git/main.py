from typing import TYPE_CHECKING

from .change_classes import DiffReport
from .layout_diffs import layout_diff
from .ssas import ssas_diff

if TYPE_CHECKING:
    from pbyx.main import LocalReport


def diff(parent: "LocalReport", child: "LocalReport") -> DiffReport:
    layout_changes = layout_diff(parent.static_files.layout, child.static_files.layout)
    ssas_changes = ssas_diff(parent.ssas, child.ssas)
    return DiffReport(
        layout_changes=layout_changes,
        ssas_changes=ssas_changes,
    )
