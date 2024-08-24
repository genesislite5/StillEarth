import pygame
import sys
import time
import os

class BlackScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        font_path = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
        self.font = pygame.font.Font(font_path, 27)
        self.message = "Press 'n' to continue or SPACE to skip"
        self.message_render = self.font.render(self.message, True, (255, 255, 255))
        self.message_rect = self.message_render.get_rect(center=(self.width // 2, self.height - 20))
        self.show_black_screen = True
        self.texts = [
            "The once-thriving forest, your home, is in danger.",
            "You take on the role of a bunny trying to save your forest...",
            "that is under threat from climate change.",
            "It’s up to you to make choices that will preserve the environment...",
            "while taking care of your own needs..",
            "HUNGER",
            "THIRST",
            "COMFORT", 
            "and ENERGY.",
            "Achieve a maximum of FIFTEEN environmental points",
            "..without falling below 0",
            "Can you find a way to live comfortably..",
            "without harming the environment?",
            "It’s time to find out.",
            "Every choice you make affects the Earth.",
            "StillEarth"
        ]
        self.current_text_index = 0
        self.current_text = ""
        self.char_index = 0
        self.last_char_time = time.time()
        self.typing_speed = 0.05  # Time between each character

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.show_black_screen = False
            elif event.key == pygame.K_n:
                if self.current_text_index < len(self.texts) - 1:
                    self.current_text_index += 1
                    self.current_text = ""
                    self.char_index = 0
                else:
                    self.show_black_screen = False

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.current_text_index < len(self.texts):
            current_time = time.time()
            if current_time - self.last_char_time >= self.typing_speed:
                if self.char_index < len(self.texts[self.current_text_index]):
                    self.current_text += self.texts[self.current_text_index][self.char_index]
                    self.char_index += 1
                    self.last_char_time = current_time

            # Render the glow effect
            glow_color = (190, 170, 56, 64)  # RGBA with transparency
            glow_render = self.font.render(self.current_text, True, glow_color)
            glow_rect = glow_render.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(glow_render, glow_rect.move(2, 2))  # Slight offset for the glow

            # Render the actual text
            text_render = self.font.render(self.current_text, True, (255, 255, 255))
            text_rect = text_render.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text_render, text_rect)

        self.screen.blit(self.message_render, self.message_rect)

    def is_active(self):
        return self.show_black_screen

