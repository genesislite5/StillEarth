import pygame
import random
from utils import check_collision
from settings import TEST2_WIDTH, TEST2_HEIGHT

class NPC4:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game
        
        self.target_width = 72  
        self.target_height = 108  
        self.width = self.target_width
        self.height = self.target_height
        self.collision_cooldown = 0
        
        self.idle_sprites = self.load_spritesheet("NPC4/idle/pixil-frame-0-98.png", 12, 18, 6, self.target_width, self.target_height)
        self.run_sprites = self.load_spritesheet("NPC4/run/pixil-frame-0-95.png", 12, 18, 4, self.target_width, self.target_height)
        
        self.current_sprite = 0
        self.animation_cooldown = 100
        self.last_update = pygame.time.get_ticks()
        self.is_running = False
        self.target_x, self.target_y = self.random_target_position()
        
        self.last_direction = 1  

    def load_spritesheet(self, path, frame_width, frame_height, frame_count, target_width, target_height):
        spritesheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(frame_count):
            frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(frame, (target_width, target_height))
            frames.append(scaled_frame)
        return frames



    def update(self, dt, camera_x, camera_y):
        current_time = pygame.time.get_ticks()
        
        # NPC Movement Logic
        if self.is_running:
            self.move_towards_target(dt)
            if self.reached_target():
                self.is_running = False
        else:
            if random.random() < 0.01:  # 1% chance each frame to start running
                self.is_running = True
                self.target_x, self.target_y = self.random_target_position()

        # Update animation
        if current_time - self.last_update >= self.animation_cooldown:
            self.current_sprite = (self.current_sprite + 1) % len(self.current_sprites())
            self.last_update = current_time

    def move_towards_target(self, dt):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
            return

        direction_x = self.target_x - self.x
        direction_y = self.target_y - self.y
        distance = (direction_x**2 + direction_y**2)**0.5

        if distance != 0:
            dx = (direction_x / distance) * 100 * dt  # Speed is 100 units/second
            dy = (direction_y / distance) * 100 * dt

            # Check for collisions
            npc_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            collision_x = check_collision(npc_rect, dx, 0)
            collision_y = check_collision(npc_rect, 0, dy)

            if not collision_x:
                self.x += dx
            if not collision_y:
                self.y += dy

            # If there's a collision, change direction
            if collision_x or collision_y:
                self.handle_collision()

            # Update direction
            if direction_x < 0:
                self.last_direction = -1
            else:
                self.last_direction = 1

            # Ensure NPC stays within game boundaries
            self.x = max(0, min(self.x, TEST2_WIDTH - self.width))
            self.y = max(0, min(self.y, TEST2_HEIGHT - self.height))

    def handle_collision(self):
        # Choose a new random direction
        self.target_x, self.target_y = self.random_target_position()
        # Set a cooldown to prevent rapid direction changes
        self.collision_cooldown = 0.5  # 0.5 seconds cooldown

    def random_target_position(self):
        return (
            random.randint(0, TEST2_WIDTH - self.width),
            random.randint(0, TEST2_HEIGHT - self.height)
        )
    

    def reached_target(self):
        return abs(self.x - self.target_x) < 5 and abs(self.y - self.target_y) < 5

    def current_sprites(self):
        # Return the appropriate sprite list
        return self.run_sprites if self.is_running else self.idle_sprites

    def draw(self, screen, camera_x, camera_y):
        # Adjust the NPC's position relative to the camera
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Ensure the sprite index is within bounds
        if 0 <= self.current_sprite < len(self.current_sprites()):
            sprite = self.current_sprites()[self.current_sprite]
            # Flip the sprite if moving to the left
            if self.last_direction == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            screen.blit(sprite, (screen_x, screen_y))
