#!/usr/bin/env python2
import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64
from ian_gregory_roslab.msg import scan_range

pub1 = rospy.Publisher('closest_point', Float64, queue_size=10)
pub2 = rospy.Publisher('farthest_point', Float64, queue_size=10)
pub3 = rospy.Publisher('scan_range', scan_range, queue_size=10)

def callback(scan):
    global pub1
    global pub2
    global pub3

    pub1.publish(scan.range_min)
    pub2.publish(scan.range_max)

    message = scan_range()
    message.range_min = scan.range_min
    message.range_max = scan.range_max
    message.angle_min = scan.angle_min
    message.angle_max = scan.angle_max
    pub3.publish(message)

def scanner():
    rospy.init_node('scanner', anonymous=True)
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()

if __name__ == '__main__':
    scanner()
