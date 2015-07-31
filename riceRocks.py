"""
This is a simple version of the famous Atari game Asteroids
This was built with as the part of the Python course offered by Rice University on Coursera

To play the game:
Please go to the below URL and hit the play button in the top-left region of your screen
http://www.codeskulptor.org/#user40_inTwHMSajOfUrov.py
"""

#Importing a GUI module 
import simplegui

import math
import random

#global variables for user interface

#dimensions for the canvas / game screen
WIDTH = 800
HEIGHT = 600

score = 0 #keep tack of the score
lives = 3 #keep track of the lives (initially you have 3 lives)
time = 0  #variable to maintain a timer
started = False #This variable if flag to identify if the game has been started or not

#class to hold all the images used for the game
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
#art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
#debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris1_blue.png")

#nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_brown.png")

#splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

#ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

#missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 75)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

#asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = [simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png"),
                  simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png"),
                  simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")]

#animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_orange.png")

#sound assets purchased from sounddogs.com, please do not redistribute
#.ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

#helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def process_sprite_group(sprite_set, canvas):
    for element in list(sprite_set):
        if element.update():
            sprite_set.remove(element)
        element.draw(canvas)

#function to handle collision between a single object and a group of objects		
def group_collide(obj_set,obj):
    global explosion_group
    for elem in list(obj_set):
        if elem.collision(obj):
            explosion_group.add(Sprite(elem.get_pos(), [0,0], 0, 0, explosion_image, explosion_info, explosion_sound))
            obj_set.remove(elem)
            return True
    return False

#function to handle collision between two groups of objects
def group_group_collide(obj1,obj2):
    numCollisions = 0
    for elem in list(obj1):
        if group_collide(obj2, elem):
            numCollisions += 1
            obj1.remove(elem)
    return numCollisions

def discard_all(obj_set):
    for elem in list(obj_set):
        obj_set.remove(elem)

#Class to handle the movement and actions of space ship
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        #canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def update(self):
        #update angle
        self.angle += self.angle_vel
        
        #update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        #update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
    
    def get_angle_vel(self):
        return self.angle_vel
        
    def shoot(self):
        global missile_group
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        missile_group.add(Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound))
    
    def get_radius(self):
        return self.radius
    
    def get_pos(self):
        return self.pos
    
        
#Sprite class : handles movements and actions of other moving objects like asteroids and missile
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            cent = [self.image_center[0]+self.image_size[0]*self.age,self.image_center[1]]
            canvas.draw_image(self.image, cent, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        #update angle
        self.angle += self.angle_vel
        
        #update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        #update age
        self.age += 1
        
        #check for aging
        if self.age <= self.lifespan:
            return False
        else:
            return True
    
    def get_radius(self):
        return self.radius
    
    def get_pos(self):
        return self.pos
    
    #detect is two objects are colliding
    def collision(self, other_obj):
        d = dist(self.get_pos(), other_obj.get_pos())
        r1 = self.get_radius()
        r2 = other_obj.get_radius()
        
        if d < r1+r2:
            return True
        else:
            return False
            
          
#key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
#mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, score, lives, my_ship, missile_group, rock_group, soundtrack
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        #initialize everything
        soundtrack.play()
        score = 0
        lives = 3
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        missile_group = set([])
        rock_group = set([])

def draw(canvas):
    global time, started, rock_group, missile_group, lives, score, my_ship, soundtrack
    
    #animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    #draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")
    i=0
    while(lives>-1 and i<lives):
        size = ship_info.get_size()
        center = ship_info.get_center()
        canvas.draw_image(ship_image,center,size,[60+(i*(size[0]/2.5)),75],[size[0]/2.5,size[1]/2.5],-math.pi/2)
        i += 1

    #update and draw ship
    my_ship.draw(canvas)
    my_ship.update()

    #update and draw sprite groups
    process_sprite_group(rock_group,canvas)
    process_sprite_group(missile_group,canvas)
    process_sprite_group(explosion_group,canvas)
    
    #check for collisions
    if group_collide(rock_group, my_ship):
        lives -= 1
        ang_vel = my_ship.get_angle_vel()
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        if ang_vel < 0:
            my_ship.decrement_angle_vel()
        elif ang_vel > 0:
            my_ship.increment_angle_vel()
        if lives <= 0:
            started = False
            discard_all(rock_group)
            discard_all(missile_group)
            soundtrack.pause()
            soundtrack.rewind()
    
    score += 10*(group_group_collide(rock_group, missile_group))
    
    #draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

#timer handler that spawns a rock    
def rock_spawner():
    global rock_group, asteriod_image, asteriod_info, my_ship
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_vel = [random.choice([-1,1])*2*random.random(),random.choice([-1,1])*2*random.random()]
    rock_avel = random.random() * .2 - .1
    if started and len(rock_group) < 12:
        rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image[random.choice([0,1,2])], asteroid_info)
        d = dist(rock.get_pos(), my_ship.get_pos())
        r1 = rock.get_radius()
        r2 = my_ship.get_radius()
        if(d > (r1+r2+40)):
            rock_group.add(rock)
            
#initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

#initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
missile_group = set([])
rock_group = set([])
explosion_group = set([])

#register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

#get things rolling
timer.start()
frame.start()