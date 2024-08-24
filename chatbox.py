import pygame
import json
import os
import threading

class ChatBox:
    def __init__(self, width, height, font_size=17, npc=None, game=None):
        self.rect = pygame.Rect(10, 50, width, 37)
        font_path = os.path.join("fonts", "Source_Sans_3", "SourceSans3-Medium.ttf")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found at {font_path}")
        self.font = pygame.font.Font(font_path, font_size)
        self.messages = []
        self.message_history = []
        self.input_text = ""
        self.visible = False
        self.active = False
        self.text_color = (255, 255, 255)
        self.background_color = (30, 30, 30, 80)
        self.input_rect = self.rect
        self.npc = npc
        self.game = game
        self.placeholder_text = "Type to send a message"
        self.placeholder_color = (200, 200, 200)
        self.load_messages()

    def is_active(self):
        return self.active and self.visible

    def show(self):
        self.visible = True
        self.active = True

    def hide(self):
        self.visible = False
        self.active = False
        self.save_messages()

    def clear(self):
        self.messages.clear()
        self.message_history.clear()
        self.input_text = ""
        self.save_messages()

    def set_text(self, text):
        self.clear()
        self.add_message(text)
        self.save_messages()

    def handle_event(self, event):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.input_text:
                    self.add_message(f"You: {self.input_text}")
                    if self.npc and hasattr(self.npc, 'ai_interact'):
                        threading.Thread(target=self.handle_npc_interaction, args=(self.input_text,)).start()
                    message = self.input_text
                    self.input_text = ""
                    self.save_messages()
                    return message
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if self.font.size(self.input_text + event.unicode)[0] < self.input_rect.width - 10:
                    self.input_text += event.unicode
        return None

    def handle_npc_interaction(self, input_text):
        ai_response = self.npc.ai_interact(input_text)
        self.add_message(f"NPC: {ai_response}")

    def render(self, surface):
        if not self.visible:
            return
        
        input_surface = pygame.Surface((self.input_rect.width, self.input_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(input_surface, self.background_color, input_surface.get_rect())
        pygame.draw.rect(input_surface, (30, 30, 30, 50), input_surface.get_rect(), 2)
        
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.text_color)
        else:
            text_surface = self.font.render(self.placeholder_text, True, self.placeholder_color)
        
        input_surface.blit(text_surface, (5, 5))
        surface.blit(input_surface, self.input_rect)

    def add_message(self, message):
        self.message_history.append(message)
        self.save_messages()

    def save_messages(self, filename='chat_history.json'):
        try:
            with open(filename, 'w') as f:
                json.dump(self.message_history, f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"An error occurred while saving messages: {e}")

    def load_messages(self, filename='chat_history.json'):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    self.message_history = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"An error occurred while loading messages: {e}")
        else:
            print(f"No chat history file found at {filename}")