import pygame
import time
import sys

class BottomText:
    def __init__(self, screen, font_path, font_size=50):
        self.screen = screen
        self.font = pygame.font.Font(font_path, font_size)
        self.full_text = ""
        self.displayed_text = ""
        self.color = (255, 255, 255)
        self.position = (screen.get_width() // 2, screen.get_height() - 650)  # Adjusted to 100 pixels from the bottom
        self.typing_speed = 0.05  # Seconds between each character
        self.last_type_time = 0
        self.display_start_time = 0
        self.display_duration = 20  # Seconds to display the text
        self.line_height = self.font.get_linesize()
        self.max_width = screen.get_width() - 500  # Margin from screen edges

    def show_text(self, text, color=(255, 255, 255)):
        self.full_text = text
        self.displayed_text = ""
        self.color = color
        self.last_type_time = time.time()
        self.display_start_time = time.time()

    def update(self):
        current_time = time.time()
        
        # Typing animation
        if len(self.displayed_text) < len(self.full_text):
            if current_time - self.last_type_time > self.typing_speed:
                self.displayed_text += self.full_text[len(self.displayed_text)]
                self.last_type_time = current_time
        
        # Check if it's time to clear the text
        if current_time - self.display_start_time > self.display_duration:
            self.full_text = ""
            self.displayed_text = ""

    def draw(self):
        if self.displayed_text:
            lines = self.wrap_text(self.displayed_text)
            y_offset = self.position[1]
            for line in lines:
                text_surface = self.font.render(line, True, self.color)
                text_rect = text_surface.get_rect(center=(self.position[0], y_offset))
                self.screen.blit(text_surface, text_rect)
                y_offset += self.line_height

    def wrap_text(self, text):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= self.max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
        
        return lines

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("BottomText Example")

    # Load the image
    image_path = 'data/images/background/background1.png'
    background_image = pygame.image.load(image_path)

    # Create BottomText instance
    font_path = pygame.font.get_default_font()  # Use default font for simplicity
    bottom_text = BottomText(screen, font_path, font_size=24)

    # Show some sample text
    bottom_text.show_text("This is a sample text to demonstrate line wrapping in Pygame. Meow meow meow meow meow meow moew")

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update text
        bottom_text.update()

        # Draw everything
        screen.blit(background_image, (0, 0))
        bottom_text.draw()
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()