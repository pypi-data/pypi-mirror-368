from concurrent.futures import ThreadPoolExecutor
from typing import List

from loguru import logger

from llmflow.config.config_parser import ConfigParser
from llmflow.embedding_model import EMBEDDING_MODEL_REGISTRY
from llmflow.pipeline.pipeline import Pipeline
from llmflow.pipeline.pipeline_context import PipelineContext
from llmflow.schema.app_config import AppConfig, HttpServiceConfig, EmbeddingModelConfig
from llmflow.schema.request import SummarizerRequest, RetrieverRequest, VectorStoreRequest, AgentRequest, \
    BaseRequest
from llmflow.schema.response import SummarizerResponse, RetrieverResponse, VectorStoreResponse, AgentResponse, \
    BaseResponse
from llmflow.vector_store import VECTOR_STORE_REGISTRY


class LLMFlowService:

    def __init__(self, args: List[str]):
        self.config_parser = ConfigParser(args)
        self.init_app_config: AppConfig = self.config_parser.get_app_config()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.init_app_config.thread_pool.max_workers)

        # The vectorstore is initialized at the very beginning and then used directly afterward.
        self.vector_store_dict: dict = {}
        for name, config in self.init_app_config.vector_store.items():
            assert config.backend in VECTOR_STORE_REGISTRY, f"backend={config.backend} is not existed"
            vector_store_cls = VECTOR_STORE_REGISTRY[config.backend]

            assert config.embedding_model in self.init_app_config.embedding_model, \
                f"embedding_model={config.embedding_model} is not existed"
            embedding_model_config: EmbeddingModelConfig = self.init_app_config.embedding_model[config.embedding_model]

            assert embedding_model_config.backend in EMBEDDING_MODEL_REGISTRY, \
                f"embedding_model={embedding_model_config.backend} is not existed"
            embedding_model_cls = EMBEDDING_MODEL_REGISTRY[embedding_model_config.backend]
            embedding_model = embedding_model_cls(model_name=embedding_model_config.model_name,
                                                  **embedding_model_config.params)

            self.vector_store_dict[name] = vector_store_cls(embedding_model=embedding_model, **config.params)

    @property
    def http_service_config(self) -> HttpServiceConfig:
        return self.init_app_config.http_service

    def __call__(self, api: str, request: dict | BaseRequest) -> BaseResponse:
        if isinstance(request, dict):
            app_config: AppConfig = self.config_parser.get_app_config(**request["config"])
        else:
            app_config: AppConfig = self.config_parser.get_app_config(**request.config)

        if api == "retriever":
            if isinstance(request, dict):
                request = RetrieverRequest(**request)
            response = RetrieverResponse()
            pipeline = app_config.api.retriever

        elif api == "summarizer":
            if isinstance(request, dict):
                request = SummarizerRequest(**request)
            response = SummarizerResponse()
            pipeline = app_config.api.summarizer

        elif api == "vector_store":
            if isinstance(request, dict):
                request = VectorStoreRequest(**request)
            response = VectorStoreResponse()
            pipeline = app_config.api.vector_store

        elif api == "agent":
            if isinstance(request, dict):
                request = AgentRequest(**request)
            response = AgentResponse()
            pipeline = app_config.api.agent

        else:
            raise RuntimeError(f"Invalid service.api={api}")

        logger.info(f"request={request.model_dump_json()}")

        try:
            context = PipelineContext(app_config=app_config,
                                      thread_pool=self.thread_pool,
                                      request=request,
                                      response=response,
                                      vector_store_dict=self.vector_store_dict)
            pipeline = Pipeline(pipeline=pipeline, context=context)
            pipeline()

        except Exception as e:
            logger.exception(f"api={api} encounter error={e.args}")
            response.success = False
            response.metadata["error"] = str(e)

        return response
