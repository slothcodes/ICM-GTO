# Poker Solver Configuration

# Table & Tournament Settings
NUM_PLAYERS = 7
PAYOUT_STRUCTURE = [500, 300, 200, 100, 80, 60, 50, 40, 30, 20] # Top 10 paid

# Abstraction Settings
MAX_BET_SIZES = 3 # e.g. Call, Raise 50%, All-in
USE_EHS_BUCKETING = True

# Performance & Concurrency Settings
NUM_THREADS = 8 # Multi-processing workers for tree traversal
CFR_ITERATIONS = 10000

# File Paths
SCENARIO_FILE = "scenario.json"
