#!/usr/bin/env python
import rospy, rospkg
from duckietown_msgs.msg import WheelsCmdStamped
from kinematics import Duty_fi_function
from numpy import *
import csv

# Trajectory Recording Node
# Authors: Jason Pazis

class TrajectoryRecordingNode(object):
    def __init__(self):
        self.node_name = 'trajectory_recording_node'

        self.prev_wheels_cmd = None
        self.FI = zeros((2,2))

        # Read parameters
        self.veh_name = self.setupParameter("~veh_name","megaman")
        self.filename = self.setupParameter("~FIfile","FIfile")
        self.fi_theta_dot_function = self.setupParameter('~fi_theta_dot_function_param', 'Duty_fi_theta_dot_compound_linear')
        self.fi_v_function = self.setupParameter('~fi_v_function_param', 'Duty_fi_v_compound_linear')

        #Setup the subscriber
        self.sub_wheels_cmd = rospy.Subscriber("~wheels_cmd", WheelsCmdStamped, self.wheelsCmdCallback)

        rospy.loginfo("[%s] has started", self.node_name)


    def wheelsCmdCallback(self, msg_wheels_cmd):
        # We can't compute dt when we receive the first message
        if self.prev_wheels_cmd is not None:
            dt = msg_wheels_cmd.header.stamp.to_sec() - self.prev_wheels_cmd.header.stamp.to_sec()
            theta_dot_fi = self.fi_theta_dot_function.computeFi(msg_wheels_cmd.vel_left, msg_wheels_cmd.vel_right)
            v_fi = self.fi_v_function.computeFi(msg_wheels_cmd.vel_left, msg_wheels_cmd.vel_right)

            self.FI[0,:] = self.FI[0,:] + dt*theta_dot_fi
            self.FI[1,:] = self.FI[1,:] + dt*v_fi
        self.prev_wheels_cmd = msg_wheels_cmd
        
    # Save accumulated FI
    def saveFI(self):
        savetxt(self.filename, self.FI)


    def setupParameter(self,param_name,default_value):
        value = rospy.get_param(param_name,default_value)
        rospy.set_param(param_name,value) #Write to parameter server for transparancy
        rospy.loginfo("[%s] %s = %s " %(self.node_name,param_name,value))
        return value


if __name__ == '__main__':
    rospy.init_node('trajectory_recording_node', anonymous=False)
    trajectory_recording_node = TrajectoryRecordingNode()
    rospy.on_shutdown(trajectory_recording_node.saveFI)
    rospy.spin()
