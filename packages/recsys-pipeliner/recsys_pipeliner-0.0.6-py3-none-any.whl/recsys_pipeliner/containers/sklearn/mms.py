from subprocess import CalledProcessError
from retrying import retry
from sagemaker_inference import model_server, environment
import logging
from recsys_pipeliner.containers.sklearn import handler_service


logging.basicConfig(level=logging.INFO)


HANDLER_SERVICE = handler_service.__name__ + ":handle"

logging.info(f"HANDLER_SERVICE: {HANDLER_SERVICE}")


def _retry_if_error(exception):
    logging.info("_## retry_if_error ##")
    logging.exception(exception)
    return isinstance(exception, CalledProcessError or OSError)


@retry(stop_max_delay=1000 * 50, retry_on_exception=_retry_if_error)
def start_server():
    logging.info("Starting model server")
    serving_env = environment.Environment()
    logging.info(f"module_name: {serving_env.module_name}")
    model_server.start_model_server(handler_service=HANDLER_SERVICE)
