import pygame

class CollisionBox(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Draw the collision box

def load_collision_boxes(background_image):
    collision_boxes = []

    # Define collision boxes based on the background image
    if background_image == 'background1':
        collision_boxes.append(CollisionBox(0, 0, 200, 800))  # Example box on background1
        collision_boxes.append(CollisionBox(300, 150, 150, 75))
    elif background_image == 'background2':
        collision_boxes.append(CollisionBox(100, 200, 250, 100))  # Example box on background2
        collision_boxes.append(CollisionBox(400, 250, 200, 50))
    elif background_image == 'background3':
        collision_boxes.append(CollisionBox(75, 50, 300, 100))  # Example box on background3
        collision_boxes.append(CollisionBox(350, 100, 150, 150))
    elif background_image == 'background4':
        collision_boxes.append(CollisionBox(200, 150, 250, 200))  # Example box on background4
        collision_boxes.append(CollisionBox(450, 300, 100, 100))

    return collision_boxes

def draw_background_and_boxes(screen, background, collision_boxes):
    screen.blit(background, (0, 0))
    for box in collision_boxes:
        box.draw(screen)
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))  # Adjust size as needed

    backgrounds = {
        'background1': pygame.image.load('data/images/background/background1.png'),
        'background2': pygame.image.load('data/images/background/background2.png'),
        'background3': pygame.image.load('data/images/background/background3.png'),
        'background4': pygame.image.load('data/images/background/background4.png')
    }

    current_background_key = 'background1'
    collision_boxes = load_collision_boxes(current_background_key)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_background_key = 'background1'
                elif event.key == pygame.K_2:
                    current_background_key = 'background2'
                elif event.key == pygame.K_3:
                    current_background_key = 'background3'
                elif event.key == pygame.K_4:
                    current_background_key = 'background4'

                collision_boxes = load_collision_boxes(current_background_key)

        draw_background_and_boxes(screen, backgrounds[current_background_key], collision_boxes)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
