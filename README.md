# 7-Max Freeroll Tournament Poker Solver

## Overview
This repository contains a high-performance Python-based poker solver specifically tailored for 7-max freeroll tournaments. It uses Chance-Sampled Monte Carlo Counterfactual Regret Minimization (MCCFR) to calculate Game Theory Optimal (GTO) strategies, combined with the Independent Chip Model (ICM) to convert chip expectation (cEV) into real tournament equity ($EV).

This solver is optimized to evaluate complex multi-way poker situations and provides optimal action frequencies based on the provided scenario.

## Features
- **MCCFR Engine**: Solves for GTO approximations using Chance-Sampled MCCFR.
- **ICM Integration**: Uses the exact Malmuth-Harville algorithm for accurate multi-way tournament equity evaluation.
- **Multiprocessing Support**: Utilizes multi-threading to speed up large CFR tree traversals.
- **Performance Focused**: Integrates `phevaluator` for blazing-fast hand evaluation, with potential for further `numba` optimizations.

## How to Use

### 1. Install Dependencies
Ensure you have Python 3.8+ installed, then install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Your Scenario
Edit the `scenario.json` file to define the current table state. The required fields include:
- `blinds`: The current small and big blind sizes.
- `stacks`: A list of chip stacks for all players at the table.
- `payouts`: The payout structure of the tournament (e.g., top 10 paid).
- `hero_position`: Your position index at the table (0-indexed).
- `hero_cards`: Your two hole cards (e.g., `["As", "Kd"]`).
- `board`: The current community cards (leave empty `[]` for preflop).
- `history` (optional): The betting history of the hand.

Example `scenario.json`:
```json
{
    "blinds": [100, 200],
    "stacks": [5000, 4500, 3000, 2000, 1500, 8000, 4000],
    "payouts": [500, 300, 200, 100, 80, 60, 50, 40, 30, 20],
    "hero_position": 2,
    "hero_cards": ["As", "Kd"],
    "board": []
}
```

### 3. Run the Solver
To execute the solver and output the optimal strategy for the given scenario:
```bash
python main.py
```
You can tweak solver settings such as the number of threads and CFR iterations in `config.py`.

## Limitations
- **Computational Overhead**: The exact Malmuth-Harville ICM calculation scales factorially ($O(n!)$). Calculating payouts for the top 10 requires ~3.6 million permutations per terminal node evaluation, which can be heavily bottlenecked in pure Python.
- **Multi-way Nash Equilibrium**: MCCFR is not mathematically guaranteed to converge to a Nash Equilibrium in multi-way (3+ players) games, although it produces strong, exploitable-resistant approximations in practice.
- **Python Performance**: Despite multiprocessing and fast evaluation libraries, Python's overhead keeps the tree traversal slower than industrial solvers written in C++ or Rust.
- **Tree Abstractions**: Currently, betting and card abstractions are basic. Expanding to deep post-flop scenarios with many bet sizes can lead to memory explosions.

## Potential Improvements
- **ICM Approximations**: Implementing faster approximation algorithms (like Harville with bounding or Malmuth-Weitzman) could significantly reduce overhead for large payout structures.
- **Advanced Abstractions**: Adding Expected Hand Strength (EHS) bucketing, K-means clustering for hand classes, and dynamic betting tree abstractions to limit branch sizes.
- **Cython/C++ Extensions**: Moving the CFR recursion and tree traversal logic to Cython or raw C++ extensions to sidestep Python's Global Interpreter Lock (GIL) and object overhead.
- **Discounted CFR (DCFR)**: Upgrading from MCCFR to Discounted CFR for faster convergence towards equilibrium.
- **Save/Load Functionality**: Allow for exporting large pre-solved strategy trees to disk so they don't have to be re-run for identical scenarios.
