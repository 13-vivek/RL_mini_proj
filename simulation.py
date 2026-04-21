import pygame
import sys
import numpy as np
import random
from q_learning import train, env, get_best_action

pygame.init()

WIDTH, HEIGHT = 600, 750
FLOORS = 5
FLOOR_HEIGHT = HEIGHT // FLOORS

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Multi-Passenger Elevator Simulation")

# Fonts
font = pygame.font.SysFont("Courier", 26, bold=True)
small_font = pygame.font.SysFont("Arial", 18, bold=True)

print("Training agent for multi-passenger scenarios... This might take ~5-10 seconds.")
train(20000) # Train more episodes because the state space is larger
print("Training complete")

def draw_person(surface, x, y, target_floor, is_inside=False):
    color = (40, 40, 50) if not is_inside else (20, 100, 20)
    scale = 1 if not is_inside else 0.8
    
    # Head
    pygame.draw.circle(surface, color, (x, y - int(35 * scale)), int(8 * scale))
    # Body
    pygame.draw.line(surface, color, (x, y - int(27 * scale)), (x, y - int(12 * scale)), 3)
    # Legs
    pygame.draw.line(surface, color, (x, y - int(12 * scale)), (x - int(7 * scale), y), 3)
    pygame.draw.line(surface, color, (x, y - int(12 * scale)), (x + int(7 * scale), y), 3)
    # Arms
    pygame.draw.line(surface, color, (x, y - int(22 * scale)), (x - int(10 * scale), y - int(15 * scale)), 3)
    pygame.draw.line(surface, color, (x, y - int(22 * scale)), (x + int(10 * scale), y - int(15 * scale)), 3)
    
    # Target Floor Badge
    badge_y = y - int(45 * scale)
    badge_rect = pygame.Rect(x - 12, badge_y - 10, 24, 20)
    pygame.draw.rect(surface, (255, 200, 50), badge_rect, border_radius=4)
    pygame.draw.rect(surface, (0, 0, 0), badge_rect, 1, border_radius=4)
    target_text = small_font.render(str(target_floor), True, (0, 0, 0))
    surface.blit(target_text, (x - 5, badge_y - 8))


def draw_environment(elevator_y, waiting_people, inside_people, doors_open):
    # wall
    screen.fill((235, 245, 255))
    
    # building structure
    building_width = 300
    building_x = WIDTH // 2 - building_width // 2
    pygame.draw.rect(screen, (200, 210, 225), (building_x, 0, building_width, HEIGHT))
    
    # elevator shaft
    shaft_w = 120
    shaft_x = WIDTH // 2 - shaft_w // 2
    pygame.draw.rect(screen, (40, 40, 50), (shaft_x, 0, shaft_w, HEIGHT))
    
    # floors and waiting persons
    for i in range(FLOORS):
        y = HEIGHT - (i + 1) * FLOOR_HEIGHT
        floor_num = i + 1
        
        # Floor line
        pygame.draw.line(screen, (120, 130, 140), (0, y), (WIDTH, y), 5)
        
        # Floor Label
        text = font.render(f"Floor {floor_num}", True, (80, 90, 100))
        screen.blit(text, (20, y + FLOOR_HEIGHT // 2 - 15))
        
        # people waiting on this floor
        waiting_here = [p for p in waiting_people if p[0] == floor_num]
        for idx, person in enumerate(waiting_here):
            target = person[1]
            person_x = shaft_x - 35 - (idx * 40)
            person_base_y = y + FLOOR_HEIGHT
            draw_person(screen, person_x, person_base_y, target, is_inside=False)
            
    # elevator cabin
    elevator_x = shaft_x + 5
    cabin_w = shaft_w - 10
    cabin_h = FLOOR_HEIGHT - 10
    
    # Inner cabin light
    pygame.draw.rect(screen, (255, 255, 230), (elevator_x, elevator_y + 5, cabin_w, cabin_h))
    
    # people inside the lift
    for idx, target in enumerate(inside_people):
        # Grid layout inside elevator
        px = elevator_x + 25 + (idx % 3) * 30
        py = elevator_y + cabin_h - 5 - (idx // 3) * 15
        draw_person(screen, px, py, target, is_inside=True)

    # Elevator doors
    door_color = (160, 170, 180)
    if doors_open:
        # Open doors
        pygame.draw.rect(screen, door_color, (elevator_x, elevator_y + 5, 20, cabin_h))
        pygame.draw.rect(screen, door_color, (elevator_x + cabin_w - 20, elevator_y + 5, 20, cabin_h))
    else:
        # Closed doors
        pygame.draw.rect(screen, door_color, (elevator_x, elevator_y + 5, cabin_w, cabin_h))
        pygame.draw.line(screen, (100, 110, 120), 
                         (elevator_x + cabin_w//2, elevator_y + 5), 
                         (elevator_x + cabin_w//2, elevator_y + FLOOR_HEIGHT - 5), 3)
                         
    # Top Information Panel
    panel_rect = pygame.Rect(15, 15, 260, 90)
    pygame.draw.rect(screen, (255, 255, 255), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 150, 200), panel_rect, 3, border_radius=8)
    
    # Summary of stats
    wait_count = len(waiting_people)
    inside_count = len(inside_people)
    
    line1 = small_font.render(f"Waiting: {wait_count} people", True, (20, 20, 20))
    line2 = small_font.render(f"In Lift: {inside_count} people", True, (20, 20, 20))
    status_text = small_font.render("Status: " + ("Doors Open" if doors_open else "Moving"), True, (40, 100, 180))
    
    screen.blit(line1, (25, 20))
    screen.blit(line2, (25, 45))
    screen.blit(status_text, (25, 70))

    pygame.display.flip()

def run_simulation():
    clock = pygame.time.Clock()
    
    # Initial Setup
    state = env.reset()
    # env.current_floor is 1, wait people list inside env.waiting_people
    actual_y = HEIGHT - env.current_floor * FLOOR_HEIGHT  
    
    while True:
        state = env.reset()
        done = False
        
        pygame.time.delay(1000) 
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            # Agent decides the action using Q-Table
            action = get_best_action(state)
            
            # Action mapping: 0=UP, 1=DOWN, 2=OPEN DOORS
            doors_open = False
            
            # Environment processes the action
            next_state, reward, done = env.step(action)
            target_floor = env.current_floor
            
            # Smooth Animation Loop for movement
            target_y = HEIGHT - target_floor * FLOOR_HEIGHT
            
            # If moving, animate pixel by pixel
            if action in [0, 1]:
                while abs(actual_y - target_y) > 0:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    
                    speed = 4
                    if actual_y < target_y:
                        actual_y += speed
                        if actual_y > target_y: actual_y = target_y
                    elif actual_y > target_y:
                        actual_y -= speed
                        if actual_y < target_y: actual_y = target_y
                        
                    draw_environment(actual_y, env.waiting_people, env.inside_people, doors_open=False)
                    clock.tick(60) 
            
            actual_y = target_y # Lock into exact position
            
            if action == 2:
                doors_open = True
            
            draw_environment(actual_y, env.waiting_people, env.inside_people, doors_open)
            
            # Pause based on action taken
            if action == 2:
                # Give user time to see people entering/exiting
                pygame.time.delay(1200)
            else:
                pygame.time.delay(200) 
            
            state = next_state
            
            if done:
                pygame.time.delay(1500) 

if __name__ == "__main__":
    run_simulation()
