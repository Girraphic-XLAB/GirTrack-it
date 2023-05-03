import pygame
from pygame.locals import *
from freed import FreeD, FreeDWrapper
import socket
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 40000

def deg_to_rad(deg):
    return (float(deg) * (math.pi/180.0))

def clamp(num, min_val, max_val):
    if (num < min_val):
        return min_val
    if (num > max_val):
        return max_val
    return num

def main():
    screen_width = 300
    screen_height = 300
    
    struct = FreeDWrapper(0,0,0,0,0,0,0,0)
    bits: 'bytes' = struct.createFreeD().encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    unit = 2
    
    pygame.init()
    girraphic_logo = pygame.image.load("Girraphic.png")
    pygame.display.set_caption("GirTrackIt-FreeD Test")
    pygame.display.set_icon(girraphic_logo)
    screen = pygame.display.set_mode((screen_width,screen_height))
    clock = pygame.time.Clock()
    running = True
    have_joystick = False
    joystick_count = pygame.joystick.get_count()
    joystick = None
    joy_left_x = 0
    joy_left_y = 0
    joy_right_x = 0
    joy_right_y = 0
    joy_left_trigger = 0
    joy_right_trigger = 0
    joy_shoulder_left = False
    joy_shoulder_right = False
    if (joystick_count > 0):
        have_joystick = True
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        num_joystick_buttons = joystick.get_numbuttons()
        print("joystick has ", num_joystick_buttons, " buttons")
        num_joystick_axes = joystick.get_numaxes()
        print("joystick has ", num_joystick_axes, " axes")
    

    #need to do proper controls
    # basically left stick should strafe/slide
    # right stick can turn, and look up/down (but not affect direction up/down)
    # then triggers can control up/down
    #so we have a heading
    heading_x = 0
    heading_y = 0

    default_font = pygame.font.SysFont(None, 24)

    BLUE = (0,0,255)
    YELLOW = (255, 255, 0)
    BLACK = (0,0,0)
    unit_inc = 2
    height_unit = 20
    while (running):
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        
        if have_joystick:
            joy_left_x = -int(joystick.get_axis(0) * 10)
            joy_left_y = -int(joystick.get_axis(1) * 10)
            joy_right_x = int(joystick.get_axis(2) * 10)
            joy_right_y = -int(joystick.get_axis(3) * 10)
            joy_left_trigger = (joystick.get_axis(4) + 1) * 0.5
            joy_right_trigger = (joystick.get_axis(5) + 1) * 0.5
            joy_shoulder_left = joystick.get_button(4)
            joy_shoulder_right = joystick.get_button(5)

        if (joy_shoulder_left):
            unit -= unit_inc
        if (joy_shoulder_right):
            unit += unit_inc

        if math.fabs(joy_right_x) > 0.1:
            heading_x += (joy_right_x * 0.25)
        if math.fabs(joy_right_y) > 0:
            if (joy_right_y > 0.0):
                heading_y += 0.5
            else:
                heading_y -= 0.5
        struct.pitch = int(heading_x) + 90
        heading_y = clamp(heading_y, -90, 90)
        struct.yaw = int(heading_y)
        
                      
        forward_vector = [math.sin(deg_to_rad((heading_x+90))),math.cos(deg_to_rad((heading_x+90)))]

        right_vector = [math.sin(deg_to_rad(heading_x)),math.cos(deg_to_rad(heading_x))]

        struct.pos_z += int(unit * joy_left_x * right_vector[0] )
        struct.pos_y += int(unit * joy_left_x * right_vector[1] )

        struct.pos_z += int(unit * joy_left_y * forward_vector[0])
        struct.pos_y += int(unit * joy_left_y * forward_vector[1])

        struct.pos_x += int(height_unit * joy_right_trigger)
        struct.pos_x -= int(height_unit * joy_left_trigger)

        if joy_right_y != 0:
            struct.yaw += (joy_right_y)
        if keys[K_w]:
            struct.pos_y += int(unit * forward_vector[1])
            struct.pos_z += int(unit * forward_vector[0])
        if keys[K_s]:
            struct.pos_y -= int(unit * forward_vector[1])
            struct.pos_z -= int(unit * forward_vector[0])
        if keys[K_a]:
            struct.pos_y += int(unit * right_vector[1])
            struct.pos_z += int(unit * right_vector[0])            
        if keys[K_d]:
            struct.pos_y -= int(unit * right_vector[1])
            struct.pos_z -= int(unit * right_vector[0])            
        if keys[K_q]:
            struct.roll -= 1
        if keys[K_e]:
            struct.roll += 1
        if keys[K_SPACE]:
            struct.pos_x += 1*unit
        if keys[K_LCTRL]:
            struct.pos_x -= 1*unit
        if keys[K_RIGHT]:
            heading_x += 1
        if keys[K_LEFT]:
            heading_x -= 1
        if keys[K_DOWN]:
            heading_y -= 1
        if keys[K_UP]:
            heading_y += 1
        if keys[K_RIGHTBRACKET]:
            unit += unit_inc
        if keys[K_LEFTBRACKET]:
            unit -= unit_inc
        if (unit < 0):
            unit = 0

        bits = struct.createFreeD().encode()
        sock.sendto(bits, (UDP_IP, UDP_PORT))
        
        font_img = default_font.render("unit scale: " + str(unit), True, YELLOW)
        screen.fill(BLACK)        
        offset = 0
        inset = -50
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))
        
        offset += 20        
        font_img = default_font.render("pos x: " + str(struct.pos_x), True, YELLOW)        
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))
        
        offset += 20        
        font_img = default_font.render("pos y: " + str(struct.pos_y), True, YELLOW)        
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))
        
        offset += 20
        font_img = default_font.render("pos z: " + str(struct.pos_z), True, YELLOW)
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))

        offset += 20
        font_img = default_font.render("pos z: " + str(struct.pos_z), True, YELLOW)
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))

        offset += 20
        font_img = default_font.render("pitch: " + str(heading_x), True, YELLOW)
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))

        offset += 20
        font_img = default_font.render("yaw: " + str(heading_y), True, YELLOW)
        screen.blit(font_img, (screen_width/2 + inset, screen_height/4 + offset))
        
        pygame.display.update()



if __name__ == "__main__":
    main()
                
    
