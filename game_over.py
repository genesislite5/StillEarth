import pygame
from pygame.locals import *
from PIL import Image
import os

class GameOver:
    # Constants
    TEXT_COLOR = (255, 255, 255)  # White
    ADDITIONAL_TEXT_COLOR = (110, 126, 78)  # #4a4d59
    BUTTON_TEXT_COLOR = (255, 255, 255)  # White
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    BUTTON_RADIUS = 10  # Radius for rounded corners
    BORDER_COLOR = (189, 171, 56, 120)  # #bdab38
    BACKGROUND_COLOR = (0, 0, 0, 64)  # More transparent black
    MAX_TEXT_WIDTH = 300  # Maximum width for wrapped text

    # Define colors for different game over scenarios
    OVERLAY_COLORS = {
        'HUNGER': (53, 73, 60, 220),  # Red with alpha
        'THIRST': (53, 73, 60, 220),  # Blue with alpha
        'ENERGY': (53, 73, 60, 220),  # Dark Blue with alpha
        'COMFORT': (53, 73, 60, 220),  # Purple with alpha
        'ENVIRONMENT': (53, 73, 60, 220),  # Same color as others
        'MULTIPLE_ZERO': (53, 73, 60, 220)  # Pink with alpha
    }

    # Define texts for different game over scenarios
    SCENARIO_TEXTS = {
        'HUNGER': "HUNGER. *grumbles* I'm hungry maybe I shouldn't have wasted that food Gaia gave me..",
        'THIRST': "THIRST. I don't need water... I don't need it... I don't need it... I NEED IT!",
        'ENERGY': "ENERGY. Maybe I finally get some sleep in the afterlife.",
        'COMFORT': "COMFORT. I am now one with the bugs I swatted..",
        'MULTIPLE_ZERO': "Don't ask me how I died, so much happened I couldnt tell ya'.",
        'ENVIRONMENT': "You ruined the environment..."

    }

    # Define vertical offsets for each scenario
    SCENARIO_OFFSETS = {
        'HUNGER': -20,
        'THIRST': -20,
        'ENERGY': -20,
        'MULTIPLE_ZERO': -20,
        'COMFORT': -23,
        'ENVIRONMENT': -20

    }

    def __init__(self, screen_width, screen_height, font_size=36):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_game_over = False
        self.game_over_reason = None

        # Load custom font for "You died" text
        font_path = os.path.join("fonts", "st-winter-pixel-24-font", "StWinterPixel24DemoRegular-RpV73.otf")
        try:
            self.custom_font = pygame.font.Font(font_path, font_size)
        except pygame.error:
            print(f"Error loading font from {font_path}. Using default font.")
            self.custom_font = pygame.font.Font(None, font_size)

        # Load custom font for additional text and "Play again" button
        additional_font_path = os.path.join("fonts", "Pixelify_Sans", "PixelifySans-VariableFont_wght.ttf")
        try:
            self.additional_font = pygame.font.Font(additional_font_path, 23)  # Smaller font size
            self.button_font = pygame.font.Font(additional_font_path, 30)  # Font for "Play again" button
        except pygame.error:
            print(f"Error loading font from {additional_font_path}. Using default font.")
            self.additional_font = pygame.font.Font(None, 24)  # Smaller font size
            self.button_font = pygame.font.Font(None, 30)  # Font for "Play again" button

        # Default font for other text
        self.default_font = pygame.font.Font(None, font_size)

        self.button_x = self.screen_width // 2 - self.BUTTON_WIDTH // 2
        self.button_y = self.screen_height * 3 // 4  # Move the button lower on the screen
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

        # Load energy GIF
        self.gif = self.load_gif('data/images/head.gif')
        self.current_frame = 0
        self.frame_delay = 200  # Adjust this value to control animation speed
        self.last_update = pygame.time.get_ticks()

        # Typing animation for "Zzz..."
        self.typing_text = "Zzz..."
        self.typing_index = 0
        self.typing_delay = self.frame_delay  # Sync typing speed with GIF frame rate
        self.last_typing_update = pygame.time.get_ticks()

        # Typing animation for scenario texts
        self.typing_scenario_text = ""
        self.typing_scenario_index = 0
        self.typing_scenario_delay = 50  # Adjust this value to control typing speed
        self.last_scenario_typing_update = pygame.time.get_ticks()

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

    def check_game_over(self, status_bars):
        zero_count = 0
        first_zero_bar = None

        for name, bar in status_bars.bars.items():
            if bar['value'] <= 0:
                zero_count += 1
                if first_zero_bar is None:
                    first_zero_bar = name

        if zero_count >= 2:
            self.is_game_over = True
            if zero_count == 4:
                self.game_over_reason = 'ALL_ZERO'
            else:
                self.game_over_reason = 'MULTIPLE_ZERO'
        elif zero_count == 1:
            self.is_game_over = True
            self.game_over_reason = first_zero_bar

        if self.is_game_over:
            self.typing_scenario_text = self.SCENARIO_TEXTS.get(self.game_over_reason, "")
            self.typing_scenario_index = 0
            self.last_scenario_typing_update = pygame.time.get_ticks()

        return self.is_game_over

    def draw(self, screen):
        print(f"Drawing game over screen. Reason: {self.game_over_reason}")

        if self.is_game_over:
            self._draw_overlay(screen)
            
            # Draw GIF and additional text for ENERGY, HUNGER, THIRST, and MULTIPLE_ZERO
            if self.game_over_reason in ['ENERGY', 'HUNGER', 'THIRST', 'COMFORT', 'MULTIPLE_ZERO', 'ENVIRONMENT']:
                self._draw_gif(screen)
                self._draw_additional_text(screen)
            
            self._draw_game_over_text(screen)
            self._draw_reset_button(screen)  # Draw the button last

    def _draw_overlay(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay_color = self.OVERLAY_COLORS.get(self.game_over_reason, (255, 0, 0, 128))  # Default to red if reason not found
        overlay.fill(overlay_color)
        screen.blit(overlay, (0, 0))

    def _draw_game_over_text(self, screen):
        game_over_text = self.custom_font.render("You Died", True, self.TEXT_COLOR)
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2 - 15, self.screen_height // 2 - 40))
        screen.blit(game_over_text, text_rect)

    def _draw_additional_text(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_scenario_typing_update > self.typing_scenario_delay:
            self.typing_scenario_index = min(self.typing_scenario_index + 1, len(self.typing_scenario_text))
            self.last_scenario_typing_update = now

        scenario_text = self.typing_scenario_text[:self.typing_scenario_index]
        wrapped_text = self.wrap_text(scenario_text, self.additional_font, self.MAX_TEXT_WIDTH)
        
        vertical_offset = self.SCENARIO_OFFSETS.get(self.game_over_reason, 0)
        y_offset = self.screen_height // 2 + 20 + vertical_offset
        for line in wrapped_text:
            text_surface = self.additional_font.render(line, True, self.ADDITIONAL_TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += text_surface.get_height()



    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def _draw_reset_button(self, screen):
        button_surface = pygame.Surface((self.BUTTON_WIDTH, self.BUTTON_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, self.BACKGROUND_COLOR, button_surface.get_rect(), border_radius=self.BUTTON_RADIUS)
        screen.blit(button_surface, self.button_rect)
        
        reset_text = self.button_font.render("play again", True, self.BUTTON_TEXT_COLOR)
        text_rect = reset_text.get_rect(center=self.button_rect.center)
        screen.blit(reset_text, text_rect)

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
        if self.game_over_reason in ['ENERGY', 'HUNGER', 'THIRST', 'COMFORT', 'MULTIPLE_ZERO', 'ENVIRONMENT']:
            if now - self.last_typing_update > self.typing_delay:
                self.typing_index = (self.typing_index + 1) % (len(self.typing_text) + 1)
                self.last_typing_update = now

            typing_text_surface = self.default_font.render(self.typing_text[:self.typing_index], True, self.TEXT_COLOR)
            # Move the text up and to the left
            typing_text_rect = typing_text_surface.get_rect(center=(gif_rect.centerx + 60, gif_rect.centery - 120))
            screen.blit(typing_text_surface, typing_text_rect)

    def handle_event(self, event):
        if self.is_game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False

    def reset(self):
        self.is_game_over = False
        self.game_over_reason = None
        self.typing_scenario_index = 0
        self.typing_scenario_text = ""

#delete this shit later

# Main game loop
def main():
    WIDTH = 1280
    HEIGHT = 720

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Over Screen")
    clock = pygame.time.Clock()

    game_over = GameOver(WIDTH, HEIGHT)

    # Simulating a game over state
    game_over.is_game_over = True
    game_over.game_over_reason = 'ENVIRONMENT'
    game_over.typing_scenario_text = game_over.SCENARIO_TEXTS['ENVIRONMENT']

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over.handle_event(event):
                # Reset the game
                game_over.reset()

        screen.fill((0, 0, 0))  # Fill the screen with black

        game_over.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
