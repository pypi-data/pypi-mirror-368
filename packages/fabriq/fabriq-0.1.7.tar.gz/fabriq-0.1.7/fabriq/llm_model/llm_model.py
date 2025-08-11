from langchain_openai.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential
from langchain_aws.chat_models import ChatBedrockConverse
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_vertexai.chat_models import ChatVertexAI
from langchain_ollama.chat_models import ChatOllama
from langchain_huggingface.chat_models import ChatHuggingFace
from typing import Any, List
import base64
from io import BytesIO
import numpy as np
from PIL import Image
import requests
import os


class LLMModel:
    def __init__(self, config):
        """Initialize the LLM model based on the specified type."""
        self.config = config
        model_type = self.config.get("llm").get("type")
        self.model_name = self.config.get("llm").get("params").get("model_name", None)
        self.device = self.config.get("llm").get("params").get("device", "cpu")
        self.api_endpoint = (
            self.config.get("llm").get("params", {}).get("api_endpoint", None)
        )
        self.api_version = (
            self.config.get("llm").get("params", {}).get("api_version", None)
        )
        self.deployment_name = (
            self.config.get("llm").get("params", {}).get("deployment_name", None)
        )
        model_kwargs = self.config.get("llm").get("model_kwargs", {})

        self.system_prompt = (
            self.config.get("prompts")
            .get("params")
            .get("system_prompt", "You are a helpful AI assistant.")
        )

        if model_type == "openai":
            self.llm_model = ChatOpenAI(
                model=self.deployment_name, base_url=self.api_endpoint, **model_kwargs
            )

        elif model_type == "azure_openai":
            self.llm_model = AzureChatOpenAI(
                azure_deployment=self.deployment_name,
                azure_endpoint=self.api_endpoint,
                api_version=self.api_version,
                seed=42,
                **model_kwargs,
            )

        elif model_type == "azure_ai":
            self.llm_model = AzureAIChatCompletionsModel(
                model=self.deployment_name,
                endpoint=self.api_endpoint,
                credential=AzureKeyCredential(os.getenv("OPENAI_API_KEY")),
                seed=42,
                **model_kwargs,
            )

        elif model_type == "gemini":
            self.llm_model = ChatGoogleGenerativeAI(
                model=self.model_name, **model_kwargs
            )

        elif model_type == "vertex":
            self.llm_model = ChatVertexAI(model_name=self.model_name, **model_kwargs)

        elif model_type == "bedrock":
            self.llm_model = ChatBedrockConverse(
                name=self.model_name,
                region=model_kwargs.get("region", "us-east-1"),
                **model_kwargs,
            )

        elif model_type == "ollama":
            self.llm_model = ChatOllama(model=self.model_name, **model_kwargs)

        elif model_type == "huggingface":
            import torch
            from transformers import pipeline
            from langchain_huggingface.llms import HuggingFacePipeline

            hf_pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                device_map=self.device,
                torch_dtype=model_kwargs.get("torch_dtype", torch.float16),
                max_new_tokens=model_kwargs.get("max_tokens", 1024),
                temperature=model_kwargs.get("temperature", 0.1),
                top_p=model_kwargs.get("top_p", 0.9),
                top_k=model_kwargs.get("top_k", 50),
                **model_kwargs,
            )
            pipeline_ = HuggingFacePipeline(pipeline=hf_pipeline)
            self.llm_model = ChatHuggingFace(llm=pipeline_)

        elif model_type == "groq":
            self.llm_model = ChatGroq(
                model=self.model_name,
                temperature=model_kwargs.get("temperature", 0.1),
                max_tokens=model_kwargs.get("max_tokens", 1024),
                timeout=model_kwargs.get("timeout", 60),
                max_retries=model_kwargs.get("max_retries", 3),
            )
        else:
            raise ValueError(
                f"Unsupported LLM model type: {model_type}. Possible values are 'openai', 'azure_openai', 'azure_ai', 'bedrock', 'gemini', 'vertex', 'huggingface', 'groq'."
            )

    def get_llm_model(self):
        """Return the initialized LLM model."""
        return self.llm_model

    def create_base64_image(self, image: Any) -> str:
        """Convert any image type to base64 string."""

        if isinstance(image, str):
            if image.startswith("http://") or image.startswith("https://"):
                response = requests.get(image)
                image = BytesIO(response.content)
            elif image.startswith("data:image/"):
                image = BytesIO(base64.b64decode(image.split(",")[1]))
            else:
                image = Image.open(image)
        elif isinstance(image, bytes):
            image = Image.open(BytesIO(image))
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        else:
            raise ValueError(
                "Unsupported image type. Must be a file path, URL, bytes, NumPy array, or base64 string."
            )

        # Convert the image to base64
        buffered = BytesIO()
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    def generate(
        self,
        prompt: str,
        image: Any = None,
        system_prompt: str = None,
        stream: bool = False,
        **kwargs,
    ) -> str:
        """Generate text based on the provided prompt."""
        if system_prompt:
            system_message = SystemMessage(system_prompt)
        else:
            system_message = SystemMessage("You are a helpful AI assistant.")

        if image:
            base64_image = self.create_base64_image(image)
            image_url = f"data:image/png;base64,{base64_image}"

            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
            human_message = HumanMessage(content)
        else:
            human_message = HumanMessage(prompt)

        prompt = [system_message, human_message]

        if stream:
            return self.llm_model.stream(prompt, **kwargs)
        else:
            return self.llm_model.invoke(prompt, **kwargs).content.strip()

    async def generate_async(
        self,
        prompt: str,
        image: Any = None,
        system_prompt: str = None,
        stream: bool = False,
        **kwargs,
    ):
        """Asynchronously generate text based on the provided prompt."""
        if system_prompt:
            system_message = SystemMessage(system_prompt)
        else:
            system_message = SystemMessage("You are a helpful AI assistant.")

        if image:
            base64_image = self.create_base64_image(image)
            image_url = f"data:image/png;base64,{base64_image}"

            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
            human_message = HumanMessage(content)
        else:
            human_message = HumanMessage(prompt)

        prompt = [system_message, human_message]

        if stream:
            return await self.llm_model.astream(prompt, **kwargs)
        else:
            response = await self.llm_model.ainvoke(prompt, **kwargs)
            return response.content

    def generate_batch(
        self,
        prompts: List[str],
        images: List[Any] = None,
        system_prompt: str = None,
        stream: bool = False,
        **kwargs,
    ) -> str:
        """Generate text in batches based on the provided prompts."""
        if system_prompt:
            system_message = SystemMessage(system_prompt)
        else:
            system_message = SystemMessage("You are a helpful AI assistant.")

        prompts_batch = []
        for idx, prompt in enumerate(prompts):
            if images and idx < len(images) and images[idx] is not None:
                base64_image = self.create_base64_image(images[idx])
                image_url = f"data:image/png;base64,{base64_image}"
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
                human_message = HumanMessage(content)
            else:
                human_message = HumanMessage(prompt)
            prompts_batch.append([system_message, human_message])

        if stream:
            responses = self.llm_model.batch_as_completed(prompts_batch, **kwargs)
            return responses
        else:
            responses = self.llm_model.batch(prompts_batch, **kwargs)
            return [resp.content.strip() for resp in responses]
