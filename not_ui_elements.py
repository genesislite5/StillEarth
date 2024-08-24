import pygame
import json

def load_overlay_images2():
    tree_image = pygame.image.load('/Users/toneanmorgan/Downloads/pixil-frame-0-56.png').convert_alpha()
    treewhite_image = pygame.image.load('/Users/toneanmorgan/Downloads/pixil-frame-0-57.png').convert_alpha()
    return tree_image, treewhite_image

def load_toolbar_item2(image_path):
    item_image = pygame.image.load(image_path).convert_alpha()
    item_size = 64  # Size of the toolbar item
    item_image = pygame.transform.scale(item_image, (item_size, item_size))
    item_id = image_path.split('/')[-1].split('.')[0]  # Use the filename as the ID
    print(f"DEBUG: Loaded toolbar item '{item_id}' from {image_path}")  # Debug print
    return item_image, item_size, item_id

def load_overlay_position2():
    try:
        with open('overlay_position2.json', 'r') as f:
            overlay_pos2 = tuple(json.load(f))
    except FileNotFoundError:
        overlay_pos2 = None
    return overlay_pos2

def remove_item_from_toolbar(toolbar_items, index):
    if 0 <= index < len(toolbar_items):
        removed_item = toolbar_items.pop(index)
        print(f"Removed item {removed_item} from toolbar at index {index}")
    else:
        print(f"Invalid index {index} for toolbar removal")

def render_overlay2(screen, current_overlay_image2, overlay_pos, camera_x, camera_y):
    if overlay_pos:
        screen.blit(current_overlay_image2, (int(overlay_pos[0] - camera_x), int(overlay_pos[1] - camera_y)))

def render_toolbar2(screen, item_image, item_slot, is_selected):
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
    item_image, item_size, item_id = load_toolbar_item2(image_path)
    item_x = len(toolbar_items) * (item_size + 10)  # 10 pixels padding between items
    item_y = 0  # Assuming the toolbar is at the top
    new_item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
    toolbar_items.append({'image': item_image, 'rect': new_item_rect, 'id': item_id})

# Example usage in a Pygame loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    # Load images and item
    tree_image, treewhite_image  = load_overlay_images2()
    overlay_pos = load_overlay_position2()

    toolbar_items = []  # List to hold toolbar items

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear screen with black

        # Render overlay and toolbar
        render_overlay2(screen, tree_image, overlay_pos, 0, 0)
        for index, item in enumerate(toolbar_items):
            render_toolbar2(screen, item['image'], item['rect'], False)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()