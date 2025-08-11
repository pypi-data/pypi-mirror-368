from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_google_vertexai.embeddings import VertexAIEmbeddings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class EmbeddingModel:
    def __init__(self, config):
        """Initialize the embedding model based on the specified type."""
        self.config = config
        model_type = config.get("embeddings").get("type", "huggingface")
        model_name = (
            config.get("embeddings").get("params").get("model_name", "all-MiniLM-L6-v2")
        )
        deployment_name = config.get("embeddings").get("params").get("deployment_name")
        endpoint = config.get("embeddings").get("params").get("endpoint")
        kwargs = config.get("embeddings").get("params").get("kwargs", {})
        
        if model_type == "huggingface":
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=model_name, **kwargs
            )
        
        elif model_type == "openai":
            self.embedding_model = OpenAIEmbeddings(model=model_name, **kwargs)
        
        elif model_type == "azure_openai":
            self.embedding_model = AzureOpenAIEmbeddings(
                model=model_name,
                azure_endpoint=endpoint,
                azure_deployment=deployment_name,
                **kwargs,
            )
        
        elif model_type == "azure_ai":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self.embedding_model = AzureOpenAIEmbeddings(
                model_name=model_name,
                azure_endpoint=endpoint,
                azure_deployment=deployment_name,
                azure_ad_token_provider=token_provider,
                **kwargs,
            )
        
        elif model_type == "gemini":
            self.embedding_model = GoogleGenerativeAIEmbeddings(model=model_name)
        
        elif model_type == "vertex":
            self.embedding_model = VertexAIEmbeddings(
                model_name=model_name,
                project=kwargs.get("project_name", None),
                location=kwargs.get("region", "us-central1"),
                **kwargs
            )
        
        elif model_type == "bedrock":
            self.embedding_model = BedrockEmbeddings(
                model_id=model_name,
                model_kwargs=kwargs,
                credentials_profile_name=kwargs.get("credentials_profile_name", None),
                region_name=kwargs.get("region", "us-east-1"),
            )
        
        elif model_type == "ollama":
            self.embedding_model = OllamaEmbeddings(model=model_name)
        
        else:
            raise ValueError(f"Unsupported embedding model type: {model_type}")

    def get_embedding_model(self) -> Embeddings:
        """Return the initialized embedding model."""
        return self.embedding_model

    def embed_documents(self, documents) -> list:
        """Embed a list of documents."""
        return self.embedding_model.embed_documents(documents)

    def embed_query(self, query: str) -> list:
        """Embed a single query."""
        return self.embedding_model.embed_query(query)

    async def async_embed_documents(self, documents) -> list:
        """Asynchronously embed a list of documents."""
        return await self.embedding_model.aembed_documents(documents)

    async def async_embed_query(self, query: str) -> list:
        """Asynchronously embed a single query."""
        return await self.embedding_model.aembed_query(query)
