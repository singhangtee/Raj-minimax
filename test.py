__author__ = "Singhang Tee"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "teesi625@student.otago.ac.nz"

import random
import numpy as np

agentName = "minimax_agent"

class RajAgent():
    """
    A class that encapsulates the code dictating the
    behaviour of the agent playing the game of Raj.

    ...

    Attributes
    ----------
    item_values : list of ints
        values of items to bid on
    card_values: list of ints
        cards agent bids with

    Methods
    -------
    AgentFunction(percepts)
        Returns the card value from hand to bid with
    """
    
    def __init__(self, item_values, card_values):
        """
        :param item_values: list of ints, values of items to bid on
        :card_values: list of ints, cards agent bids with
        """

        self.card_values = card_values
        self.item_values = item_values



    def AgentFunction(self, percepts):
        """Returns the bid value of the next bid

        :param percepts: a tuple of four items: bidding_on, items_left, my_cards, opponents_cards

                , where

                bidding_on - is an integer value of the item to bid on;

                items_left - the items still to bid on after this bid (the length of the list is the number of
                            bids left in the game)

                my_cards - the list of cards in the agent's hand

                bank - total value of items in this game
                
                opponents_cards - a list of lists of cards in the opponents' hands, so in two player game, this is
                                a list of one list of cards, in three player game, this is a list of two lists, etc.


        :return: value - card value to bid with, must be a number from my_cards
        """
        bidding_on = percepts[0]
        items_left = percepts[1]
        my_cards = percepts[2]
        bank = percepts[3]
        opponents_cards = percepts[4:]

        if(len(my_cards) == 1):
           return my_cards[0]

        depth = 50  # Depth of Minimax search
        best_value = -np.inf  # Initialize to negative infinity
        best_move = None

        # Get all possible moves for the agent
        possible_moves = my_cards
        
        for move in possible_moves:
            value = self.minimax(percepts, move, depth - 1, False)
            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def minimax(self, percepts, my_move, depth, maximizing_player):
        """Minimax algorithm to evaluate the best move.

        :param move: Current move of the board.
        :param depth: Depth of the minimax search.
        :param maximizing_player: Boolean indicating if the current player is the maximizing player.
        :return: The value of the move after applying minimax.
        """
        bidding_on = percepts[0]
        items_left = percepts[1]
        my_cards = percepts[2]
        bank = percepts[3]
        opponents_cards = percepts[4:]

        # Base case: when depth is 0 or there are no more cards in hand left
        if depth < 0 or len(my_cards) == 0:
            return self.evaluate(percepts)

        if maximizing_player:
            max_eval = -np.inf
            for my_move in my_cards:  
                    for bid in items_left:
                        new_bidding_on = bid + bidding_on
                        new_percepts = (new_bidding_on, items_left, my_cards, bank, opponents_cards) 
                        eval = self.minimax(percepts, my_move, depth, False)
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = np.inf
            for opp_move in opponents_cards[0]:
                new_percepts =  self.update_percepts(percepts, opp_move, my_move)
                eval = self.minimax(new_percepts, opp_move, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def update_percepts(self, percepts, opp_move, my_move):
        """
        Transitions the game state to a new state based on the given move.

        :param percepts: A tuple representing the current game state.
                        (bidding_on, items_left, my_cards, my_bank, opponents_cards)
        :param move: The bid (card) the agent decides to play.

        :return: A new state tuple representing the game state after the move is taken.
        """
        bidding_on, items_left, my_cards, bank, opponents_cards = percepts
        # Create a deep copy of the state to avoid changing the original state
        new_my_cards = list(my_cards)
        new_opponents_cards = list(opponents_cards)
        new_items_left = list(items_left)
        new_bank = bank
        new_bidding_on = bidding_on
            
        new_my_cards.remove(my_move)
        new_opponents_cards.remove(opp_move)

        opp_bank = 0
        # Calculate the outcome of the bid
        if my_move > opp_move:
            new_bank += bidding_on
        elif my_move < opp_move:
            opp_bank += bidding_on 
        else:
            # Tie, the item carries over to the next round
            if len(new_items_left) > 0:
                new_bidding_on += new_items_left.pop(0)
            else:
                new_bidding_on = 0


        # Construct the new state
        new_percepts = (
            new_bidding_on,
            tuple(new_items_left),
            tuple(new_my_cards),
            new_bank,
            tuple(new_opponents_cards)
        )

        return new_percepts

    
    def evaluate(self, percepts):
        """
        Evaluate the game state using a heuristic function that includes the bank value.

        :param percepts: A tuple (bidding_on, items_left, my_cards, bank, opponents_cards)
        :return: A heuristic score for the current game state.
        """
        # Extract percepts
        bidding_on = percepts[0]
        items_left = percepts[1]
        my_cards = percepts[2]
        bank = percepts[3]
        opponents_cards = percepts[4:]

        opp_bank = sum(self.item_values) - bank

        if len(my_cards) == 0:
            return np.sign(bank-opp_bank) * 100
        
        # Initialize heuristic score
        score = 0

        # 1. Card Strength: Higher card values are better
        card_strength = sum(my_cards)

        # 4. Opponent Strength: Lower opponent strength is better
        # Flatten opponents_cards if it's a list of lists
        flat_opponents_cards = [card for sublist in opponents_cards for card in sublist]
        opponent_strength = sum(flat_opponents_cards)


        # Combine components into heuristic score
        score += card_strength  # Higher card values are better
        score += bank 
        # score -= opp_bank
        score -= opponent_strength  # Lower opponent strength is better

        
        return score

