import random
import math

class Node:
    def __init__(self, state, parent=None):
        """
        A Node in the MCTS tree
        """
        self.state = state  # Current game state
        self.parent = parent  # Parent node
        self.children = []  # Child nodes
        self.visits = 0  # Visit count
        self.wins = 0  # Win count
        self.is_terminal = False  # Whether this is a terminal node
        self.untried_actions = self.get_possible_actions(state)
        #print(f"Node created: state={self.state}, is_terminal={self.is_terminal}, untried_actions={self.untried_actions}")

    def get_possible_actions(self, state):
        """
        Generate all possible actions from the current state.
        """
        if not state or 'player_score' not in state:
            return []
        player_score = state['player_score']
        if player_score >= 21:  # No valid actions if player already has 21 or more
            return []
        return ["HIT", "STICK"]

    def add_child(self, child_state, action):
        """
        Add a child node for a given action.
        """
        child_node = Node(child_state, parent=self)
        self.children.append((action, child_node))
        return child_node

    def best_child(self, exploration_weight=1.41):
        """
        Select the best child node based on UCB1 formula.
        """
        if not self.children:
            return None
        return max(
            self.children,
            key=lambda c: c[1].wins / c[1].visits + exploration_weight * math.sqrt(math.log(self.visits) / c[1].visits)
            if c[1].visits > 0 else float('-inf')
        )[1]


class BlackjackMCTS:
    def __init__(self, game, simulations=100):
        """
        Initialize MCTS with the game instance and number of simulations.
        """
        self.game = game
        self.simulations = simulations
        print(f"Initialized MCTS with {simulations} simulations.")

    def decide_action(self, player_hand, dealer_hand):
        """
        Use MCTS to decide the next action (HIT or STICK).
        """
        root = Node(self.get_state(player_hand, dealer_hand))

        for _ in range(self.simulations):
            node = self.tree_policy(root)
            if node is None:
                continue
            result = self.default_policy(node.state)
            self.backpropagate(node, result)

        # If no children are available, return a default action
        if not root.children:
            print("No children available, defaulting to STICK.")
            return "STICK"

        # Choose the best action based on simulation results
        best_action, _ = max(
            root.children,
            key=lambda c: c[1].wins / c[1].visits if c[1].visits > 0 else float('-inf')
        )
        return best_action

    def tree_policy(self, node):
        """
        Select a node to expand using the tree policy (UCB1).
        """
        while not node.is_terminal:
            if node.untried_actions:
                # Expand: Add a new child node
                action = node.untried_actions.pop()
                next_state = self.simulate_action(node.state, action)
                return node.add_child(next_state, action)
            elif node.children:
                # Select the best child node based on UCB1
                node = node.best_child()
            else:
                # Mark as terminal if no actions or children available
                node.is_terminal = True
                break
        return node

    def default_policy(self, state):
        """
        Simulate a complete game from the given state and return the result.
        """
        if not state:
            return 0  # Treat invalid state as a loss

        temp_deck = self.game.deck.copy()
        random.shuffle(temp_deck)

        player_hand = state['player_hand'][:]
        dealer_hand = state['dealer_hand'][:]
        player_score = state['player_score']
        dealer_score = state['dealer_score']

        # Simulate player's turn if not already terminal
        while player_score < 21:
            if random.random() < 0.5:  # Randomly decide HIT or STICK during simulation
                if not temp_deck:  # If deck is empty, break the loop
                    break
                player_hand.append(temp_deck.pop())
                player_score = self.game.calculate_score(player_hand)
            else:
                break

        # Player busts
        if player_score > 21:
            return 0  # Loss for player

        # Simulate dealer's turn
        while dealer_score < 17:
            if not temp_deck:  # If deck is empty, break the loop
                break
            dealer_hand.append(temp_deck.pop())
            dealer_score = self.game.calculate_score(dealer_hand)

        # Determine the result
        if dealer_score > 21 or player_score > dealer_score:
            return 1  # Win for player
        elif player_score < dealer_score:
            return 0  # Loss for player
        else:
            return 0.5  # Tie

    def backpropagate(self, node, result):
        """
        Update the win and visit counts along the path back to the root.
        """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def get_state(self, player_hand, dealer_hand):
        """
        Create a state representation for the current game state.
        """
        if not player_hand or not dealer_hand:
            return None
        return {
            'player_hand': player_hand[:],
            'dealer_hand': dealer_hand[:],
            'player_score': self.game.calculate_score(player_hand),
            'dealer_score': self.game.calculate_score(dealer_hand),
        }

    def simulate_action(self, state, action):
        """
        Simulate taking an action and return the resulting state.
        """
        if not state:
            return None

        new_state = {
            'player_hand': state['player_hand'][:],
            'dealer_hand': state['dealer_hand'][:],
            'player_score': state['player_score'],
            'dealer_score': state['dealer_score'],
        }

        if action == "HIT":
            # Simulate HIT: Add a card to player's hand
            if self.game.deck:
                new_card = self.game.deck.pop()
                new_state['player_hand'].append(new_card)
                new_state['player_score'] = self.game.calculate_score(new_state['player_hand'])

        return new_state
