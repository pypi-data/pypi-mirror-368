import os
import glob
import yaml
from typing import Optional, Union, List, Type, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel

from dtx_models.providers.hf import HFModels, HuggingFaceProviderConfig
from dtx_models.providers.litellm import LitellmProviderConfig
from dtx_models.providers.anthropic import AnthropicProviderConfig
from dtx_models.providers.mistral import MistralProviderConfig
from dtx_models.providers.gemini import GeminiProviderConfig
from dtx_models.providers.cerebras import CerebrasProviderConfig
from dtx_models.providers.azure_openAI import AzureProviderConfig
from dtx_models.providers.bedrock_claude import BedrockClaudeProviderConfig
from dtx_models.providers.openai import OpenaiProviderConfig


# --- Exceptions ---
class ModelNotFoundError(Exception):
    pass

class ModelFilesNotFoundError(Exception):
    pass


# --- Base Models ---
class LiteLLMModels(BaseModel):
    litellm: List[LitellmProviderConfig] = []



class BaseModelRepo(ABC):
    provider_name: str

    @abstractmethod
    def get_model(self, model_name: str) -> Any:
        pass

    @abstractmethod
    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        pass

    @abstractmethod
    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[Any]:
        pass

    @abstractmethod
    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[Any]:
        pass

class StaticFileModelRepo(BaseModelRepo):
    provider_name: str  # must be set by subclass
    _yaml_key: str      # key in YAML (e.g. "openai", "huggingface")
    _model_class: Type[BaseModel]  # pydantic model

    def __init__(self, models_path: Optional[str] = None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self._models_path = os.path.join(script_dir, models_path or f"{self.provider_name}_models.yml")
        self.models = self._load_from_file()

    def _load_from_file(self) -> List[BaseModel]:
        if not os.path.exists(self._models_path):
            return []
        with open(self._models_path, "r") as file:
            data = yaml.safe_load(file) or {}
        return [self._model_class(**model) for model in data.get(self._yaml_key, [])]

    def get_model(self, model_name: str) -> BaseModel:
        model = next((m for m in self.models if m.model == model_name), None)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[BaseModel]:
        keyword = keyword.lower()
        matches = [m for m in self.models if keyword in str(m.model_dump_json()).lower()]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[BaseModel]:
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]

class OpenAIModelsRepo(StaticFileModelRepo):
    provider_name = "openai"
    _yaml_key = "openai"
    _model_class = OpenaiProviderConfig


# # --- Fetcher for HuggingFace ---
# class HuggingFaceModelFetcher:
#     TASK_TAGS_TO_ENUM = {
#         "text-generation": HuggingFaceTask.TEXT_GENERATION,
#         "text2text-generation": HuggingFaceTask.TEXT2TEXT_GENERATION,
#         "text-classification": HuggingFaceTask.TEXT_CLASSIFICATION,
#         "token-classification": HuggingFaceTask.TOKEN_CLASSIFICATION,
#         "fill-mask": HuggingFaceTask.FILL_MASK,
#         "feature-extraction": HuggingFaceTask.FEATURE_EXTRACTION,
#         "sentence-similarity": HuggingFaceTask.SENTENCE_SIMILARITY,
#     }

#     DEFAULT_CONFIGS = {
#         HuggingFaceTask.TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
#         HuggingFaceTask.TEXT2TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
#         HuggingFaceTask.FILL_MASK: {},
#         HuggingFaceTask.TEXT_CLASSIFICATION: {},
#         HuggingFaceTask.TOKEN_CLASSIFICATION: {},
#         HuggingFaceTask.FEATURE_EXTRACTION: {},
#         HuggingFaceTask.SENTENCE_SIMILARITY: {},
#     }

#     def __init__(self):
#         self.api = HfApi()

#     def fetch(self, model_name: str) -> HuggingFaceProviderConfig:
#         try:
#             info = self.api.model_info(model_name)

#             task_enum = next(
#                 (self.TASK_TAGS_TO_ENUM[tag] for tag in info.tags if tag in self.TASK_TAGS_TO_ENUM),
#                 HuggingFaceTask.TEXT_GENERATION
#             )

#             support_multi = any(
#                 re.search(r"(chat|dialog|instruct|conversational)", tag, re.IGNORECASE)
#                 for tag in info.tags
#             )

#             config = self.DEFAULT_CONFIGS.get(task_enum, {}).copy()
#             gen_cfg = info.config.get("generation_config") or {}
#             config.update({k: v for k, v in gen_cfg.items() if k in config})

#             return HuggingFaceProviderConfig(
#                 model=model_name,
#                 task=task_enum,
#                 support_multi_turn=support_multi,
#                 supported_input_format="openai",
#                 config=config,
#             )

#         except HfHubHTTPError as e:
#             raise ModelNotFoundError(model_name) from e


# --- HuggingFace Repo ---
class HFModelsRepo(BaseModelRepo):
    provider_name = "huggingface"

    def __init__(self, models_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self._models_path = os.path.join(script_dir, models_path or "hf_models.yml")
        self.models = self._load_from_file()

    def _load_from_file(self) -> HFModels:
        if not os.path.exists(self._models_path):
            return HFModels(huggingface=[])
        with open(self._models_path, "r") as file:
            data = yaml.safe_load(file) or {}
        return HFModels(
            huggingface=[HuggingFaceProviderConfig(**model) for model in data.get("huggingface", [])]
        )

    def get_model(self, model_name: str) -> HuggingFaceProviderConfig:
        model = self.get_huggingface_model(model_name)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def get_huggingface_model(self, model_name: str) -> HuggingFaceProviderConfig:
        return next((m for m in self.models.huggingface if m.model == model_name), None)

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models.huggingface]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[HuggingFaceProviderConfig]:
        keyword = keyword.lower()
        matches = [
            m for m in self.models.huggingface if keyword in str(m.model_dump_json()).lower()
        ]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[HuggingFaceProviderConfig]:
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models.huggingface
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]


# --- LiteLLM Repo ---
class LiteLLMRepo(BaseModelRepo):
    provider_name = "litellm"

    def __init__(self, directory: str = None):
        self.directory = directory or os.path.dirname(os.path.abspath(__file__))
        self.models = self._load_models()

    def _load_models(self) -> LiteLLMModels:
        pattern = os.path.join(self.directory, "litellm_models_*.yml")
        files = glob.glob(pattern)
        if not files:
            raise ModelFilesNotFoundError(f"No model files matching pattern: {pattern}")

        merged_models = []
        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                    for model_dict in data.get("litellm", []):
                        merged_models.append(LitellmProviderConfig(**model_dict))
            except Exception as e:
                raise ModelFilesNotFoundError(f"Error loading file {file_path}: {e}") from e

        return LiteLLMModels(litellm=merged_models)

    def get_model(self, model_name: str) -> LitellmProviderConfig:
        model = next((m for m in self.models.litellm if m.model == model_name), None)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models.litellm]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[LitellmProviderConfig]:
        keyword = keyword.lower()
        matches = [
            m for m in self.models.litellm if keyword in str(m.model_dump_json()).lower()
        ]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[LitellmProviderConfig]:
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models.litellm
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]


# ------------------------------------------------------------------
# --- DRY Static Repo for YAML-backed Providers (Anthropic etc) ----
# ------------------------------------------------------------------
class StaticFileModelRepo(BaseModelRepo):
    """
    Generic Repo class for providers whose models are declared in YAML files.
    Just set provider_name, _yaml_key, _model_class, _file_name.
    """
    provider_name: str
    _yaml_key: str
    _model_class: type
    _file_name: str

    def __init__(self, models_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self._models_path = os.path.join(script_dir, models_path or self._file_name)
        self.models = self._load_from_file()

    def _load_from_file(self):
        if not os.path.exists(self._models_path):
            return []
        with open(self._models_path, "r") as file:
            data = yaml.safe_load(file) or {}
        return [self._model_class(**model) for model in data.get(self._yaml_key, [])]

    def get_model(self, model_name: str):
        model = next((m for m in self.models if m.model == model_name), None)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ):
        keyword = keyword.lower()
        matches = [
            m for m in self.models if keyword in str(m.model_dump_json()).lower()
        ]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ):
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]

# ------------------------------------------------------------------
# ---- Provider-Specific Repo Classes (Just Inherit, No Duplication)
# ------------------------------------------------------------------

# --- Anthropic Repo ----
class AnthropicModelsRepo(StaticFileModelRepo):
    provider_name = "anthropic"
    _yaml_key = "anthropic"
    _model_class = AnthropicProviderConfig
    _file_name = "anthropic_models.yml"

# ------ Mistral Repo ------
class MistralModelsRepo(StaticFileModelRepo):
    provider_name = "mistral"
    _yaml_key = "mistral"
    _model_class = MistralProviderConfig
    _file_name = "mistral_models.yml"

# ------ Gemini Repo --------
class GeminiModelsRepo(StaticFileModelRepo):
    provider_name = "gemini"
    _yaml_key = "gemini"
    _model_class = GeminiProviderConfig
    _file_name = "gemini_models.yml"

# ------- Cerebras Repo -------
class CerebrasModelsRepo(StaticFileModelRepo):
    """
    Loads and manages Cerebras models from YAML config file.
    """
    provider_name = "cerebras"
    _yaml_key = "cerebras"
    _model_class = CerebrasProviderConfig
    _file_name = "cerebras_models.yml"

# ----- Azure Repo -----
class AzureModelsRepo(StaticFileModelRepo):
    """
    Loads and manages Azure OpenAI models from YAML config file.
    """
    provider_name = "azure"
    _yaml_key = "azure"
    _model_class = AzureProviderConfig
    _file_name = "azure_models.yml"

#  ------ Bedrock Repo -------
class BedrockClaudeModelsRepo(StaticFileModelRepo):
    """
    Loads and manages Bedrock Claude (and others) models from YAML config file.
    """
    provider_name = "bedrock_claude"
    _yaml_key = "bedrock_claude"
    _model_class = BedrockClaudeProviderConfig
    _file_name = "bedrock_claude_models.yml"


# --- Model Registry ---
class ModelRegistry:
    def __init__(self):
        self.repos: List[BaseModelRepo] = self._initialize_repos()
        self.repo_map: dict[str, BaseModelRepo] = self._build_repo_map()

    def _initialize_repos(self) -> List[BaseModelRepo]:
        repo_classes: List[Type[BaseModelRepo]] = [
            HFModelsRepo, 
            LiteLLMRepo,
            AnthropicModelsRepo,
            MistralModelsRepo,
            GeminiModelsRepo,
            CerebrasModelsRepo,
            AzureModelsRepo,
            BedrockClaudeModelsRepo
            ]
        return [cls() for cls in repo_classes]

    def _build_repo_map(self) -> dict[str, BaseModelRepo]:
        repo_map = {}
        for repo in self.repos:
            repo_map[repo.provider_name] = repo
        return repo_map

    def _get_repos_by_provider(self, provider: Optional[str]) -> List[BaseModelRepo]:
        if provider is None:
            return self.repos
        repo = self.repo_map.get(provider.lower())
        return [repo] if repo else []

    def search_by_keyword(
        self, keyword: str, provider: Optional[str] = None,
        limit: Optional[int] = None, offset: int = 0
    ) -> List[Union[HuggingFaceProviderConfig, LitellmProviderConfig]]:
        results = []
        for repo in self._get_repos_by_provider(provider):
            results.extend(repo.search_models_by_keyword(keyword.lower()))
        return results[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], provider: Optional[str] = None,
        limit: Optional[int] = None, offset: int = 0
    ) -> List[Union[HuggingFaceProviderConfig, LitellmProviderConfig]]:
        lower_keywords = [kw.lower() for kw in keywords]
        results = []
        for repo in self._get_repos_by_provider(provider):
            results.extend(repo.search_keywords_all(lower_keywords))
        return results[offset : offset + limit if limit is not None else None]

    def list_all_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        all_models = [model for repo in self.repos for model in repo.list_models()]
        return all_models[offset : offset + limit if limit is not None else None]

    def get_model(self, model_name: str, provider: Optional[str] = None
    ) -> Union[HuggingFaceProviderConfig, LitellmProviderConfig]:
        for repo in self._get_repos_by_provider(provider):
            try:
                return repo.get_model(model_name)
            except ModelNotFoundError:
                continue
        raise ModelNotFoundError(f"Model not found: {model_name}")

    def get_all_models_by_provider(
        self,
        provider: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Union[
        dict[str, List[Union[HuggingFaceProviderConfig, LitellmProviderConfig, OpenaiProviderConfig]]],
        List[Union[HuggingFaceProviderConfig, LitellmProviderConfig, OpenaiProviderConfig]]
    ]:
        results = {}
        for repo in self._get_repos_by_provider(provider):
            model_names = repo.list_models()
            paged_names = model_names[offset : offset + limit]
            results[repo.provider_name] = [
                repo.get_model(model_name) for model_name in paged_names
            ]

        # If a specific provider is requested, return just the list
        if provider:
            return next(iter(results.values()), [])
        return results



