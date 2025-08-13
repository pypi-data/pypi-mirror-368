from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .evaluator import EvaluatorInScope
from .providers.base import ProviderType
from .providers.gradio import GradioProvider
from .providers.hf import HFProvider
from .providers.http import HttpProvider
from .providers.litellm import LitellmProvider
from .providers.ollama import OllamaProvider
from .providers.openai import OpenaiProvider
from .tactic import PromptMutationTactic
from .template.prompts.base import PromptsRepoType
from .template.prompts.langhub import LangHubPromptTemplate


class AgentInfo(BaseModel):
    """Represents an AI agent with various integrations, capabilities, and restrictions."""

    name: Optional[str] = Field(default_factory=lambda: "")  # Default value for name
    description: str
    external_integrations: Optional[List[str]] = Field(default_factory=lambda: [])
    internal_integrations: Optional[List[str]] = Field(default_factory=lambda: [])
    trusted_users: Optional[List[str]] = Field(default_factory=lambda: [])
    untrusted_users: Optional[List[str]] = Field(default_factory=lambda: [])
    llms: Optional[List[str]] = Field(default_factory=lambda: [])
    capabilities: Optional[List[str]] = Field(default_factory=lambda: [])
    restrictions: Optional[List[str]] = Field(default_factory=lambda: [])
    security_note: Optional[str] = Field(default_factory=lambda: "")
    include_attacker_goals: Optional[List[str]] = Field(default_factory=lambda: [])


class RiskTaxonomy(Enum):
    """
    Enum representing different risk taxonomies.
    """

    DETOXIO = "DETOXIO"
    OWASP_2025 = "OWASP_2025"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class PluginTaxonomyMapping(BaseModel):
    """
    Provides mapping between plugins and different taxonomies.
    """

    taxonomy: RiskTaxonomy  # Taxonomy Name
    category: str
    id: str
    title: str  # Mapped name in the taxonomy


class Plugin(BaseModel):
    """
    Pydantic model representing a Plugin entry.
    """

    id: str
    title: str
    name: str
    category: str
    subcategory: str
    summary: Optional[str] = None  # Summary is optional
    taxonomy_mappings: Optional[List[PluginTaxonomyMapping]] = []  # List of taxonomies
    tags: Optional[List[str]] = []


class PluginInScopeConfig(BaseModel):
    """Configuration for each plugin with an ID and number of tests."""

    id: str  # Now using string from PluginRepo
    num_tests: int = 5


class PluginsInScope(BaseModel):
    """
    Represents a collection of plugins, allowing either:
    - A list of plugin IDs (str)
    - A list of PluginConfig objects (which include ID and num_tests)
    """

    plugins: List[Union[str, PluginInScopeConfig]]

    def get_plugin_ids(self) -> List[str]:
        plugin_ids = []
        for p in self.plugins:
            if isinstance(p, str):
                plugin_ids.append(p)
            else:
                plugin_ids.append(p.id)
        return plugin_ids


class RedTeamSettings(BaseModel):
    """Other red team settings."""

    max_prompts: int = 15
    max_plugins: int = 5
    max_prompts_per_plugin: int = 5
    max_goals_per_plugin: int = 1 # Number of goals/behaviours per plugin
    max_prompts_per_tactic: int = 5
    plugins: PluginsInScope
    # Various strategies to perform red teaming
    tactics: Optional[List[PromptMutationTactic]] = Field(
        default_factory=list, description="Strategies to perform red teaming"
    )
    # An optional evaluator to override all evaluation methods globally.
    global_evaluator: Optional[EvaluatorInScope] = Field(
        default=None, description="Global Evaluator, if any, to evaluate the prompts"
    )


class ProviderVars(BaseModel):
    """
    Holds key-value pairs where values may include `{{env.ENV_NAME}}` placeholders.
    """

    vars: Dict[str, Any] = Field(
        description="List of key and value pairs", default_factory=dict
    )


class ProvidersWithEnvironments(BaseModel):
    providers: Optional[
        List[
            HttpProvider
            | HFProvider
            | GradioProvider
            | OllamaProvider
            | OpenaiProvider
            | LitellmProvider
        ]
    ] = Field(description="List of targets to Test", default_factory=list)

    prompts: Optional[List[LangHubPromptTemplate]] = Field(
        description="List of targets to Test", default_factory=list
    )
    environments: Optional[List[ProviderVars]] = Field(
        description="List of Variables to customize providers",
        default_factory=list,
    )

    @model_validator(mode="before")
    @classmethod
    def validate_providers(cls, values):
        """
        Ensure the correct provider type is instantiated based on 'id'.
        """
        providers_data = values.get("providers", [])
        parsed_providers = []

        for provider_data in providers_data:
            if isinstance(provider_data, dict):
                provider_id = provider_data.get("provider")
                if provider_id == ProviderType.HTTP.value:
                    parsed_providers.append(HttpProvider(**provider_data))
                elif provider_id == ProviderType.GRADIO.value:
                    parsed_providers.append(GradioProvider(**provider_data))
                elif provider_id == ProviderType.HF.value:
                    parsed_providers.append(HFProvider(**provider_data))
                elif provider_id == ProviderType.OLLAMA.value:
                    parsed_providers.append(OllamaProvider(**provider_data))
                elif provider_id == ProviderType.OPENAI.value:
                    parsed_providers.append(OpenaiProvider(**provider_data))
                elif provider_id == ProviderType.LITE_LLM.value:
                    parsed_providers.append(LitellmProvider(**provider_data))
                else:
                    raise ValueError(f"Unknown provider type: {provider_id}")
            else:
                parsed_providers.append(provider_data)

        values["providers"] = parsed_providers
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_prompts(cls, values):
        """
        Ensure the correct prompt type is instantiated based on 'id'.
        """
        prompts_data = values.get("prompts", [])
        parsed_prompts = []

        for prompt_data in prompts_data:
            if isinstance(prompt_data, dict):
                prompt_id = prompt_data.get("id")
                if prompt_id == PromptsRepoType.LANGHUB.value:
                    parsed_prompts.append(LangHubPromptTemplate(**prompt_data))
                else:
                    raise ValueError(f"Unknown prompt repo type: {prompt_id}")
            else:
                parsed_prompts.append(prompt_data)

        values["prompts"] = parsed_prompts
        return values


class RedTeamScope(ProvidersWithEnvironments):
    """Represents a red teaming scope, which includes an agent and its related details."""

    agent: AgentInfo
    redteam: RedTeamSettings
