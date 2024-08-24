import pygame, sys, os, random, math, json
from utils import load_sprites, apply_color_grading, check_collision
from npc import NPC
from chatbox import ChatBox
import ui_elements  
from chat_bubble import ChatBubbleManager
from status_bars import StatusBars
from floating_text import FloatingText, YellowFloatingText, RedFloatingText
import time
from bottom_text import BottomText
from player import Player
from black_screen import BlackScreen
from loading_screen import LoadingScreen
from game_over import GameOver
from bs4 import BeautifulSoup
import requests
from functools import partial
from globals2 import sync_is_environmentally_friendly
import not_ui_elements, ui_elements2, ui_elements3
from pause_screen import GamePaused
from pygame.locals import *
from npc2 import NPC2
from settings import collision_boxes
from npc3 import NPC3
from npc4 import NPC4
from npc5 import NPC5
from cache import environmental_cache



# Initialize Pygame
pygame.init()

pygame.mixer.init()


# Set up the initial screen dimension
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE, 32)
pygame.display.set_caption("StillEarth")

status_bars = StatusBars(WINDOWWIDTH, WINDOWHEIGHT)

# To combat the long run time with Python

class ResourceManager:
    def __init__(self):
        self.images = {}

    def load_image(self, path, convert_alpha=False):
        if path not in self.images:
            if convert_alpha:
                self.images[path] = pygame.image.load(path).convert_alpha()
            else:
                self.images[path] = pygame.image.load(path).convert()
        return self.images[path]

# Create a global instance of ResourceManager
resource_manager = ResourceManager()

# Load background images
background_img1 = resource_manager.load_image('data/images/background/background1.png')
background_img2 = resource_manager.load_image('data/images/background/background2.png')
background_img3 = resource_manager.load_image('data/images/background/background3.png')
background_img4 = resource_manager.load_image('data/images/background/background4.png')

# Load key image
key_image = resource_manager.load_image('data/images/key.png', convert_alpha=True)

pause_screen = GamePaused(WINDOWWIDTH, WINDOWHEIGHT)

# Music 
music_started = False
is_walking_sound_playing = False
walking_sound = pygame.mixer.Sound("music/walking_sound.mp3")



# Define the boundaries of test2.png
TEST2_WIDTH = background_img1.get_width()
TEST2_HEIGHT = background_img1.get_height()

game_over = GameOver(WINDOWWIDTH, WINDOWHEIGHT)
bottle_uses = 0
MAX_BOTTLE_USES = 3

overlay_click_count = 0

player_moving = False
show_key_image = True
 
# Not prefined items
item_uses = {}
MAX_ITEM_USES = 3

# Predefined items
meat_uses = 0
MAX_MEAT_USES = 3

spray_uses = 0
MAX_SPRAY_USES = 3

coffee_uses = 0
MAX_COFFEE_USES = 3

energy_drink_uses = 0
MAX_ENERGY_DRINK_USES = 3


toolbar_height = 100
RAIN_COLOR = (87, 105, 90)
SPLASH_COLOR = (87, 105, 90)
NUM_RAINDROPS = 150
MAX_SPLASHES = 100

raindrops = []
splashes = []

start_time = time.time()

key_image = pygame.image.load("data/images/key.png").convert_alpha()



def apply_item_effects(item_id, effects):
    global environment_points
    for status, value in effects.items():
        if status in ['COMFORT', 'THIRST', 'ENERGY', 'HUNGER']:
            status_bars.modify_bar(status, value)
            if value > 0:
                yellow_text.show_text(f"+{value} {status}", font_size=20)
            elif value < 0:
                red_text.show_text(f"{value} {status}", font_size=20)
                



class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.max_radius = random.randint(3, 7)
        self.growth_rate = 0.5

    def update(self):
        self.radius += self.growth_rate
        return self.radius > self.max_radius

    def draw(self, surface):
        pygame.draw.circle(surface, SPLASH_COLOR, (int(self.x), int(self.y)), int(self.radius), 1)
def initialize_raindrops(width, height):
    global WINDOWWIDTH, WINDOWHEIGHT, raindrops, splashes
    WINDOWWIDTH = width
    WINDOWHEIGHT = height
    raindrops = []
    splashes = []
    for _ in range(NUM_RAINDROPS):
        length = random.randint(10, 20)
        x = random.randint(0, width)
        y = random.randint(-50, height // 2)
        speed = random.randint(7, 13)
        splash_height = random.randint(height // 2, height - 50)
        raindrops.append([x, y, speed, length, splash_height])

def update_and_draw_raindrops(screen):
    for drop in raindrops:
        # Update raindrop position
        drop[1] += drop[2]
        drop[0] += 1  # Slight diagonal movement

        if drop[1] > drop[4]:
            if len(splashes) < MAX_SPLASHES:
                splashes.append(Splash(drop[0], drop[4]))
            reset_raindrop(drop)

        # Draw the raindrop
        end_y = min(drop[1] + drop[3], drop[4])
        pygame.draw.line(screen, RAIN_COLOR, (drop[0], drop[1]), (drop[0] + 1, end_y))

    # Update and draw splashes
    splashes[:] = [splash for splash in splashes if not splash.update()]
    for splash in splashes:
        splash.draw(screen)

def reset_raindrop(drop):
    drop[1] = random.randint(-50, -1)
    drop[0] = random.randint(0, WINDOWWIDTH)
    drop[2] = random.randint(7, 13)
    drop[3] = random.randint(10, 20)
    drop[4] = random.randint(WINDOWHEIGHT // 2, WINDOWHEIGHT - 50)

# Initialize raindrops
initialize_raindrops(WINDOWWIDTH, WINDOWHEIGHT)

# Create a larger surface to hold all four images
total_width = max(background_img1.get_width() + background_img2.get_width(), background_img3.get_width() + background_img4.get_width())
total_height = background_img1.get_height() + background_img3.get_height()
combined_background = pygame.Surface((total_width, total_height))

# Blit the images onto the combined surface
combined_background.blit(background_img1, (0, 0))
combined_background.blit(background_img2, (background_img1.get_width(), 0))
combined_background.blit(background_img3, (0, background_img1.get_height()))
combined_background.blit(background_img4, (background_img3.get_width(), background_img1.get_height()))

# Load the new idle spritesheet
def load_new_idle_spritesheet(path, frame_width, frame_height, scale_factor, frame_count):
    spritesheet = resource_manager.load_image(path, convert_alpha=True)
    frames = []
    for i in range(frame_count):
        frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
        frames.append(scaled_frame)
    return frames

def load_new_run_spritesheet(path, frame_width, frame_height, scale_factor, frame_count):
    spritesheet = resource_manager.load_image(path, convert_alpha=True)
    frames = []
    for i in range(frame_count):
        frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
        frames.append(scaled_frame)
    return frames

# Load the new run sprites

# Load player sprites
PLAYER_WIDTH, PLAYER_HEIGHT = 64, 64
run_sprites = load_new_run_spritesheet('data/images/sprites/player_run.png', 12, 18, 6, 4)
idle_sprites = load_new_idle_spritesheet('data/images/sprites/player_idle.png', 12, 18, 6, 6)
jump_sprites = load_sprites('player/jump', PLAYER_WIDTH, PLAYER_HEIGHT)
print(f"Loaded {len(idle_sprites)} idle sprites, {len(run_sprites)} run sprites, and {len(jump_sprites)} jump sprites")




current_sprite = 0
animation_cooldown = 100
last_update = pygame.time.get_ticks()

# Player variables
player_x = float(TEST2_WIDTH // 2)
player_y = float(TEST2_HEIGHT // 2)
move_speed = 2.5 #character speed
player_state = 'idle'
player_direction = 'right'
is_jumping = False
jump_count = 10

player = Player(player_x, player_y, sys.modules[__name__])

initial_player_x, initial_player_y = player_x, player_y
show_key_image = True

# Initialize an empty toolbar
toolbar_items = []
num_slots = 5

black_screen = BlackScreen(screen, WINDOWWIDTH, WINDOWHEIGHT)

loading_screen = LoadingScreen(screen, WINDOWWIDTH, WINDOWHEIGHT, duration=10000)



font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
font = pygame.font.Font(font_path, 30) 


# Initialize BottomText
font_pathh = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
bottom_text = BottomText(screen, font_pathh, font_size=24)

environment_points = 0
max_environment_points = 15
selected_item_index = None
chat_bubble_manager = ChatBubbleManager()
floating_text = FloatingText()
yellow_text = YellowFloatingText()
red_text = RedFloatingText()

status_bars = StatusBars(WINDOWWIDTH, WINDOWHEIGHT)



#NPC instance
npc = NPC(TEST2_WIDTH // 2 + 100, TEST2_HEIGHT // 2)
npc.game = sys.modules[__name__]
chatbox = ChatBox(550, 200, npc=npc, game=sys.modules[__name__])
sys.modules[__name__].chatbox = chatbox 
npc.chatbox = chatbox

npc2 = NPC2(TEST2_WIDTH // 2 + 150, TEST2_HEIGHT // 2 + 50, sys.modules[__name__])
npc3 = NPC3(TEST2_WIDTH // 2 + 150, TEST2_HEIGHT // 2 + 50, sys.modules[__name__], chat_bubble_manager, npc_id=1)
npc4 = NPC4(TEST2_WIDTH // 2 + 150, TEST2_HEIGHT // 2 + 50, sys.modules[__name__])
npc5 = NPC5(TEST2_WIDTH // 2 + 150, TEST2_HEIGHT // 2 + 50, sys.modules[__name__])


player = Player(player_x, player_y, sys.modules[__name__])


# Camera position
camera_x = player_x - WINDOWWIDTH // 2
camera_y = player_y - WINDOWHEIGHT // 2
camera_smoothing = 0.1

# Load overlay images and position to be able to click on them
nowhite_image, yeswhite_image = ui_elements.load_overlay_images()
current_overlay_image = nowhite_image
overlay_pos = ui_elements.load_overlay_position()

tree_image, treewhite_image = not_ui_elements.load_overlay_images2()
current_overlay_image2 = tree_image
overlay_pos2 = not_ui_elements.load_overlay_position2()

boxes_image, boxeswhite_image = ui_elements2.load_overlay_images3()
current_overlay_image3 = boxes_image
overlay_pos3 = ui_elements2.load_overlay_position3()

bot_image, botwhite_image = ui_elements3.load_overlay_images4()
current_overlay_image4 = bot_image
overlay_pos4 = ui_elements3.load_overlay_position4()




bottle_image = resource_manager.load_image('data/images/bottle.png', convert_alpha=True)
meat_image = resource_manager.load_image('data/images/meat.png', convert_alpha=True)
spray_image = resource_manager.load_image('data/images/bug_spray.png', convert_alpha=True)
energy_drink_image = resource_manager.load_image('data/images/energy_drink.png', convert_alpha=True)
coffee_image = resource_manager.load_image('data/images/coffee.png', convert_alpha=True)

bottle_id = 'bottle'
meat_id = 'meat'
spray_id = 'spray'
energy_id = 'energy_drink'
coffee_id = 'coffee'



# Main game loop
clock = pygame.time.Clock()
running = True
game_paused = False  # Variable to track game pause state

is_hovering = False
selected_item = False
while running:
    dt = clock.tick(60) / 1000.0
    
    if game_paused:
        pause_screen.draw(screen)  # Draw pause screen if paused
        # Only handle pause screen events when the game is paused
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    game_paused = not game_paused
                    print(f"Game paused: {game_paused}") 
                    floating_text.show_text(f"Game Pauses", font_size=20)

                    
                elif event.key == pygame.K_n:
                    # Skip text or other elements if applicable
                    pass
                elif event.key == pygame.K_SPACE:
                    game_paused = False
                    print("Paused screen skipped.")  # Debug print
            elif pause_screen.handle_event(event):
                game_paused = False  # Reset paused state if pause screen handles the event
    else:
    
        if not game_over.is_game_over:
            if environment_points < 0:
                print(f"Environment points below zero: {environment_points}")
                game_over.is_game_over = True
                game_over.game_over_reason = 'ENVIRONMENT'
                game_over.typing_scenario_text = game_over.SCENARIO_TEXTS['ENVIRONMENT']
            elif game_over.check_game_over(status_bars):
                pass
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif black_screen.is_active():
                black_screen.handle_event(event)
                if not black_screen.is_active():
                    status_bars = StatusBars(WINDOWWIDTH, WINDOWHEIGHT)
            elif loading_screen.is_active():
                loading_screen.handle_event(event)
                if not loading_screen.is_active():
                    # Reset status_bars after loading_screen is no longer active
                    status_bars = StatusBars(WINDOWWIDTH, WINDOWHEIGHT)
                    if not music_started:
                        pygame.mixer.music.load('music/main_music.mp3')
                        pygame.mixer.music.play(-1)  
                        music_started = True

            elif game_over.is_game_over:
                if game_over.handle_event(event):
                    status_bars = StatusBars(WINDOWWIDTH, WINDOWHEIGHT)
                    player_x = float(TEST2_WIDTH // 2)
                    player_y = float(TEST2_HEIGHT // 2)
                    environment_points = 0
                    toolbar_items = []
                    selected_item_index = None
                    bottle_uses = 0
                    meat_uses = 0
                    spray_uses = 0
                    coffee_uses = 0
                    energy_drink_uses = 0

                    game_over.reset()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        game_paused = not game_paused
                        print(f"Game paused: {game_paused}")  

                if not chatbox.is_active():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            if not chatbox.is_active() and npc.is_near_player(player_x, player_y):
                                if not npc.interacting:
                                    npc.interact(player_x, player_y)
                                    chatbox.show()
                        elif event.key == pygame.K_SPACE:
                            if not chatbox.is_active() and npc.show_x_button:
                                npc.interact(player_x, player_y)
                                chatbox.show()
                            else:
                                message = chatbox.handle_event(event)
                                if message:
                                    player.say(message)

                elif chatbox.is_active():
                    message = chatbox.handle_event(event)
                    if message:
                        player.say(message)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        adjusted_mouse_pos = (mouse_pos[0] + camera_x, mouse_pos[1] + camera_y)

                        # Handle overlay clicks
                        if overlay_pos and current_overlay_image.get_rect(topleft=overlay_pos).collidepoint(adjusted_mouse_pos):
                            print("Click detected on overlay image")
                            if selected_item_index is not None and selected_item_index < len(toolbar_items):
                                selected_item = toolbar_items[selected_item_index]
                                item_id = selected_item.get('id')

                                # Check if the selected item is a bottle or meat
                                if item_id == bottle_id:
                                    environment_points += 1
                                    floating_text.show_text(f"threw away {item_id}", font_size=20)
                                elif item_id == meat_id:
                                    environment_points -= 1
                                    floating_text.show_text(f"wasted {item_id}", font_size=20)
                                elif item_id == coffee_id:
                                    floating_text.show_text(f"threw away {item_id}", font_size=20)
                                elif item_id == energy_id:
                                    floating_text.show_text(f"threw away {item_id}", font_size=20)

                                # Remove the item from the toolbar
                                ui_elements.remove_item_from_toolbar(toolbar_items, selected_item_index)
                                selected_item_index = None
                                item_uses[item_id] = 0
                                floating_text.show_text(f"threw away {item_id}", font_size=20)

                            else:
                                print("No item selected or invalid selection")
                        # Handle other overlay clicks similarly

        # Game updates and rendering code here

                        else:
                            print("Click not on overlay image")  # Debug print

                        if overlay_pos2 and current_overlay_image2.get_rect(topleft=overlay_pos2).collidepoint(adjusted_mouse_pos):
                            print("Click detected on overlay image")  # Debug print
                            # Check if an item is selected
                            overlay_click_count += 1

                            # Check if clicked three times
                            if overlay_click_count >= 3:
                                environment_points -= 1
                                floating_text.show_text("interfering with nature", font_size=20)
                                overlay_click_count = 0  




                        
                        if overlay_pos3 and current_overlay_image3.get_rect(topleft=overlay_pos3).collidepoint(adjusted_mouse_pos):
                            print("Click detected on overlay image")  # Debug print
                            floating_text.show_text("just some boxes", font_size=20)


                        if overlay_pos4 and current_overlay_image4 and current_overlay_image4.get_rect(topleft=overlay_pos4).collidepoint(adjusted_mouse_pos):
                            print("Click detected on overlay image")  # Debug print
                            floating_text.show_text("just a bottle", font_size=20)



                        if mouse_pos[1] < WINDOWHEIGHT - toolbar_height:
                            if selected_item_index is not None and selected_item_index < len(toolbar_items):
                                selected_item = toolbar_items[selected_item_index]
                                item_id = selected_item.get('id')
                                
                                if item_id not in item_uses:
                                    item_uses[item_id] = 0

                                if item_uses[item_id] < MAX_ITEM_USES:
                                    item_uses[item_id] += 1
                                    
                                    
                                    if item_id in ['bottle', 'meat', 'spray', 'enery_drink', 'coffee']:
                                        # Handle predefined items
                                        if item_id == 'bottle':

                                            status_bars.modify_bar('THIRST', 5)
                                        elif item_id == 'meat':
                                            yellow_text.show_text("+1 point Hunger", font_size=20)
                                            status_bars.modify_bar('HUNGER', 5)
                                        elif item_id == 'coffee':
                                            environment_points += 1
                                            yellow_text.show_text("+1 point Energy", font_size=20)
                                            status_bars.modify_bar('ENERGY', 5)
                                        elif item_id == 'energy_drink':
                                            environment_points -= 1
                                            red_text.show_text("-1 point Eco", font_size=20)
                                            status_bars.modify_bar('THIRST', 5)
                                    else:
                                            # Handle custom items using AI-generated effects changing the status bars
                                            npc.get_item_effects_from_ai(item_id, status_bars, yellow_text, red_text)

                                        
                                    if sync_is_environmentally_friendly(item_id):
                                        environment_points += 1
                                        yellow_text.show_text("+1 point Eco", font_size=20)
                                    else:
                                        environment_points -= 1
                                        print(f"Decreased environment points for {item_id}. Current points: {environment_points}")  # Debug print
                                        red_text.show_text("-1 point Eco", font_size=20)
                                    
                                    if item_uses[item_id] >= MAX_ITEM_USES:
                                        # Display explanation using BottomText
                                        explanation = npc.generate_explanation(item_id)
                                        bottom_text.show_text(explanation)
                                        
                                        # Remove the item from the toolbar
                                        ui_elements.remove_item_from_toolbar(toolbar_items, selected_item_index)
                                        selected_item_index = None
                                        del item_uses[item_id]
                                        print(f"{item_id} removed from toolbar")

                        # Check if the click is on a toolbar item
                        for index, item in enumerate(toolbar_items):
                            item_rect = item['rect'].copy()
                            item_rect.topleft = (
                                (WINDOWWIDTH // 2) - (len(toolbar_items) * (item['rect'].width + 10)) // 2 + index * (item['rect'].width + 10),
                                WINDOWHEIGHT - item['rect'].height - 10
                            )
                            if item_rect.collidepoint(mouse_pos):
                                if selected_item_index == index:
                                    selected_item_index = None  # Deselect if already selected
                                else:
                                    selected_item_index = index  # Select the clicked item
                                break

                    bottle_to_remove = False
            # Ensure NPC handles events when interacting
            if npc.interacting:
                npc.handle_event(event, player_x, player_y)

        if not loading_screen.is_active() and not game_over.is_game_over:
            # Update player position based on input
            player_x += dx
            player_y += dy

            # Check if player has reached the top of the screen
            if player_y < 0 and (player_x < background_img1.get_width() + background_img2.get_width()):
                player_y = 0  # Prevent player from moving above the top edge
                floating_text.show_text("Can't leave yet", font_size=20)

        if not loading_screen.is_active():
                status_bars.update(dt)


        #Overlay images  
        # Check for mouse hover over overlay
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] + camera_x, mouse_pos[1] + camera_y)
        if overlay_pos and nowhite_image.get_rect(topleft=overlay_pos).collidepoint(adjusted_mouse_pos):
            current_overlay_image = yeswhite_image
            is_hovering = True
        else:
            current_overlay_image = nowhite_image
            is_hovering = False


        if overlay_pos2 and tree_image.get_rect(topleft=overlay_pos2).collidepoint(adjusted_mouse_pos):
            current_overlay_image2 = treewhite_image
            is_hovering2 = True
        else:
            current_overlay_image2 = tree_image
            is_hovering2 = False



        if overlay_pos3 and boxes_image.get_rect(topleft=overlay_pos3).collidepoint(adjusted_mouse_pos):
            current_overlay_image3 = boxeswhite_image
            is_hovering3 = True
        else:
            current_overlay_image3 = boxes_image
            is_hovering3 = False


        if overlay_pos4 and current_overlay_image4:  # Ensure current_overlay_image4 is not None
            if current_overlay_image4.get_rect(topleft=overlay_pos4).collidepoint(adjusted_mouse_pos):
                current_overlay_image4 = botwhite_image
                is_hovering4 = True
            else:
                current_overlay_image4 = bot_image
                is_hovering4 = False




        keys = pygame.key.get_pressed()
        
        dx, dy = 0, 0

        if not chatbox.is_active():
            player_state = 'idle'
            dx, dy = 0, 0
            if keys[pygame.K_a]:
                dx -= move_speed * dt * 60
                player_state = 'run'
                player_direction = 'left'
            if keys[pygame.K_d]:
                dx += move_speed * dt * 60
                player_state = 'run'
                player_direction = 'right'
            if keys[pygame.K_w]:
                dy -= move_speed * dt * 60
            if keys[pygame.K_s]:
                dy += move_speed * dt * 60

            if show_key_image and (dx != 0 or dy != 0):
                show_key_image = False

            distance_to_npc = math.sqrt((player_x - npc.x)**2 + (player_y - npc.y)**2)
            if distance_to_npc > npc.detection_radius and npc.interacting:
                npc.end_interaction()
                chatbox.hide()

            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            if not check_collision(player_rect, dx, 0):
                player_x += dx
            else:
                dx = 0  # Stop horizontal movement if colliding

            if not check_collision(player_rect, 0, dy):
                player_y += dy
            else:
                dy = 0  # Stop vertical movement if colliding

            if is_jumping:
                if jump_count >= -10:
                    jump_dy = (jump_count * abs(jump_count)) * 0.5
                    if not check_collision(player_rect, 0, -jump_dy):
                        player_y -= jump_dy
                    jump_count -= 1
                else:
                    jump_count = 10
                    is_jumping = False

            player_x = max(0, min(player_x, total_width - 1))
            player_y = max(0, min(player_y, total_height - 1))

            target_camera_x = player_x - WINDOWWIDTH // 2
            target_camera_y = player_y - WINDOWHEIGHT // 2
            camera_x += (target_camera_x - camera_x) * camera_smoothing
            camera_y += (target_camera_y - camera_y) * camera_smoothing
            camera_x = max(0, min(camera_x, total_width - WINDOWWIDTH))
            camera_y = max(0, min(camera_y, total_height - WINDOWHEIGHT))

            if player_state == 'run':
                if not is_walking_sound_playing:
                    walking_sound.play(loops=-1)  # Play sound in loop
                    is_walking_sound_playing = True
            else:
                if is_walking_sound_playing:
                    walking_sound.stop()  # Stop sound if not running
                    is_walking_sound_playing = False


            # Update player animation
            current_time = pygame.time.get_ticks()
            if current_time - last_update >= animation_cooldown:
                if player_state == 'idle':
                    current_sprite = (current_sprite + 1) % len(idle_sprites)
                elif player_state == 'run':
                    current_sprite = (current_sprite + 1) % len(run_sprites)
                elif player_state == 'jump':
                    current_sprite = 0  # Assuming jump is a single frame
                last_update = current_time


        # Update NPC
        npc.update(dt, player_x, player_y)
        npc3.update(dt, player_x, player_y)
        npc4.update(dt, player_x, player_y)
        npc5.update(dt, player_x, player_y)

        npc2.update(dt, player_x, player_y)


        if npc.toolbar_items:
            new_item = npc.toolbar_items.pop()
            if isinstance(new_item, dict):
                # If new_item is already a dictionary, use it directly
                toolbar_items.append(new_item)
            elif hasattr(new_item, 'get_rect'):
                # If new_item is a Pygame surface
                new_item_rect = new_item.get_rect()
                toolbar_items.append({'image': new_item, 'rect': new_item_rect, 'id': bottle_id})
            else:
                print(f"Unexpected item type in npc.toolbar_items: {type(new_item)}")


        # Render game objects
                
        
        visible_bg = combined_background.subsurface((int(camera_x), int(camera_y), WINDOWWIDTH, WINDOWHEIGHT))
        

        screen.blit(visible_bg, (0, 0))
        
        not_ui_elements.render_overlay2(screen, current_overlay_image2, overlay_pos2, camera_x, camera_y)

        ui_elements.render_overlay(screen, current_overlay_image, overlay_pos, camera_x, camera_y)
        ui_elements2.render_overlay3(screen, current_overlay_image3, overlay_pos3, camera_x, camera_y)
        ui_elements3.render_overlay4(screen, current_overlay_image4, overlay_pos4, camera_x, camera_y)


        update_and_draw_raindrops(screen)
        if show_key_image:
            key_image_x = player_x + PLAYER_WIDTH // 2 - key_image.get_width() // 2
            key_image_y = player_y - key_image.get_height() - 10  # 10 pixels above the player's head
            screen.blit(key_image, (key_image_x - camera_x, key_image_y - camera_y))


        points_text = font.render(f"Environment Points: {environment_points} / 15", True, (201, 200, 170))
    # Get the rectangle of the rendered text
        points_text_rect = points_text.get_rect()


        # Set the position of the text (adjust these values as needed)
        points_text_rect.topleft = (500, 20)  # 20 pixels from the left, 20 pixels from the top

        # Blit the text onto the screen
        screen.blit(points_text, points_text_rect)

        # Render toolbar items
        toolbar_start_x = (WINDOWWIDTH - (len(toolbar_items) * (64 + 10) - 10)) // 2  # Center the toolbar
        for index, item in enumerate(toolbar_items):
            item_slot = pygame.Rect(
                toolbar_start_x + index * (item['rect'].width + 10),
                WINDOWHEIGHT - item['rect'].height - 10,
                item['rect'].width,
                item['rect'].height
            )
            ui_elements.render_toolbar(screen, item['image'], item_slot, index == selected_item_index)


        if selected_item_index is not None:
            selected_item = toolbar_items[selected_item_index]
            outline_rect = pygame.Rect(
                toolbar_start_x + selected_item_index * (selected_item['rect'].width + 10),
                WINDOWHEIGHT - selected_item['rect'].height - 10,
                selected_item['rect'].width,
                selected_item['rect'].height
            )
            pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)


        # Render player
        if player_state == 'idle' and idle_sprites:
            current_image = idle_sprites[current_sprite % len(idle_sprites)]
        elif player_state == 'run' and run_sprites:
            current_image = run_sprites[current_sprite % len(run_sprites)]
        elif player_state == 'jump' and jump_sprites:
            current_image = jump_sprites[0]
        else:
            # Fallback to a default image if no sprites are available
            current_image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            current_image.fill((255, 0, 0))  # Fill with red color as a placeholder

        if player_direction == 'left':
            current_image = pygame.transform.flip(current_image, True, False)

        # Draw the shadow
        SHADOW_COLOR = (39, 41, 29)
        shadow_height = 20
        shadow_offset_y = 5  # New variable to control how much lower the shadow appears
        shadow_offset_x = 2  # New variable to control how much to the left the shadow appears
        shadow_rect = pygame.Rect(
            player_x - camera_x - shadow_offset_x, 
            player_y - camera_y + current_image.get_height() - shadow_height + shadow_offset_y, 
            current_image.get_width(), 
            shadow_height
        )
        pygame.draw.ellipse(screen, SHADOW_COLOR, shadow_rect)

        # Draw the player sprite
        screen.blit(current_image, (player_x - camera_x, player_y - camera_y))

        # Draw the player sprite
        screen.blit(current_image, (player_x - camera_x, player_y - camera_y))
        
        # Render NPC
        npc.render(screen, camera_x, camera_y)
        
        

        # Render overlay image if it has been placed
 
        #here

        is_insect_bite = status_bars.update(dt)
        if is_insect_bite:
            current_time = time.time() - start_time
            print(f"Insect bite at {current_time:.2f} seconds")
            floating_text.show_text("Insect bite!", font_size=20)
            status_bars.apply_insect_bite()
        

        #updated floating text
        floating_text.update(dt)
        yellow_text.update(dt)
        red_text.update(dt)

        npc2.draw( screen, camera_x, camera_y)
        npc3.draw( screen, camera_x, camera_y)
        npc4.draw( screen, camera_x, camera_y)
        npc5.draw( screen, camera_x, camera_y)




        #After drawing the player but before the UI elements
        floating_text.draw(screen, player_x, player_y, camera_x, camera_y)
        yellow_text.draw(screen, player_x, player_y, camera_x, camera_y)
        red_text.draw(screen, player_x, player_y, camera_x, camera_y)
        bottom_text.update()
        bottom_text.draw()



        # Inside the main game loop
        chat_bubble_manager.update(dt)
        chat_bubble_manager.draw(screen, {npc3.id: (npc3.x, npc3.y)}, camera_x, camera_y)






        # After drawing the player and NPC, but before the chatbox
        entities = {'player': (player_x, player_y), 'npc': (npc.x, npc.y)}
        
        chat_bubble_manager.draw(screen, entities, camera_x, camera_y)


        # Render chat box
        chatbox.render(screen)


        status_bars.draw(screen)
        
        if black_screen.is_active():
            black_screen.draw()
        elif loading_screen.is_active():
            loading_screen.draw()
        if game_over.is_game_over:
            print(f"Game over state: {game_over.is_game_over}, Reason: {game_over.game_over_reason}")
            game_over.draw(screen)


        pygame.display.update()

# Save chat messages before quitting
chatbox.save_messages()

pygame.quit()
sys.exit()
