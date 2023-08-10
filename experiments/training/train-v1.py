import os
import sys
import shutil
import click
from typing import Dict, Any
import json

import torch
import ray
from ray import tune
from ray.rllib.utils.framework import try_import_torch
import pprint
from ray.rllib.algorithms.impala import ImpalaConfig
from ray.rllib.algorithms.ddpg.ddpg import DDPGConfig
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.pg import PGConfig
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.a2c import A2CConfig
from ray.rllib.algorithms.a3c import A3CConfig
from ray import air
from ray.air import CheckpointConfig, RunConfig

# get an absolute path to the directory that contains parent files
project_dir = os.path.dirname(os.path.join(os.getcwd(), __file__))
sys.path.append(os.path.normpath(os.path.join(project_dir, '..', '..')))

from experiments.utils.constants import (
    TRAIN_RESULTS_PATH,
    CONFIGS_PATH,
    ENVSMAP
)
from experiments.utils import (
    add_path_to_config_edge,
    make_env_class,
    CloudCallback
)

torch, nn = try_import_torch()


def impala_func(env_class, env_config, callback):
    config = ImpalaConfig()
    print(config.vtrace)

    config = (
        config
        .environment(env=env_class, env_config=env_config)
        .training(lr=tune.grid_search([0.0003]),
                  model={"fcnet_hiddens": [64, 64], "fcnet_activation": "linear", "vf_share_layers": "true"},
                  train_batch_size=1000)
        .resources(num_gpus=0)
        .rollouts(num_rollout_workers=3)
        .callbacks(callback)
    )
    config.gamma = 0.99
    config.environment(env_config=env_config)
    config.vf_loss_coeff = 0.01
    config.seed = 203

    return config.to_dict()


def ppo_func(env_class, env_config, callback):
    config = PPOConfig()
    config = (
        config.environment(env_class, env_config=env_config)
        .training(lr=0.0003,
                  model={"fcnet_hiddens": [64, 64], "fcnet_activation": "linear", "vf_share_layers": "true"},
                  train_batch_size=1000, sgd_minibatch_size=128,
                  num_sgd_iter=1)
        .resources(num_gpus=0)
        .rollouts(num_rollout_workers=4)
        .callbacks(callback)
    )
    config.gamma = 0.99
    config.vf_loss_coeff = 0.01
    config.seed = 203
    config.observation_filter = "MeanStdFilter"
    return config.to_dict()


def pg_func(env_class, env_config, callback):
    config = PGConfig()
    config = (
        config
        .environment(env_class, env_config=env_config)
        .training(lr=0.0003,
                  train_batch_size=1000,
                  model={"fcnet_hiddens": [64, 64], "fcnet_activation": "linear"}
                  )
        .resources(num_gpus=0)
        .rollouts(num_rollout_workers=1)
        .callbacks(callback)
    )
    config.gamma = 0.99
    config.observation_filter = "NoFilter"
    config.seed = 203

    return config.to_dict()


def a2c_func(env_class, env_config, callback):
    config = A2CConfig()
    config = (
        config
        .environment(env_class, env_config=env_config)
        .training(
            lr=0.0003,
            train_batch_size=200,
            model={"fcnet_hiddens": [64, 64], "fcnet_activation": "linear", "vf_share_layers": "true"}
        )
        .resources(num_gpus=0)
        .rollouts(rollout_fragment_length='auto', num_rollout_workers=20)
        .callbacks(callback)
    )
    config.gamma = 0.99
    config.observation_filter = "MeanStdFilter"
    config.vf_loss_coeff = 0.01
    config.seed = 203

    return config.to_dict()


def a3c_func(env_class, env_config, callback):
    config = A3CConfig()
    config = (
        config
        .environment(env_class, env_config=env_config)
        .training(
            lr=0.0003,
            train_batch_size=200,
            model={"fcnet_hiddens": [64, 64], "fcnet_activation": "linear", "vf_share_layers": "true"}
        )
        .resources(num_gpus=0)
        .rollouts(rollout_fragment_length='auto', num_rollout_workers=13) # set it to auto because of error
        .callbacks(callback)
    )
    config.gamma = 0.99
    config.vf_loss_coeff = 0.01
    config.seed = 203

    return config.to_dict()


def learner(*, config_file_path: str, config: Dict[str, Any],
            series: int, type_env: str, dataset_id: int,
            workload_id: int, network_id: int, trace_id: int,
            use_callback: bool, checkpoint_freq: int,
            local_mode: bool):
    stop = config['stop']
    # learn_config = config['learn_config']
    run_or_experiment = config["run_or_experiment"]
    env_config_base = config['env_config_base']

    env_config = add_path_to_config_edge(
        config=env_config_base,
        dataset_id=dataset_id,
        workload_id=workload_id,
        network_id=network_id,
        trace_id=trace_id
    )

    # generate the ray_config
    # make the learning config based on the type of the environment
    if type_env not in ['CartPole-v0', 'Pendulum-v0', 'CartPole-v1']:
        ray_config = {"env": make_env_class(type_env),
                      "env_config": env_config}
    else:
        ray_config = {"env": type_env}

    experiments_folder = os.path.join(TRAIN_RESULTS_PATH,
                                      "series", str(series),
                                      "envs", str(type_env),
                                      "datasets", str(dataset_id),
                                      "workloads", str(workload_id),
                                      "networks", str(network_id),
                                      "traces", str(trace_id),
                                      "experiments")
    # make the base path if it does not exists
    if not os.path.isdir(experiments_folder):
        os.makedirs(experiments_folder)
    # generate new experiment folder
    content = os.listdir(experiments_folder)
    new_experiment = len(content)
    this_experiment_folder = os.path.join(experiments_folder,
                                          str(new_experiment))
    # make the new experiment folder
    os.mkdir(this_experiment_folder)

    # copy our input json to the path a change
    # the name to a unified name
    shutil.copy(config_file_path, this_experiment_folder)
    source_file = os.path.join(this_experiment_folder,
                               os.path.split(config_file_path)[-1])
    dest_file = os.path.join(this_experiment_folder, 'experiment_config.json')
    os.rename(source_file, dest_file)

    if run_or_experiment == 'PPO':
        learn_config = ppo_func(ray_config['env'], env_config_base, CloudCallback)
    elif run_or_experiment == 'IMPALA':
        learn_config = impala_func(ray_config['env'], env_config_base, CloudCallback)
    elif run_or_experiment == 'PG':
        learn_config = pg_func(ray_config['env'], env_config_base, CloudCallback)
    elif run_or_experiment == 'A2C':
        learn_config = a2c_func(ray_config['env'], env_config_base, CloudCallback)
    elif run_or_experiment == 'A3C':
        learn_config = a3c_func(ray_config['env'], env_config_base, CloudCallback)

    ray.init(local_mode=local_mode)
    tuner = tune.Tuner(
        run_or_experiment,
        run_config=RunConfig(stop=stop,
                             local_dir=this_experiment_folder,
                             checkpoint_config=CheckpointConfig(
                                 num_to_keep=5,
                                 checkpoint_frequency=1000,
                                 checkpoint_at_end=True,
                             )
                             ),
        param_space=learn_config,
    ).fit()

    # delete the unnecessary big json file
    # TODO maybe of use in the analysis
    this_experiment_trials_folder = os.path.join(
        this_experiment_folder, run_or_experiment)
    this_experiment_trials_folder_contents = os.listdir(
        this_experiment_trials_folder)
    for item in this_experiment_trials_folder_contents:
        if 'json' in item:
            json_file_name = item
            break
    json_file_path = os.path.join(
        this_experiment_trials_folder,
        json_file_name)
    os.remove(json_file_path)


@click.command()
@click.option('--local-mode', type=bool, default=False)
@click.option('--config-file', type=str, default='final-DQN')
@click.option('--series', required=True, type=int, default=70)
# @click.option('--type-env', required=True,
#              type=click.Choice(['sim-edge', 'sim-binpacking', 'sim-edge-greedy',
#                                 'CartPole-v0', 'Pendulum-v0']),
#              default='sim-edge')
@click.option('--type-env', required=True,
              type=click.Choice(['sim-edge', 'sim-binpacking', 'sim-greedy',
                                 'sim-mango', 'CartPole-v0', 'Pendulum-v0', 'CartPole-v1']),
              default='sim-edge')
@click.option('--dataset-id', required=True, type=int, default=6)
@click.option('--workload-id', required=True, type=int, default=0)
@click.option('--network-id', required=False, type=int, default=0)
@click.option('--trace-id', required=False, type=int, default=0)
@click.option('--use-callback', required=True, type=bool, default=True)
@click.option('--checkpoint-freq', required=False, type=int, default=1000)
def main(local_mode: bool, config_file: str, series: int,
         type_env: str, dataset_id: int, workload_id: int, network_id: int,
         trace_id: int, use_callback: bool, checkpoint_freq: int):
    config_file_path = os.path.join(
        CONFIGS_PATH, 'train', f"{config_file}.json")
    with open(config_file_path) as cf:
        config = json.loads(cf.read())

    pp = pprint.PrettyPrinter(indent=4)
    print('start experiments with the following config:\n')
    pp.pprint(config)

    learner(config_file_path=config_file_path,
            config=config, series=series,
            type_env=type_env, dataset_id=dataset_id,
            workload_id=workload_id, network_id=network_id,
            trace_id=trace_id, use_callback=use_callback,
            checkpoint_freq=checkpoint_freq, local_mode=local_mode)


if __name__ == "__main__":
    main()
