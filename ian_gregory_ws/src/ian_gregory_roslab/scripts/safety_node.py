#!/usr/bin/env python

import math
import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64
from ackermann_msgs.msg import AckermannDriveStamped

class Safety:
    def __init__(self):
        self.initial_speed = 3.0
        self.current_speed = self.initial_speed
        self.aeb_threshold = 0.1
        self.min_ttc_pub = rospy.Publisher("/minimum_ttc", Float64, queue_size=10)
        self.aeb_threshold_pub = rospy.Publisher("/aeb_threshold", Float64, queue_size=10)
        self.active = True

        self.speed_pub = rospy.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1000)

        self.scan_sub = rospy.Subscriber("/scan", LaserScan, self.scan_callback)
        self.odom_sub = rospy.Subscriber("/vesc/odom", Odometry, self.odom_callback)

        self.drive_msg = AckermannDriveStamped()

        #rospy.loginfo("Safety node initialized, starting with speed: %s", self.initial_speed)

    def odom_callback(self, odom_msg):
        self.current_speed = odom_msg.twist.twist.linear.x
        #rospy.logdebug("Current speed updated: %s", self.current_speed)

    def scan_callback(self, scan_msg):
        if not self.active:
            return 
        
        ttc_msg = Float64()
        current_angle = scan_msg.angle_min
        min_ttc = float('inf')

        if self.current_speed != 0.0:
            for dist in scan_msg.ranges:
                if scan_msg.range_min <= dist <= scan_msg.range_max and self.current_speed * math.cos(current_angle) > 0:
                    current_scan_ttc = dist / (self.current_speed * math.cos(current_angle))
                    if current_scan_ttc < min_ttc:
                        min_ttc = current_scan_ttc
                        ttc_msg.data = min_ttc

                current_angle += scan_msg.angle_increment

        #rospy.loginfo("Minimum TTC: %s", min_ttc)
        self.min_ttc_pub.publish(min_ttc)
        self.aeb_threshold_pub.publish(Float64(self.aeb_threshold))
        if min_ttc <= self.aeb_threshold:
            #rospy.loginfo("AEB threshold reached, stopping vehicle.")
            self.control_vehicle(0.0)
            self.active = False
        else:
            self.control_vehicle(self.initial_speed)

    def control_vehicle(self, speed):
        if not self.active:
            return 
        self.drive_msg.header.stamp = rospy.Time.now()
        self.drive_msg.drive.speed = speed
        self.drive_msg.drive.steering_angle = 0.0
        #self.speed_pub.publish(self.drive_msg)
        rospy.logdebug("Published speed: %s", speed)

def main():
    rospy.init_node("safety_node", log_level=rospy.INFO)
    sn = Safety()
    rospy.spin()

if __name__ == '__main__':
    main()
