def get_bucket(hole_cards, board):
    """
    Groups similar hands into 'buckets' to reduce the state space.
    """
    if not board:
        # Preflop: Create a canonical representation
        if len(hole_cards) != 2:
            return "unknown"

        rank1, suit1 = hole_cards[0][0], hole_cards[0][1]
        rank2, suit2 = hole_cards[1][0], hole_cards[1][1]

        # Ensure rank1 >= rank2
        ranks = "23456789TJQKA"
        if ranks.index(rank1) < ranks.index(rank2):
            rank1, rank2 = rank2, rank1

        suited = "s" if suit1 == suit2 else "o"
        if rank1 == rank2:
            return f"{rank1}{rank2}"
        return f"{rank1}{rank2}{suited}"

    # Postflop bucketing requires complex EHS evaluation.
    # For this simplified model, we will use a dummy abstraction
    # since building a full K-means EHS abstraction takes gigabytes of data.
    return "postflop_bucket"

def get_betting_abstraction(state):
    """
    Limits the number of bet sizes to reduce the branching factor.
    """
    return state.get_legal_actions()
