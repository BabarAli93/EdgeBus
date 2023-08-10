"""base class for non learning heterogeneous environments
"""
import numpy as np
from copy import deepcopy
from typing import (
    Dict,
    Any,
    Tuple
)

from gymnasium.spaces import (
    Box,
    MultiDiscrete
)

from mobile_kube.util import (
    Preprocessor,
    override,
    load_object
)
from mobile_kube.network import NetworkSimulator

from .sim_edge_env import SimEdgeEnv


class SimMangoEnv(SimEdgeEnv):

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, int, bool, dict]:
        """ Move container based on Migration cost, Edge server power and
        the amount of resources
        """

        prev_services_nodes = deepcopy(self.services_nodes)
        action, hetero_reward = self._next_mango_action(prev_services_nodes)
        assert self.action_space.contains(action)
        self.services_nodes = deepcopy(action)

        # move to the next timestep
        self.global_timestep += 1
        self.timestep = self.global_timestep % self.workload.shape[1]

        # make user movements --> network parts
        self.users_stations = self.edge_simulator.sample_users_stations(
            timestep=self.timestep)
        users_distances = self.edge_simulator.users_distances
        # update network with the new placements
        self.edge_simulator.update_services_nodes(self.services_nodes)

        num_moves = len(np.where(
            self.services_nodes != prev_services_nodes)[0])
        self.total_num_moves += num_moves
        #print(f"TimeStep {self.timestep} has Moves: {num_moves}")
        #print(f"Total Moves: {self.total_num_moves}")

        reward, rewards = self._reward(
            num_overloaded=self.num_overloaded,
            users_distances=users_distances,
            num_moves=num_moves,
            num_overused=self.num_overusage,
            hetero_reward=hetero_reward
        )

        info = {'num_consolidated': self.num_consolidated,
                'num_moves': num_moves,
                'num_overused': self.num_overusage,
                'num_overloaded': self.num_overloaded,
                'users_distances': np.sum(users_distances),
                'total_reward': reward,
                'timestep': self.timestep,
                'global_timestep': self.global_timestep,
                'rewards': rewards}

        assert self.observation_space.contains(self.observation), \
            (f"observation:\n<{self.raw_observation}>\noutside of "
             f"observation_space:\n <{self.observation_space}>")

        return self.observation, reward, self.done, False, info

    def _next_mango_action(self, prev_services_nodes) -> np.ndarray:
        """
        I can either write my function here like SimBinpacking or call network base greedy
        funtion like SimGreedy
            """
        action, hetero_reward = self.edge_simulator._next_action_mango(
            nodes_mem_cap=self.nodes_resources_cap[:, 0],
            services_mem_request=self.services_resources_request[:, 0],
            nodes_cpu_cap=self.nodes_resources_cap[:, 1],
            services_cpu_request=self.services_resources_request[:, 1],
        )

        return action, hetero_reward
