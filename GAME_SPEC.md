This is a 1-player game that lasts N turns.
The board is specified by a graph G(V,E).
The player has a movement budget B that resets each turn.
The board has point values at the nodes, which are drawn from a unif({1,2,3,4,5,6}).
The board has edge weights, which are drawn from a unif({1,2...,20}).
The above distributions should be taken as defualt distributions unless the user specifies otherwise in a config file. 
On the players turn they plot a path by picking adjacent nodes within the budget one at a time. 
The path takes them over edges and the sum of the edges' weights must not exceed the players budget B. 
The players path takes them over nodes as they stand on a node they collect the point value at that node (it combines to their total) and for the rest of that turn the point value at that node is zero.
When the player is finished the nodes and edge values are redrawn according to the specified distribution and the player gets another turn until the player reaches N-turns at which point the game ends and the user/player may evaluate their point total (aim is to try and maximize points).
For turn 1 the player may pick any node to start on. 
For the rest of the turns the player must start from where they ended the last turn.
The player may end up with no valid moves (budget constraints that force stationary) at which point the turn must end. 
The player may opt to end the turn early but that does not mean the budget gets rolled: the player will start with the same budget that had previously. 
The graph edges are NOT bi-directional: the graph should be strongly connected, contain no nodes that have out degree zero, and should contain no self loops/edges.
