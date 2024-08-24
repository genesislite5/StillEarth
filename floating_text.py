import pygame
import os

class FloatingText:
    def __init__(self):
        self.text = ""
        self.timer = 0
        self.display_time = 2  # Display time in seconds
        self.alpha = 0  # Transparency level (0-255)
        self.y_offset = 0  # Vertical offset for the floating effect

        # Define the path to the custom font
        self.font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        self.default_font_size = 18
        self.font = pygame.font.Font(self.font_path, self.default_font_size)  # Use the custom font with default size

    def show_text(self, text, font_size=None):
        self.text = text
        self.timer = self.display_time
        self.alpha = 0  # Start with fully transparent text
        self.y_offset = 0  # Start with no vertical offset

        # Set the font size if specified, otherwise use the default size
        if font_size:
            self.font = pygame.font.Font(self.font_path, font_size)
        else:
            self.font = pygame.font.Font(self.font_path, self.default_font_size)

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            if self.timer > self.display_time * 0.8:
                # Fade-in effect
                self.alpha = min(255, self.alpha + 255 * dt / (self.display_time * 0.2))
            elif self.timer < self.display_time * 0.2:
                # Fade-out effect
                self.alpha = max(0, self.alpha - 255 * dt / (self.display_time * 0.2))
            else:
                self.alpha = 255  # Fully opaque during the middle of the display time

            # Floating up effect
            self.y_offset -= 20 * dt  # Adjust the speed of floating up as needed

    def draw(self, screen, player_x, player_y, camera_x, camera_y):
        if self.timer > 0:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_surface.set_alpha(self.alpha)  # Set the transparency level
            text_rect = text_surface.get_rect()
            text_rect.centerx = player_x - camera_x + 30  # Moved 30 pixels to the right
            text_rect.bottom = player_y - camera_y - 10 + self.y_offset  # Floating up effect

            screen.blit(text_surface, text_rect)

class RedFloatingText:
    def __init__(self):
        self.text = ""
        self.timer = 0
        self.display_time = 2  # Display time in seconds
        self.alpha = 0  # Transparency level (0-255)
        self.y_offset = 0  # Vertical offset for the floating effect

        # Define the path to the custom font
        self.font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        self.default_font_size = 18
        self.font = pygame.font.Font(self.font_path, self.default_font_size)  # Use the custom font with default size

    def show_text(self, text, font_size=None):
        self.text = text
        self.timer = self.display_time
        self.alpha = 0  # Start with fully transparent text
        self.y_offset = 0  # Start with no vertical offset

        # Set the font size if specified, otherwise use the default size
        if font_size:
            self.font = pygame.font.Font(self.font_path, font_size)
        else:
            self.font = pygame.font.Font(self.font_path, self.default_font_size)

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            if self.timer > self.display_time * 0.8:
                # Fade-in effect
                self.alpha = min(255, self.alpha + 255 * dt / (self.display_time * 0.2))
            elif self.timer < self.display_time * 0.2:
                # Fade-out effect
                self.alpha = max(0, self.alpha - 255 * dt / (self.display_time * 0.2))
            else:
                self.alpha = 255  # Fully opaque during the middle of the display time

            # Floating up effect
            self.y_offset -= 20 * dt  # Adjust the speed of floating up as needed

    def draw(self, screen, player_x, player_y, camera_x, camera_y):
        if self.timer > 0:
            text_surface = self.font.render(self.text, True, (255, 0, 0)) 
            text_surface.set_alpha(self.alpha)  # Set the transparency level
            text_rect = text_surface.get_rect()
            text_rect.centerx = player_x - camera_x + 30  # Moved 30 pixels to the right
            text_rect.bottom = player_y - camera_y - 60 + self.y_offset  # Higher y-coordinate (-40 instead of -10)

            screen.blit(text_surface, text_rect)

class YellowFloatingText:
    def __init__(self):
        self.text = ""
        self.timer = 0
        self.display_time = 2  # Display time in seconds
        self.alpha = 0  # Transparency level (0-255)
        self.y_offset = 0  # Vertical offset for the floating effect

        # Define the path to the custom font
        self.font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        self.default_font_size = 18
        self.font = pygame.font.Font(self.font_path, self.default_font_size)  # Use the custom font with default size

    def show_text(self, text, font_size=None):
        self.text = text
        self.timer = self.display_time
        self.alpha = 0  # Start with fully transparent text
        self.y_offset = 0  # Start with no vertical offset

        # Set the font size if specified, otherwise use the default size
        if font_size:
            self.font = pygame.font.Font(self.font_path, font_size)
        else:
            self.font = pygame.font.Font(self.font_path, self.default_font_size)

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            if self.timer > self.display_time * 0.8:
                # Fade-in effect
                self.alpha = min(255, self.alpha + 255 * dt / (self.display_time * 0.2))
            elif self.timer < self.display_time * 0.2:
                # Fade-out effect
                self.alpha = max(0, self.alpha - 255 * dt / (self.display_time * 0.2))
            else:
                self.alpha = 255  # Fully opaque during the middle of the display time

            # Floating up effect
            self.y_offset -= 20 * dt  # Adjust the speed of floating up as needed

    def draw(self, screen, player_x, player_y, camera_x, camera_y):
        if self.timer > 0:
            text_surface = self.font.render(self.text, True, (255, 255, 0))  # Yellow color (255, 255, 0)
            text_surface.set_alpha(self.alpha)  # Set the transparency level
            text_rect = text_surface.get_rect()
            text_rect.centerx = player_x - camera_x + 30  # Moved 30 pixels to the right
            text_rect.bottom = player_y - camera_y - 40 + self.y_offset  # Higher y-coordinate (-40 instead of -10)

            screen.blit(text_surface, text_rect)


# Ensure pygame is initialized before using the FloatingText or YellowFloatingText classes
pygame.init()