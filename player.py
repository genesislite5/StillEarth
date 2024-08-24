import pygame
from utils import load_sprites

class Player:
    def __init__(self, x, y, game):
        self.x = float(x)
        self.y = float(y)
        self.width = 64
        self.height = 64
        self.move_speed = 5.0
        self.state = 'idle'
        self.direction = 'right'
        self.is_jumping = False
        self.jump_count = 10
        self.game = game

        # Idle spritesheet dimensions
        self.idle_frame_width = 12
        self.idle_frame_height = 18
        self.idle_scale_factor = 6
        self.idle_frame_count = 6
        self.idle_animation_speed = 0.1

        # Run spritesheet dimensions
        self.run_frame_width = 12
        self.run_frame_height = 18
        self.run_scale_factor = 6
        self.run_frame_count = 4


        self.current_sprite = 0
        self.animation_cooldown = 100
        self.last_update = pygame.time.get_ticks()

        # Shadow attributes
        self.shadow_radius = 20
        self.shadow_offset_y = 100
        self.shadow_width = 60
        self.shadow_height = 20



    def say(self, message):
        if self.game and hasattr(self.game, 'chat_bubble_manager'):
            # Remove any existing bubble for the player
            if 'player' in self.game.chat_bubble_manager.bubbles:
                del self.game.chat_bubble_manager.bubbles['player']
            # Add the new bubble
            self.game.chat_bubble_manager.add_bubble('player', message, (self.x, self.y))
        if hasattr(self.game, 'chatbox'):
            self.game.chatbox.add_message(f"Meow: {message}")

    def update(self, keys, dt, check_collision):
        dx, dy = 0, 0
        self.state = 'idle'

        if keys[pygame.K_a]:
            dx -= self.move_speed * dt * 60
            self.state = 'run'
            self.direction = 'left'
        if keys[pygame.K_d]:
            dx += self.move_speed * dt * 60
            self.state = 'run'
            self.direction = 'right'
        if keys[pygame.K_w]:
            dy -= self.move_speed * dt * 60
        if keys[pygame.K_s]:
            dy += self.move_speed * dt * 60

        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not check_collision(player_rect, dx, dy):
            self.x += dx
            self.y += dy

        if self.is_jumping:
            if self.jump_count >= -10:
                jump_dy = (self.jump_count * abs(self.jump_count)) * 0.5
                if not check_collision(player_rect, 0, -jump_dy):
                    self.y -= jump_dy
                self.jump_count -= 1
            else:
                self.jump_count = 10
                self.is_jumping = False

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            if self.state == 'idle' and self.idle_sprites:
                self.current_sprite = (self.current_sprite + 1) % len(self.idle_sprites)
            elif self.state == 'run' and self.run_sprites:
                self.current_sprite = (self.current_sprite + 1) % len(self.run_sprites)
            self.last_update = current_time

    def draw_shadow(self, screen, camera_x, camera_y):
        shadow_x = int(self.x - camera_x)
        shadow_y = int(self.y - camera_y + self.shadow_offset_y)
        shadow_rect = pygame.Rect(
            shadow_x - self.shadow_width // 2,
            shadow_y - self.shadow_height // 2,
            self.shadow_width,
            self.shadow_height
        )
        pygame.draw.ellipse(screen, (0, 0, 0, 128), shadow_rect)  # Semi-transparent black

    def render(self, screen, camera_x, camera_y):
        # Draw shadow first
        self.draw_shadow(screen, camera_x, camera_y)

        # Then draw the player sprite
        if self.state == 'idle' and self.idle_sprites:
            current_image = self.idle_sprites[self.current_sprite % len(self.idle_sprites)]
        elif self.state == 'run' and self.run_sprites:
            current_image = self.run_sprites[self.current_sprite % len(self.run_sprites)]
        elif self.state == 'jump' and self.jump_sprites:
            current_image = self.jump_sprites[0]
        else:
            current_image = pygame.Surface((self.width, self.height))
            current_image.fill((255, 0, 0))  # Fill with red color as a placeholder

        if self.direction == 'left':
            current_image = pygame.transform.flip(current_image, True, False)

        screen.blit(current_image, (int(self.x - camera_x), int(self.y - camera_y)))
