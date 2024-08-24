import pygame
import textwrap
import os
class ChatBubble:
    def __init__(self, text, pos, color=(235, 232, 215), max_width=300, font_size=18):
        self.full_text = text
        self.current_text = ""
        self.pos = pos
        self.color = color
        self.max_width = max_width
        font_path = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
        self.font = pygame.font.Font(font_path, font_size)
        self.lifetime = 3.0  # 1 second after fully typed
        self.max_lifetime = 30  # 10 seconds for typing
        self.corner_radius = 15
        self.tail_height = 20
        self.tail_width = 20
        self.typing_speed = 18  # characters per second
        self.typing_timer = 0
        self.min_bubble_width = 50  # Minimum width for empty bubbles
        self.text_fully_revealed = False
        self.total_lifetime = 0
        self.fade_out_time = 0.5  # 0.5 seconds to fade out
        self.is_visible = True

    def wrap_text(self, text):
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] <= self.max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def update(self, dt):
        self.total_lifetime += dt
        #print(f"Updating bubble: total_lifetime={self.total_lifetime}, dt={dt}")

        if not self.text_fully_revealed:
            self.typing_timer += dt
            chars_to_add = int(self.typing_timer * self.typing_speed)
            if chars_to_add > 0 and len(self.current_text) < len(self.full_text):
                self.current_text = self.full_text[:len(self.current_text) + chars_to_add]
                self.typing_timer = 0

            if len(self.current_text) == len(self.full_text):
                self.text_fully_revealed = True

        if self.text_fully_revealed:
            time_since_reveal = self.total_lifetime - (len(self.full_text) / self.typing_speed)
            if time_since_reveal > self.lifetime + self.fade_out_time:
                self.is_visible = False
                print(f"Bubble for text '{self.full_text}' marked as invisible after {self.total_lifetime} seconds")
                return True  # Signal to remove the bubble

        return False

    def draw(self, screen, camera_x, camera_y):
        if not self.is_visible:
            return
        wrapped_current_text = self.wrap_text(self.current_text)
        
        padding = 10
        line_spacing = 1

        if wrapped_current_text:
            max_line_width = max(self.font.size(line)[0] for line in wrapped_current_text)
            total_height = sum(self.font.size(line)[1] for line in wrapped_current_text) + line_spacing * (len(wrapped_current_text) - 1)
        else:
            max_line_width = 0
            total_height = 0

        bubble_width = max(max_line_width + padding * 2, self.min_bubble_width)
        bubble_height = max(total_height + padding * 2, self.corner_radius * 2)

        horizontal_offset = 30  # Adjust this value to move the bubble more or less to the right
        bubble_rect = pygame.Rect(
            self.pos[0] - camera_x - bubble_width // 2 + horizontal_offset, 
            self.pos[1] - camera_y - bubble_height - 30,  # Adjust vertical offset as needed
            bubble_width, 
            bubble_height
        )

        # Add fade-out effect
        alpha = 255
        if self.text_fully_revealed:
            time_since_reveal = self.total_lifetime - (len(self.full_text) / self.typing_speed)
            if time_since_reveal > self.lifetime:
                alpha = 255 * (1 - (time_since_reveal - self.lifetime) / self.fade_out_time)
                alpha = max(0, min(255, int(alpha)))

        bubble_surface = pygame.Surface((bubble_width, bubble_height + self.tail_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (*self.color, alpha), (0, 0, bubble_width, bubble_height), border_radius=self.corner_radius)

        tail_center_x = bubble_width // 2
        tail_points = [
            (tail_center_x - self.tail_width // 2, bubble_height),
            (tail_center_x + self.tail_width // 2, bubble_height),
            (tail_center_x, bubble_height + self.tail_height)
        ]
        pygame.draw.polygon(bubble_surface, (*self.color, alpha), tail_points)

        screen.blit(bubble_surface, (bubble_rect.x, bubble_rect.y))

        y_offset = padding
        for line in wrapped_current_text:
            text_surface = self.font.render(line, True, (71, 71, 103))
            text_surface.set_alpha(alpha)
            bubble_surface.blit(text_surface, (padding, y_offset))
            y_offset += self.font.size(line)[1] + line_spacing

        screen.blit(bubble_surface, (bubble_rect.x, bubble_rect.y))

class ChatBubbleManager:
    def __init__(self):
        self.bubbles = {}

    def add_bubble(self, entity_id, text, pos):
        self.bubbles[entity_id] = ChatBubble(text, pos)

    def update(self, dt):
        to_remove = [entity_id for entity_id, bubble in self.bubbles.items() if bubble.update(dt)]
        for entity_id in to_remove:
            del self.bubbles[entity_id]

    def draw(self, screen, entities, camera_x, camera_y):
        for entity_id, bubble in self.bubbles.items():
            if entity_id in entities and bubble.is_visible:
                entity_pos = entities[entity_id]
                bubble.pos = entity_pos  # Update bubble position based on entity position
                bubble.draw(screen, camera_x, camera_y)