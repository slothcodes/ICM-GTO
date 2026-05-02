import copy

class GameState:
    def __init__(self, num_players, stacks, blinds):
        self.num_players = num_players
        self.stacks = list(stacks)
        self.blinds = blinds
        self.pot = 0
        self.bets = [0] * num_players
        self.active_players = [True] * num_players
        self.current_player = 0
        self.round = 0
        self.history = []
        self.highest_bet = 0
        self.last_raiser = -1

        if sum(self.bets) == 0 and len(self.history) == 0:
            self._post_blinds()

    def _post_blinds(self):
        sb_amt = min(self.stacks[0], self.blinds[0])
        self.stacks[0] -= sb_amt
        self.bets[0] = sb_amt
        self.pot += sb_amt

        if self.num_players > 1:
            bb_amt = min(self.stacks[1], self.blinds[1])
            self.stacks[1] -= bb_amt
            self.bets[1] = bb_amt
            self.pot += bb_amt

        self.highest_bet = max(self.bets)
        self.current_player = 2 % self.num_players
        # Preflop, the BB is the last raiser (they act last if no one raises)
        # However, UTG starts. To ensure BB gets their option, we set last_raiser to an impossible value initially,
        # or handle it by checking if history is just folds/calls.
        # A simpler way is to set last_raiser to UTG initially. If everyone calls, it wraps back to BB and ends.
        self.last_raiser = 2 % self.num_players

    def is_terminal(self):
        active_count = sum(self.active_players)
        if active_count <= 1:
            return True
        if self.round > 3:
            return True
        return False

    def get_legal_actions(self):
        if self.is_terminal():
            return []

        actions = ['fold']
        call_amt = self.highest_bet - self.bets[self.current_player]

        # A player can always call if they have chips, even if stack is less than call_amt (all-in call)
        if self.stacks[self.current_player] > 0:
             actions.append('call')

        if self.stacks[self.current_player] > call_amt:
            actions.append('push')

        return actions

    def apply_action(self, action):
        new_state = copy.deepcopy(self)
        p = new_state.current_player

        if action == 'fold':
            new_state.active_players[p] = False
        elif action == 'call':
            call_amt = min(new_state.stacks[p], new_state.highest_bet - new_state.bets[p])
            new_state.stacks[p] -= call_amt
            new_state.bets[p] += call_amt
            new_state.pot += call_amt
        elif action == 'push':
            push_amt = new_state.stacks[p]
            new_state.stacks[p] -= push_amt
            new_state.bets[p] += push_amt
            new_state.pot += push_amt
            if new_state.bets[p] > new_state.highest_bet:
                new_state.highest_bet = new_state.bets[p]
                new_state.last_raiser = p

        new_state.history.append((p, action))
        new_state._advance_player()
        return new_state

    def _advance_player(self):
        active_count = sum(self.active_players)
        if active_count <= 1:
            return

        next_p = (self.current_player + 1) % self.num_players

        all_matched = True
        for i in range(self.num_players):
            if self.active_players[i] and self.stacks[i] > 0 and self.bets[i] < self.highest_bet:
                all_matched = False
                break

        # Check if everyone has acted once. The simplest way in this structure is:
        # If everyone has matched AND the next player is the one who made the last raise
        # For preflop, if everyone just calls the BB, the next player is UTG.
        if all_matched and next_p == self.last_raiser:
            # But preflop, BB must get an option if no one raised.
            if self.round == 0 and self.highest_bet == self.blinds[1] and self.current_player != 1:
                 pass # Let it wrap to BB
            else:
                 self._next_round()
                 return

        while not self.active_players[next_p] or self.stacks[next_p] == 0:
            next_p = (next_p + 1) % self.num_players
            if next_p == self.current_player:
                while self.round <= 3:
                     self._next_round()
                return

        self.current_player = next_p

    def _next_round(self):
        self.round += 1
        self.bets = [0] * self.num_players
        self.highest_bet = 0

        if self.round <= 3:
             next_p = 0
             while not self.active_players[next_p] or self.stacks[next_p] == 0:
                 next_p = (next_p + 1) % self.num_players
                 if next_p == 0:
                     break
             self.current_player = next_p
             self.last_raiser = next_p
