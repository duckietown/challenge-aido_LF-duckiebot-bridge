import logging
import os

import rospy
from duckietown_msgs.msg import WheelsCmdStamped
from sensor_msgs.msg import CompressedImage

logger = logging.getLogger("ROSClient")
logger.setLevel(logging.DEBUG)


class ROSClient(object):
    def __init__(self):
        # Get the vehicle name, which comes in as HOSTNAME
        # TODO not sure about this
        self.vehicle = os.getenv("HOSTNAME")

        self.nsent_commands = 0
        self.nreceived_images = 0
        self.shutdown = False

        self.initialized = False

        # Initializes the node
        rospy.init_node("ROSClient")
        rospy.on_shutdown(self.on_shutdown)

        self.r = rospy.Rate(15)
        msg = "ROSClient initialized."
        logger.info(msg)

        self.cmd_pub = rospy.Publisher(
            "/{}/wheels_driver_node/wheels_cmd".format(self.vehicle), WheelsCmdStamped, queue_size=10
        )
        logger.info("publisher created")

        self.cam_sub = rospy.Subscriber(
            "/{}/camera_node/image/compressed".format(self.vehicle), CompressedImage, self._cam_cb
        )

        logger.info("subscriber created")

    def on_shutdown(self):
        self.shutdown = True
        msg = "ROSClient on_shutdown will send 0,0 command now."
        logger.info(msg)
        commands = {"motor_right": 0.0, "motor_left": 0.0}
        self.send_commands(commands)

    def _cam_cb(self, msg):
        """
        Callback to listen to last outputted camera image and store it
        """
        self.image = msg.data

        self.initialized = True

        if self.nreceived_images == 0:
            msg = "ROSClient received first camera image."
            logger.info(msg)
        self.nreceived_images += 1

    def send_commands(self, cmds):
        """
        Publishes the wheel commands to ROS
        """
        time = rospy.get_rostime()
        cmd_msg = WheelsCmdStamped()
        cmd_msg.header.stamp.secs = time.secs
        cmd_msg.header.stamp.nsecs = time.nsecs
        cmd_msg.vel_right = cmds["motor_right"]
        cmd_msg.vel_left = cmds["motor_left"]
        if self.nsent_commands == 0:
            msg = "ROSClient publishing first commands."
            logger.info(msg)

        self.cmd_pub.publish(cmd_msg)
        self.nsent_commands += 1
