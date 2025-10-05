import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from functools import partial
from statistics import mean
import time


class Controller:
    def __init__(self, P, D, set_point):
        self.Kp = P
        self.Kd = D
        self.set_point = set_point
        self.previous_error = 0.0

    def update(self, current_value):
        error = self.set_point - current_value
        P_term = self.Kp * error
        D_term = self.Kd * (error - self.previous_error)
        self.previous_error = error
        return P_term + D_term

    def setPoint(self, set_point):
        self.set_point = set_point
        self.previous_error = 0.0


class ObstacleAvoidanceNode(Node):
    def __init__(self):
        self.safe_distance = 0.6
        super().__init__("obstacle_avoidance")
        self.publisher_ = self.create_publisher(Twist, "cmd_vel", 10)
        distance_controller = Controller(P=0.75, D=0.05, set_point=self.safe_distance)
        angle_controller = Controller(P=0.75, D=0.05, set_point=self.safe_distance)
        self.front_readings = []
        self.mode = "moving"

        self.subscription = self.create_subscription(
            LaserScan,
            "scan",
            partial(self.laser_callback, distance_controller, angle_controller),
            10,
        )

    def laser_callback(self, distance_controller, angle_controller, msg):
        velocity_msg = Twist()
        velocity_msg.linear.x = 0.0
        velocity_msg.linear.z = 0.0
        self.publisher_.publish(velocity_msg)

        front_distance = msg.ranges[0]

        self.front_readings.append(front_distance)
        front_distance = mean(self.front_readings)
        # Keep only the last 5 readings
        self.front_readings = self.front_readings[-3:]

        front_error = front_distance - self.safe_distance

        if self.mode == "following":
            right = msg.ranges[269]

            print("turning")

            velocity_msg.angular.z = 1.5708
            self.publisher_.publish(velocity_msg)
            # time.sleep(0.5)
            angle_controller.setPoint(self.safe_distance)
            self.mode = "moving"
            return

        if front_error <= 0.1:
            self.mode = "following"
            return

        linear_velocity = distance_controller.update(front_distance)

        velocity_msg.linear.x = abs(linear_velocity)

        self.publisher_.publish(velocity_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Manually stopped the node.")
    finally:
        if rclpy.ok():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
