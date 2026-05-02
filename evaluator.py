from phevaluator.evaluator import evaluate_cards

def evaluate_hand(hole_cards, board):
    """
    Evaluates a 5, 6, or 7 card hand.
    hole_cards: list of 2 strings, e.g., ["Ah", "Kh"]
    board: list of 0, 3, 4, or 5 strings, e.g., ["2s", "3d", "4c", "5h", "6s"]
    Returns an integer rank. Lower is better (1 is Royal Flush).
    """
    cards = hole_cards + board
    if len(cards) < 5:
        return 9999 # Cannot evaluate preflop or flop without full board

    return evaluate_cards(*cards)
