import pygame
import os
import random

class LoadingScreen:
    def __init__(self, screen, width, height, duration=1000, scale_factor=0.8):
        self.screen = screen
        self.width = width
        self.height = height
        self.show_loading_screen = True
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.was_active = True

        # Load and scale the image
        self.image = pygame.image.load("/Users/toneanmorgan/Downloads/head.png")
        original_width, original_height = self.image.get_size()
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.image_rect = self.image.get_rect(center=(self.width // 2, self.height // 2))

        # Load fonts
        custom_font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        pixelify_font_path = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
        self.custom_font = pygame.font.Font(custom_font_path, 48)
        self.smaller_font = pygame.font.Font(pixelify_font_path, 24)
        self.press_key_font = pygame.font.Font(pixelify_font_path, 28)

        # Render "StillEarth" text
        self.stillearth_text = self.custom_font.render("StillEarth", True, (190, 170, 56))
        self.stillearth_rect = self.stillearth_text.get_rect(center=(self.width // 2, self.image_rect.bottom - 270))
        self.stillearth_rect.x -= 20

        # Typing animation variables
        self.typing_speed1 = 100
        self.typing_speed2 = 100
        self.current_text1 = ""
        self.current_text2 = ""
        self.next_char_time1 = 0
        self.next_char_time2 = 0
        self.full_text1 = "After all"
        self.full_text2 = "it's still Earth."
        self.typing_finished = False

        # "Press any key to continue" text
        self.press_key_text = "Press any key to continue"
        self.press_key_render = self.press_key_font.render(self.press_key_text, True, (255, 255, 255))
        self.press_key_rect = self.press_key_render.get_rect(center=(self.width // 2, self.height - 50))
        self.press_key_rect.x += 1

        # Blinking animation variables
        self.blink_interval = 500
        self.last_blink_time = pygame.time.get_ticks()
        self.show_press_key = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.show_loading_screen = False

    def update_typing_animation(self):
        current_time = pygame.time.get_ticks()

        # Update first line of text
        if len(self.current_text1) < len(self.full_text1):
            if current_time >= self.next_char_time1:
                self.current_text1 = self.full_text1[:len(self.current_text1) + 1]
                self.next_char_time1 = current_time + self.typing_speed1
        elif len(self.current_text2) < len(self.full_text2):
            # Update second line of text
            if current_time >= self.next_char_time2:
                self.current_text2 = self.full_text2[:len(self.current_text2) + 1]
                self.next_char_time2 = current_time + self.typing_speed2
        else:
            # Typing animation finished
            self.typing_finished = True

    def draw(self):
        self.screen.fill((14, 18, 34))
        self.screen.blit(self.image, self.image_rect)
        self.screen.blit(self.stillearth_text, self.stillearth_rect)

        # Update and draw the typing animation
        self.update_typing_animation()
        text1_render = self.smaller_font.render(self.current_text1, True, (136, 144, 119))
        text1_rect = text1_render.get_rect(center=(self.width // 2, self.stillearth_rect.bottom + 20))
        text1_rect.x -= 20
        self.screen.blit(text1_render, text1_rect)

        text2_render = self.smaller_font.render(self.current_text2, True, (136, 144, 119))
        text2_rect = text2_render.get_rect(center=(self.width // 2, text1_rect.bottom + 20))
        self.screen.blit(text2_render, text2_rect)

        # Blinking animation for "Press any key to continue"
        if self.typing_finished:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time > self.blink_interval:
                self.show_press_key = not self.show_press_key
                self.last_blink_time = current_time

            if self.show_press_key:
                self.screen.blit(self.press_key_render, self.press_key_rect)

    def is_active(self):
        return self.show_loading_screen

    def has_just_ended(self):
        if self.was_active and not self.show_loading_screen:
            self.was_active = False
            return True
        self.was_active = self.show_loading_screen
        return False