import os
import re
import yaml
from typing import Dict, List, Optional
from pydantic import BaseModel


# -----------------------------------------------------------------------------
# 1) Shared “minimal fields” base class
# -----------------------------------------------------------------------------
class EntitySummary(BaseModel):
    id: str
    name: str
    title: str


# -----------------------------------------------------------------------------
# 2) Full domain models extend EntitySummary
# -----------------------------------------------------------------------------
class AIControl(EntitySummary):
    description: Optional[str] = ""
    plugins: List[str] = []
    tactics: List[str] = []


class AIFramework(EntitySummary):
    description: Optional[str] = ""
    controls: List[AIControl] = []


# -----------------------------------------------------------------------------
# 3) DTO/View classes reuse EntitySummary for minimal fields
# -----------------------------------------------------------------------------
class AIFrameworkSummary(EntitySummary):
    pass


class AIControlSummary(EntitySummary):
    pass


class AIControlView(AIControlSummary):
    framework: AIFrameworkSummary


class AIFrameworkView(AIFrameworkSummary):
    controls: List[AIControlSummary] = []


# -----------------------------------------------------------------------------
# 4) Repository managing YAML-backed frameworks + utility methods
# -----------------------------------------------------------------------------
class AIFrameworkRepo:
    """
    Repository for managing AI risk frameworks.
    Reads framework definitions from `ai_frameworks.yml`.
    """
    _frameworks: Dict[str, AIFramework] = {}

    @classmethod
    def get_file_path(cls, file_name: str) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, file_name)

    @classmethod
    def load_frameworks(cls, file_name: str = "ai_frameworks.yml") -> None:
        path = cls.get_file_path(file_name)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        cls._frameworks = {}
        for fw_data in data.get("frameworks", []):
            controls = [AIControl(**section) for section in fw_data.get("sections", [])]
            framework = AIFramework(
                id=fw_data.get("id"),
                name=fw_data.get("name"),
                title=fw_data.get("title"),
                description=fw_data.get("description", ""),
                controls=controls,
            )
            cls._frameworks[framework.id] = framework

    # Detailed methods (return full domain objects)
    @classmethod
    def get_all_frameworks_detailed(cls) -> List[AIFramework]:
        if not cls._frameworks:
            cls.load_frameworks()
        return list(cls._frameworks.values())

    @classmethod
    def get_framework_detailed(cls, framework_id: str) -> Optional[AIFramework]:
        if not cls._frameworks:
            cls.load_frameworks()
        return cls._frameworks.get(framework_id)

    @classmethod
    def get_controls_detailed(cls, framework_id: str) -> List[AIControl]:
        fw = cls.get_framework_detailed(framework_id)
        return fw.controls if fw else []

    # Summary/minimal methods
    @classmethod
    def get_frameworks_minimal(cls) -> List[AIFrameworkSummary]:
        if not cls._frameworks:
            cls.load_frameworks()
        return [AIFrameworkSummary(id=fw.id, name=fw.name, title=fw.title)
                for fw in cls._frameworks.values()]

    @classmethod
    def get_frameworks(cls) -> List[AIFrameworkView]:
        if not cls._frameworks:
            cls.load_frameworks()
        views: List[AIFrameworkView] = []
        for fw in cls._frameworks.values():
            ctrl_summaries = [AIControlSummary(id=c.id, name=c.name, title=c.title)
                              for c in fw.controls]
            views.append(AIFrameworkView(id=fw.id, name=fw.name, title=fw.title,
                                         controls=ctrl_summaries))
        return views

    @classmethod
    def get_framework_by_id(cls, framework_id: str) -> Optional[AIFrameworkView]:
        if not cls._frameworks:
            cls.load_frameworks()
        fw = cls._frameworks.get(framework_id)
        if not fw:
            return None
        ctrl_summaries = [AIControlSummary(id=c.id, name=c.name, title=c.title)
                          for c in fw.controls]
        return AIFrameworkView(id=fw.id, name=fw.name, title=fw.title,
                                controls=ctrl_summaries)

    @classmethod
    def get_control_by_id(cls, control_id: str) -> Optional[AIControlView]:
        if not cls._frameworks:
            cls.load_frameworks()
        for fw in cls._frameworks.values():
            for c in fw.controls:
                if c.id == control_id:
                    fw_sum = AIFrameworkSummary(id=fw.id, name=fw.name, title=fw.title)
                    return AIControlView(id=c.id, name=c.name, title=c.title,
                                          framework=fw_sum)
        return None

    @classmethod
    def get_controls_by_plugin(cls, plugin_id: str) -> List[AIControlView]:
        if not cls._frameworks:
            cls.load_frameworks()
        result: List[AIControlView] = []
        for fw in cls._frameworks.values():
            fw_sum = AIFrameworkSummary(id=fw.id, name=fw.name, title=fw.title)
            for c in fw.controls:
                if plugin_id in c.plugins:
                    result.append(AIControlView(id=c.id, name=c.name, title=c.title,
                                                 framework=fw_sum))
        return result

    @classmethod
    def search_frameworks(cls, pattern: str) -> List[AIFramework]:
        """
        Search frameworks by ID, name, or title using a keyword or regex pattern (case-insensitive).
        """
        if not cls._frameworks:
            cls.load_frameworks()

        regex = re.compile(pattern, re.IGNORECASE)
        matched: List[AIFramework] = []

        for fw in cls._frameworks.values():
            if regex.search(fw.id) or regex.search(fw.name) or regex.search(fw.title):
                matched.append(fw)

        return matched

    @classmethod
    def search_plugins(cls, pattern: str) -> List[str]:
        """
        Search frameworks by keyword or regex, and return a unique list of plugin IDs
        from all matching framework controls.
        """
        if not cls._frameworks:
            cls.load_frameworks()

        import re
        regex = re.compile(pattern, re.IGNORECASE)
        plugin_set = set()

        for fw in cls._frameworks.values():
            if regex.search(fw.id) or regex.search(fw.name) or regex.search(fw.title):
                for control in fw.controls:
                    plugin_set.update(control.plugins)

        return sorted(plugin_set)


"""
# How will to be used 
#
#

Generate Dashboard

Score by framework names (ids)

under each framework 
 score by ai control

for each detailed finding, add impacted AI Framework: AI Controls

Get list of frameworks to display 

"""

