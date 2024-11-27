import pygame
import random
import os
from MCTS_AI import BlackjackMCTS 

# Initialize Pygame
pygame.init()

# Define screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack AI")

# Define fonts and colors
FONT = pygame.font.Font(None, 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

# Load background image
BACKGROUND_IMAGE = pygame.image.load("./cards/background.jpg")
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load card images
CARD_PATH = "./cards/"
cards = {}
for filename in os.listdir(CARD_PATH):
    if filename.endswith(".png"):
        card_name = filename.split(".")[0]
        cards[card_name] = pygame.image.load(os.path.join(CARD_PATH, filename))

# Load facedown card image
face_down_card = cards.get("faceDown", None)
if face_down_card:
    face_down_card = pygame.transform.scale(face_down_card, (100, 150))

# Define card size
CARD_WIDTH = 100
CARD_HEIGHT = 150
for card_name in cards:
    cards[card_name] = pygame.transform.scale(cards[card_name], (CARD_WIDTH, CARD_HEIGHT))

# Define button drawing function
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    text_surface = FONT.render(text, True, WHITE)
    screen.blit(text_surface, (x + (w - text_surface.get_width()) // 2, y + (h - text_surface.get_height()) // 2))
    return pygame.Rect(x, y, w, h)

# Define Blackjack game logic
class BlackjackGame:
    def __init__(self):
        self.deck = self.generate_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.player_turn = True
        self.player_score = 0
        self.dealer_score = 0
        self.reveal_dealer = False

        # Statistics
        self.player_wins = 0      # Number of player wins
        self.total_games = 0      # Total games played
        self.statistics_updated = False  # Flag to check if statistics have been updated

    def update_statistics(self, result):
        """
        Update statistics
        """
        self.total_games += 1
        if result == "Player Wins!":
            self.player_wins += 1

    def generate_deck(self):
        deck = []
        for suit in ["hearts", "diamonds", "clubs", "spades"]:
            for value in range(2, 11):
                deck.append(f"{value}_of_{suit}")
            for face in ["A", "Q", "K", "J"]:
                deck.append(f"{face}_of_{suit}")
        random.shuffle(deck)
        return deck

    def deal_card(self, hand):
        if self.deck:
            hand.append(self.deck.pop())

    def calculate_score(self, hand):
        score = 0
        aces = 0
        for card in hand:
            value = card.split("_")[0]
            if value in ["K", "Q", "J"]:
                score += 10
            elif value == "A":
                aces += 1
                score += 11
            else:
                score += int(value)
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def start_new_game(self):
        self.deck = self.generate_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.player_turn = True
        self.reveal_dealer = False
        self.statistics_updated = False  # Reset statistics flag
        self.deal_card(self.player_hand)
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        self.deal_card(self.dealer_hand)
        self.player_score = self.calculate_score(self.player_hand)
        self.dealer_score = self.calculate_score(self.dealer_hand)

    def player_hit(self):
        self.deal_card(self.player_hand)
        self.player_score = self.calculate_score(self.player_hand)
        if self.player_score > 21:
            self.game_over = True
            self.reveal_dealer = True

    def dealer_turn(self):
        self.reveal_dealer = True
        while self.dealer_score < 17:
            self.deal_card(self.dealer_hand)
            self.dealer_score = self.calculate_score(self.dealer_hand)
        self.game_over = True

    def check_winner(self):
        if self.player_score > 21:
            return "Dealer Wins!"
        elif self.dealer_score > 21 or self.player_score > self.dealer_score:
            return "Player Wins!"
        elif self.player_score < self.dealer_score:
            return "Dealer Wins!"
        else:
            return "It's a Tie!"

# Initialize game instance
game = BlackjackGame()
game.start_new_game()

# Main game loop
running = True
ai_mode = True  # Manual mode (False) or AI mode (True)
while running:
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    
    # Display player's and dealer's cards
    dealer_display_score = game.dealer_score if game.reveal_dealer else "?"
    screen.blit(FONT.render(f"Dealer's Current Sum: {dealer_display_score}", True, WHITE), (20, 20))
    screen.blit(FONT.render(f"Player's Current Sum: {game.player_score}", True, WHITE), (20, 300))
    for i, card in enumerate(game.dealer_hand):
        if i == 0 and not game.reveal_dealer:
            screen.blit(face_down_card, (20 + i * (CARD_WIDTH + 10), 60))
        else:
            screen.blit(cards.get(card, face_down_card), (20 + i * (CARD_WIDTH + 10), 60))
    for i, card in enumerate(game.player_hand):
        screen.blit(cards.get(card, face_down_card), (20 + i * (CARD_WIDTH + 10), 340))

    # Draw buttons
    hit_button = draw_button("HIT", 600, 100, 150, 50, RED)
    stick_button = draw_button("STICK", 600, 200, 150, 50, GREEN)
    next_game_button = None
    if game.game_over:
        next_game_button = draw_button("NEXT GAME", 600, 300, 150, 50, GREEN)
        if not game.statistics_updated:
            result = game.check_winner()
            game.update_statistics(result)
            game.statistics_updated = True  # Ensure statistics are updated only once
        result = game.check_winner()
        screen.blit(FONT.render(result, True, WHITE), (300, 500))

    # Display statistics
    win_text = f"Player Wins: {game.player_wins}"
    total_text = f"Total Games: {game.total_games}"
    win_rate = f"Win Rate: {game.player_wins / game.total_games * 100:.2f}%" if game.total_games > 0 else "Win Rate: N/A"
    screen.blit(FONT.render(win_text, True, WHITE), (600, 400))
    screen.blit(FONT.render(total_text, True, WHITE), (600, 440))
    screen.blit(FONT.render(win_rate, True, WHITE), (600, 480))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not ai_mode and not game.game_over:
                if hit_button.collidepoint(event.pos):
                    game.player_hit()
                elif stick_button.collidepoint(event.pos):
                    game.dealer_turn()
            elif game.game_over and next_game_button and next_game_button.collidepoint(event.pos):
                game.start_new_game()
    
    # AI mode logic
    if ai_mode and not game.game_over:
        ai = BlackjackMCTS(game)
        if game.player_turn:
            action = ai.decide_action(game.player_hand, game.dealer_hand)
            if action == "HIT":
                game.player_hit()
            else:
                game.dealer_turn()

    pygame.display.flip()

pygame.quit()
