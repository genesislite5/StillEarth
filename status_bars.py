import pygame
import os
import random
from floating_text import FloatingText

class StatusBars:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bar_width = 100
        self.bar_height = 20
        self.margin = 20
        self.bars = {
            'HUNGER': {'value': 100, 'color': (226, 230, 197), 'position': (20, screen_height - 40), 'decrease_rate': 0.4},
            'THIRST': {'value': 100, 'color': (176, 133, 65), 'position': (20, screen_height - 120), 'decrease_rate': 0.4},
            'ENERGY': {'value': 100, 'color': (64, 71, 66), 'position': (140, screen_height - 40), 'decrease_rate': 0.4},
            'COMFORT': {'value': 100, 'color': (126, 101, 91), 'position': (140, screen_height - 120), 'decrease_rate': 0.25}
        }
        font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        self.font = pygame.font.Font(font_path, 24)
        self.insect_bite_timer = 0
        self.insect_bite_interval = 10  # Seconds between insect bites

    def update(self, dt):
        # Update other status bars
        for name, bar in self.bars.items():
            bar['value'] = max(0, bar['value'] - bar['decrease_rate'] * dt)
        
        # Update insect bite timer
        self.insect_bite_timer += dt
        if self.insect_bite_timer >= self.insect_bite_interval:
            self.insect_bite_timer = 0  # Reset timer
            return True  # Signal an insect bite
        return False

    def apply_insect_bite(self):
        self.modify_bar('COMFORT', -5)

    def draw(self, screen):
        for name, bar in self.bars.items():
            x, y = bar['position']
            
            # Draw background
            pygame.draw.rect(screen, (250, 250, 250), (x, y, self.bar_width, self.bar_height), border_radius=15)
            
            # Draw filled portion
            fill_width = int(self.bar_width * (bar['value'] / 100))
            pygame.draw.rect(screen, bar['color'], (x, y, fill_width, self.bar_height), border_radius=15)
            
            # Draw border
            pygame.draw.rect(screen, (126, 121, 91), (x, y, self.bar_width, self.bar_height), 2, border_radius=15)
            
            # Draw text
            text = self.font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(bottomleft=(x, y - 5))
            screen.blit(text, text_rect)

    def modify_bar(self, bar_name, amount):
        if bar_name in self.bars:
            self.bars[bar_name]['value'] = max(0, min(100, self.bars[bar_name]['value'] + amount))
            print(f"{bar_name} bar modified by {amount}. New value: {self.bars[bar_name]['value']}")  # Debug print