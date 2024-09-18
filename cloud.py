import pgzrun
import random
import time
import pygame.mixer  # Import pygame.mixer for music control
from pgzrun import *
from pygame import Rect

# Initialize pygame mixer
pygame.mixer.init()

# Define game attributes
TITLE = 'Kun Game'
WIDTH = 600
HEIGHT = 720

# Custom game constants
T_WIDTH = 60
T_HEIGHT = 66
TOOLBAR_HEIGHT = 80  # Add toolbar height

# Position of the card stack below
DOCK = Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# Game state variables
reset_clicks = 0
max_reset_clicks = 3
countdown = 180  # Set countdown to 180 seconds
start_time = None
tiles = []
docks = []
game_over = False  # Flag to check if the game is over
in_menu = True  # Flag to check if the game is in the main menu
difficulty = None  # Flag to determine difficulty level
restart_button_rect = Rect(250, 350, 100, 50)  # Restart button dimensions
hard_button_rect = Rect(250, 250, 100, 50)  # Hard button dimensions
easy_button_rect = Rect(250, 300, 100, 50)  # Easy button dimensions
leaderboard_button_rect = Rect(450, 600, 150, 50)  # Leaderboard button dimensions

# Background music paths
hard_bgm = './music/bgm01.mp3'
easy_bgm = './music/easy_bgm01.mp3'

# Leaderboard data structure (simplified, can be expanded to use a file or database)
leaderboard = []

# Initialize game state
def initialize_game():
    global tiles, docks, reset_clicks, start_time, game_over, in_menu
    reset_clicks = 0
    game_over = False
    in_menu = False
    start_time = time.time()  # Reset the timer
    docks = []

    # Choose game mode based on difficulty
    if difficulty == "hard":
        initialize_hard_mode()
        play_music(hard_bgm)
    elif difficulty == "easy":
        initialize_easy_mode()
        play_music(easy_bgm)

def initialize_hard_mode():
    global tiles
    # Initialize the deck, shuffle 12*12 cards randomly
    ts = list(range(1, 13)) * 12
    random.shuffle(ts)
    tiles = []

    # Create cards and add them to the deck
    for k in range(7):   # 7 layers
        for i in range(7-k):
            for j in range(7-k):
                t = ts.pop()
                tile = Actor(f'tile{t}')
                tile.pos = 120 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9
                tile.tag = t
                tile.layer = k
                tile.status = 1 if k == 6 else 0
                tiles.append(tile)

    # The remaining 4 cards are placed below
    for i in range(4):
        t = ts.pop()
        tile = Actor(f'tile{t}')
        tile.pos = 210 + i * tile.width, 516
        tile.tag = t
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

def initialize_easy_mode():
    global tiles
    # Initialize the deck with images 1-6, each appearing 3 times
    ts = list(range(1, 7)) * 3
    random.shuffle(ts)

    # Ensure we have exactly 3 layers
    tiles = []

    # Create cards and add them to the deck with 3 layers
    for k in range(3):  # 3 layers
        for i in range(3-k):
            for j in range(3-k):
                t = ts.pop()
                tile = Actor(f'tile{t}')
                tile.pos = 120 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9
                tile.tag = t
                tile.layer = k
                tile.status = 1 if k == 2 else 0
                tiles.append(tile)

    # The remaining 4 cards are placed below
    for i in range(4):
        t = ts.pop()
        tile = Actor(f'tile{t}')
        tile.pos = 210 + i * tile.width, 516
        tile.tag = t
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

def initialize_menu():
    global in_menu
    in_menu = True  # Set to True to display the menu

# Call the initialize_menu function to start the game
initialize_menu()

# Draw the main menu
def draw_menu():
    try:
        screen.blit('backg', (0, 0))  # Draw menu background
    except Exception as e:
        print(f"Error loading background image: {e}")
    screen.draw.filled_rect(hard_button_rect, (0, 0, 255))  # Blue button for hard mode
    screen.draw.text("Start Hard", center=hard_button_rect.center, color="white", fontsize=40)
    screen.draw.filled_rect(easy_button_rect, (0, 255, 0))  # Green button for easy mode
    screen.draw.text("Start Easy", center=easy_button_rect.center, color="white", fontsize=40)
    screen.draw.filled_rect(leaderboard_button_rect, (255, 255, 0))  # Yellow button for leaderboard
    screen.draw.text("Leaderboard", center=leaderboard_button_rect.center, color="black", fontsize=30)

# Game frame drawing function
def draw():
    if in_menu:
        draw_menu()
        return

    screen.clear()
    screen.blit('back', (0, 0))   # Background image
    draw_toolbar()  # Draw toolbar
    for tile in tiles:
        tile.draw()
        if tile.status == 0:
            screen.blit('mask', tile.topleft)   # Add mask for unclickable tiles
    for i, tile in enumerate(docks):
        tile.left = (DOCK.x + i * T_WIDTH)
        tile.top = DOCK.y
        tile.draw()

    # Display countdown timer
    if start_time is not None:
        elapsed_time = time.time() - start_time
        remaining_time = countdown - elapsed_time
        if remaining_time > 0:
            screen.draw.text(f"Time left: {int(remaining_time)} seconds", topleft=(10, 10), color="red")
        else:
            game_over_screen()  # If time runs out, show game over screen

    # No cards left, victory
    if len(tiles) == 0:
        screen.blit('win', (0, 0))
        game_over_screen(win=True)

    # More than 7 cards, fail
    if len(docks) >= 7:
        game_over_screen()  # Game over if dock exceeds limit

# Draw the toolbar
def draw_toolbar():
    # Draw toolbar background
    screen.draw.rect(Rect(0, 0, WIDTH, TOOLBAR_HEIGHT), (200, 200, 200))  # Gray toolbar background
    # Draw reset image
    reset_image = 'tile'  # Assume the image name is 'tile'
    reset_image_rect = Rect(10, 10, 60, 60)  # Position and size of reset image
    screen.blit(reset_image, reset_image_rect)  # Draw reset image

    # Display remaining reset times
    remaining_clicks = max_reset_clicks - reset_clicks
    screen.draw.text(f"Resets: {remaining_clicks}", (80, 10), color="black")

    # If reset limit is reached, display a disabled effect
    if reset_clicks >= max_reset_clicks:
        screen.draw.text("Reset limit reached", (80, 40), color="red")

# Game over screen (called when the game ends)
def game_over_screen(win=False):
    global game_over
    game_over = True
    if win:
        screen.blit('win', (0, 0))
    else:
        screen.blit('end', (0, 0))  # Show game over image
    draw_restart_button()

# Draw restart button
def draw_restart_button():
    screen.draw.filled_rect(restart_button_rect, (255, 0, 0))  # Red button
    screen.draw.text("Restart", center=restart_button_rect.center, color="white", fontsize=40)

# Mouse click response
def on_mouse_down(pos):
    global docks, reset_clicks, game_over, in_menu, difficulty

    if in_menu:
        if hard_button_rect.collidepoint(pos):  # Hard button clicked
            difficulty = "hard"
            initialize_game()  # Start the game in hard mode
        elif easy_button_rect.collidepoint(pos):  # Easy button clicked
            difficulty = "easy"
            initialize_game()  # Start the game in easy mode
        elif leaderboard_button_rect.collidepoint(pos):
            show_leaderboard()
        return

    if game_over:
        if restart_button_rect.collidepoint(pos):  # Restart button clicked
            initialize_menu()  # Return to the main menu
        return

    if len(docks) >= 7 or len(tiles) == 0:
        return

    # Check if the reset image is clicked
    reset_image_rect = Rect(10, 10, 60, 60)
    if reset_image_rect.collidepoint(pos):
        if reset_clicks < max_reset_clicks:
            reset_tiles()  # Call reset function
            reset_clicks += 1  # Increment click counter
        return

    for tile in reversed(tiles):
        if tile.status == 1 and tile.collidepoint(pos):
            tile.status = 2
            tiles.remove(tile)
            diff = [t for t in docks if t.tag!= tile.tag]
            if len(docks) - len(diff) < 2:
                docks.append(tile)
            else:
                docks = diff
            for down in tiles:
                if down.layer == tile.layer - 1 and down.colliderect(tile):
                    for up in tiles:
                        if up.layer == down.layer + 1 and up.colliderect(down):
                            break
                    else:
                        down.status = 1
            return

# Reset tiles (shuffle)
def reset_tiles():
    global tiles
    # Get the position of each card
    positions = [tile.pos for tile in tiles]
    # Get the tag of each card
    tags = [tile.tag for tile in tiles]
    
    # Shuffle the tags
    random.shuffle(tags)

    # Update the card's tag and keep the position unchanged
    for tile, new_tag in zip(tiles, tags):
        tile.tag = new_tag
        tile.image = f'tile{new_tag}'  # Update image

# Update function to track time and play appropriate music
def update():
    global start_time, game_over
    if game_over:
        return

    if start_time is None:
        start_time = time.time()  # Record game start time

    # Check if time is up
    if time.time() - start_time > countdown:
        game_over_screen()  # Game over logic when time is up

    # Check if music needs to be played (if not playing)
    play_music(hard_bgm if difficulty == "hard" else easy_bgm)

# Play background music
def play_music(track):
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("./music/bgm01.mp3")
        pygame.mixer.music.play(-1)  # Play the track on loop

def show_leaderboard():
    if difficulty!= "hard":
        return
    screen.clear()
    if not leaderboard:
        screen.draw.text("暂无通关记录", (200, 300), color="black", fontsize=40)
    else:
        screen.draw.text("Hard Mode Leaderboard", (200, 50), color="black", fontsize=40)
        for index, entry in enumerate(leaderboard[:5], start=1):
            time_taken, player_name = entry
            screen.draw.text(f"{index}. {player_name} - {time_taken} seconds", (150, 100 + index * 30), color="black", fontsize=30)
    screen.draw.text("Press any key to return to menu", (150, 600), color="black", fontsize=30)

pgzrun.go()