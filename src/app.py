from lib import *
from logic import AngleFinder
from painter import ArmPainter

# Create arm and target
arm = Arm([5.0, 5.0])
target = Point(0.0, 6.0)


finder = AngleFinder(arm, target)

painter = ArmPainter(arm)
start_point = Point(arm.joints[-1].pos.x + arm.link_lengths[-1], 0.0)
painter.markup(start_point, "green")
painter.markup(target, "red")
painter.show_canvas()


# visualisation loop
iterations = 500
for iteration in range(iterations):
    angles = finder.ik()
    arm.move(angles)
    painter.update()

painter.wait(5.0)
