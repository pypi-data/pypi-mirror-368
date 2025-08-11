import logging
from recsys_pipeliner.containers.sklearn.handlers import HandlerService

logging.basicConfig(level=logging.INFO)

_service = HandlerService()


def ping():
    return "healthy"


def handle(data, context):
    logging.info(f"handle called, system_properties: {context.system_properties}")

    if not _service.initialized:
        _service.initialize(context)

    return _service.handle(data, context)
