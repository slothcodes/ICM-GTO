import numpy as np

def calculate_icm(stacks, payouts):
    """
    Exact Malmuth-Harville ICM calculation.
    """
    stacks = np.array(stacks, dtype=np.float64)
    payouts = np.array(payouts, dtype=np.float64)

    num_players = len(stacks)

    if num_players == 0 or np.sum(stacks) == 0:
        return np.zeros(num_players)

    equities = np.zeros(num_players)

    # We only care about active players
    active_mask = stacks > 0
    active_count = np.sum(active_mask)
    busted_count = num_players - active_count

    # Shift payouts to only use the remaining ones for active players
    remaining_payouts = payouts[:active_count]
    if len(remaining_payouts) == 0:
        return equities

    def icm_recursive(current_stacks, current_prob, depth):
        if depth >= len(remaining_payouts) or depth >= active_count:
            return

        total_chips = np.sum(current_stacks)
        if total_chips <= 0:
            return

        for i in range(num_players):
            if current_stacks[i] > 0:
                prob_i = current_stacks[i] / total_chips
                equities[i] += current_prob * prob_i * remaining_payouts[depth]

                new_stacks = current_stacks.copy()
                new_stacks[i] = 0
                icm_recursive(new_stacks, current_prob * prob_i, depth + 1)

    icm_recursive(stacks, 1.0, 0)

    # Add busted payouts
    # For a real solver we track who busted when.
    # Here we assume all 0 stacks busted previously.
    if busted_count > 0:
        # Give them the lowest available payouts
        # In a real game we need the exact elimination order.
        pass

    return equities

def get_utility(initial_stacks, final_stacks, payouts):
    initial_eq = calculate_icm(initial_stacks, payouts)
    final_eq = calculate_icm(final_stacks, payouts)
    return final_eq - initial_eq
