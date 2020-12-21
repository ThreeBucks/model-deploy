import os
import socket
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Alarm:
    def __init__(self, project_name):
        self.monitor_name = "icpm_auto_deploy_timeout"
        self.project_name = project_name
        self.ip = socket.gethostbyname(socket.gethostname())

    def send(self, message, error_code):
        try:
            command = ["/monitor/tools/send_metrics", self.monitor_name, str(error_code), "ip="+str(self.ip),
                "project_name="+self.project_name, "alarm_message="+str(message)]
            subprocess.run(command)
            logger.info('Send alarm metrics to {}'.format(self.monitor_name))
        except Exception as err:
            logger.error("Could not send alarm, error info:{}".format(err))
