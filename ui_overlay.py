# ui_overlay.py

import pygame

def draw_transparent_rectangle(screen, width, height, color=(0, 0, 0), alpha=128, position=(0, 50)):
    """
    Draws a slightly transparent rectangle on the screen.

    :param screen: The Pygame screen surface to draw on.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param color: The color of the rectangle (default is black).
    :param alpha: The transparency level of the rectangle (default is 128, range 0-255).
    :param position: The position of the top-left corner of the rectangle (default is (0, 0)).
    """
    # Create a surface with the given width and height
    rect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Fill the surface with the color and alpha
    rect_surface.fill((*color, alpha))
    
    # Blit the surface onto the screen at the given position
    screen.blit(rect_surface, position)