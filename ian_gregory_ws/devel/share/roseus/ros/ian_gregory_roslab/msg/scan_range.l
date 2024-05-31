;; Auto-generated. Do not edit!


(when (boundp 'ian_gregory_roslab::scan_range)
  (if (not (find-package "IAN_GREGORY_ROSLAB"))
    (make-package "IAN_GREGORY_ROSLAB"))
  (shadow 'scan_range (find-package "IAN_GREGORY_ROSLAB")))
(unless (find-package "IAN_GREGORY_ROSLAB::SCAN_RANGE")
  (make-package "IAN_GREGORY_ROSLAB::SCAN_RANGE"))

(in-package "ROS")
;;//! \htmlinclude scan_range.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass ian_gregory_roslab::scan_range
  :super ros::object
  :slots (_header _range_min _range_max _angle_min _angle_max ))

(defmethod ian_gregory_roslab::scan_range
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:range_min __range_min) 0.0)
    ((:range_max __range_max) 0.0)
    ((:angle_min __angle_min) 0.0)
    ((:angle_max __angle_max) 0.0)
    )
   (send-super :init)
   (setq _header __header)
   (setq _range_min (float __range_min))
   (setq _range_max (float __range_max))
   (setq _angle_min (float __angle_min))
   (setq _angle_max (float __angle_max))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:range_min
   (&optional __range_min)
   (if __range_min (setq _range_min __range_min)) _range_min)
  (:range_max
   (&optional __range_max)
   (if __range_max (setq _range_max __range_max)) _range_max)
  (:angle_min
   (&optional __angle_min)
   (if __angle_min (setq _angle_min __angle_min)) _angle_min)
  (:angle_max
   (&optional __angle_max)
   (if __angle_max (setq _angle_max __angle_max)) _angle_max)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; float32 _range_min
    4
    ;; float32 _range_max
    4
    ;; float32 _angle_min
    4
    ;; float32 _angle_max
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; float32 _range_min
       (sys::poke _range_min (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _range_max
       (sys::poke _range_max (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _angle_min
       (sys::poke _angle_min (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _angle_max
       (sys::poke _angle_max (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; float32 _range_min
     (setq _range_min (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _range_max
     (setq _range_max (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _angle_min
     (setq _angle_min (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _angle_max
     (setq _angle_max (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get ian_gregory_roslab::scan_range :md5sum-) "aada86769d7aab743bbb3d0fa41ba261")
(setf (get ian_gregory_roslab::scan_range :datatype-) "ian_gregory_roslab/scan_range")
(setf (get ian_gregory_roslab::scan_range :definition-)
      "Header header
float32 range_min
float32 range_max
float32 angle_min
float32 angle_max

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

")



(provide :ian_gregory_roslab/scan_range "aada86769d7aab743bbb3d0fa41ba261")


