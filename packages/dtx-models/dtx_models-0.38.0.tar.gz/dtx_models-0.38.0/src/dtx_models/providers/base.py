from enum import Enum
import os
from typing import Dict
from pydantic import BaseModel


class ProviderType(str, Enum):
    ECHO = "echo"
    ELIZA = "eliza"
    HF = "huggingface"
    HTTP = "http"
    GRADIO = "gradio"
    OLLAMA = "ollama"
    OPENAI = "openai"
    GROQ = "groq"
    LITE_LLM = "litellm"
    ANTHROPIC = "anthropic"
    AZURE_AI = "azure_ai"
    MISTRAL = "mistral"
    COHERE = "cohere"
    SAGEMAKER = "sagemaker"
    BEDROCK_CLAUDE = "bedrock_claude"
    META_LLAMA = "meta_llama"
    DEEPSEEK = "deepseek"
    XAI = "xai"
    FIREWORKS = "fireworks"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"
    ANYSCALE = "anyscale"
    REPLICATE = "replicate"
    IBM_WATSONX = "ibm_watsonx"
    DATABRICKS = "databricks"
    AI21 = "ai21"
    CLARIFAI = "clarifai"
    CLOUDFLARE_WORKERS = "cloudflare_workers"
    LMSTUDIO = "lmstudio"
    VLLM = "vllm"
    PETALS = "petals"
    DEEPGRAM = "deepgram"
    ELEVENLABS = "elevenlabs"
    TOPAZ = "topaz"
    VOYAGEAI = "voyageai"
    AZURE = "azure"
    GOOGLE_VERTEX_AI = "google_vertex_ai"
    NEBIUS_AI_STUDIO = "nebius_ai_studio"
    SNOWFLAKE = "snowflake"
    INFINITY = "infinity"
    FEATHERLESS_AI = "featherless_ai"
    TORCHSERVE = "torchserve"
    TRITON = "triton"
    ALEPH_ALPHA = "aleph_alpha"
    BASETEN = "baseten"
    NOVITA_AI = "novita_ai"
    GALADRIEL = "galadriel"
    SAMBANOVA = "sambanova"
    NSCALE = "nscale"
    JINA_AI = "jina_ai"
    CEREBRAS = "cerebras"
    GOOGLE_AISTUDIO = "google_aistudio"
    PREDIBASE = "predibase"
    NVIDIA_NIM = "nvidia_nim"
    MOONSHOTAI = "moonshotai"
    VOLCENGINE = "volcengine"
    GEMINI = "gemini"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]



class BaseProviderConfigWithEnvLoader(BaseModel):
    """
    Base class for provider configs that support loading values from environment variables.
    Supports flat and nested field assignment.
    """

    # Mapping: ENV_VAR -> "field" or "nested.field"
    env_vars: Dict[str, str] = {}


    def load_from_env(self):
        """Populate config fields from mapped environment variables."""
        for env_var, attr_name in self.env_vars.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                setattr(self, attr_name, env_value)



