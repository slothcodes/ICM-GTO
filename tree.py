from state import GameState

class Node:
    def __init__(self, action_history, current_player, is_terminal, highest_bet, active_players, stacks, pot, round_num, bets):
        self.action_history = action_history
        self.current_player = current_player
        self.is_terminal = is_terminal
        self.highest_bet = highest_bet
        self.active_players = active_players
        self.stacks = stacks
        self.pot = pot
        self.round = round_num
        self.bets = bets
        self.children = {} # action -> Node

def build_tree(state, depth=0, max_depth=10):
    """
    Recursively builds the game tree focusing strictly on betting structure.
    Does NOT store deck, cards, or board. Those are passed down during CFR.
    """
    node = Node(
        action_history=list(state.history),
        current_player=state.current_player,
        is_terminal=state.is_terminal() or depth >= max_depth,
        highest_bet=state.highest_bet,
        active_players=list(state.active_players),
        stacks=list(state.stacks),
        pot=state.pot,
        round_num=state.round,
        bets=list(state.bets)
    )

    if node.is_terminal:
        return node

    legal_actions = state.get_legal_actions()
    for action in legal_actions:
        next_state = state.apply_action(action)
        node.children[action] = build_tree(next_state, depth + 1, max_depth)

    return node
