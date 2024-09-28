import numpy as np
from dataclasses import dataclass

@dataclass
class Point:
    x: float        
    y: float

@dataclass
class Joint:
    pos: Point      # position of the joint
    angle: float    # angle of rotation with respect to the OX axis
    link: float     # length of the link attached to the front of the joint

class Arm:

    def __init__(self, link_lengths: list[float], origin = Point(0.0, 0.0)):
        self.link_lengths = link_lengths
        self.origin = origin
        self.joints: list[Joint] = []
        self.calculate_joints()

    """
    Recalculates the joint's parameters with the use of new angle values 
    """
    def move(self, angles):
        total_angle = 0.0
        x, y = self.origin.x, self.origin.y

        for joint, angle in zip(self.joints, angles):
            total_angle += angle
            joint.angle = total_angle

            joint.pos.x = x
            joint.pos.y = y

            x += np.cos(joint.angle) * joint.link
            y += np.sin(joint.angle) * joint.link

    """
    Initializes the arm as flush with the ground; expanding along the +X half-axis
    """
    def calculate_joints(self):
        last_pos = self.origin
        last_length = 0.0

        for length in self.link_lengths:
            new_pos = Point(last_pos.x + last_length, last_pos.y)
            new_angle = 0.0
            self.joints.append(Joint(new_pos, new_angle, length))
            last_pos = new_pos
            last_length = length
