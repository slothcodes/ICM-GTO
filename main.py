import json
import time
import multiprocessing
from state import GameState
from tree import build_tree
from cfr import CFRSolver
import config

global_root_node = None
global_scenario = None

def parse_input(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def worker_cfr(iterations):
    solver = CFRSolver(global_root_node, global_scenario["payouts"], global_scenario["stacks"])
    # Hero position and cards are passed down. The solver now samples all cards,
    # but we can query the strategy for the specific hero state.
    solver.solve(iterations)

    # We must find the node where the hero acts and get strategy for their cards
    return solver.get_hero_strategy(global_root_node, global_scenario["hero_position"], global_scenario["hero_cards"], global_scenario.get("history", []))

def run_solver(scenario):
    global global_root_node
    global global_scenario

    global_scenario = scenario
    num_players = len(scenario["stacks"])

    initial_state = GameState(
        num_players=num_players,
        stacks=scenario["stacks"],
        blinds=scenario["blinds"]
    )

    # Advance state to match provided history
    # History format: list of "fold", "call", "push"
    for action in scenario.get("history", []):
         initial_state = initial_state.apply_action(action)

    print(f"Building abstraction tree for {num_players} players...")
    start_time = time.time()
    global_root_node = build_tree(initial_state)
    print(f"Tree built in {time.time() - start_time:.2f} seconds.")

    print(f"Starting Chance-Sampled MCCFR solver for {config.CFR_ITERATIONS} iterations across {config.NUM_THREADS} threads...")
    solve_start = time.time()

    pool = multiprocessing.Pool(processes=config.NUM_THREADS)
    iters_per_thread = config.CFR_ITERATIONS // config.NUM_THREADS
    results = pool.map(worker_cfr, [iters_per_thread] * config.NUM_THREADS)
    pool.close()
    pool.join()

    print(f"CFR complete in {time.time() - solve_start:.2f} seconds.")

    final_strategy = {}
    for result in results:
        for action, prob in result.items():
            if action not in final_strategy:
                final_strategy[action] = 0
            final_strategy[action] += prob

    for action in final_strategy:
        final_strategy[action] /= config.NUM_THREADS

    return final_strategy

def format_output(strategy):
    print("\n--- OPTIMAL STRATEGY ---")
    for action, prob in strategy.items():
        print(f"{action.capitalize()}: {prob * 100:.2f}%")
    print("------------------------\n")

if __name__ == "__main__":
    print("Loading Scenario...")
    scenario_data = parse_input(config.SCENARIO_FILE)

    final_strategy = run_solver(scenario_data)

    format_output(final_strategy)
