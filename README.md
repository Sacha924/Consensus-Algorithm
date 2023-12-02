# Overview

This is an implementation of the snowball consensus algorithm.

I first decide to explore Slush and Snowflake algorithm.


## Slush


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


## Snowflake


```
1:  procedure snowflakeLoop(u, col0 ∈ {R, B, ⊥})
2:    col := col0, cnt := 0
3:    while undecided do
4:      if col = ⊥ then continue
5:      K := sample(N \u, k)
6:      P := [query(v, col) for v ∈ K]
7:      for col' ∈ {R, B} do
8:        if P.count(col') ≥ α · k then
9:          if col != col then
10:           col := col', cnt := 0
11:         else
12:           if ++cnt > β then accept(col)
```


## Snowball


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

