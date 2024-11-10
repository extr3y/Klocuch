import numpy as np
import matplotlib.pyplot as plt

from lib import *


class ArmPainter:

    def __init__(self, arm: Arm, center = Point(0.0, 0.0)):
        self.arm = arm
        self.center = center

        # trigger interactive mode to enable repainting
        plt.ion()
        self.fig, self.ax = plt.subplots()

        self.line = self.setup()

    """
    Initial setup; summons an arm parallel to the X axis
    Returns mutable plot data
    """
    def setup(self):
        x, y = self.point_array_to_coord_lists()
        line, = self.ax.plot(x, y)

        # defines plot limits
        size = 10
        self.ax.set_xlim(-size, size)
        self.ax.set_ylim(-size, size)
        plt.pause(1)

        return line

    """
    Calculates the position of joints and the end effector (point designed to make contact with the target)
    Returns: list of x and y coordinates used for plotting
    """
    def point_array_to_coord_lists(self):
        x = []
        y = []
 
        for joint in self.arm.joints:
            x.append(joint.pos.x)
            y.append(joint.pos.y)
            
        x.append(self.arm.joints[-1].pos.x + np.cos(self.arm.joints[-1].angle) * self.arm.joints[-1].link)
        y.append(self.arm.joints[-1].pos.y + np.sin(self.arm.joints[-1].angle) * self.arm.joints[-1].link)
        
        return (x, y)
    
    """
    Refreshes the plot
    """
    def update(self):

        x, y = self.point_array_to_coord_lists()

        self.line.set_xdata(x)
        self.line.set_ydata(y)

        # recalculates plot's limits
        self.ax.relim()
        # updates axes based on new data
        self.ax.autoscale_view(True, True, True)  
        # redraws the plot
        plt.draw()
    
        # pause for a second to simulate real-time updating
        plt.pause(0.1)

    """
    Displays the plot
    """
    def show_canvas(self):
        plt.show()

    """
    Plots a single point of interest (eg. the target)
    Accepts the point's position, color and size values 
    """
    def markup(self, point: Point, color: str, s = 35):
        self.ax.scatter(point.x, point.y, s = s, color = color)

    """
    Shuts down plotting
    """
    def close(self):
        plt.ioff()
        plt.close()

    def wait(self, time: float):
        plt.pause(time)
