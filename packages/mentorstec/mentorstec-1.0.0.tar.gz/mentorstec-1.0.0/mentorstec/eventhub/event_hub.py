# Funções globais para compatibilidade com EventHubClient
from typing import Any, Callable, Optional

from .event_hub_client import EventHubClient

# Instance global opcional
_global_client: Optional[EventHubClient] = None


def setup_global_hub(
    project: str, layer: str = "undefined", **kwargs: Any
) -> EventHubClient:
    """
    Configura instância global do EventHubClient para uso em funções standalone

    Args:
        project: Nome do projeto
        layer: Camada da aplicação (web, api, service, etc.)
        **kwargs: Argumentos adicionais passados para create_azure_client()

    Returns:
        EventHubClient: Instância configurada que também fica disponível globalmente

    Example:
        setup_global_hub("meu-projeto", "api", connection_string="...")
        send_event(event_type="INFO", message="Sistema iniciado")
    """
    global _global_client
    _global_client = EventHubClient.create_azure_client(project, layer, **kwargs)
    return _global_client


def send_event(event_type: str = "UNDEFINED", message: str = "", **kwargs: Any) -> None:
    """
    Envia evento usando instância global (requer setup_global_hub primeiro)

    Args:
        event_type: Tipo do evento
        message: Mensagem do evento
        **kwargs: Campos adicionais do evento

    Raises:
        ValueError: Se setup_global_hub() não foi chamado antes

    Example:
        setup_global_hub("meu-projeto")
        send_event(event_type="INFO", message="Sistema iniciado")
    """
    if not _global_client:
        raise ValueError("Configure global hub primeiro: setup_global_hub()")
    return _global_client.send_event(event_type, message, **kwargs)


def send_error(exception: Exception, context: str = "", **kwargs: Any) -> None:
    """
    Envia erro usando instância global (requer setup_global_hub primeiro)

    Args:
        exception: Exception capturada
        context: Contexto do erro
        **kwargs: Campos adicionais do evento

    Raises:
        ValueError: Se setup_global_hub() não foi chamado antes

    Example:
        setup_global_hub("meu-projeto")
        try:
            risky_operation()
        except Exception as e:
            send_error(e, context="risky_operation")
    """
    if not _global_client:
        raise ValueError("Configure global hub primeiro: setup_global_hub()")
    return _global_client.send_error(exception, context, **kwargs)


def capture_errors(context: str = "") -> Callable:
    """
    Decorator usando instância global (requer setup_global_hub primeiro)

    Args:
        context: Contexto do erro (default: module.function_name)

    Raises:
        ValueError: Se setup_global_hub() não foi chamado antes

    Example:
        setup_global_hub("meu-projeto")

        @capture_errors("important_function")
        def my_function():
            raise Exception("Something went wrong")
    """
    if not _global_client:
        raise ValueError("Configure global hub primeiro: setup_global_hub()")
    return _global_client.capture_errors(context)
