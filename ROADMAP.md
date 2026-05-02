# Poker Solver Roadmap (7-Max Freeroll Tournament, GTO + ICM)

## Overview
This document outlines the step-by-step process for building a poker solver tailored for freeroll tournaments. The solver uses Game Theory Optimal (GTO) play and the Independent Chip Model (ICM) to output the optimal decision for a player in a 7-max table scenario. The tournament has 400-1000 players, paying the top 10.

Given the complexities of multi-way poker and Python's performance characteristics, this roadmap emphasizes performance optimizations (like Numba, Cython, and multiprocessing) and necessary game abstractions.

---

## Step 1: Project Setup and Core Poker Mechanics
Before solving for GTO or ICM, we need a robust, lightning-fast core engine to evaluate hands and manage game states.

### Files to Create:
*   `evaluator.py`
    *   **Purpose:** Fast evaluation of poker hands (determining hand strength and winner).
    *   **Functions:**
        *   `evaluate_hand(hole_cards, board)`: Returns a rank for a 5-to-7 card hand.
        *   *Optimization:* Precompute a lookup table (like a 2-step lookup array similar to the 2+2 evaluator) or use C-extensions to ensure evaluation takes sub-microseconds.
*   `deck.py`
    *   **Purpose:** Representation of cards and decks.
    *   **Functions:** `draw()`, `shuffle()`, `get_card_int()`. Represent cards as integers (bitmasks) for fast bitwise operations instead of object instances.
*   `state.py`
    *   **Purpose:** Track the current game state (pot size, active players, chip stacks, betting history).
    *   **Functions:**
        *   `apply_action(action)`: Updates the state with a fold, call, or raise.
        *   `get_legal_actions()`: Returns available moves for the current player.
        *   `is_terminal()`: Checks if the hand is over.
        *   `get_payoffs()`: Distributes chips to the winner(s) at terminal nodes.

## Step 2: ICM (Independent Chip Model) Engine
With 400-1000 players and only the top 10 paid, early play is mostly Chip EV (cEV), but late-game play (bubble and final table) requires ICM to convert chip expectation into tournament equity expectation ($EV).

### Files to Create:
*   `icm.py`
    *   **Purpose:** Convert a list of chip stacks into real tournament equity based on the payout structure.
    *   **Functions:**
        *   `calculate_icm(stacks, payouts)`: Implements the Malmuth-Harville method to calculate the equity of each stack.
        *   `get_utility(initial_stacks, final_stacks, payouts)`: Calculates the difference in equity ($EV) before and after a hand. This replaces raw chip winnings in the CFR utility function.
        *   *Optimization:* The Malmuth-Harville algorithm is $O(n!)$ where n is the number of paid spots. For top 10 paid, $10!$ is ~3.6 million iterations. We will need an approximation algorithm (e.g., Harville approximation with bounds) or Numba JIT compilation for performance.

## Step 3: Game Tree Building & Abstraction
A full 7-max post-flop game tree is too large to hold in memory. We need to implement abstractions (grouping similar hands/bet sizes) and build a simplified game tree.

### Files to Create:
*   `abstraction.py`
    *   **Purpose:** Reduces the state space to make CFR tractable.
    *   **Functions:**
        *   `get_bucket(hole_cards, board)`: Maps a specific hand to a "bucket" of similar hands (e.g., using EHS - Expected Hand Strength, K-means clustering).
        *   `get_betting_abstraction(pot, stack)`: Restricts legal actions to a few sizes (e.g., fold, call, half-pot, all-in).
*   `tree.py`
    *   **Purpose:** Builds the in-memory tree of all possible abstracted actions.
    *   **Functions:**
        *   `build_tree(initial_state, abstractions)`: Recursively builds nodes for every decision point.

## Step 4: The GTO Solver (CFR Implementation)
This is the mathematical core. We will use Monte Carlo Counterfactual Regret Minimization (MCCFR), specifically External Sampling CFR, as it handles multi-player and large state spaces better than vanilla CFR.

### Files to Create:
*   `cfr.py`
    *   **Purpose:** Runs the CFR algorithm to find the Nash Equilibrium/GTO strategy.
    *   **Functions:**
        *   `cfr_iteration(node, probabilities)`: Traverses the tree, calculating counterfactual values and updating regrets.
        *   `update_strategy(node)`: Updates the current strategy profile based on accumulated regrets using Regret Matching.
        *   `get_final_strategy()`: Averages the strategies over all iterations to output the final GTO solution.
        *   *Note on ICM Integration:* During the CFR traversal, when a terminal node is reached, the payoff must be calculated using the `get_utility` function from `icm.py` rather than raw chips.

## Step 5: Optimization & Concurrency
Python is inherently slow for billions of iterations. To reach acceptable solver speeds, performance optimization is critical.

### Files to Create:
*   `config.py`
    *   **Purpose:** Constants and configurations for threading and memory allocation.
*   `performance.py` (or integrate into `cfr.py`)
    *   **Purpose:** Multi-processing and JIT compilation setup.
    *   **Functions:**
        *   Use `numba.jit` on the `evaluate_hand` and `calculate_icm` functions.
        *   Use `multiprocessing` to run multiple CFR traversals in parallel, aggregating regrets safely in a shared memory array (e.g., NumPy memory-mapped files or `multiprocessing.Array`).

## Step 6: User Interface & API
To provide the player with a solution, we need a way to input the current situation (blinds, stacks, positions, cards) and retrieve the output strategy.

### Files to Create:
*   `main.py`
    *   **Purpose:** Entry point for the solver.
    *   **Functions:**
        *   `parse_input(user_json)`: Reads the table scenario.
        *   `run_solver(scenario)`: Triggers the tree building and CFR loop.
        *   `format_output(strategy)`: Presents the optimal action frequencies (e.g., "Fold: 10%, Call: 40%, Raise All-in: 50%").
*   `scenario.json`
    *   **Purpose:** Example input file containing stacks, blinds, payouts, and hero's cards.

## Summary of the Data Flow
1. User defines the situation in `main.py` (e.g., 7 players, specific stacks, top 10 payout structure, Hero is on the Button with AsKd).
2. `icm.py` maps the current chip stacks to their baseline real money value.
3. `tree.py` builds the game tree with betting abstractions (e.g., limiting actions to fold/call/push for preflop scenarios).
4. `cfr.py` runs MCCFR iterations. At terminal nodes, it calculates the new stacks and uses `icm.py` to find the real money payout difference.
5. After $N$ iterations, `main.py` outputs the average strategy for the root node, giving the user the optimal percentage breakdown of actions to take.
