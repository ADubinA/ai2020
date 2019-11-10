# ai2020
github for the ai2020 bgu course 

TODO  06/11/19:
1. ---DONE--- Add a travel time function that will be used by all agents.
2. ---SEMI DONE--- Add a score evaluation once all agents were terminated.
3. Break ties in a consistent way.
4. Add a slightly more robust graph.
5. Test the s*** out of it.

TODO 06/11/19
6. IMPORTANT: Ask if we need to solve destroyer/helpful agents interaction -> meaning that if a road the greedy agent was going to use is destroyed by the annihilator, the greedy agent should terminate.

7. IMPORTANT: Have the greedy save the whole path rather than re-calculate at every node.

TODO 09/11/19
1.  ---DONE--- Small graphical error - The agent arrives at a destination but the graph display doesn't reflect it.
2. PC agent currently doesn't pick people up. 
3. Go through all agents check if they are terminate. If they are, terminate the simulation early.
4. display score per agent

10/11/19 (Almog)
added graphic fixes and fixes for the greedy agent
TODO
1. If an agent is traversing to an annihilated node, it is annihilated.
2. If will traversing the source is annihilated, it is annihilated.
3. ---DONE--- reduce score to annihilated agent, by K (constant) + number of people carried.