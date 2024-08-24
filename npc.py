import pygame
import random
import math
import os
import google.generativeai as genai
from settings import TEST2_WIDTH, TEST2_HEIGHT
from chatbox import ChatBox
from config import GEMINI_API_KEY
from ui_elements import add_item_to_toolbar
import requests
from PIL import Image, ImageEnhance
from io import BytesIO
import time
import threading 
from status_bars import StatusBars
import threading
from functools import partial
from globals import environment_points
from globals2 import is_environmentally_friendly
import re
import json
from settings import collision_boxes
from utils import check_collision





with open('config.json', 'r') as file:
    config = json.load(file)

CUSTOM_SEARCH_API_KEY = config.get('CUSTOM_SEARCH_API_KEY')
CUSTOM_SEARCH_ENGINE_ID = config.get('CUSTOM_SEARCH_ENGINE_ID')

second_api_key = config.get('SECOND_API_KEY')


def sanitize_text(text):
    """Remove special characters and numbers from the text."""
    return re.sub(r'[^a-zA-Z\s]', '', text)

class NPC:
    def __init__(self, x, y, interaction_range=100):
        self.x = float(x)
        self.y = float(y)
        self.width = 72
        self.height = 108
        self.move_speed = 1.0
        self.follow_speed = 4.0
        self.state = 'idle'
        self.direction = 'right'
        self.current_sprite = 0
        self.move_timer = 0
        self.move_duration = 2000
        self.detection_radius = 100
        self.face_player = False
        self.face_player_timer = 0
        self.should_face_player = False
        self.should_face_player_timer = 0
        self.should_follow_player = False
        self.stop_distance = 50
        self.idle_sprites = self.load_sprites('NPC/idle', self.width, self.height)
        self.run_sprites = self.load_sprites('NPC/run', self.width, self.height)
        self.jump_sprites = self.load_sprites('NPC/jump', self.width, self.height)
        self.x_button = pygame.image.load('misc/button4.png').convert_alpha()
        self.show_x_button = False
        self.chatbox = ChatBox(self.width, self.height)
        self.interacting = False
        self.toolbar_items = []
        self.game = None  
        self.interaction_range = interaction_range  # Initialize interaction_range
        self.last_api_call_time = 0
        self.api_call_cooldown = 0.1  # 10 seconds cooldown between API 
        self.chat_history = []
        self.load_chat_history()




        # Initialize Gemini API
        api_key = GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it and try again.")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("Gemini API configured successfully.")
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")


    def generate_explanation(self, item_id):
        try:
            genai.configure(api_key=second_api_key)  
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            return "Unable to configure API."

        current_time = time.time()
        if self.last_api_call_time != 0 and (current_time - self.last_api_call_time < self.api_call_cooldown):
            return "Please wait before requesting another explanation."

        self.last_api_call_time = current_time

        # Determine the environmental status
        is_eco_friendly = is_environmentally_friendly(item_id)
        eco_status = "eco-friendly" if is_eco_friendly else "not eco-friendly"

        # Ensure the prompt directs the AI to provide a focused explanation
        prompt = (f"Explain in one sentence why the item '{item_id}' is {eco_status}. "
                f"Do not discuss the opposite status or any other unrelated factors. "
                f"Provide a direct reason why it is considered {eco_status}.")

        try:
            response = model.generate_content(prompt)
            explanation = response.text.strip()

            # Ensure the explanation is concise and adheres to the eco-status
            if not explanation:
                explanation = f"The item '{item_id}' is considered {eco_status} due to factors such as its environmental impact or sustainability practices."

            # Make sure explanation does not contradict the eco_status
            if "not eco-friendly" in explanation and is_eco_friendly:
                explanation = f"The item '{item_id}' is considered {eco_status} due to its positive environmental impact or sustainable practices."
            elif "eco-friendly" in explanation and not is_eco_friendly:
                explanation = f"The item '{item_id}' is considered {eco_status} due to its adverse environmental impact or unsustainable practices."

            # Sanitize the explanation
            explanation = sanitize_text(explanation)

            # Limit the length of the explanation
            if len(explanation) > 350:
                explanation = explanation[:350]
                last_space_idx = explanation.rfind(' ')
                if last_space_idx != -1:
                    explanation = explanation[:last_space_idx] + '.'

            return explanation
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return "Unable to generate explanation at this time."


    # Has safety feuatures for image content filtering
    def search_and_add_item(self, query):
        current_time = time.time()
        if current_time - self.last_api_call_time < self.api_call_cooldown:
            print("API call cooldown in effect. Please wait.")
            return

        url = f'https://www.googleapis.com/customsearch/v1?key={CUSTOM_SEARCH_API_KEY}&cx={CUSTOM_SEARCH_ENGINE_ID}&q={query}+pixel+art&searchType=image'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            results = response.json()
            
            if 'items' in results and len(results['items']) > 0:
                image_url = results['items'][0]['link']
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                image = Image.open(BytesIO(image_response.content)).convert("RGBA")
                image = image.resize((64, 64))  # Resize to match other toolbar items
                
                # Make the image transparent
                alpha = image.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
                image.putalpha(alpha)
                
                # Convert PIL Image to Pygame Surface
                mode = image.mode
                size = image.size
                data = image.tobytes()
                py_image = pygame.image.fromstring(data, size, mode).convert_alpha()
                
                # Add to toolbar
                item_rect = py_image.get_rect()
                self.toolbar_items.append({'image': py_image, 'rect': item_rect, 'id': query})
                print(f"Added {query} to the toolbar")
                
                self.last_api_call_time = current_time

                # Get item effects from AI
                self.get_item_effects_from_ai(query, self.apply_item_effects)
            else:
                print(f"No image results found for {query}")
        except Exception as e:
            print(f"Error searching for image: {e}")


    def is_near_player(self, player_x, player_y):
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        return distance <= self.interaction_range
    
    def load_sprites(self, path, width, height):
        sprites = []
        try:
            for file_name in sorted(os.listdir(path)):
                if file_name.endswith('.png'):
                    image = pygame.image.load(os.path.join(path, file_name)).convert_alpha()
                    image = pygame.transform.scale(image, (width, height))
                    sprites.append(image)
        except FileNotFoundError:
            print(f"Warning: Sprite directory '{path}' not found.")
        except pygame.error as e:
            print(f"Error loading sprites from '{path}': {e}")
        return sprites if sprites else [pygame.Surface((width, height))]

    def update(self, dt, player_x, player_y):
        if self.interacting:
            self.state = 'idle'
            return

        self.move_timer += dt * 1000
        if self.move_timer >= self.move_duration and not self.face_player and not self.should_face_player and not self.should_follow_player:
            self.move_timer = 0
            self.direction = random.choice(['left', 'right', 'up', 'down', 'idle'])

        distance_to_player = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
        self.show_x_button = distance_to_player <= self.detection_radius

        if self.face_player or self.should_face_player or self.should_follow_player:
            dx = player_x - self.x
            dy = player_y - self.y
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

        if self.should_follow_player:
            self.move(dt, player_x, player_y)
        else:
            self.move(dt)

        self.update_animation(dt)

    def move(self, dt, player_x=None, player_y=None):
        dx, dy = 0, 0
        if self.should_follow_player and player_x is not None and player_y is not None:
            dx = player_x - self.x
            dy = player_y - self.y
            length = math.sqrt(dx**2 + dy**2)
            if length > self.stop_distance:
                dx /= length
                dy /= length
                self.state = 'run'
            else:
                self.state = 'idle'
                return
        elif self.direction == 'left':
            dx = -1
        elif self.direction == 'right':
            dx = 1
        elif self.direction == 'up':
            dy = -1
        elif self.direction == 'down':
            dy = 1
        else:
            self.state = 'idle'
            return

        speed = self.follow_speed if self.should_follow_player else self.move_speed
        dx *= speed * dt * 60
        dy *= speed * dt * 60

        # Check for collisions using the imported check_collision function
        npc_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not check_collision(npc_rect, dx, 0):
            self.x += dx
        if not check_collision(npc_rect, 0, dy):
            self.y += dy

        self.x = max(0, min(self.x, TEST2_WIDTH - self.width))
        self.y = max(0, min(self.y, TEST2_HEIGHT - self.height))

        self.state = 'run' if (dx != 0 or dy != 0) else 'idle'


    def check_collision(self, dx, dy):
        future_rect = pygame.Rect(self.x + dx, self.y + dy, self.width, self.height)
        for box in collision_boxes:
            if future_rect.colliderect(box):
                return True
        return False





    def update_animation(self, dt):
        animation_cooldown = 100
        current_time = pygame.time.get_ticks()
        if current_time - getattr(self, 'last_update', 0) >= animation_cooldown:
            if self.state == 'idle' and self.idle_sprites:
                self.current_sprite = (self.current_sprite + 1) % len(self.idle_sprites)
            elif self.state == 'run' and self.run_sprites:
                self.current_sprite = (self.current_sprite + 1) % len(self.run_sprites)
            self.last_update = current_time
        
    def render(self, screen, camera_x, camera_y):
        # Draw sprite
        if self.state == 'idle' and self.idle_sprites:
            current_image = self.idle_sprites[self.current_sprite % len(self.idle_sprites)]
        elif self.state == 'run' and self.run_sprites:
            current_image = self.run_sprites[self.current_sprite % len(self.run_sprites)]
        else:
            current_image = pygame.Surface((self.width, self.height))

        if self.direction == 'left':
            current_image = pygame.transform.flip(current_image, True, False)

        screen.blit(current_image, (int(self.x - camera_x), int(self.y - camera_y)))

        # Draw rounded rectangle
        if self.show_x_button:
            button_rect = pygame.Rect(0, 0, 100, 50)  # Size of the button
            button_color = (0, 0, 0, 165)  # More transparent black
            offset_x = 40
            offset_y = -25
            rect_x = int(self.x - camera_x - 50 + offset_x)
            rect_y = int(self.y - camera_y - 40 + offset_y)
            
            # Create a surface with per-pixel alpha for the button
            rect_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)
            rect_surface.fill((0, 0, 0, 0))  # Transparent background
            pygame.draw.rect(rect_surface, button_color, button_rect, border_radius=20)
            
            # Blit the surface onto the main screen
            screen.blit(rect_surface, (rect_x, rect_y))

            # Draw smaller circle with increased transparency
            circle_surface = pygame.Surface((35, 35), pygame.SRCALPHA)  # Smaller surface for the circle
            circle_color = (255, 255, 255, 120)  # More transparent white
            circle_center = (17, 17)  # Center of the circle on the circle_surface
            pygame.draw.circle(circle_surface, circle_color, circle_center, 15)  # Smaller radius
            
            # Blit the circle_surface onto the main screen
            screen.blit(circle_surface, (rect_x + 10, rect_y + button_rect.height // 2 - 17))  # Adjusted position

            # Draw text "e" inside the circle in white
            font_size = 40  # Font size to match smaller circle
            font = pygame.font.Font(None, font_size)
            text_surface = font.render("e", True, (255, 255, 255))  # White color
            text_rect = text_surface.get_rect(center=circle_center)  # Center text in the circle
            circle_surface.blit(text_surface, text_rect)
            
            # Blit the circle_surface with text onto the main screen
            screen.blit(circle_surface, (rect_x + 10, rect_y + button_rect.height // 2 - 17))  # Adjusted position

            # Draw "Chat" text (moved right by 20 pixels)
            chat_font = pygame.font.Font(None, 25)
            chat_surface = chat_font.render("Chat", True, (255, 255, 255))
            screen.blit(chat_surface, (rect_x + 60 + 10 - 20, rect_y + button_rect.height // 2 - 10))  # Moved 20 pixels to the right
            
        # Draw chatbox if interacting
        if self.interacting:
            self.chatbox.render(screen)




    def interact(self, player_x, player_y):
        if self.show_x_button and not self.interacting:
            self.interacting = True
            self.face_player = True
            self.face_player_timer = 0
            self.should_face_player = True
            self.should_face_player_timer = pygame.time.get_ticks()
            dx = player_x - self.x
            dy = player_y - self.y
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            self.state = 'idle'
            self.chatbox.show()

    def end_interaction(self):
        self.interacting = False
        if self.chatbox:
            self.chatbox.save_messages()
            self.chatbox.hide()
        self.should_follow_player = False
        self.should_face_player = False
        self.face_player = False
        self.direction = random.choice(['left', 'right', 'up', 'down', 'idle'])
        self.state = 'idle'


    def say(self, message):
        if self.game and hasattr(self.game, 'chat_bubble_manager'):
            # Pass the NPC's position (self.x, self.y) as the third argument
            self.game.chat_bubble_manager.add_bubble('npc', message, (self.x, self.y))
        
        if self.chatbox:
            self.chatbox.add_message(f"Gaia: {message}")

    def get_item_effects_from_ai(self, item_name, status_bars, yellow_text, red_text):
        def fetch_effects():
            prompt = f"""Determine the effects of the item '{item_name}' on the following status bars: COMFORT, THIRST, ENERGY, HUNGER. 
            Provide the effects in the format: COMFORT:+1, THIRST:-1, ENERGY:0, HUNGER:+2. 
            Base your decision on the item's properties and how it might realistically affect a person in a forest setting."""
            
            try:
                response = self.model.generate_content(prompt)
                print(f"AI Response for item effects: {response.text}")  # Debug print
                effects = self.parse_item_effects(response.text)
                callback(effects)  # Call the callback with the effects
            except Exception as e:
                print(f"Error fetching item effects from AI: {e}")
                callback({})  # Call the callback with an empty dict if there's an error

        callback = partial(self.apply_item_effects, status_bars, yellow_text, red_text, item_name)
        thread = threading.Thread(target=fetch_effects)
        thread.start()

    def parse_item_effects(self, response):
        effects = {}
        lines = response.split(',')
        for line in lines:
            parts = line.split(':')
            if len(parts) >= 2 and parts[0].strip() in ['COMFORT', 'THIRST', 'ENERGY', 'HUNGER']:
                status = parts[0].strip()
                try:
                    value = int(parts[1].strip())
                    # Ensure the value is not below 5
                    if value < 5:
                        value = 5
                    effects[status] = value
                except ValueError:
                    print(f"Invalid value for {status}: {parts[1]}")
        print(f"Parsed effects: {effects}")  # Debug print
        return effects

    def ai_interact(self, player_input):
        self.chat_history.append(f"Player: {player_input}")
        self.save_chat_history()

        context = " ".join(self.chat_history[-20:])  
        prompt = f"""
        You are Gaia, an older bunny living in the forest. You have a deep understanding of this place and its challenges. The forest has seen better days, and everyone feels the effects. Speak casually and naturally, sharing your knowledge based on your daily life and observations. The player has just said: "{player_input}"

        Respond to the player in a friendly, relaxed manner. Pay close attention to the context and the player's needs.

        Key instructions:
        1. Interpret the player's wishes carefully:
        - For explicit requests or strong hints about items or actions, always suggest the appropriate action.
        - For follow requests: suggest 'follow_player' action.
        - For requests to stop following or be alone: suggest 'stop_following' action.
        - If thirst is mentioned or implied: suggest 'give_water' action.
        - If hunger is mentioned or implied: suggest 'give_meat' action.
        - If discomfort from insects is mentioned or implied: suggest 'give_spray' action.
        - If tiredness or low energy is mentioned or implied:
            - For mild tiredness: suggest 'give_energy_drink' action.
            - For extreme tiredness: suggest 'give_coffee' action.
        - For any other item request or hint: suggest 'search_item' action with the item name.
        - Use context clues to understand implied needs (e.g., 'wood log' for 'starting a fire').

        2. Maintain natural conversation:
        - Vary your responses and avoid repetition.
        - Use different phrases and sentence structures.
        - Include environmental topics and nature facts when relevant.
        - Adjust your tone based on the conversation context.

        3. Format your response as:
        Response: [Your unique, context-appropriate dialogue]
        Action: [Suggested action or 'None' if no action is needed]
        Item: [Item name if 'search_item' action is suggested, else 'None']

        4. Keep responses concise (no more than three sentences).

        5. Show contextual awareness:
        - Recognize shared challenges in the forest environment.
        - Subtly reference the forest's changing state.

        6. Express emotion:
        - Show concern for the forest and empathy for the player.

        7. Only suggest following if the player explicitly asks.

        Recent interactions: {context}
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Truncate response if it exceeds 200 characters
            if len(response_text) > 200:
                response_text = response_text[:200] + "..."

            print(f"API Response: {response_text}")
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Sorry, I couldn't process that request."

        dialogue, action, item = self.parse_ai_response(response_text)
        print(f"Dialogue: {dialogue}")
        print(f"Action: {action}")
        print(f"Item: {item}")

        self.say(dialogue)
        self.perform_action(action, item)

        # Update the chat history with NPC's response
        self.chat_history.append(f"NPC: {dialogue}")
        self.save_chat_history()

        return f"NPC: {dialogue}"

    def parse_ai_response(self, response):
        parts = response.split('Response:')
        if len(parts) > 1:
            dialogue = parts[1].split('Action:')[0].strip()
        else:
            dialogue = response.strip()
        
        action = 'None'
        item = 'None'
        
        if 'Action:' in response:
            action_part = response.split('Action:')[1]
            if 'Item:' in action_part:
                action = action_part.split('Item:')[0].strip()
                item = action_part.split('Item:')[1].strip()
            else:
                action = action_part.strip()

        # Ensure item is a noun
        if item and not item.isdigit():
            item = item.split()[-1]  # Take the last word as the item name
        
        return dialogue, action, item


    def load_chat_history(self, filename='chat_history.json'):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    self.chat_history = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"An error occurred while loading chat history: {e}")
        else:
            print(f"No chat history file found at {filename}")

    def save_chat_history(self, filename='chat_history.json'):
        try:
            with open(filename, 'w') as f:
                json.dump(self.chat_history, f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"An error occurred while saving chat history: {e}")

    def perform_action(self, action, item=None):
        if action == "follow_player":
            self.follow_player()
        elif action == "stop_following":
            self.stop_following()
        elif action == "search_item" and item:
            if not any(existing_item['id'] == item for existing_item in self.toolbar_items):
                self.search_and_add_item(item)
        elif action == "give_water":
            self.give_water()
        elif action == "give_meat":
            self.give_meat()
        elif action == "give_spray":
            self.give_spray()
        elif action == "give_energy_drink":
            self.give_energy_drink()
        elif action == "give_coffee":
            self.give_coffee()

    
    def apply_item_effects(self, status_bars, yellow_text, red_text, item_id, effects):
        print(f"Applying effects for {item_id}: {effects}")  # Debug print
        for status, value in effects.items():
            if status in ['COMFORT', 'THIRST', 'ENERGY', 'HUNGER']:
                status_bars.modify_bar(status, value)
                if value > 0:
                    yellow_text.show_text(f"+{value} {status}", font_size=20)
                elif value < 0:
                    red_text.show_text(f"{value} {status}", font_size=20)

    def follow_player(self):
        self.interacting = False
        self.chatbox.hide()
        self.state = 'run'
        self.should_face_player = True
        self.should_follow_player = True
        self.move_timer = 0
        self.move_duration = 10000  # Follow for 10 seconds

    def give_water(self):
        bottle_image = pygame.image.load('data/images/bottle.png').convert_alpha()
        bottle_image = pygame.transform.scale(bottle_image, (64, 64))  # Resize if needed
        bottle_rect = bottle_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': bottle_image, 'rect': bottle_rect, 'id': 'bottle'})
        print("Added bottle of water to the toolbar")

    def give_meat(self):
        meat_image = pygame.image.load('data/images/meat.png').convert_alpha()
        meat_image = pygame.transform.scale(meat_image, (64, 64))  # Resize if needed
        meat_rect = meat_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': meat_image, 'rect': meat_rect, 'id': 'meat'})
        print("Added meat to the toolbar")

    def give_spray(self):
        spray_image = pygame.image.load('data/images/bug_spray.png').convert_alpha()
        spray_image = pygame.transform.scale(spray_image, (64, 64))  # Resize if needed
        spray_rect = spray_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': spray_image, 'rect': spray_rect, 'id': 'spray'})
        print("Added bug spray to the toolbar")

    def give_spray(self):
        spray_image = pygame.image.load('data/images/bug_spray.png').convert_alpha()
        spray_image = pygame.transform.scale(spray_image, (64, 64))  # Resize if needed
        spray_rect = spray_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': spray_image, 'rect': spray_rect, 'id': 'spray'})
        print("Added bug spray to the toolbar")

    def give_energy_drink(self):
        spray_image = pygame.image.load('data/images/energy_drink.png').convert_alpha()
        spray_image = pygame.transform.scale(spray_image, (64, 64))  # Resize if needed
        spray_rect = spray_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': spray_image, 'rect': spray_rect, 'id': 'spray'})
        print("Added bug spray to the toolbar")
    
    def give_coffee(self):
        spray_image = pygame.image.load('data/images/coffee.png').convert_alpha()
        spray_image = pygame.transform.scale(spray_image, (64, 64))  # Resize if needed
        spray_rect = spray_image.get_rect()  # Get rect for collision or positioning
        self.toolbar_items.append({'image': spray_image, 'rect': spray_rect, 'id': 'spray'})
        print("Added bug spray to the toolbar")


    def stop_following(self):
        self.should_follow_player = False
        self.state = 'idle'
        self.move_timer = 0
        self.move_duration = 2000  # Reset to normal movement duration
        self.should_face_player = False
        self.face_player = False
        self.direction = random.choice(['left', 'right', 'up', 'down', 'idle'])
        self.interacting = False
        if self.chatbox:
            self.chatbox.hide()

    def handle_event(self, event, player_x, player_y):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                chatbox_rect = self.chatbox.rect  # Assuming chatbox has a rect attribute defining its area
                if not chatbox_rect.collidepoint(mouse_x, mouse_y):
                    self.end_interaction()  # Close chatbox if clicked outside
