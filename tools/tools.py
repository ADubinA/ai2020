def is_terminated(agents):
    if {agent.active_state for agent in agents} == {"terminated"}:
        return True
    else:
        return False