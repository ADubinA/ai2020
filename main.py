import time
from environment import Environment

def main(save_dir, seconds_per_tick, max_tick=1000):

    env = Environment(save_dir)


    iteration = 0
    while iteration < max_tick:
        env.display()
        env.tick()
        time.sleep(seconds_per_tick)
        """if (env.active_agents < 1): ## meaning there are no more agents to run.
            break"""
        iteration += 1
    env.display()

if __name__ == "__main__":

    main("", 1)