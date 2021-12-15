![stats](https://wakatime.com/badge/user/75e033f5-beb6-4359-afae-db8209348d42/project/bc9c7ddb-8dfa-482e-ae44-35eeb5e77b9c.svg)

# Third Body Problem

This is a simulation of a three-body problem where we are in the frame of reference of two bodies that satisfy the 2-body problem (they orbit each other and we rotate with them) and we are examining the behavior of third-body of negligible mass (In the simulation, the blue body is the third body and the two red ones, are the other two). 

## Running The Simulation

First, make sure you have dependencies installed. To do this, when in the directory you can run:
``` pip install -r "dependencies.txt" ```

Running ``` python main.py ``` will then just run the simulation (this will open a new window, hopefully this scales fine?)

## Information For Simulation 

In the top left corner of the screen, there is all the information about the third body. Coordinates, velocities, and accelerations. In the top right, there are text entry boxes for changing initial values. Typing valid floats into each text box will be accepted. The initial x, y, z as well as x velocity, y velocity, and z velocity will change those values when starting the simulation over. The "lambda" value is a unitless value that changes relative masses of the two bodies (0 < lambda < 1). **In order to restart the simulation, press the: / key (or ? key)**. Restarting the simulation will start over at the initial conditions specified in the input boxes (it will crash if these can't convert to floats). 

Lagrange points are an important part of this simulation. In order to start over at a lagrange point, simply type in 1, 2, 3, 4, or 5 into the "Lagrange Point" input box. Restarting the simlation as specified above will then start the third body at a lagrange point. If you want to examine how slight errors in the lagrange point correspond to the point being unstable, you can specify the error you want in any direction in the error boxes below (even an error of 10^(-7) is noticable). 

Finally, if you want to change the scale, which could be necessary depending on the resolution of your monitor, simply change the number in the "scale" input box. The smaller the number, the more zoomed out the simulation will be. Once you change the number to the scale you want (must be convertible to an integer), **Press the ` key (or ~ key) in order to reset the scale**. This will not affect the simulation. 