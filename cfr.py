import numpy as np
from icm import get_utility
from evaluator import evaluate_hand
from abstraction import get_bucket
import random
from deck import Deck

class CFRSolver:
    def __init__(self, root_node, payouts, initial_stacks):
        self.root_node = root_node
        self.payouts = payouts
        self.initial_stacks = initial_stacks
        self.num_players = len(initial_stacks)
        self.inf_sets = {}

    def _get_inf_set_key(self, node, hole_cards, board):
        player = node.current_player
        bucket = get_bucket(hole_cards[player], board)
        history_str = "-".join([f"P{p}:{a}" for p, a in node.action_history])
        return f"{bucket}|{history_str}"

    def _get_node_data(self, inf_set_key, legal_actions):
        if inf_set_key not in self.inf_sets:
            self.inf_sets[inf_set_key] = {
                'regret_sum': {a: 0.0 for a in legal_actions},
                'strategy_sum': {a: 0.0 for a in legal_actions}
            }
        return self.inf_sets[inf_set_key]

    def _get_strategy(self, node_data, legal_actions):
        strategy = {}
        normalizing_sum = 0
        for a in legal_actions:
            strategy[a] = max(node_data['regret_sum'].get(a, 0), 0)
            normalizing_sum += strategy[a]

        num_actions = len(legal_actions)
        for a in legal_actions:
            if normalizing_sum > 0:
                strategy[a] /= normalizing_sum
            else:
                strategy[a] = 1.0 / num_actions
        return strategy

    def cfr(self, node, reach_probs, hole_cards, board, deck_cards):
        if node.is_terminal:
            active = node.active_players
            active_count = sum(active)
            final_stacks = list(node.stacks)

            if active_count == 1:
                winner_idx = active.index(True)
                final_stacks[winner_idx] += node.pot
            else:
                current_board = list(board)
                cards_needed = 5 - len(current_board)
                if cards_needed > 0:
                    drawn = deck_cards[:cards_needed]
                    deck_cards = deck_cards[cards_needed:]
                    current_board.extend(drawn)

                ranks = []
                for i in range(self.num_players):
                    if active[i] and hole_cards[i]:
                        rank = evaluate_hand(hole_cards[i], current_board)
                        ranks.append((rank, i))
                    elif active[i]:
                        ranks.append((99999, i))

                ranks.sort()
                winner_idx = ranks[0][1]
                final_stacks[winner_idx] += node.pot

            return get_utility(self.initial_stacks, final_stacks, self.payouts)

        current_player = node.current_player

        current_board = list(board)
        current_deck_cards = list(deck_cards)

        target_board_len = 0
        if node.round == 1: target_board_len = 3
        elif node.round == 2: target_board_len = 4
        elif node.round >= 3: target_board_len = 5

        if len(current_board) < target_board_len:
             needed = target_board_len - len(current_board)
             drawn = current_deck_cards[:needed]
             current_deck_cards = current_deck_cards[needed:]
             current_board.extend(drawn)

        inf_set_key = self._get_inf_set_key(node, hole_cards, current_board)
        legal_actions = list(node.children.keys())
        node_data = self._get_node_data(inf_set_key, legal_actions)
        strategy = self._get_strategy(node_data, legal_actions)

        action_utils = {}
        node_util = np.zeros(self.num_players)

        for action, child in node.children.items():
            new_reach = list(reach_probs)
            new_reach[current_player] *= strategy[action]

            # Pass lists instead of objects to avoid deepcopy overhead
            child_util = self.cfr(child, new_reach, hole_cards, current_board, list(current_deck_cards))
            action_utils[action] = child_util

            node_util += strategy[action] * child_util

        for action in legal_actions:
            regret = action_utils[action][current_player] - node_util[current_player]
            cf_prob = 1.0
            for i in range(self.num_players):
                if i != current_player:
                    cf_prob *= reach_probs[i]

            node_data['regret_sum'][action] += cf_prob * regret
            node_data['strategy_sum'][action] += reach_probs[current_player] * strategy[action]

        return node_util

    def solve(self, iterations):
        for _ in range(iterations):
            deck = Deck()
            deck_cards = list(deck.cards)

            hole_cards = [[] for _ in range(self.num_players)]

            for i in range(self.num_players):
                if self.initial_stacks[i] > 0:
                    hole_cards[i] = [deck_cards.pop(), deck_cards.pop()]

            reach_probs = [1.0] * self.num_players
            self.cfr(self.root_node, reach_probs, hole_cards, [], deck_cards)

    def get_hero_strategy(self, root_node, hero_pos, hero_cards, history):
        # Traverse tree to match history
        node = root_node

        # We assume the tree was built from the end of history.
        # So root_node is already the current state.

        # Find inf set key for hero
        dummy_cards = [[] for _ in range(self.num_players)]
        dummy_cards[hero_pos] = hero_cards
        inf_set_key = self._get_inf_set_key(node, dummy_cards, [])

        if inf_set_key not in self.inf_sets:
            return {a: 1.0/len(node.children) for a in node.children}

        node_data = self.inf_sets[inf_set_key]
        legal_actions = list(node.children.keys())

        strategy = {}
        normalizing_sum = 0
        for a in legal_actions:
            normalizing_sum += node_data['strategy_sum'].get(a, 0)

        num_actions = len(legal_actions)
        for a in legal_actions:
            if normalizing_sum > 0:
                strategy[a] = node_data['strategy_sum'][a] / normalizing_sum
            else:
                strategy[a] = 1.0 / num_actions
        return strategy
