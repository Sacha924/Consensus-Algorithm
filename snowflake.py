import random

from plot_population import plot


class Node:
    def __init__(self, identifier, initial_state):
        self.identifier = identifier
        self.state = initial_state
        self.counter = 0 
        self.neighbors = []

    def query(self, querying_color=None):
        if self.state == '⊥' and querying_color:
            self.state = querying_color
        return self.state

    def update_state(self, new_state):
        self.state = new_state

    def sample_neighbors(self, k):
        return random.sample(self.neighbors, min(k, len(self.neighbors)))
    
    def accept(self, state):
        self.state = state


class SnowflakeAlgorithm:
    def __init__(self, k, alpha, beta, initial_states):
        self.nodes = [Node(i, state) for i, state in enumerate(initial_states)]
        self.k = k
        self.alpha = alpha
        self.beta = beta
        for node in self.nodes:
            node.neighbors = self.nodes

    def on_query(self, node, col):
        return node.query(col)

    def run_snowflake_round(self):
        changes = False
        for node in self.nodes:
            if node.state == '⊥':
                continue

            sampled_neighbors = node.sample_neighbors(self.k)
            neighbor_states = [self.on_query(neighbor, node.state) for neighbor in sampled_neighbors]
            state_count = {state: neighbor_states.count(state) for state in set(neighbor_states)}

            maj = False
            for state, count in state_count.items():
                if count >= self.alpha * self.k:
                    maj = True
                    if state != node.state:
                        node.update_state(state)
                        node.counter = 1
                        changes = True
                    else:
                        node.counter += 1
                    if node.counter >= self.beta:
                        node.accept(state)
            if not maj:
                node.counter = 0
        return changes

    def run(self):
        rounds_taken = 0
        while True:
            rounds_taken += 1
            changes = self.run_snowflake_round()
            if not changes:  
                break
        
        return rounds_taken, self.nodes[0].state


def generate_initial_states(num_R, num_B, num_neutral):
    initial_states = ['R'] * num_R + ['B'] * num_B + ['⊥'] * num_neutral
    random.shuffle(initial_states)
    return initial_states

n = 600
k = 10
alpha = 0.8
beta = 10
initial_states = generate_initial_states(n//3,n//3,n//3)
slush = SnowflakeAlgorithm(k, alpha, beta, initial_states)
rounds_taken, final_state = slush.run()

print("all nodes become ",final_state, " after ", rounds_taken, " rounds")

# plot(rounds_result, [0.5, 0.5], "Snowflake. n={0}; k={1}; alpha={2}; beta={3};".format(n, k, alpha, beta), "/snowflake.gif")

