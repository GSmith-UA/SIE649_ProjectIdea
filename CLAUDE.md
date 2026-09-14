This repo is meant to contain 3 modules: game logic/play, a very simply gui demo/prototype for users to get a feel for the game, and finally optimization/analysis of the game. 
Only focus on the first two modules. 
Do not write optimization solvers, do performance analysis of strategies, or implement the stochastic program formally.
If asked to do analysis of the stochastic program/game stop and ask first.

Implement in python 3 using standard libraries.
For the GUI I want a simple implementation (perhaps tkinter or possibly a matplotlib board).

The game logic (state, moves, budget, RNG draws, etc) need to be separate from the GUI as I want to be able to test/simulate/run analysis without spinning up displays.  

A finished module 1 and 2 would allow me to play the game according to the rules in GAME_SPEC.md. I.e. a runnable demo where I can click/select a neighboring node, see budget decrement, see points accrue and see the turn counter advance for a graph of say 20 nodes. 

Use pytest for unit tests on the logic module: some test ideas might be positivity of the budget, the turn counter terminates at N turns, moves only succeed along valid edges, edge/point draws fall within the Random Variables support, graph/board is path connected.
Write tests alongside the logic module (not after the fact) and use git to commit to the a local repo once a significant milestone has been reached and succesfully tested. 

The game should have a setup file (.sh or .txt .md) that allows the user to specify: the turn number N, the budget parameter B, the distribution for the edge weights, the distribution for the point values at the nodes, the structure of the graph (matrix representation).
