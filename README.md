# Overview

This is an implementation of the snowball consensus algorithm.

I first decide to explore Slush and Snowflake algorithm.


## Slush, non-BFT protocol 

**Pseudocode**
```
1:  procedure onQuery(v, col')
2:    if col = ⊥ then col := col'
3:    respond(v, col)
4:  procedure slushLoop(u, col0 ∈ {R, B, ⊥})
5:    col := col0 // initialize with a color
6:    for r ∈ {1 . . . m} do
7:      // if ⊥, skip until onQuery sets the color
8:      if col = ⊥ then continue
9:      // randomly sample from the known nodes
10:     K := sample(N \u, k)
11:     P := [query(v, col) for v ∈ K]
12:     for col' ∈ {R, B} do
13:       if P.count(col') ≥ α · k then
14:         col := col'
15:   accept(col)
```

The Slush algorithm is a consensus protocol designed to achieve agreement across a distributed system. It's probabilistic and operates under the assumption of a partially synchronous network. Here's a summary of its operation based on the provided pseudocode:

1. Initialization: Each node in the network starts with an initial state (color), which can be red ('R'), blue ('B'), or undecided ('⊥').

2. Query Handling (onQuery): When a node receives a query (onQuery) with a color from another node, it adopts this color if it is currently undecided ('⊥'). Then it responds with its current color.

3. Main Loop (slushLoop): The main function slushLoop runs for a predefined number of rounds 'm'. In each round, if a node's color is undecided, it skips processing until it receives a color via onQuery.

4. Sampling and Decision: If the node has a decided color, it randomly samples 'k' other nodes and queries their colors. It then counts the occurrences of each color in the responses.

5. State Update: If a significant majority of sampled nodes (determined by a threshold 'α') have a color different from its own, the node updates its color to the majority color.

6. Convergence and Acceptance: The process repeats for 'm' rounds or until the system converges to a state where nodes no longer change their color. Finally, each node accepts its current color as the consensus.

NB : As you can see in my implementation, instead of waiting for m rounds I just decided that the algorithm stop when all nodes have the same color

## Snowflake


```
1: procedure snowflakeLoop(u, col0 ∈ {R,B,⊥})
2:      col := col0, cnt := 0
3:      while undecided do
4:          if col = ⊥ then continue
5:          K := sample(N \u, k)
6:          P := [query(v, col) for v ∈ K ]
7:          maj := false
8:          for col' ∈ {R,B} do
9:              if P.count(col') ≥ α then
10:                 maj := true
11:                 if col' != col then
12:                     col := col', cnt := 1
13:                 else cnt++
14:                 if cnt ≥ β then accept(col')
15:         if maj = false then cnt := 0
```


## Snowball, BFT


```
1:  procedure snowballLoop(u, col0 ∈ {R, B, ⊥})
2:    col := col0, lastcol := col0, cnt := 0
3:    d[R] := 0, d[B] := 0
4:    while undecided do
5:      if col = ⊥ then continue
6:      K := sample(N \u, k)
7:      P := [query(v, col) for v ∈ K]
8:      for col' ∈ {R, B} do
9:        if P.count(col') ≥ α · k then
10:         d[col']++
11:         if d[col'] > d[col] then
12:           col := col'
13:           if col' != lastcol then
14:             lastcol := col', cnt := 0
15:           else
16:             if ++cnt > β then accept(col)
```

### __Major differences in my implementation with Slush__


**Node Class:**

Counter Variable: In the Snowflake algorithm, the counter tracks the number of consecutive rounds a node sees the same majority color. This is a crucial element in determining when a node should accept a color.
Accepted Flag: The accepted boolean flag indicates whether a node has finalized its state (color) based on the Snowflake algorithm's criteria. Once a node has accepted a color, it no longer changes its state.


**SnowflakeAlgorithm Class:**

Beta Parameter: The beta parameter is specific to the Snowflake algorithm and represents the number of consecutive rounds a color must be seen as a majority before a node can accept it. This parameter is central to ensuring that the consensus is stable and not easily swayed by transient changes or Byzantine behaviors.
Run Method:
The run method in the Snowflake algorithm includes logic to check if consensus has been reached. This is done by checking the accepted flag of each node and ensuring that all nodes agree on the same color.
The method of determining consensus (checking all nodes have accepted the same color) is specific to Snowflake and is not present in the Slush implementation.

**Global Variable (consensus_reached):**

In my implementation, the consensus_reached variable is used as a flag to indicate whether the algorithm should stop running. This is a design choice to manage the termination condition of the algorithm's loop.

**Overall Algorithm Logic:**

The fundamental difference between Slush and Snowflake lies in the convergence criteria. While Slush may converge when a majority color is simply observed, Snowflake requires this majority to be consistent over several consecutive rounds, as dictated by the beta parameter.

NB : In the context of Byzantine fault tolerance, particularly for protocols like Snowflake (and more broadly in the Avalanche family of consensus algorithms), the goal is typically to achieve consensus despite some fraction of nodes being Byzantine. This fraction is often bounded by ⌊N-1/3⌋Byzantine nodes in a network of N nodes, meaning that the system should still reach consensus as long as no more than a third of the nodes are Byzantine. This is why my run SnowFlake function looks like this :

```py
    def run(self):
        rounds_taken = 0

        while not self.consensus_reached:
            rounds_taken += 1
            self.run_snowflake_round()

            accepted_states = [node.state for node in self.nodes if getattr(node, 'accepted', False)]
            for state in set(accepted_states):
                if accepted_states.count(state) > len(self.nodes) * 2 / 3:
                    self.consensus_reached = True
                    return rounds_taken, self.nodes[0].state
```

## Snowflake

Snowflake augments Slush with a single counter that captures
the strength of a node’s conviction in its current color. This
per-node counter stores how many consecutive samples of the
network by that node have all yielded the same color. A node
accepts the current color when its counter reaches β, another
security parameter.