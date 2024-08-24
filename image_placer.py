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
            with open('overlay_position.json', 'r') as f:
                self.overlay_pos = tuple(json.load(f))
        except FileNotFoundError:
            self.overlay_pos = None

    def save_position(self):
        if self.overlay_pos:
            with open('overlay_position.json', 'w') as f:
                json.dump(list(self.overlay_pos), f)
            print("Overlay position saved.")

    def delete_position(self):
        self.overlay_pos = None
        if os.path.exists('overlay_position.json'):
            os.remove('overlay_position.json')
        print("Overlay position deleted.")

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
                        self.dragging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.overlay_pos[0] - mouse_x
                        self.offset_y = self.overlay_pos[1] - mouse_y
                    else:
                        self.overlay_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mouse_x, mouse_y = event.pos
                    self.overlay_pos = (mouse_x + self.offset_x, mouse_y + self.offset_y)

    def render(self, screen):
        screen.blit(self.combined_background, (0, 0))
        if self.overlay_pos:
            screen.blit(self.overlay_image, self.overlay_pos)

def main():
    pygame.init()
    WINDOWWIDTH = 1290
    WINDOWHEIGHT = 719
    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Image Placer")
    clock = pygame.time.Clock()
    background_paths = ['data/images/background/background1.png', 'data/images/background/background2.png']
    image_placer = ImagePlacer('data/images/nowhite.png', background_paths)

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