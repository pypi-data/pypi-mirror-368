from __future__ import absolute_import
import logging
from sagemaker_training import entry_point, environment, runner

logger = logging.getLogger(__name__)


def train(training_env):
    logger.info("Invoking user training script.")

    entry_point.run(
        uri=training_env.module_dir,
        user_entry_point=training_env.user_entry_point,
        args=training_env.to_cmd_args(),
        env_vars=training_env.to_env_vars(),
        runner_type=runner.ProcessRunnerType,
    )


def main():
    training_env = environment.Environment()
    train(training_env)
