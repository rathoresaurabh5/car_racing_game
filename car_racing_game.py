import pygame
import random
import time
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import tkinter as tk
from tkinter import messagebox

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (217, 242, 229)
GREY = (52, 52, 76)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Road dimensions and position
ROAD_WIDTH = 500
ROAD_X = (SCREEN_WIDTH - 50 - ROAD_WIDTH) // 2

# Set screen size and title
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Car Racing")

# Load sounds
background_music = "background_music.mp3"
car_crash_sound = "car_crash.mp3"

# Load the sounds
pygame.mixer.music.load(background_music)
crash_sound = pygame.mixer.Sound(car_crash_sound)

# Variable to keep track of sound state
sound_on = True

# Car class definition
class Car(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, image_path, width, height, speed):
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        # Load the image of the car, and set it to be transparent
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        # Initialize attributes of the car
        self.width = width
        self.height = height
        self.speed = speed
        
        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()

    def move_right(self, pixels):
        self.rect.x += pixels
        # Ensure the car doesn't move beyond the right boundary of the road
        if self.rect.right > ROAD_X + ROAD_WIDTH:
            self.rect.right = ROAD_X + ROAD_WIDTH

    def move_left(self, pixels):
        self.rect.x -= pixels
        # Ensure the car doesn't move beyond the left boundary of the road
        if self.rect.left < ROAD_X:
            self.rect.left = ROAD_X
        
    def move_forward(self, speed):
        self.rect.y += self.speed * speed / 20

    def move_backward(self, speed):
        self.rect.y -= self.speed * speed / 20

    def change_speed(self, speed):
        self.speed = speed

# Tree class definition
class Tree(pygame.sprite.Sprite):
    def __init__(self, image_path, width, height, speed):
        super().__init__()
        
        # Load the image of the tree and set it to be transparent
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        # Initialize attributes of the tree
        self.width = width
        self.height = height
        self.speed = speed
        
        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()

    def move_forward(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = -self.height
            self.rect.x = random.choice([random.randint(0, ROAD_X - self.width), random.randint(ROAD_X + ROAD_WIDTH, SCREEN_WIDTH - self.width)])

def show_game_over_popup(total_time, score):
    # Initialize Tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    def on_retry():
        root.destroy()
        main()  # Restart the game

    def on_quit():
        root.destroy()
        pygame.quit()
        quit()

    messagebox = tk.Toplevel(root)
    messagebox.title("Game Over")
    messagebox.geometry("300x150")

    msg = tk.Label(messagebox, text=f"Total Race Time: {total_time:.2f} seconds\nScore: {score}")
    msg.pack(pady=10)

    retry_button = tk.Button(messagebox, text="Retry Game", command=on_retry)
    retry_button.pack(side=tk.LEFT, padx=20, pady=10)

    quit_button = tk.Button(messagebox, text="Quit Game", command=on_quit)
    quit_button.pack(side=tk.RIGHT, padx=20, pady=10)

    messagebox.protocol("WM_DELETE_WINDOW", on_quit)
    root.mainloop()

def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def draw_button(screen, text, rect, color):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.Font(None, 15)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def main():
    global sound_on

    # Start background music
    pygame.mixer.music.play(-1)

    # Create a list to contain all the sprites
    all_sprites_list = pygame.sprite.Group()

    # Paths to car images
    player_car_image = "player_car.png"
    car_images = ["car1.png", "car2.png", "car3.png", "car4.png"]

    # Paths to tree images
    tree_images = ["tree1.png", "tree2.png", "tree3.png", "tree4.png"]

    # Create the player's car
    player_car = Car(player_car_image, 60, 80, 70)
    player_car.rect.x = ROAD_X + ROAD_WIDTH // 2 - player_car.width // 2
    player_car.rect.y = SCREEN_HEIGHT - 100

    # Create opponent cars
    cars = []
    for i in range(4):
        car_image = random.choice(car_images)
        car = Car(car_image, 60, 80, random.randint(50, 100))
        car.rect.x = ROAD_X + (i * 100) + 60
        car.rect.y = random.randint(-900, -100)
        cars.append(car)
        all_sprites_list.add(car)

    # Add the player's car to the sprite list
    all_sprites_list.add(player_car)

    # Create a group for opponent cars
    all_coming_cars = pygame.sprite.Group()
    for car in cars:
        all_coming_cars.add(car)

    # Create trees for the background
    trees = pygame.sprite.Group()
    for _ in range(10):  # More trees for a better effect
        tree_image = random.choice(tree_images)
        tree = Tree(tree_image, 50, 100, 5)
        tree.rect.x = random.choice([random.randint(0, ROAD_X - tree.width), random.randint(ROAD_X + ROAD_WIDTH, SCREEN_WIDTH - tree.width)])
        tree.rect.y = random.randint(-SCREEN_HEIGHT, 0)
        trees.add(tree)
        all_sprites_list.add(tree)

    # Variable to keep the main loop running
    carry_on = True

    # Clock to control game speed
    clock = pygame.time.Clock()

    # Initialize speed variable
    speed = 1

    # Initialize score variable
    score = 0

    # Store the start time
    start_time = time.time()

    # Font for displaying text
    font = pygame.font.Font(None, 36)

    # Sound toggle button dimensions
    button_rect = pygame.Rect(10, 10, 55, 20)

    # Main program loop
    while carry_on:
        for event in pygame.event.get():
            if event.type == QUIT:
                carry_on = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                    carry_on = False
            elif event.type == MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    toggle_sound()

        # Get key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_car.move_left(5)
        if keys[pygame.K_RIGHT]:
            player_car.move_right(5)
        if keys[pygame.K_UP]:
            speed += 0.05
        if keys[pygame.K_DOWN]:
            speed -= 0.05
                            
        # Game Logic
        for car in all_coming_cars:
            car.move_forward(speed)
            if car.rect.y > SCREEN_HEIGHT:
                car_image = random.choice(car_images)
                car.image = pygame.image.load(car_image).convert_alpha()
                car.image = pygame.transform.scale(car.image, (60, 80))
                car.change_speed(random.randint(50, 100))
                car.rect.y = -200
                score += 1  # Increase score when an opponent car reappears

        # Move the trees
        for tree in trees:
            tree.move_forward()

        # Check for car collisions
        car_collision_list = pygame.sprite.spritecollide(player_car, all_coming_cars, False)
        if car_collision_list:
            if sound_on:
                pygame.mixer.music.stop()
                crash_sound.play()
            carry_on = False  # End the game on collision

        all_sprites_list.update()

        # Drawing on Screen
        screen.fill(BROWN)

        # Draw the road
        pygame.draw.rect(screen, GREY, [ROAD_X, 0, ROAD_WIDTH, SCREEN_HEIGHT])

        # Draw road lines
        pygame.draw.line(screen, WHITE, [ROAD_X + 167, 0], [ROAD_X + 167, SCREEN_HEIGHT], 5)
        pygame.draw.line(screen, WHITE, [ROAD_X + 333, 0], [ROAD_X + 333, SCREEN_HEIGHT], 5)

        # Draw all sprites
        all_sprites_list.draw(screen)

        # Display the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, [325, 10])

        # Draw the sound toggle button
        draw_button(screen, "Sound: " + ("On" if sound_on else "Off"), button_rect, GREEN if sound_on else RED)

        # Refresh Screen
        pygame.display.flip()

        # Set frames per second
        clock.tick(60)

    # Calculate total race time
    total_time = time.time() - start_time

    # Show game over popup
    show_game_over_popup(total_time, score)

if __name__ == "__main__":
    main()
