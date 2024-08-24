import pygame
import json
import os

class ImagePlacer:
    def __init__(self, image_path, background_paths):
        self.overlay_image = pygame.image.load(image_path).convert_alpha()
        self.background_images = [pygame.image.load(path).convert() for path in background_paths]
        self.combined_background = self.create_combined_background()
        self.overlay_pos = None
        self.dragging = False
        self.offset_x, self.offset_y = 0, 0
        self.placing_image = False
        self.load_position()

    def create_combined_background(self):
        total_width = sum(img.get_width() for img in self.background_images)
        total_height = max(img.get_height() for img in self.background_images)
        combined_background = pygame.Surface((total_width, total_height))
        x_offset = 0
        for img in self.background_images:
            combined_background.blit(img, (x_offset, 0))
            x_offset += img.get_width()
        return combined_background

    def load_position(self):
        try:
            with open('overlay_position4.json', 'r') as f:
                self.overlay_pos = tuple(json.load(f))
            print(f"Loaded position: {self.overlay_pos}")  # Debug statement
        except FileNotFoundError:
            self.overlay_pos = None
            print("No saved position found.")

    def save_position(self):
        if self.overlay_pos:
            with open('overlay_position4.json', 'w') as f:
                json.dump(list(self.overlay_pos), f)
            print("Overlay position saved.")
        else:
            print("No overlay position to save.")  # Debug statement

    def delete_position(self):
        self.overlay_pos = None
        if os.path.exists('overlay_position4.json'):
            os.remove('overlay_position4.json')
            print("Overlay position file deleted.")
        else:
            print("Overlay position file not found.")  # Debug statement

    def toggle_placement_mode(self):
        self.placing_image = not self.placing_image
        if self.placing_image:
            print("Image placement mode activated. Click to place the image.")
        else:
            print("Image placement mode deactivated.")

    def handle_event(self, event):
        if self.placing_image:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.overlay_pos and self.overlay_image.get_rect(topleft=self.overlay_pos).collidepoint(event.pos):
                        print("Click detected on overlay image")  # Debug statement
                        self.dragging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.overlay_pos[0] - mouse_x
                        self.offset_y = self.overlay_pos[1] - mouse_y
                    else:
                        self.overlay_pos = event.pos
                        print(f"Overlay position updated to: {self.overlay_pos}")  # Debug statement
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mouse_x, mouse_y = event.pos
                    self.overlay_pos = (mouse_x + self.offset_x, mouse_y + self.offset_y)

    def render(self, screen):
        screen.blit(self.combined_background, (0, 0))
        if self.overlay_pos and self.overlay_image:
            screen.blit(self.overlay_image, self.overlay_pos)
        else:
            print("Overlay image not rendered.")  # Debug statement

    def clear_overlay_image(self):
        print("Clearing overlay image...")  # Debug statement
        self.overlay_image = None
        self.delete_position()  # This will remove the position from the JSON file as well



def main():
    pygame.init()
    WINDOWWIDTH = 1280
    WINDOWHEIGHT = 720
    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Image Placer")
    clock = pygame.time.Clock()
    background_paths = ['/Users/toneanmorgan/Downloads/pixil-frame-0-21.png', 'data/images/background3.jpg']
    image_placer = ImagePlacer('/Users/toneanmorgan/Downloads/bottle1.png', background_paths)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    image_placer.toggle_placement_mode()
                elif event.key == pygame.K_s:
                    image_placer.save_position()
                elif event.key == pygame.K_d:
                    image_placer.delete_position()

            image_placer.handle_event(event)

        image_placer.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()