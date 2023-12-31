# 0 - red, 1 - blue.
import math
import random

from tqdm import tqdm

from plot_population import plot


def main(n, k, alpha, beta, adv, rounds):
    splits = []
    colors = []
    decided = []
    cnt = []
    d = []
    lastcol = []
    honest = math.floor(n * (1.0 - adv))
    initial_colors = []

    def total_blues():
        return sum(colors)

    def total_reds():
        return honest - total_blues()

    def query(requester_ind, responder_ind):
        if responder_ind < honest:
            return colors[responder_ind]
        return initial_colors[requester_ind] # Adversarial case

    for i in range(honest):
        color = random.randint(0, 1)
        colors.append(color)
        lastcol.append(color)
        initial_colors.append(color)
        decided.append(False)
        cnt.append(0)
        d.append([0, 0])

    for r in tqdm(range(rounds)):
        for i in range(honest):
            if decided[i]:
                continue
            peers = random.sample([x for x in range(n) if x != i], k)
            queries = [query(i, p) for p in peers]
            for col in 0, 1:
                if len([q for q in queries if q == col]) > alpha*k:
                    d[i][col] += 1
                    if d[i][col] > d[i][colors[i]]:
                        colors[i] = col
                    if col != lastcol[i]:
                        lastcol[i] = col
                        cnt[i] = 0
                    else:
                        cnt[i] += 1
                        if cnt[i] > beta:
                            decided[i] = True

        if all(decided):
            print("Consensus achieved!")
        splits.append((r, total_reds() / honest))

    return splits


n = 1000
k = 10
alpha = 0.8
beta = 5
adv = 0.10
rounds = 200
rounds = main(n, k, alpha, beta, adv, rounds)
plot(rounds, [0.5 - adv, 0.5 + adv], "Snowball. n={0}; k={1}; alpha={2}; beta={3}; adversaries={4}; ".format(n, k, alpha, beta, adv),
        "snowball.gif")
