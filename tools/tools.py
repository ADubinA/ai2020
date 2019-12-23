def is_terminated(agents):
    if {agent.active_state for agent in agents} == {"terminated"}:
        return True
    else:
        return False

def clear_data(agent):
    """
    will remove deep copy clones
    """

    # start the heap and set the graph with a root of root
    heap = [agent]

    # loop until the heap is empty
    while len(heap) != 0:
        parent = heap.pop()

        # for every agent check if it's not a leaf add children to heap
        for child in parent.current_options:
            if not child.is_cutoff:
                heap.append(child)
                del child

        if parent != agent:
            del parent
