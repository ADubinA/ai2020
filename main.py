import time
from environment import Environment

def main(save_dir, seconds_per_tick, max_tick=1000):

    env = Environment(save_dir)
    iteration = 0
    while iteration < max_tick:
        env.display()
        if env.is_terminated():
            break

        env.tick()
        time.sleep(seconds_per_tick)
        iteration += 1
    env.display()


if __name__ == "__main__":
    main("test/loops.json", 0.05)
