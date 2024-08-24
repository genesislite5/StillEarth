import pygame
from pygame.locals import *
from PIL import Image
import os

class GamePaused:
    # Constants
    TEXT_COLOR = (255, 255, 255)  # White
    BUTTON_TEXT_COLOR = (255, 255, 255)  # White
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    BUTTON_RADIUS = 10  # Radius for rounded corners
    BORDER_COLOR = (189, 171, 56, 120)  # #bdab38
    BACKGROUND_COLOR = (0, 0, 0, 64)  

    def __init__(self, screen_width, screen_height, font_size=36):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_paused = False

        # Load custom font for "Paused" text
        font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        try:
            self.custom_font = pygame.font.Font(font_path, font_size)
        except pygame.error:
            print(f"Error loading font from {font_path}. Using default font.")
            self.custom_font = pygame.font.Font(None, font_size)

        # Load custom font for "Resume" button
        additional_font_path = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
        try:
            self.button_font = pygame.font.Font(additional_font_path, 30)  # Font for "Resume" button
        except pygame.error:
            print(f"Error loading font from {additional_font_path}. Using default font.")
            self.button_font = pygame.font.Font(None, 30)  # Font for "Resume" button

        # Default font for other text
        self.default_font = pygame.font.Font(None, font_size)

        self.button_x = self.screen_width // 2 - self.BUTTON_WIDTH // 2
        self.button_y = self.screen_height * 3 // 4  # Move the button lower on the screen
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

        self.gif = self.load_gif('data/images/head.gif')
        self.current_frame = 0
        self.frame_delay = 200  # Adjust this value to control animation speed
        self.last_update = pygame.time.get_ticks()

        # Typing animation for "Zzz..."
        self.typing_text = "Zzz..."
        self.typing_index = 0
        self.typing_delay = self.frame_delay  # Sync typing speed with GIF frame rate
        self.last_typing_update = pygame.time.get_ticks()

    def load_gif(self, filename):
        gif = Image.open(filename)
        frames = []
        try:
            while True:
                frame = gif.convert("RGBA")
                # Calculate new dimensions
                new_width = int(frame.width * 0.65)
                new_height = int(frame.height * 0.65)
                # Resize the frame
                frame = frame.resize((new_width, new_height), Image.LANCZOS)
                frame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                if frame_surface.get_alpha() != 0:  # Skip fully transparent frames
                    frames.append(frame_surface)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        return frames

    def draw(self, screen):
        if self.is_paused:
            print(f"Drawing paused screen.")
            self._draw_overlay(screen)
            self._draw_paused_text(screen)
            self._draw_resume_button(screen)
            self._draw_gif(screen)
            print(f"Paused screen drawn with overlay and GIF.")

    def _draw_overlay(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay_color = (53, 73, 60, 220)  # Single overlay color
        overlay.fill(overlay_color)
        screen.blit(overlay, (0, 0))

    def _draw_paused_text(self, screen):
        paused_text = self.custom_font.render("Paused", True, self.TEXT_COLOR)
        text_rect = paused_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        screen.blit(paused_text, text_rect)

    def _draw_resume_button(self, screen):
        button_surface = pygame.Surface((self.BUTTON_WIDTH, self.BUTTON_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, self.BACKGROUND_COLOR, button_surface.get_rect(), border_radius=self.BUTTON_RADIUS)
        screen.blit(button_surface, self.button_rect)
        
        resume_text = self.button_font.render("Resume", True, self.BUTTON_TEXT_COLOR)
        text_rect = resume_text.get_rect(center=self.button_rect.center)
        screen.blit(resume_text, text_rect)

    def _draw_gif(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.gif)
            self.last_update = now

        gif_frame = self.gif[self.current_frame]
        gif_rect = gif_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))  # Moved up by 50 pixels

        # Draw a smaller and more transparent black rectangle behind the GIF with a border
        background_rect = pygame.Rect(gif_rect.left + 70, gif_rect.top + 150, gif_rect.width - 200, gif_rect.height - 200)
        background_surface = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background_surface.fill(self.BACKGROUND_COLOR)
        
        # Draw the border
        pygame.draw.rect(background_surface, self.BORDER_COLOR, (0, 0, background_rect.width, background_rect.height), 2)
        
        screen.blit(background_surface, background_rect.topleft)
        screen.blit(gif_frame, gif_rect)

        # Typing animation for "Zzz..."
        if self.is_paused:
            if now - self.last_typing_update > self.typing_delay:
                self.typing_index = (self.typing_index + 1) % (len(self.typing_text) + 1)
                self.last_typing_update = now

            typing_text_surface = self.default_font.render(self.typing_text[:self.typing_index], True, self.TEXT_COLOR)
            # Move the text up and to the left
            typing_text_rect = typing_text_surface.get_rect(center=(gif_rect.centerx + 60, gif_rect.centery - 120))
            screen.blit(typing_text_surface, typing_text_rect)

    def handle_event(self, event):
        if self.is_paused and event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False

    def reset(self):
        self.is_paused = False
