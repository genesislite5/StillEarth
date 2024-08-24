import pygame
import os

def load_sprites(path, width, height):
    images = []
    try:
        for file_name in sorted(os.listdir(path)):
            if file_name.endswith('.png'):
                image = pygame.image.load(os.path.join(path, file_name)).convert()
                image = pygame.transform.scale(image, (width, height))
                image.set_colorkey((0, 0, 0))

                images.append(image)
    except FileNotFoundError:
        print(f"Warning: Sprite directory '{path}' not found.")
    except pygame.error as e:
        print(f"Error loading sprites from '{path}': {e}")
    return images if images else [pygame.Surface((width, height), pygame.SRCALPHA)]

def apply_color_grading(surface, grading, intensity):
    graded = surface.copy()
    graded.blit(grading, (0, 0), special_flags=pygame.BLEND_MULT)
    return graded

def check_collision(player_rect, dx, dy):
    from settings import collision_boxes
    temp_rect = player_rect.copy()
    temp_rect.x += dx
    temp_rect.y += dy
    for box in collision_boxes:
        if temp_rect.colliderect(box):
            return True
    return False