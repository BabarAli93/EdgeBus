from gymnasium.envs.registration import register

register(
    id='SimEdgeEnv-v1',
    entry_point='mobile_kube.envs:SimEdgeEnv',
    max_episode_steps=500,
)

register(
    id='SimBinpackingEnv-v0',
    entry_point='mobile_kube.envs:SimBinpackingEnv',
)

register(
    id='SimGreedyEnv-v0',
    entry_point='mobile_kube.envs:SimGreedyEnv',
)

register(
    id='SimMangoEnv-v1',
    entry_point='mobile_kube.envs:SimMangoEnv',
)

register(
    id='KubeEdgeEnv-v1',
    entry_point='mobile_kube.envs:KubeEdgeEnv',
)

register(
    id='KubeBinpackingEnv-v0',
    entry_point='mobile_kube.envs:KubeBinpackingEnv',
)

register(
    id='KubeGreedyEnv-v0',
    entry_point='mobile_kube.envs:KubeGreedyEnv',
)

register(
    id='KubeMangoEnv-v1',
    entry_point='mobile_kube.envs:KubeMangoEnv',
)
