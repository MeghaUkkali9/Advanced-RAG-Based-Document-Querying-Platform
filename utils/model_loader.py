import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_groq import ChatGroq

from logger.logger_instance import logger as log
from utils.config_loader import load_config
from exception.custom_exception import DocumentQueryingPortalException

class ModelLoader:
    """
    Loads embeddings and LLM based on YAML config.
    """
    def __init__(self):
        load_dotenv()
        self.__validate_env()
        self.config = load_config()

        log.info(
            "ModelLoader initialized",
            config_keys=list(self.config.keys())
        )

    def load_embeddings(self):
        """
        Load embeddings based on YAML config.
        """
        try:
            emb_config = self.config["embedding_model"]
            model_name = emb_config["model_name"]
            provider = emb_config["provider"]

            log.info(f"Loading embeddings: {provider} | {model_name}")

            if provider == "openai":
                return OpenAIEmbeddings(
                    model=model_name,
                    api_key=self.api_keys["OPENAI_API_KEY"]
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
            llm_block = self.config["llm"]

            # use YAML active config
            provider_key = self.config.get("active", {}).get("llm", "openai")

            if provider_key not in llm_block:
                raise ValueError(f"LLM provider '{provider_key}' not found")

            llm_config = llm_block[provider_key]
            provider = llm_config["provider"]
            model_name = llm_config["model_name"]
            temperature = llm_config.get("temperature", 0)

            # YAML uses max_output_tokens
            max_tokens = llm_config.get("max_output_tokens", 1000)

            log.info(f"Loading LLM: {provider} | {model_name}")

            if provider == "openai":
                return ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.api_keys["OPENAI_API_KEY"]
                )

            elif provider == "groq":
                return ChatGroq(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.api_keys["GROQ_API_KEY"]
                )

            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        except Exception as e:
            log.error(f"LLM load failed: {e}")
            raise DocumentQueryingPortalException(e, sys)
        
    def __validate_env(self):
        """
        Validate required environment variables for API keys.
        """
        required_env_vars = ["OPENAI_API_KEY", "GROQ_API_KEY"]

        self.api_keys = {key: os.getenv(key) for key in required_env_vars}

        missing_vars = [k for k, v in self.api_keys.items() if not v]

        if missing_vars:
            log.error(f"Missing env vars: {missing_vars}")
            raise DocumentQueryingPortalException(
                f"Missing required env vars: {missing_vars}",
                sys
            )

        log.info("Environment variables validated")


# if __name__ == "__main__":
#     loader = ModelLoader()

#     # Embeddings test
#     emb = loader.load_embeddings()
#     print("Embedding loaded")

#     vec = emb.embed_query("Hello world")
#     print(f"Vector size: {len(vec)}")

#     # LLM test
#     llm = loader.load_llm()
#     print("LLM loaded")

#     response = llm.invoke("What is the capital of France?")
#     print(response.content)