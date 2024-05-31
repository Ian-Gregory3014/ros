#!/usr/bin/env python

import rospy
import math
from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped
from std_msgs.msg import Float64

class WallFollow:
    def __init__(self):
        # Initialize ROS node
        rospy.init_node("wall_follow_node", anonymous=True)

        # PID PARAMETERS
        self.kp = 0.6
        self.kd = 0.3
        self.ki = 0.00001
        self.prev_error = 0.0
        self.integral = 0.0

        # WALL FOLLOW PARAMS
        self.desired_distance_left = 0.5
        self.velocity = 1.9
        self.safety_threshold = 0.3

        # Subscribers and Publishers
        self.drive_pub = rospy.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        self.lidar_sub = rospy.Subscriber("/scan", LaserScan, self.lidar_callback)
        self.ttc_sub = rospy.Subscriber("/minimum_ttc", Float64, self.ttc_callback)
        self.wall_dist_pub = rospy.Publisher("/wall_distance", Float64, queue_size=10)
        self.desired_dist_pub = rospy.Publisher("/desired_distance", Float64, queue_size=10)
        self.wall_dist = Float64()
        self.desired_dist = Float64()
        self.desired_dist = self.desired_distance_left

        # Active flag to control the vehicle motion
        self.active = True

    def get_range(self, data, angle):
        """ Compute the range at a given angle from LIDAR data """
        angle_radians = angle * (math.pi / 180.0)
        index = int((angle_radians - data.angle_min) / data.angle_increment)
        if index < 0 or index >= len(data.ranges):
            return float('inf')
        return data.ranges[index]

    def follow_left(self, data):
        """ Calculate the PID error based on the desired following distance """
        angle_a = 45  
        angle_b = 90 
        a = self.get_range(data, angle_a)
        b = self.get_range(data, angle_b)
        alpha = math.atan2(a * math.cos(math.radians(45)) - b, a * math.sin(math.radians(45)))
        D_t = b * math.cos(alpha)
        L = 0.9 + (self.velocity * 0.11)  
        D_tplus1 = D_t + L * math.sin(alpha)
        error = self.desired_distance_left - D_tplus1

        self.wall_dist = D_t
        self.wall_dist_pub.publish(self.wall_dist)  
        self.desired_dist_pub.publish(self.desired_dist)
        return error

    def pid_control(self, error):
        """ Apply PID control to compute the steering angle and vehicle speed """
        if not self.active:
            return
        
        self.integral += error * self.ki
        derivative = (error - self.prev_error)
        angle = -(self.kp * error + self.ki * self.integral + self.kd * derivative)
        self.prev_error = error

        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = rospy.Time.now()
        drive_msg.drive.speed = self.velocity
        drive_msg.drive.steering_angle = angle
        self.drive_pub.publish(drive_msg)

    def ttc_callback(self, msg):
        rospy.logdebug("Received TTC: {:.2f}, Threshold: {:.2f}".format(msg.data, self.safety_threshold))
        if msg.data < self.safety_threshold:
            rospy.logwarn("TTC below threshold, stopping vehicle.")
            self.active = False
            self.stop_vehicle()

    def stop_vehicle(self):
        rospy.loginfo("Publishing stop command.")
        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = rospy.Time.now()
        drive_msg.drive.speed = 0
        drive_msg.drive.steering_angle = 0
        self.drive_pub.publish(drive_msg)
        rospy.loginfo("Stop command published: Speed = 0, Angle = 0")

    def lidar_callback(self, data):
        """ Handle LIDAR data updates """
        if self.active:
            error = self.follow_left(data)
            self.pid_control(error)
        else:
            return

if __name__ == '__main__':
    wf = WallFollow()
    rospy.spin()
