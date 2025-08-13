import os
import re
import yaml
from typing import Dict, List, Optional
from dtx_models.scope import Plugin, PluginTaxonomyMapping, RiskTaxonomy

class PluginRepo:
    """
    Repository for managing plugins.

    Reads plugin details from `plugins.yml` and taxonomy mappings from `taxonomy.yml`.
    """

    _plugins: Dict[str, Plugin] = {}

    @classmethod
    def get_file_path(cls, file_name: str) -> str:
        """
        Determines the absolute path of a YAML file in the current script's directory.
        """
        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # Get the directory of this script
        return os.path.join(current_dir, file_name)

    @classmethod
    def load_plugins(cls):
        """
        Loads plugins from `plugins.yml` and updates their taxonomy mappings using `taxonomy.yml`.
        """
        plugin_file_path = cls.get_file_path("plugins.yml")
        taxonomy_file_path = cls.get_file_path("taxonomy.yml")

        # Load plugins.yml
        with open(plugin_file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            cls._plugins = {
                plugin_data["id"]: Plugin(**plugin_data)
                for plugin_data in data.get("plugins", [])
            }

        # Load taxonomy.yml and update plugin taxonomy mappings
        with open(taxonomy_file_path, "r", encoding="utf-8") as file:
            taxonomy_data = yaml.safe_load(file)

            for taxonomy_name, mappings in taxonomy_data.items():
                for mapping in mappings:
                    plugin_id = mapping["plugin_id"]
                    if plugin_id in cls._plugins:
                        taxonomy_mapping = PluginTaxonomyMapping(
                            taxonomy=RiskTaxonomy[
                                taxonomy_name
                            ],  # Convert string to Enum
                            category=mapping["category"],
                            id=mapping["id"],
                            title=mapping["title"],
                        )
                        cls._plugins[plugin_id].taxonomy_mappings.append(
                            taxonomy_mapping
                        )

    @classmethod
    def get_all_plugins(cls) -> List[str]:
        """
        Returns a list of all available plugin IDs.
        """
        if not cls._plugins:
            cls.load_plugins()
        return list(cls._plugins.keys())

    @classmethod
    def get_plugins(cls) -> List[Plugin]:
        """
        Returns a list of all available plugin IDs.
        """
        if not cls._plugins:
            cls.load_plugins()
        return list(cls._plugins.values())

    @classmethod
    def get_plugin_descriptions(
        cls, plugins: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Returns a dictionary of all plugin IDs and their summaries.
        If a list of plugin IDs is provided, only those descriptions will be returned.
        """
        if not cls._plugins:
            cls.load_plugins()

        if plugins:
            return {
                plugin_id: cls._plugins[plugin_id].summary
                for plugin_id in plugins
                if plugin_id in cls._plugins
            }

        return {plugin_id: plugin.summary for plugin_id, plugin in cls._plugins.items()}

    @classmethod
    def get_plugin_descriptions_as_str(cls, plugins: Optional[List[str]] = None) -> str:
        list_of_risks = cls.get_plugin_descriptions(plugins)
        risks = ""
        for k, v in list_of_risks.items():
            risks += f"{k}: {v}\n--\n"
        return risks

    @classmethod
    def get_plugin_taxonomy_mappings(
        cls, plugin_id: str
    ) -> Optional[List[PluginTaxonomyMapping]]:
        """
        Retrieves the taxonomy mappings for a given plugin ID.
        """
        if not cls._plugins:
            cls.load_plugins()

        plugin = cls._plugins.get(plugin_id)
        return plugin.taxonomy_mappings if plugin else None

    @classmethod
    def get_plugin_by_id(cls, plugin_id: str) -> Optional[Plugin]:
        """
        Return the Plugin object for `plugin_id`, or None if unknown.
        """
        if not cls._plugins:
            cls.load_plugins()
        return cls._plugins.get(plugin_id)

    @classmethod
    def get_unique_categories(cls) -> List[str]:
        """
        Returns a sorted list of all unique plugin categories.
        """
        if not cls._plugins:
            cls.load_plugins()
        return sorted({plugin.category for plugin in cls._plugins.values()})

    @classmethod
    def get_unique_subcategories(cls) -> List[str]:
        """
        Returns a sorted list of all unique plugin subcategories.
        """
        if not cls._plugins:
            cls.load_plugins()
        return sorted({plugin.subcategory for plugin in cls._plugins.values()})

    @classmethod
    def get_unique_tags(cls) -> List[str]:
        """
        Returns a sorted list of all unique tags across all plugins.
        """
        if not cls._plugins:
            cls.load_plugins()
        tags_set = set()
        for plugin in cls._plugins.values():
            # plugin.tags is a List[str], or may not exist
            for t in getattr(plugin, "tags", []) or []:
                tags_set.add(t)
        return sorted(tags_set)

    @classmethod
    def get_plugins_by_tag(cls, tag: str) -> List[Plugin]:
        """
        Returns all Plugin objects that include the given tag.
        """
        if not cls._plugins:
            cls.load_plugins()
        return [p for p in cls._plugins.values() if tag in (getattr(p, "tags", []) or [])]
    
    @classmethod
    def search(cls, expressions: List[str]) -> List[Plugin]:
        """
        Searches for plugins whose IDs or tags match any of the provided expressions.
        Supports both regex patterns and plain keywords (case-insensitive).

        Args:
            expressions (List[str]): A list of regex patterns or plain text keywords.

        Returns:
            List[Plugin]: A list of matching Plugin objects.
        """
        if not cls._plugins:
            cls.load_plugins()

        results = []
        seen_plugin_ids = set()

        for plugin in cls._plugins.values():
            searchable_fields = [plugin.id.lower()] + [tag.lower() for tag in getattr(plugin, "tags", []) or []]

            for expr in expressions:
                pattern = re.compile(expr, re.IGNORECASE)
                if any(pattern.search(field) for field in searchable_fields):
                    if plugin.id not in seen_plugin_ids:
                        results.append(plugin)
                        seen_plugin_ids.add(plugin.id)
                    break  # Stop checking other expressions if a match is found

        return results
