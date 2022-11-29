#!/usr/bin/env python2

import logging
import signal
import sys
import time


import numpy as np

from rosclient import ROSClient
from zuper_nodes_python2 import ComponentInterface

logger = logging.getLogger("DuckiebotBridge")
logger.setLevel(logging.DEBUG)


class DuckiebotBridge(object):
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        AIDONODE_DATA_IN = "/fifos/agent-in"
        AIDONODE_DATA_OUT = "/fifos/agent-out"
        logger.info("DuckiebotBridge starting communicating with the agent.")
        self.ci = ComponentInterface(AIDONODE_DATA_IN, AIDONODE_DATA_OUT, "agent", timeout=30)
        self.ci.write_topic_and_expect_zero("seed", 32)
        self.ci.write_topic_and_expect_zero("episode_start", {"episode_name": "episode"})
        logger.info("DuckiebotBridge successfully sent to the agent the seed and episode name.")
        self.client = ROSClient()
        logger.info("DuckiebotBridge has created ROSClient.")

    def exit_gracefully(self, signum, frame):
        logger.info("DuckiebotBridge exiting gracefully.")
        sys.exit(0)

    def run(self):
        nimages_received = 0
        t0 = time.time()
        t_last_received = None
        while True:
            if not self.client.initialized:
                if nimages_received == 0:
                    elapsed = time.time() - t0
                    msg = "DuckiebotBridge still waiting for the first image: elapsed %s" % elapsed
                    logger.info(msg)
                    time.sleep(0.5)
                else:
                    elapsed = time.time() - t_last_received
                    if elapsed > 2:
                        msg = "DuckiebotBridge has waited %s since last image" % elapsed
                        logger.info(msg)
                        time.sleep(0.5)
                    else:
                        time.sleep(0.01)
                continue

            np_arr = np.fromstring(self.client.image, np.uint8)
            data = np_arr.tostring()
            if nimages_received == 0:
                logger.info("DuckiebotBridge got the first image from ROS.")

            obs = {"camera": {"jpg_data": data}}
            self.ci.write_topic_and_expect_zero("observations", obs)
            commands = self.ci.write_topic_and_expect("get_commands", expect="commands")
            commands = commands.data["wheels"]

            self.client.send_commands(commands)
            if nimages_received == 0:
                logger.info("DuckiebotBridge published the first commands.")

            nimages_received += 1
            t_last_received = time.time()


def main():
    node = DuckiebotBridge()
    node.run()


if __name__ == "__main__":
    main()
