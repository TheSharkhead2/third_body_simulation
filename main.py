#external library import
import pygame, sys, random, math
from pygame.locals import *
from screeninfo import get_monitors #found in: https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python
import numpy as np

class InputBox:
    """
    Textbox class because I couldn't find a good library. But I still got
    this class from: 
    https://www.semicolonworld.com/question/55305/how-to-create-a-text-input-box-with-pygame

    """

    COLOR_INACTIVE = (1, 61, 77) #define color when box isn't highlighted
    COLOR_ACTIVE = (0, 180, 224) #define color when box is highlighted

    def __init__(self, x, y, w, h, font, text=''):
        self.initial_width = w
        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.FONT = font
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == K_RETURN: #on key press enter, "deactivate" cell
                    self.active = False
                    self.color = self.COLOR_INACTIVE
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(self.initial_width, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Sim:

    windowWidth = int(get_monitors()[0].width)
    windowHeight = int(get_monitors()[0].height)-100

    def __init__(self):
        self._running = True
        self._display = None

        self.updateOrder = "random" #order in which x, y, and z of body is updated. "together" == all at once; "random" == random order

        #define "center pixel" coordinates
        self.centerX = int(self.windowWidth/2)
        self.centerY = int(self.windowHeight/2)

        self.thirdRadius = 0.01 #radius of circle (third body rendered)
        self.thirdColor = (0, 0, 255) #color of third body

        self.tPerFrame = 1000 #number of delta Ts renders per frame
        self.deltaT = 0.00001 #define standard time increment 

        #set scale from x and y coords to pygame coords
        self.scale = 800

        self.l = 0.7 #define the lambda for the equations. 0 < lambda < 1

        #set initial conditions for initial x and x velocity and y and y velocity and z and z velocity (x=0.27, y=0 is cool) (x=0.48, y=0.34, l=0.7, scale=1000 is cool) (x=0.26, and then y=1, y=0.9, y=0.8, y=0.6 shows diversity of initial conditions (l=0.7)) (x=0, y=0.4, l=0.7) (x=0.26, y=0.5, l=0.7) (x=0.286, y=0, z=0.5, l=0.7)
        self.thirdX = 0.27
        self.thirdXvel = 0
        self.thirdY = 0
        self.thirdYvel = 0
        self.thirdZ = 0
        self.thirdZvel = 0

        #empty variables for accelerations
        self.thirdXacc = None
        self.thirdYacc = None
        self.thirdZacc = None

        #define coordinates for third body in pygame. Center pixel plus the starting positions scaled by x and y scales
        self.thirdRenderX = self.centerX + self.scale * self.thirdX
        self.thirdRenderY = self.centerY + self.scale * self.thirdY * -1 #multiply by negative 1 so increase y is up

        self.body1X = self.l
        self.body2X = self.l - 1

        self.bodyRadius = 0.02

        self.thirdPrevious = [] #list of previous locations of third body to make path
        self.pathLength = 1200 #number of saved positions in path

        self.collided = False

    def on_init(self):
        pygame.init()
        self._display = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE, vsync=1)
        pygame.display.set_caption("Third Body Simulation")

        self.font = pygame.font.SysFont('Times New Roman', 20) #define font

        #text input boxes for initial conditions 
        self.initial_l_input = InputBox(self.windowWidth-280, 20, 280, 30, self.font, text=str(self.l))

        self.initial_x_input = InputBox(self.windowWidth-275, 50, 275, 30, self.font, text=str(self.thirdX))

        self.initial_y_input = InputBox(self.windowWidth-275, 80, 275, 30, self.font, text=str(self.thirdY))

        self.initial_z_input = InputBox(self.windowWidth-275, 110, 275, 30, self.font, text=str(self.thirdZ))

        self.initial_xVel_input = InputBox(self.windowWidth-202, 140, 202, 30, self.font, text=str(self.thirdXvel))

        self.initial_yVel_input = InputBox(self.windowWidth-202, 170, 202, 30, self.font, text=str(self.thirdYvel))

        self.initial_zVel_input = InputBox(self.windowWidth-202, 200, 202, 30, self.font, text=str(self.thirdZvel))

        self.lagrange_point_input = InputBox(self.windowWidth-260, 230, 260, 30, self.font, text=("none")) #input box to start at a specific lagrange point (only have 4 and 5 currently available)

        #errors for starting at lagrange point (if you want to look at behavor not quite exactly at point)
        self.lagrange_point_errorX = InputBox(self.windowWidth-195, 260, 195, 30, self.font, text="0")
        self.lagrange_point_errorY = InputBox(self.windowWidth-195, 290, 195, 30, self.font, text="0")
        self.lagrange_point_errorZ = InputBox(self.windowWidth-195, 320, 195, 30, self.font, text="0")

        self.scale_input = InputBox(self.windowWidth-340, 350, 340, 30, self.font, text=str(self.scale)) #input box for changing scale

    def add_pos(self, x, y):
        """
        add position to list of previous positions for path
        
        """

        self.thirdPrevious.append((x,y)) #append tuple
        
        if len(self.thirdPrevious) > self.pathLength: #if list is over a certain length, cut list
            del self.thirdPrevious[0]

    def reset_sim(self):
        #reset accelerations
        self.thirdXacc = None
        self.thirdYacc = None
        self.thirdZacc = None

        self.collided = False #it hasn't collided yet

        #three cases for L1, L2, and L3:
        # L2 : 0 = -x(x-l)^2(x+1-l)^2 - l(x-l)^2 - (1-l)(x+1-l)^2
        # L1 : 0 = -x(x-l)^2(x+1-l)^2 + l(x-l)^2 - (1-l)(x+1-l)^2
        # L3 : 0 = -x(x-l)^2(x+1-l)^2 + l(x-l)^2 + (1-l)(x+1-l)^2

        #these as coefficients (calculated by wolfram alpha)
        #L2 : [-1, (4L - 2), (-6L**2 + 6L - 1), (4L**3 - 6L**2 + 2L - 1), (-L**4 + 2L**3 - L**2 + 4L - 2), (-3L**2 + 3L - 1)]
        #L1 : [-1, (4L - 2), (-6L**2 + 6L - 1), (4L**3 - 6L**2 + 4L - 1), (-L**4 + 2L**3 - 5L**2 + 4L - 1), (2L**3 - 3L**2 + 3L - 1)]
        #L3 : [-1, (4L - 2), (-6L**2 + 6L - 1), (4L**3 - 6L**2 + 2L + 1), (-L**4 + 2L**3 - L**2 - 4L + 2), (3L**2 - 3L + 1)]

        if self.lagrange_point_input.text == "4": #if the user specified starting at L4, override other settings and start there
            self.l = float(self.initial_l_input.text) #only take in other parameter of lambda as it affects lagrange points
            #reset velocities
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.thirdZvel = 0

            self.thirdZ = 0 + float(self.lagrange_point_errorZ.text) #just set z to 0 plus the error... This is for Fan Fan

            self.thirdX = self.l - 0.5 + float(self.lagrange_point_errorX.text) #defined x coord plus error
            self.thirdY = (math.sqrt(3)/2) + float(self.lagrange_point_errorY.text) #defined y coord plus error

        elif self.lagrange_point_input.text == "5": #if the user specified starting at L5, override other settings and start there
            self.l = float(self.initial_l_input.text) #only take in other parameter of lambda as it affects lagrange points
            #reset velocities
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.thirdZvel = 0

            self.thirdZ = 0 + float(self.lagrange_point_errorZ.text) #just set z to 0 plus the error... This is for Fan Fan

            self.thirdX = self.l - 0.5 + float(self.lagrange_point_errorX.text) #defined x coord plus error
            self.thirdY = -(math.sqrt(3)/2) + float(self.lagrange_point_errorY.text) #defined y coord plus error

        elif self.lagrange_point_input.text == "2": #looking at second lagrange point
            self.l = float(self.initial_l_input.text) #only take in other parameter of lambda as it affects lagrange points
            #calculate roots of coorisponding polynomial
            lRoots = (np.roots([-1, (4*self.l - 2), (-6*(self.l**2) + 6*self.l - 1), (4*(self.l**3) - 6*(self.l**2) + 2*self.l - 1), (-(self.l**4) + 2*(self.l**3) - self.l**2 + 4*self.l - 2), (-3*(self.l**2) + 3*self.l - 1)]))

            #take only real roots --> this should just return one root. But could not in some cases I don't see? 
            lRoots = [i.real for i in lRoots if i.imag == 0] #take only real roots
            print(lRoots)
            
            #reset velocities
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.thirdZvel = 0

            self.thirdZ = 0 + float(self.lagrange_point_errorZ.text) #just set z to 0 plus the error... This is for Fan Fan

            self.thirdX = lRoots[0] + float(self.lagrange_point_errorX.text) #defined x coord plus error
            self.thirdY = 0 + float(self.lagrange_point_errorY.text) #defined y coord plus error (y is just 0)
        
        elif self.lagrange_point_input.text == "3": #looking at second lagrange point
            self.l = float(self.initial_l_input.text) #only take in other parameter of lambda as it affects lagrange points
            #calculate roots of coorisponding polynomial
            lRoots = (np.roots([-1, (4*self.l - 2), (-6*(self.l**2) + 6*self.l - 1), (4*(self.l**3) - 6*(self.l**2) + 2*self.l + 1), (-(self.l**4) + 2*(self.l**3) - self.l**2 - 4*self.l + 2), (3*(self.l**2) - 3*self.l + 1)]))

            #take only real roots --> this should just return one root. But could not in some cases I don't see? 
            lRoots = [i.real for i in lRoots if i.imag == 0] #take only real roots
            print(lRoots)
            
            #reset velocities
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.thirdZvel = 0

            self.thirdZ = 0 + float(self.lagrange_point_errorZ.text) #just set z to 0 plus the error... This is for Fan Fan

            self.thirdX = lRoots[0] + float(self.lagrange_point_errorX.text) #defined x coord plus error
            self.thirdY = 0 + float(self.lagrange_point_errorY.text) #defined y coord plus error (y is just 0)

        elif self.lagrange_point_input.text == "1": #looking at second lagrange point
            self.l = float(self.initial_l_input.text) #only take in other parameter of lambda as it affects lagrange points
            #calculate roots of coorisponding polynomial
            lRoots = (np.roots([-1, (4*self.l - 2), (-6*(self.l**2) + 6*self.l - 1), (4*(self.l**3) - 6*(self.l**2) + 4*self.l - 1), (-(self.l**4) + 2*(self.l**3) - 5*(self.l**2) + 4*self.l - 2), (2*(self.l**3) - 3*(self.l**2) + 3*self.l - 1)]))

            #take only real roots --> this should just return one root. But could not in some cases I don't see? 
            lRoots = [i.real for i in lRoots if i.imag == 0] #take only real roots
            print(lRoots)
            
            #reset velocities
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.thirdZvel = 0

            self.thirdZ = 0 + float(self.lagrange_point_errorZ.text) #just set z to 0 plus the error... This is for Fan Fan

            self.thirdX = lRoots[0] + float(self.lagrange_point_errorX.text) #defined x coord plus error
            self.thirdY = 0 + float(self.lagrange_point_errorY.text) #defined y coord plus error (y is just 0)

        else: #if no lagrange point is specified, use defined initial values
            #set initial values based on text box
            self.l = float(self.initial_l_input.text)
            self.thirdX = float(self.initial_x_input.text)
            self.thirdXvel = float(self.initial_xVel_input.text)
            self.thirdY = float(self.initial_y_input.text)
            self.thirdYvel = float(self.initial_yVel_input.text)
            self.thirdZ = float(self.initial_z_input.text)
            self.thirdZvel = float(self.initial_zVel_input.text)

        #reset these after lambda value is changed
        self.body1X = self.l
        self.body2X = self.l - 1

        self.thirdPrevious = [] #clear path

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_SLASH: #reset simulation with new initial values if user presses forward slash (random key, idk)
                self.reset_sim()
            if event.key == pygame.K_BACKQUOTE: #set scale if backquote pressed
                self.scale = int(self.scale_input.text)

        #handle all textbox event updates
        self.initial_l_input.handle_event(event)
        self.initial_x_input.handle_event(event)
        self.initial_y_input.handle_event(event)
        self.initial_z_input.handle_event(event)
        self.initial_xVel_input.handle_event(event)
        self.initial_yVel_input.handle_event(event)
        self.initial_zVel_input.handle_event(event) 
        self.lagrange_point_input.handle_event(event)
        self.lagrange_point_errorX.handle_event(event)
        self.lagrange_point_errorY.handle_event(event)
        self.lagrange_point_errorZ.handle_event(event)
        self.scale_input.handle_event(event)

    def on_loop(self):

        if self.updateOrder == "together" and not self.collided: #don't run if has collided
            for i in range(self.tPerFrame): #run position updates set number of times
                #update accelerations for x, y, and z 
                self._calc_d2dx()
                self._calc_d2dy()
                self._calc_d2dz()

                #update positions and velocities 
                self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)
                self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)
                self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                #run collision detection
                self._collision_detection(1)
                self._collision_detection(2)

                if i % 100 == 0: #save position value every 100 calculations
                    self.add_pos(self.thirdX, self.thirdY)    
        
        elif self.updateOrder == "random" and not self.collided: #don't run if has collided
            for i in range(self.tPerFrame): #run position updates set number of times
                randomSeed = random.randint(1,6) #6 options for update order

                if randomSeed == 1 or randomSeed == 4:
                    self._calc_d2dx()
                    self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)

                    if randomSeed == 1:
                        self._calc_d2dy()
                        self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)

                        self._calc_d2dz()                
                        self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                    else: 
                        self._calc_d2dz()                
                        self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                        self._calc_d2dy()
                        self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)
                
                elif randomSeed == 2 or randomSeed == 5:
                    self._calc_d2dy()
                    self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)

                    if randomSeed == 1:
                        self._calc_d2dx()
                        self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)

                        self._calc_d2dz()                
                        self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                    else: 
                        self._calc_d2dz()                
                        self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                        self._calc_d2dx()
                        self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)
                else:
                    self._calc_d2dz()                
                    self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

                    if randomSeed == 1:
                        self._calc_d2dx()
                        self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)

                        self._calc_d2dy()
                        self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)

                    else: 
                        self._calc_d2dy()
                        self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)

                        self._calc_d2dx()
                        self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)

                #run collision detection
                self._collision_detection(1)
                self._collision_detection(2)

                if i % 100 == 0: #save position value every 100 calculations
                    self.add_pos(self.thirdX, self.thirdY) 


        #update all textboxes
        self.initial_l_input.update()
        self.initial_x_input.update()
        self.initial_y_input.update()
        self.initial_z_input.update()
        self.initial_xVel_input.update()
        self.initial_yVel_input.update()
        self.initial_zVel_input.update()
        self.lagrange_point_input.update()
        self.lagrange_point_errorX.update()
        self.lagrange_point_errorY.update()
        self.scale_input.update()

        #update pygame render coords
        self._update_pygame_coords()        

    def on_render(self):
        
        self._display.fill((0,0,0))
        self._display.blit(self.font.render("Best Planet", True, (255, 255, 255)), (20, 20))
        
        #render third body coords 
        self._display.blit(self.font.render(" x = {}".format(self.thirdX), True, (255, 255, 255)), (20, 50))
        self._display.blit(self.font.render(" y = {}".format(self.thirdY), True, (255, 255, 255)), (20, 70))
        self._display.blit(self.font.render(" z = {}".format(self.thirdZ), True, (255, 255, 255)), (20, 90))

        self._display.blit(self.font.render(" x velocity = {}".format(self.thirdXvel), True, (255, 255, 255)), (20, 110))
        self._display.blit(self.font.render(" y velocity = {}".format(self.thirdYvel), True, (255, 255, 255)), (20, 130))
        self._display.blit(self.font.render(" z velocity = {}".format(self.thirdZvel), True, (255, 255, 255)), (20, 150))

        self._display.blit(self.font.render(" x acceleration = {}".format(self.thirdXacc), True, (255, 255, 255)), (20, 170))
        self._display.blit(self.font.render(" y acceleration = {}".format(self.thirdYacc), True, (255, 255, 255)), (20, 190))
        self._display.blit(self.font.render(" z acceleration = {}".format(self.thirdZacc), True, (255, 255, 255)), (20, 210))

        #render path of third body 
        for position, index in zip(self.thirdPrevious, list(range(len(self.thirdPrevious)))): #loop through all previous locations
            pygame.draw.circle(self._display, (0, 0, int(index * 200/self.pathLength) ), (self.centerX + position[0]*self.scale, self.centerY + position[1]*self.scale*-1), int(self.thirdRadius * self.scale))

        #render third body
        pygame.draw.circle(self._display, self.thirdColor, (self.thirdRenderX, self.thirdRenderY), int(self.thirdRadius * self.scale))

        #render first and second body 
        pygame.draw.circle(self._display, (255,0,0), ( self.centerX + self.body1X*self.scale, self.centerY ), int(self.bodyRadius * self.scale) )
        pygame.draw.circle(self._display, (255, 0,0), ( self.centerX + self.body2X*self.scale, self.centerY ), int(self.bodyRadius * self.scale)  )

        #render text box labels
        self._display.blit(self.font.render("lambda value: ", True, (255, 255, 255)), (self.windowWidth-400, 20))
        self._display.blit(self.font.render("initial x value: ", True, (255, 255, 255)), (self.windowWidth-400, 50))
        self._display.blit(self.font.render("initial y value: ", True, (255, 255, 255)), (self.windowWidth-400, 80))
        self._display.blit(self.font.render("initial z value: ", True, (255, 255, 255)), (self.windowWidth-400, 110))
        self._display.blit(self.font.render("initial x velocity value: ", True, (255, 255, 255)), (self.windowWidth-400, 140))
        self._display.blit(self.font.render("initial y velocity value: ", True, (255, 255, 255)), (self.windowWidth-400, 170))
        self._display.blit(self.font.render("initial z velocity value: ", True, (255, 255, 255)), (self.windowWidth-400, 200))
        self._display.blit(self.font.render("Lagrange Point: ", True, (255, 255, 255)), (self.windowWidth-400, 230))
        self._display.blit(self.font.render("Lagrange Point Error X: ", True, (255, 255, 255)), (self.windowWidth-400, 260))
        self._display.blit(self.font.render("Lagrange Point Error Y: ", True, (255, 255, 255)), (self.windowWidth-400, 290))
        self._display.blit(self.font.render("Lagrange Point Error Z: ", True, (255, 255, 255)), (self.windowWidth-400, 320))
        self._display.blit(self.font.render("Scale: ", True, (255, 255, 255)), (self.windowWidth-400, 350))

        #draw all text boxes
        self.initial_l_input.draw(self._display)
        self.initial_x_input.draw(self._display)
        self.initial_y_input.draw(self._display)
        self.initial_z_input.draw(self._display)
        self.initial_xVel_input.draw(self._display)
        self.initial_yVel_input.draw(self._display)
        self.initial_zVel_input.draw(self._display)
        self.lagrange_point_input.draw(self._display)
        self.lagrange_point_errorX.draw(self._display)
        self.lagrange_point_errorY.draw(self._display)
        self.lagrange_point_errorZ.draw(self._display)
        self.scale_input.draw(self._display)

    def on_quit(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        pygame.display.flip()
        while self._running:
            events = pygame.event.get() #grab events
            for event in events: #process all events
                self.on_event(event)
            self.on_loop()
            self.on_render()
            pygame.display.update()
        self.on_quit()

    def _collision_detection(self, bodyNumber):
        if bodyNumber == 1:
            centerX = self.body1X
        elif bodyNumber == 2:
            centerX = self.body2X

        total_radius = self.bodyRadius + self.thirdRadius
        differenceVector = (self.thirdX - centerX, self.thirdY) #recalculate vector representing difference between bodies
        norm = math.sqrt(differenceVector[0]**2 + differenceVector[1]**2)
        unitDifference = [elem/norm for elem in differenceVector]
        difference = total_radius - norm

        if difference > 0:
            self.thirdX -= unitDifference[0] * difference
            self.thirdY -= unitDifference[1] * difference
            self.thirdXvel = 0
            self.thirdYvel = 0
            self.collided = True #set true for collision 
        

    def _update_pygame_coords(self):
        """
        With new x, y, and z coordinates for planet, update coordinates in pygame
        for rendering
        
        """

        #update pygame coordinates for third body. Center pixel plus x and y coords multiplied by scaler
        self.thirdRenderX = self.centerX + self.scale * self.thirdX 
        self.thirdRenderY = self.centerY + self.scale * self.thirdY * -1 

    def _updateX(self, x, xVel, xAcc, t=0.0001):
        """
        Calculate new x and xVel using kinematics. This can be used for x, y, and z

        """

        newX = x + xVel*t + (xAcc/2)*(t**2) #calculate new x after t seconds
        newXvel = xVel + xAcc*t

        return newX, newXvel


    def _calc_d2dx(self):
        """
        Calculate x acceleration
        
        """

        #get all values for calculation
        l = self.l
        x = self.thirdX
        y = self.thirdY
        yVel = self.thirdYvel
        z = self.thirdZ

        #update x acceleration
        self.thirdXacc = ( 2*yVel + x - ( (1-l)*(x-l)/( ( (x - l)**2 + y**2 + z**2 )**(3/2) ) ) - ( l*(x + 1 - l)/(( (x + 1 - l)**2 + y**2 + z**2 )**(3/2)) ) )

    def _calc_d2dy(self):
        """
        Calculate y acceleration
        
        """

        #get all values for calculation 
        l = self.l 
        x = self.thirdX 
        xVel = self.thirdXvel
        y = self.thirdY
        z = self.thirdZ

        #update y acceleration
        self.thirdYacc = ( y - 2*xVel - ( ((1-l)*y)/(( (x - l)**2 + y**2 + z**2 )**(3/2)) ) - (l * y)/(( (x + 1 - l)**2 + y**2 + z**2 )**(3/2)) )

    def _calc_d2dz(self):
        """
        Calculate z acceleration

        """

        #get all values for calculation 
        l = self.l 
        x = self.thirdX 
        y = self.thirdY
        z = self.thirdZ

        #update z acceleration
        self.thirdZacc = ( -(( (1-l)*z )/(( (x - l)**2 + y**2 + z**2 )**(3/2)) ) - ( (l*z)/(( (x + 1 - l)**2 + y**2 + z**2 )**(3/2)) ) )

Sim().on_execute()
