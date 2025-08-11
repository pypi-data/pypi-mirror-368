import argparse

from dependency_injection.container import DependencyContainer

from codius.domain.model.config.config import Config
from codius.domain.model.config.llm_provider import LlmProvider
from codius.domain.model.port.llm_port import LlmPort
from codius.domain.services.config_service import ConfigService
from codius.domain.services.session_service import SessionService
from codius.infrastructure.adapter.llm.ollama.ollama_llm_adapter import OllamaLlmAdapter

from codius.infrastructure.adapter.llm.openai.openai_llm_adapter import OpenAiLlmAdapter
from codius.infrastructure.repository.session_repository import SessionRepository
from codius.infrastructure.services.code_generator.code_generator_service import \
    CodeGeneratorService
from codius.infrastructure.services.code_scanner.code_scanner_service import CodeScannerService
from codius.infrastructure.services.graph_service import GraphService
from codius.infrastructure.services.llm_service import LlmService
from codius.infrastructure.services.logging_service import LoggingService
from codius.infrastructure.services.openddd_convention_service import OpenDddConventionService
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService
from codius.infrastructure.services.project_scanner_service import ProjectScannerService
from codius.infrastructure.services.tree_sitter_service import TreeSitterService


class ContainerProxy:
    def __getattr__(self, attr):
        container = DependencyContainer.get_instance()
        return getattr(container, attr)

    def __setattr__(self, attr, value):
        container = DependencyContainer.get_instance()
        setattr(container, attr, value)


container = ContainerProxy()


def register_services(config: Config, args: argparse.Namespace):

    container.register_instance(Config, config)
    container.register_transient(
        ProjectMetadataService,
        constructor_args={"project_path": args.path}
    )
    container.register_scoped(ConfigService)
    container.register_scoped(SessionRepository)
    container.register_singleton(LoggingService)
    container.register_scoped(SessionService)
    container.register_scoped(GraphService)
    container.register_scoped(ProjectScannerService)
    container.register_scoped(CodeScannerService)
    container.register_scoped(CodeGeneratorService)
    container.register_scoped(OpenDddConventionService)
    container.register_scoped(TreeSitterService)
    container.register_scoped(LlmService)

    adapter_by_provider = {
        LlmProvider.OPENAI: OpenAiLlmAdapter,
        LlmProvider.OLLAMA: OllamaLlmAdapter,
    }

    provider = config.llm.provider
    adapter_cls = adapter_by_provider.get(provider)

    if adapter_cls is None:
        raise RuntimeError(f"Unsupported LLM provider in config: {provider}")

    container.register_scoped(LlmPort, adapter_cls)
