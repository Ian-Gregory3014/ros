#!/usr/bin/env python
from __future__ import print_function
import sys
import math
import numpy as np

#ROS Imports
import rospy
from sensor_msgs.msg import Image, LaserScan
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
from std_msgs.msg import Float64


class reactive_follow_gap:
    def __init__(self):
        #Topics & Subscriptions,Publishers
        lidarscan_topic = '/scan'
        drive_topic = '/vesc/high_level/ackermann_cmd_mux/input/nav_0'
        ttc_topic = '/minimum_ttc'

        self.lidar_sub = rospy.Subscriber(lidarscan_topic, LaserScan, self.lidar_callback)
        self.drive_pub = rospy.Publisher(drive_topic, AckermannDriveStamped, queue_size=10)
        self.ttc_sub = rospy.Subscriber(ttc_topic, Float64, self.ttc_callback)
        
        self.active = True
        self.range_cutoff = 4.0
        self.bubble_size = 100

        self.steering_history = []
        self.max_history_size = 5
    
    def preprocess_lidar(self, ranges):
        """ Preprocess the LiDAR scan array. Expert implementation includes:
            1.Setting each value to the mean over some window
            2.Rejecting high values (eg. > 3m)
        """
        proc_ranges = list(ranges)
        proc_len = len(proc_ranges)
        mean = 0
        count = 0
        for i in range(proc_len):
            mean += proc_ranges[i]
            count += 1
            if count == 40:
                mean /= count
                for j in range(i-39, i+1):
                    if mean > self.range_cutoff:
                        proc_ranges[j] = np.inf
                    else:
                        proc_ranges[j] = mean
                mean = 0
                count = 0
        return proc_ranges

    def find_max_gap(self, free_space_ranges):
        """ Return the start index & end index of the max gap in free_space_ranges
        """
        fStart = 0
        fEnd = 0
        start = 270
        end = 0
        i = 270
        zero = False
        while i < 810:
            if free_space_ranges[i] > 0 and zero == False:
                start = i
                zero = True
            elif (free_space_ranges[i] == 0 and zero) or i == 809:
                zero = False
                end = i
                if (end-start) > (fEnd-fStart):
                    fStart = start
                    fEnd = end
                start = end
            i += 1
        return fStart, fEnd
    
    def find_best_point(self, start_i, end_i, ranges, closest, proc_ranges):
        """Start_i & end_i are start and end indicies of max-gap range, respectively
        Return index of best point in ranges
	Naive: Choose the furthest point within ranges and go there
        """
        center = start_i+((end_i-start_i)/2)
        best = -1
        for i in range(start_i, end_i):
            if best == -1:
                best = i
            if ranges[i] > ranges[best]:
                best = i
        inf_count = 0
        for i in range(50):
            if proc_ranges[best-i] == np.inf:
                inf_count += 1
            if proc_ranges[best+i] == np.inf:
                inf_count += 1
        if inf_count < 90:
            best = center
        return best

    def lidar_callback(self, data):
        """ Process each LiDAR scan as per the Follow Gap algorithm & publish an AckermannDriveStamped Message
        """
        if not self.active:
            return
        ranges = data.ranges
        proc_ranges = self.preprocess_lidar(ranges)

        #Find closest point to LiDAR
        closest = 0
        for j in range(270, 810):
            if ranges[j] < ranges[closest]:
                closest = j 
        #Eliminate all points inside 'bubble' (set them to zero) 
        for i in range(self.bubble_size):
            right = closest+i
            left = closest-i
            if right > len(ranges)-1:
                proc_ranges[0+(right-len(ranges))]
            else:
                proc_ranges[right] = 0
            if left < 0:
                proc_ranges[len(ranges)+left]
            else:
                proc_ranges[left] = 0
        #Find max length gap 
        start_i, end_i = self.find_max_gap(proc_ranges)
        #Find the best point in the gap 
        idx = self.find_best_point(start_i, end_i, ranges, closest, proc_ranges)
        fwd = math.pi
        angle = (idx/171.8873) - fwd
        sign = 1
        if angle < 0:
            sign = -1
        steering = 0.0
        if abs(angle) >= 0 and abs(angle) < 0.3:
            velocity = 0.8
        elif abs(angle) >= 0.3 and abs(angle) < 0.8:
            velocity = 0.8
        else:
            velocity = 0.6
        steering = steering * sign 
        steering = angle
        #Publish Drive message

        self.steering_history.append(steering)
        # self.speed_history.append(velocity)
        if len(self.steering_history) > self.max_history_size:
            self.steering_history.pop(0)
        steering_avg = sum(self.steering_history) / len(self.steering_history)

        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = rospy.Time.now()
        drive_msg.header.frame_id = "laser"
        drive_msg.drive.steering_angle = steering_avg
        drive_msg.drive.speed = velocity
        self.drive_pub.publish(drive_msg)
    
    def ttc_callback(self, msg):
        if msg.data < 0.3:
            self.stop_vehicle()
            self.active = False

    def stop_vehicle(self):
        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = rospy.Time.now()
        drive_msg.header.frame_id = "laser"
        drive_msg.drive.steering_angle = 0
        drive_msg.drive.speed = 0
        self.drive_pub.publish(drive_msg)
        rospy.logwarn("Car stopped due to low TTC")

def main(args):
    rospy.init_node("FollowGap_node", anonymous=True)
    rfgs = reactive_follow_gap()
    rospy.sleep(0.1)
    rospy.spin()

if __name__ == '__main__':
    main(sys.argv)

