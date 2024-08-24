import pygame
import json

def load_overlay_images4():
    bot_image = pygame.image.load('data/overlay_images/bottle1.png').convert_alpha()
    botwhite_image = pygame.image.load('data/overlay_images/bottle2.png').convert_alpha()
    return bot_image, botwhite_image

def load_toolbar_item4(image_path):
    item_image = pygame.image.load(image_path).convert_alpha()
    item_size = 64  # Size of the toolbar item
    item_image = pygame.transform.scale(item_image, (item_size, item_size))
    item_id = image_path.split('/')[-1].split('.')[0]  # Use the filename as the ID
    print(f"DEBUG: Loaded toolbar item '{item_id}' from {image_path}")  # Debug print
    return item_image, item_size, item_id


def load_overlay_position4():
    try:
        with open('overlay_position4.json', 'r') as f:
            overlay_pos = tuple(json.load(f))
    except FileNotFoundError:
        overlay_pos = None
    return overlay_pos

def remove_item_from_toolbar(toolbar_items, index):
    if 0 <= index < len(toolbar_items):
        removed_item = toolbar_items.pop(index)
        print(f"Removed item {removed_item} from toolbar at index {index}")
    else:
        print(f"Invalid index {index} for toolbar removal")

def render_overlay4(screen, current_overlay_image, overlay_pos, camera_x, camera_y):
    if overlay_pos and current_overlay_image:  # Ensure the overlay image is not None
        screen.blit(current_overlay_image, (int(overlay_pos[0] - camera_x), int(overlay_pos[1] - camera_y)))


def render_toolbar4(screen, item_image, item_slot, is_selected):
    # Create a transparent square surface
    transparent_square = pygame.Surface((item_slot.width, item_slot.height), pygame.SRCALPHA)
    transparent_square.fill((0, 0, 0, 50))  # RGBA with 50 alpha for transparency

    # Blit the transparent square onto the screen
    screen.blit(transparent_square, (item_slot.x, item_slot.y))

    # Blit the item image onto the screen
    screen.blit(item_image, (item_slot.x, item_slot.y))

    # Draw a white rectangle around the item slot if selected
    if is_selected:
        pygame.draw.rect(screen, (255, 255, 255), item_slot, 2)

def add_item_to_toolbar(toolbar_items, image_path):
    item_image, item_size, item_id = load_toolbar_item4(image_path)
    item_x = len(toolbar_items) * (item_size + 10)  # 10 pixels padding between items
    item_y = 0  # Assuming the toolbar is at the top
    new_item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
    toolbar_items.append({'image': item_image, 'rect': new_item_rect, 'id': item_id})
