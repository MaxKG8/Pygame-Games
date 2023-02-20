import pygame
import os
import time
import random
pygame.font.init()

# Pygame library information to start game
WIDTH, HEIGHT = 750,750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load image assets into script
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Class for all lasers
# Since laser object is called within the Ship object, once the ship dies the laser array associeted with the ship will also be deleted
class Laser:
    # Laser x pos will always be constant
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        # For making laser hitbox
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
    
    def move(self, velocity):
        self.y += velocity

    # if y position is below of above screen return "True"
    def off_screen(self, height):
        return self.y >= height and self.y <= 0

    def collision(self, object):
        return collide(self, object)


# Abstract Class... Class not used, but we inheirit from it (Have Subclasses for other ships)
class Ship:

    # 60 frames in a second so 30 frames will be half a second
    COOLDOWN = 30 

    # All ships have these properties (x,y) for popsition. All ships start with 100 health
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        # Defined as none for now but these attributes will be inherited by enemy ship subclasse
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

        self.max_health = 100

    def draw(self, WINDOW):
        # Pygame function to draw ship
        WINDOW.blit(self.ship_image, (self.x, self.y))

        for laser in self.lasers:
            laser.draw(WINDOW)

    # Object is to check for collision of player and enemy laser
    def move_lasers(self, velocity, object):
        # Increments cooldown
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            # If laser doesnt hit anything
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # If laser Hits player
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        # If our counter is more than or equal to o.5s, we set it back to 0
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        # If our counter is more than 0, we increment it by 1 frame (out of 30)
        # Cant be "counter >= 0" cuz it shouldnt increment until shoot method is called
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # Yellow ship pic has same dimesions as all laser pics so laser will be centered when coming out ship
    # Since enemy ship images have diff dimesions than laser you will have to calculate for center in its own shoot method (below)
    def shoot(self):
        # If we are allowed to shoot
        if self.cool_down_counter == 0:
            # This position for the laser is only good for player ship size
            # Enemy subclass can have its own starting position for laser
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            # Set to one just to show that laser has been shot and cooldown can start incrementing till "COOLDOWN" frames
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        # Automatically calls the parent init method
        super().__init__(x, y, health)
        self.ship_image = YELLOW_SPACE_SHIP
        self.laser_image = YELLOW_LASER
        # Pygame has this function to know which pixels are filled in by image and can be hitbox
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.health = health


    # Objects is to check for collision of enemy and player laser
    def move_lasers(self, velocity, objects):
        # Increments cooldown
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            # If laser leaves screen
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # If laser is still on screen iterate through each enemy to find id on eis hit and if it is remove it
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        # Just make sure laser in in the list before youremove it
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # Override parent draw method
    # Adding the healthbar to the parent draw function
    def draw(self, WINDOW):
        super().draw(WINDOW)
        self.healthbar(WINDOW)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        # Gets percentage of red rectangle that will be filled by green rectangle
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_image.get_height() + 10, (self.ship_image.get_width()) * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER)
        }
    def __init__(self, x, y, color,health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        # for hitbox
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, velocity):
        self.y += velocity

    # Static Polymorphism
    # Method is already in Ship class but since this is a subclass, it will overide the Ship shoot method for all enemies so they have diff shoot properties
    def shoot(self):
        if self.cool_down_counter == 0:
            # width of laser pic has diff pixels than width of enemy pics (laser width is 100px) (enemy pics vary so we get width enem every time)
            # So to get enemy center, "self.x - 100/50 px + enemy_width/2" 
            laser = Laser(self.x - (self.laser_image.get_width()/2) + (self.ship_image.get_width()/2), self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(object1, object2):
    # Distance from object1 to object2
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None 

def main():
    run = True
    FPS = 60
    # Level starts at beginning of game there are no enemies so game will incrememnt to start at 1
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("agencyfb", 50, True)
    lost_font = pygame.font.SysFont("agencyfb", 80, True)

    enemies = []
    wave_length = 5

    enemy_velocity = 1
    player_velocity = 5
    laser_velocity = 5

    # Instance of Ship and starting position (x is centered cuz its half of window minus half of ship)
    player = Player(375-50, 500)

    # Creating an instance of clock that will be told to click 60 times a second in the while loop
    clock = pygame.time.Clock()

    lost = False
    # Number of frames we have gone thru with lost text rendered
    lost_count = 0

    # Funtion can only be called from within main function
    def redraw_window():
        WINDOW.blit(BG, (0,0))

        # Add text to screen
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 0))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        WINDOW.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))
        WINDOW.blit(level_label, (10,10))


        for enemy in enemies:
            enemy.draw(WINDOW)
        
        player.draw(WINDOW)

        # This is before the other "if lost == True" statement cuz we want to be executed each time before the "continue"
        if lost == True:
            lost_label = lost_font.render("You Lost", 1, (255, 0, 0))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    # Tells game too keep refreshing and checking stuff till run is no longer set to true
    while run == True:
        clock.tick(FPS)

        # Keep redrawing window for every tick
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # While we lost and are waiting for 3 second loss screen we keep continuing the loop
        # "Continue" keeps starting back at top of while loop so nun below gets done during this time
        if lost == True:
            if lost_count > FPS * 3:
                run = False
            else:
                continue


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            #Spawns new enemeies for new level
            for i in range(wave_length):
                # Creates multiple instances of enemy
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        
        # Gets every event from queue
        for event in pygame.event.get():
            # This checks for click even for quit button which will make run = false and stop the while loop stoppping game
            if event.type == pygame.QUIT: # "Quit is the red x button"
                # run = False <-- can use this if i want x button to just stop running game which will send me back to menu
                quit() # <-- Exits window completely when x button is pressed

        # Returns dictionary of all keyes and whether they are pressed or not (for every frame)
        keys = pygame.key.get_pressed()
        # Remember y == 0 is the top of the page
        if keys[pygame.K_UP] and player.y - player_velocity > 0:
            player.y -= player_velocity
        # Player velocity is the number of pixels in the next move, so if the pixels will move it past the height, dont move
        if keys[pygame.K_DOWN] and player.y + player_velocity + player.get_height() + 20 < HEIGHT:
            player.y += player_velocity
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity
        # Uses Atribute from Ship class on player instance
        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        # Space to shoot
        if keys[pygame.K_SPACE]:
            player.shoot()

        # Move method is in the Enemy Subclass and is being used on these instances of enemy
        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            # For erry frame the enemy is randomly going to chose number
            # If random number is 1 then enemy shoots
            # Since rand is 0-10*60, and game is 60fps, we can assume the enemy gonna shoot on average once erry 10s
            if random.randrange(0, 10*60) == 1:
                enemy.shoot()

            # If enemy and player collide, player loses health (uses collide function)
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            # If enemies get past end of screen you lose a life
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        
        # When move_laser is called for a player the laser will go up because we give a negative velocity so pos will go towards 0 (top of screen)
        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    title_font = pygame.font.SysFont("agencyfb", 80, True)
    # This run is local (for main menu running) and has nothing to do with run in main funciton
    run = True

    while run == True:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press mouse to begin", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2 , HEIGHT/2 - title_label.get_height()/2))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # If mouse buttons are pressed, then run is true and while loop from main funciton starts to play game
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()


if __name__ == "__main__":
    main_menu()
