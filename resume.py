from stable_baselines.a2c.utils import conv, linear, conv_to_fc
import sys
import tensorflow as tf
import numpy as np
from stable_baselines.common.policies import FeedForwardPolicy, MlpPolicy, MlpLstmPolicy, MlpLnLstmPolicy, CnnPolicy, CnnLstmPolicy, CnnLnLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from stable_baselines.common.callbacks import CheckpointCallback
from CustomEvalCallback import CustomEvalCallback
from stable_baselines.common import set_global_seeds
from stable_baselines import ACKTR, PPO2
from env.field_env import FieldEnv

def make_env(env_class, rank, seed=0):
    """
    Utility function for multiprocessed env.
    
    :param env_id: (str) the environment ID
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = env_class()
        # Important: use a different seed for each environment
        env.seed(seed + rank)
        return env
    set_global_seeds(seed)
    return _init

def run():
    print("Setting up env")


    n_procs = 8
    env = SubprocVecEnv([make_env(FieldEnv, i) for i in range(n_procs)], start_method='spawn')

    if (str(sys.argv[2]) == "n"):
        env = VecNormalize.load("bests/best_model_env", env)
        #env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=10.)
    elif (str(sys.argv[2]) == "nr"):
        env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.)


    print("Setting up model")
    print("Policy = " + str(sys.argv[1]))

    #model = PPO2(sys.argv[1], env, verbose=1, tensorboard_log="./tensey/")
    model = PPO2.load("bests/best_model.zip", env=env, verbose=1, tensorboard_log="./tensey/"))
    num_steps = int(1e7)
    print("Making callbacks");
    eval_env = DummyVecEnv([make_env(FieldEnv, i) for i in range(n_procs)])
    if (str(sys.argv[2]) == "n"):
        eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False, clip_obs=10.)
    cb = [CheckpointCallback(save_freq=num_steps//(100*n_procs), save_path="./cps/", name_prefix=("fe-" + str(num_steps) + "-ppo2-" + str(sys.argv[1]) + "-" + str(sys.argv[2]))), CustomEvalCallback(eval_env, best_model_save_path="./bests/", log_path="./logs/", eval_freq=num_steps//(100*n_procs), deterministic=True, render=False, verbose=1)]
    print("About to start");
    model.learn(num_steps, callback=cb, reset_num_timesteps=False)



    # Save the agent
    model.save("field-env-" + str(num_steps) + "-ppo2-" + str(sys.argv[1]) + "-" + str(sys.argv[2]))

if __name__ == '__main__':
    run()

