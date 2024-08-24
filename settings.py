import pygame
import sys

# Game settings
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720

TEST2_WIDTH = 1290  # Replace with actual width of test2.png
TEST2_HEIGHT = 719  # Replace with actual height of test2.png

total_width = TEST2_WIDTH + 1290  # Assuming background3.jpg is also 1290 wide
total_height = max(TEST2_HEIGHT, 719)

collision_boxes = [
    pygame.Rect(0, 20, 115, 620), #x position, y position, x height, y height
    pygame.Rect(670, 0, 180, 120),  
    #pygame.Rect(705, 360, 70, 100), 
    #pygame.Rect(800, 430, 70, 100), 
    pygame.Rect(1035, 0, 160, 420)

]

camera_smoothing = 0.1

# Path to the image
IMAGE_PATH = 'data/images/background/background1.png'

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Collision Box Visualization")

    # Load the image
    image = pygame.image.load(IMAGE_PATH).convert()
    image = pygame.transform.scale(image, (WINDOWWIDTH, WINDOWHEIGHT))

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the image
        screen.blit(image, (0, 0))

        # Draw collision boxes
        for box in collision_boxes:
            pygame.draw.rect(screen, (255, 0, 0), box, 2)  # Red boxes with 2-pixel border

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()
