# dtx_service/db/pgv/crud/plugin_mapper.py

from typing import List, Optional
from pydantic import BaseModel

from .plugin import PluginRepo
from .ai_frameworks import AIFrameworkRepo


# --- 1)  Pydantic models for the view layer --- #

class ComplianceControl(BaseModel):
    """
    A minimal view of one compliance control, with framework + control metadata.
    """
    framework_id: str
    framework_title: str
    framework_description: Optional[str]

    control_id: str
    control_title: str
    control_description: Optional[str]


class PluginDetail(BaseModel):
    """
    Full plugin info + the set of compliance controls it maps to.
    """
    id: str
    name: str
    title: str
    category: str
    subcategory: str
    summary: Optional[str]

    compliance_controls: List[ComplianceControl] = []


# --- 2) The Mapper itself --- #

class Plugin2FrameworkMapper:
    def __init__(
        self,
        plugin_repo: Optional[PluginRepo] = None,
        framework_repo: Optional[AIFrameworkRepo] = None,
    ):
        self.plugin_repo = plugin_repo or PluginRepo()
        self.framework_repo = framework_repo or AIFrameworkRepo()

    def get_plugin_with_frameworks(self, plugin_id: str) -> Optional[PluginDetail]:
        plugin = self.plugin_repo.get_plugin_by_id(plugin_id)
        if not plugin:
            return None

        controls_list: List[ComplianceControl] = []
        for fw in self.framework_repo.get_all_frameworks_detailed():
            for ctrl in fw.controls:
                if plugin_id in ctrl.plugins:
                    controls_list.append(
                        ComplianceControl(
                            framework_id=fw.id,
                            framework_title=fw.title,
                            framework_description=fw.description,
                            control_id=ctrl.id,
                            control_title=ctrl.title,
                            control_description=ctrl.description,
                        )
                    )

        return PluginDetail(
            id=plugin.id,
            name=plugin.name,
            title=plugin.title,
            category=plugin.category,
            subcategory=plugin.subcategory,
            summary=plugin.summary,
            compliance_controls=controls_list,
        )
