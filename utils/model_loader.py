import os
import sys
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_groq import ChatGroq

from logger.logger_instance import logger as log
from utils.config_loader import load_config
from exception.custom_exception import DocumentQueryingPortalException


class ModelLoader:
    """
    Loads embeddings and LLM based on YAML config.
    AWS-ready: supports API_KEYS JSON, env vars, and .env (local only)
    """

    def __init__(self):
        # Load .env only in local/dev
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_keys = self.__load_api_keys()
        self.config = load_config()

        log.info(
            "ModelLoader initialized",
            config_keys=list(self.config.keys())
        )

    def __load_api_keys(self):
        """
        Load API keys from:
        1. AWS Secrets (API_KEYS JSON)
        2. Individual environment variables
        """
        api_keys = {}

        raw = os.getenv("API_KEYS")
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    api_keys.update(parsed)
                    log.info("Loaded API_KEYS from AWS secret")
                else:
                    log.warning("API_KEYS is not a valid JSON object")
            except Exception as e:
                log.warning(f"Failed to parse API_KEYS JSON: {e}")

        for key in ["OPENAI_API_KEY", "GROQ_API_KEY"]:
            if key not in api_keys:
                val = os.getenv(key)
                if val:
                    api_keys[key] = val
                    log.info(f"Loaded {key} from env")

        return api_keys

    def __get_api_key(self, key: str) -> str:
        """
        Lazy validation of required API key
        """
        val = self.api_keys.get(key)
        if not val:
            log.error(f"Missing API key: {key}")
            raise DocumentQueryingPortalException(
                f"Missing required API key: {key}",
                sys
            )
        return val

    def load_embeddings(self):
        """
        Load embeddings based on YAML config.
        """
        try:
            emb_config = self.config.get("embedding_model", {})
            model_name = emb_config.get("model_name")
            provider = emb_config.get("provider")

            if not model_name or not provider:
                raise ValueError("Embedding config missing model_name or provider")

            log.info(f"Loading embeddings: {provider} | {model_name}")

            if provider == "openai":
                return OpenAIEmbeddings(
                    model=model_name,
                    api_key=self.__get_api_key("OPENAI_API_KEY")
                )

            elif provider == "groq":
                raise ValueError("Groq embeddings not supported")

            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")

        except Exception as e:
            log.error(f"Embedding load failed: {e}")
            raise DocumentQueryingPortalException(e, sys)

    def load_llm(self):
        """
        Load LLM based on active provider in YAML config.
        """
        try:
            llm_block = self.config.get("llm", {})

            provider_key = self.config.get("active", {}).get("llm", "openai")

            if provider_key not in llm_block:
                raise ValueError(f"LLM provider '{provider_key}' not found")

            llm_config = llm_block[provider_key]

            provider = llm_config.get("provider")
            model_name = llm_config.get("model_name")
            temperature = llm_config.get("temperature", 0)
            max_tokens = llm_config.get("max_output_tokens", 1000)

            if not provider or not model_name:
                raise ValueError("LLM config missing provider or model_name")

            log.info(f"Loading LLM: {provider} | {model_name}")

            if provider == "openai":
                return ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=30,
                    api_key=self.__get_api_key("OPENAI_API_KEY")
                )

            elif provider == "groq":
                return ChatGroq(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.__get_api_key("GROQ_API_KEY")
                )

            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        except Exception as e:
            log.error(f"LLM load failed: {e}")
            raise DocumentQueryingPortalException(e, sys)

# if __name__ == "__main__":
#     loader = ModelLoader()

#     emb = loader.load_embeddings()
#     print("Embedding loaded")

#     vec = emb.embed_query("Hello world")
#     print(f"Vector size: {len(vec)}")

#     llm = loader.load_llm()
#     print("LLM loaded")

#     response = llm.invoke("What is the capital of France?")
#     print(response.content)