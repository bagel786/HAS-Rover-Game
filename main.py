import asyncio
import pygame
import os
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 50, 200)
ORANGE = (255, 165, 0)
HUD_BG = (0, 0, 0, 150)  # Semi-transparent black

# Game Settings
ROVER_SPEED = 5
ROTATION_SPEED = 5
GAME_DURATION = 60  # seconds
SCORE_PER_TARGET = 100
HAZARD_PENALTY_TIME = 5  # seconds deducted
HAZARD_PENALTY_SCORE = 50

# Assets Paths
ASSETS_DIR = 'assets'
BG_IMAGE_NAME = 'Jezero Crater Mars.jpg'
ROVER_IMAGE_NAME = 'roversprite.png'

class Rover(pygame.sprite.Sprite):
    def __init__(self, x, y, image=None):
        super().__init__()
        if image:
            self.original_image = image
            # Scale rover if it's too big, typical sprite size ~64x64
            if self.original_image.get_width() > 80:
                scale_factor = 80 / self.original_image.get_width()
                new_size = (int(self.original_image.get_width() * scale_factor),
                           int(self.original_image.get_height() * scale_factor))
                self.original_image = pygame.transform.scale(self.original_image, new_size)
        else:
            # Fallback square
            self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, WHITE, (0, 0, 50, 50))
            pygame.draw.line(self.original_image, RED, (25, 25), (25, 0), 3) # Front indicator

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(0, -1) # Pointing UP initially
        self.angle = 0
        self.speed = 0

    def get_input(self):
        keys = pygame.key.get_pressed()
        self.speed = 0
        
        # Movement
        move_vector = pygame.math.Vector2(0, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_vector.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_vector.y += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_vector.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_vector.x += 1
            
        if move_vector.length_squared() > 0:
            move_vector = move_vector.normalize()
            self.pos += move_vector * ROVER_SPEED
            
            # Rotation: Face the direction of movement
            target_angle = move_vector.angle_to(pygame.math.Vector2(0, -1)) # Angle relative to UP
            # Simple smooth rotation could go here, but instant turn is often better for top-down arcade feel
            # unless tank controls are requested. "Rover rotates to face direction of movement" usually implies 
            # standard top-down movement where the sprite faces where it goes.
            
            # We need to map the vector angle to the sprite rotation.
            # Pygame rotation is counter-clockwise.
            # Vector (0, -1) is 0 degrees. (1,0) is -90.
            
            # Let's use simple angle calculation
            self.angle = math.degrees(math.atan2(-move_vector.y, move_vector.x)) - 90
            
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.get_input()
        
        # Screen bounds
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT))
        
        self.rect.center = self.pos

class ScienceTarget(pygame.sprite.Sprite):
    def __init__(self, x, y, type_index):
        super().__init__()
        self.type_index = type_index
        self.radius = 15
        
        # Create a visual for the target
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        colors = [GREEN, BLUE, YELLOW, ORANGE]
        color = colors[type_index % len(colors)]
        
        pygame.draw.circle(self.image, color, (15, 15), 15)
        # Add a little "shine" or detail
        pygame.draw.circle(self.image, WHITE, (10, 10), 5)
        
        self.rect = self.image.get_rect(center=(x, y))

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, visible=True):
        super().__init__()
        self.visible = visible
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if visible:
            # Draw a "rocky" or "dangerous" area
            pygame.draw.rect(self.image, (100, 50, 50, 180), (0, 0, width, height), border_radius=5)
            pygame.draw.rect(self.image, RED, (0, 0, width, height), 2, border_radius=5)
        else:
            # We'll make it fully transparent
            # pygame.draw.rect(self.image, (255, 0, 0, 50), (0, 0, width, height)) # Debug view
            pass

        self.rect = self.image.get_rect(topleft=(x, y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mars Rover Mission")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        # Load Assets
        self.bg_image = None
        try:
            bg_path = os.path.join(ASSETS_DIR, BG_IMAGE_NAME)
            if os.path.exists(bg_path):
                self.bg_image = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Could not load background: {e}")
            
        self.rover_image = None
        try:
            rover_path = os.path.join(ASSETS_DIR, ROVER_IMAGE_NAME)
            if os.path.exists(rover_path):
                self.rover_image = pygame.image.load(rover_path).convert_alpha()
        except Exception as e:
            print(f"Could not load rover image: {e}")

        self.reset_game()
        
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.remaining_time = GAME_DURATION
        
        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        
        # Create Rover
        self.rover = Rover(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.rover_image)
        self.all_sprites.add(self.rover)
        
        # Create Science Targets (Random positions but not too close to center)
        for i in range(5):
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                # Ensure not too close to start
                if math.hypot(x - SCREEN_WIDTH//2, y - SCREEN_HEIGHT//2) > 100:
                    target = ScienceTarget(x, y, i)
                    self.targets.add(target)
                    self.all_sprites.add(target)
                    break
        
        # Create Hazards
        # Visible
        for _ in range(3):
             x = random.randint(0, SCREEN_WIDTH - 100)
             y = random.randint(0, SCREEN_HEIGHT - 100)
             if math.hypot(x - SCREEN_WIDTH//2, y - SCREEN_HEIGHT//2) > 150:
                 hazard = Hazard(x, y, random.randint(60, 100), random.randint(60, 100), True)
                 self.hazards.add(hazard)
                 # Note: Hazards are NOT in all_sprites if we want to draw them specially or if simple layered drawing is enough.
                 # Let's add them to all_sprites but make sure they are drawn below rover?
                 # Pygame Groups don't enforce order easily without LayeredUpdates.
                 # We'll just draw hazards first manually or use order of addition.
                 # Actually, sprite groups are not ordered. We'll draw explicitly.

        # Hidden Hazards
        for _ in range(3):
             x = random.randint(0, SCREEN_WIDTH - 50)
             y = random.randint(0, SCREEN_HEIGHT - 50)
             if math.hypot(x - SCREEN_WIDTH//2, y - SCREEN_HEIGHT//2) > 150:
                 hazard = Hazard(x, y, 50, 50, False) # Invisible
                 self.hazards.add(hazard)

        self.last_hazard_hit_time = 0
        self.hazard_message = ""
        self.hazard_message_timer = 0

    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    async def run(self):
        while True:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Restart
                        self.reset_game()

            # 2. Update
            dt = self.clock.tick(FPS) / 1000.0 # Delta time if needed
            current_time = pygame.time.get_ticks()
            
            if not self.game_over:
                elapsed = (current_time - self.start_time) / 1000
                self.remaining_time = max(0, GAME_DURATION - elapsed)
                
                if self.remaining_time <= 0:
                    self.game_over = True
                    self.remaining_time = 0
                
                self.rover.update()
                
                # Collisions: Targets
                hits = pygame.sprite.spritecollide(self.rover, self.targets, True)
                for hit in hits:
                    self.score += SCORE_PER_TARGET
                    # Optional: Add sound here
                    # pygame.mixer.Sound('ping.wav').play() 
                
                # Collisions: Hazards
                # Use collide_rect ratio for simpler forgiving collision
                hazard_hits = pygame.sprite.spritecollide(self.rover, self.hazards, False, pygame.sprite.collide_circle_ratio(0.8))
                
                if hazard_hits:
                    # Debounce hazard hits to avoid draining score instantly per frame
                    if current_time - self.last_hazard_hit_time > 1000: # 1 second immunity
                        self.score = max(0, self.score - HAZARD_PENALTY_SCORE)
                        # Penalty time?
                        # Changing start_time effectively reduces remaining time
                        self.start_time -= HAZARD_PENALTY_TIME * 1000 
                        
                        self.last_hazard_hit_time = current_time
                        self.hazard_message = "HAZARD! -50 pts"
                        self.hazard_message_timer = current_time + 1500
                        
                        # Only handle one hazard collision per check to avoid double penalty
                        pass

            # 3. Draw
            self.screen.fill(BLACK)
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill((200, 100, 50)) # Mars reddish fallback

            # Draw Hazards
            for hazard in self.hazards:
                if hazard.visible:
                    self.screen.blit(hazard.image, hazard.rect)
                # Debug: Show invisible hazards slightly
                # else:
                #    pygame.draw.rect(self.screen, (255, 0, 0), hazard.rect, 1)

            # Draw Targets
            self.targets.draw(self.screen)
            
            # Draw Rover
            self.screen.blit(self.rover.image, self.rover.rect)
            
            # UI / HUD
            # Timer
            timer_color = WHITE if self.remaining_time > 10 else RED
            self.draw_text(f"Time: {int(self.remaining_time)}", self.font, timer_color, 20, 20)
            
            # Score
            self.draw_text(f"Score: {self.score}", self.font, YELLOW, 20, 50)
            
            # Hazard Warning
            if current_time < self.hazard_message_timer:
                self.draw_text(self.hazard_message, self.font, RED, SCREEN_WIDTH//2, 100, center=True)

            if self.game_over:
                # Overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                self.draw_text("MISSION OVER", self.title_font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, center=True)
                self.draw_text(f"Final Score: {self.score}", self.font, YELLOW, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, center=True)
                self.draw_text("Press 'R' to Restart", self.font, GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, center=True)

            pygame.display.flip()
            await asyncio.sleep(0) # Critical for web build

if __name__ == "__main__":
    pygame.init()
    game = Game()
    asyncio.run(game.run())
