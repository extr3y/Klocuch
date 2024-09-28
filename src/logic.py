import numpy as np
import copy

from lib import *


class AngleFinder:
    
    def __init__(self, arm: Arm, target: Point):
        self.arm = arm
        self.target = target

    """
    Checks whether the desired target escapes the arm's reach
    """
    def within_reach_2D(self):
        required_reach = np.sqrt(self.target.x ** 2 + self.target.y ** 2)
        return abs(self.arm.link_lengths[0] - self.arm.link_lengths[1]) <= required_reach <= sum(self.arm.link_lengths)
    
    """
    Returns the current position of the effector
    """
    def current_pos(self):
        return self.fk(self.arm.joints, [joint.angle for joint in self.arm.joints])
    
    """
    Returns current joint angles as a python array
    """
    def current_angles(self):
        return [joint.angle for joint in self.arm.joints]
    
    """
    Multiplies the jacobian p-inverse and the error vector
    (difference between target and current position)
    Returns approximate end angles
    """
    def find_angles(self, jacobian_pinv):
        # convert from point class to np.array
        error_vector = np.array([self.target.x - self.current_pos().x, self.target.y - self.current_pos().y])
        angles = jacobian_pinv @ error_vector
        print(angles)
        return angles

    """
    Jacobian calculation. Returns a matrix
    """
    def jacobian(self):
        # small change in angles to approximate derivatives
        dTheta = 0.001

        # get the current end-effector position using FK
        actual_pos = self.current_pos()

        # adjust the angles with respect to the assumption of linearity
        angles1 = self.current_angles()
        angles1[0] += dTheta
        angles2 = self.current_angles()
        angles2[1] += dTheta

        # calculate hypothetical positions of the arm after adjusting a
        # single joint at a time
        pos_delta_theta1 = self.fk(copy.deepcopy(self.arm.joints), angles1)
        pos_delta_theta2 = self.fk(copy.deepcopy(self.arm.joints), angles2)

        # construct the jacobian matrix
        jacobian = np.array([
            [(pos_delta_theta1.x - actual_pos.x) / dTheta, (pos_delta_theta2.x - actual_pos.x) / dTheta],
            [(pos_delta_theta1.y - actual_pos.y) / dTheta, (pos_delta_theta2.y - actual_pos.y) / dTheta]
        ])

        print(jacobian)
        return jacobian


    """
    Wrapper for jacobian calculations
    Returns angles array
    """
    def ik(self):
        if self.within_reach_2D():
            # obtain the jacobian
            jacobian = self.jacobian()
            # calculate the Moore-Penrose inversion
            jacobian_pinv = np.linalg.pinv(jacobian)
            # find new approximate angles
            angles = self.find_angles(jacobian_pinv)
            return angles
        else:
            print("Target out of reach")
            return None
        
    """
    Calculates the position of the effector given new angles
    Returns Point
    """
    def fk(self, joints, angles):
        total_angle = 0.0
        x, y = self.arm.origin.x, self.arm.origin.y

        for joint, angle in zip(joints, angles):
            total_angle += angle
            joint.angle = total_angle

            joint.pos.x = x
            joint.pos.y = y

            x += np.cos(joint.angle) * joint.link
            y += np.sin(joint.angle) * joint.link

        # return end position of an effector
        result = Point(x, y)

        return result




