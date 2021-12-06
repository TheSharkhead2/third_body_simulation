#external library import
import pygame, sys
from pygame.locals import *
from screeninfo import get_monitors #found in: https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python

class Sim:

    windowWidth = int(get_monitors()[0].width)
    windowHeight = int(get_monitors()[0].height)-100

    def __init__(self):
        self._running = True
        self._display = None

        #define "center pixel" coordinates
        self.centerX = int(self.windowWidth/2)
        self.centerY = int(self.windowHeight/2)

        self.body1X = -1 
        self.body2X = 1

        self.thirdRadius = 10 #radius of circle (third body rendered)
        self.thirdColor = (0, 0, 255) #color of third body

        self.tPerFrame = 100 #number of delta Ts renders per frame
        self.deltaT = 0.0001 #define standard time increment 

        #set scales from x and y coords to pygame coords
        self.xScale = 100
        self.yScale = 100

        self.l = 0.8 #define the lambda for the equations. 0 < lambda < 1

        #set initial conditions for initial x and x velocity and y and y velocity and z and z velocity
        self.thirdX = 1.6
        self.thirdXvel = 0
        self.thirdY = -1
        self.thirdYvel = 1
        self.thirdZ = -0.1
        self.thirdZvel = 0

        #empty variables for accelerations
        self.thirdXacc = None
        self.thirdYacc = None
        self.thirdZacc = None

        #define coordinates for third body in pygame. Center pixel plus the starting positions scaled by x and y scales
        self.thirdRenderX = self.centerX + self.xScale * self.thirdX
        self.thirdRenderY = self.centerY + self.yScale * self.thirdY


    def on_init(self):
        pygame.init()
        self._display = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
        pygame.display.set_caption("Third Body Simulation")

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False


    def on_loop(self):
        
        for i in range(self.tPerFrame): #run position updates set number of times
            #update accelerations for x, y, and z 
            self._calc_d2dx()
            self._calc_d2dy()
            self._calc_d2dz()

            #update positions and velocities 
            self.thirdX,self.thirdXvel = self._updateX(self.thirdX, self.thirdXvel, self.thirdXacc, t=self.deltaT)
            self.thirdY,self.thirdYvel = self._updateX(self.thirdY, self.thirdYvel, self.thirdYacc, t=self.deltaT)
            self.thirdZ,self.thirdZvel = self._updateX(self.thirdZ, self.thirdZvel, self.thirdZacc, t=self.deltaT)

        #update pygame render coords
        self._update_pygame_coords()        

    def on_render(self):
        testFont = pygame.font.SysFont('Times New Roman', 20)
        self._display.fill((0,0,0))
        self._display.blit(testFont.render("Best Planet", True, (255, 255, 255)), (20, 20))
        
        #render third body coords 
        self._display.blit(testFont.render("Third body x = {}".format(self.thirdX), True, (255, 255, 255)), (20, 40))
        self._display.blit(testFont.render("Third body y = {}".format(self.thirdY), True, (255, 255, 255)), (20, 60))
        self._display.blit(testFont.render("Third body z = {}".format(self.thirdZ), True, (255, 255, 255)), (20, 80))

        #render first and second body 
        pygame.draw.circle(self._display, (255,0,0), ( self.centerX + self.body1X*self.xScale, self.centerY ), self.thirdRadius*2 )
        pygame.draw.circle(self._display, (0, 255,0), ( self.centerX + self.body2X*self.xScale, self.centerY ), self.thirdRadius*2 )

        #render third body
        pygame.draw.circle(self._display, self.thirdColor, (self.thirdRenderX, self.thirdRenderY), self.thirdRadius)

    def on_quit(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        pygame.display.flip()
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            pygame.display.update()
        self.on_quit()

    def _update_pygame_coords(self):
        """
        With new x, y, and z coordinates for planet, update coordinates in pygame
        for rendering
        
        """

        #update pygame coordinates for third body. Center pixel plus x and y coords multiplied by scaler
        self.thirdRenderX = self.centerX + self.xScale * self.thirdX 
        self.thirdRenderY = self.centerY + self.yScale * self.thirdY

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
