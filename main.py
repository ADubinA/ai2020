import time
from environment import Environment

def main(save_dir, seconds_per_tick, max_tick=1000):

    env = Environment(save_dir)
    env.add_vertex()
    env.add_vertex()
    env.add_vertex()
    env.add_vertex()
    env.add_vertex()
    env.add_vertex()
    env.add_edge(1, 2)
    env.add_edge(1, 3)
    env.add_edge(1, 4)
    env.add_edge(2, 3)
    env.add_edge(2, 5)


    iteration = 0
    while iteration < max_tick:
        env.display()

        env.tick()
        time.sleep(seconds_per_tick)

        iteration += 1

    env.display()

if __name__ == "__main__":

    main("", 1)