import logging

import sys
import time
from custom_exceptions import ToRaiseException
import docker
import boto3
import botocore.errorfactory


class Runner(object):
    """Runner is responsible for running the container and sending the logs to cloudwatch"""

    def __init__(
        self,
        image_name,
        command,
        cw_group,
        cw_stream,
        aws_access_key,
        aws_secret_key,
        region,
        retention_policy=7,
        debug=False,
    ):
        self.image_name = image_name
        self.command = command
        self.cw_group = cw_group
        self.cw_stream = cw_stream
        self.cw_retention_policy = retention_policy
        self.region = region
        self._container = None
        self._client = docker.from_env()
        self._unsend_logs = []
        if debug:
            logging.root.setLevel(logging.NOTSET)
        self._log_client = boto3.client(
            "logs",
            region_name=self.region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

    def setup(self):
        """Setup will try to create the group and the stream with the given names.
        In case of group or stram existance, it will continue the program accordingly
        In case of another error, it will raise ToRaiseException and retries the code after a few seconds"""
        try:
            res = self._log_client.create_log_group(logGroupName=self.cw_group)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                pass
            elif error.response["Error"]["Code"] == "UnrecognizedClientException":
                raise Exception("Invalid credentials")
            else:
                raise ToRaiseException()
        except Exception as e:
            raise ToRaiseException()

        try:
            res = self._log_client.create_log_stream(
                logGroupName=self.cw_group, logStreamName=self.cw_stream
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                pass
            else:
                raise ToRaiseException()
        except Exception as e:
            raise ToRaiseException()

        try:
            res = self._log_client.put_retention_policy(
                logGroupName=self.cw_group, retentionInDays=self.cw_retention_policy
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                pass
            else:
                raise ToRaiseException()
        except Exception as e:
            raise ToRaiseException()

    def send_logs(self):
        """send_log is responsible for sending the container logs to cloudwatch.
        It will store the logs in an array and tries to send the array to cloudwatch
        If the proccess was successfull, it will reset the _unsend_logs list
        If not, it will keep all the unsend logs and it will try to send them again
        with the next log"""
        for line in self._container.logs(stream=True):
            self._unsend_logs.append(
                {"timestamp": int(time.time()), "message": str(line)}
            )
            try:
                res = self._log_client.put_log_events(
                    logGroupName=self.cw_group,
                    logStreamName=self.cw_stream,
                    logEvents=self._unsend_logs,
                )
                logging.debug(f" [!] Sent {len(self._unsend_logs)} logs to server")
                self._unsend_logs = []
            except Exception as e:
                logging.error(
                    f" [*] Got an error while tried to add {len(self._unsend_logs)} logs: {e}"
                )

    def main(self):
        """Main is responsible for running the runner.
        It is going to setup the credentials and also it will create the
        the group and stream.
        After that it will run the container in detached mode
        after tht it will send the logs to cloudwatch.
        """
        self.setup()
        # TODO: get the enviroment variables as an argument too
        self._container = self._client.containers.run(
            self.image_name,
            self.command,
            environment=["PYTHONUNBUFFERED=1"],
            detach=True,
        )
        self.send_logs()

    def reset(self):
        """resets the container by first stopping it and then removing it"""
        try:
            self._container.stop()
            self._container.remove()
        except Exception:
            pass
        finally:
            self._container = None

    def runner(self):
        """runner method is responsible for running the program. It will prevent the program to crash in case of some specific errors"""
        while True:
            try:
                self.main()
                break
            except KeyboardInterrupt:
                """In case of keyboard intrupt, We assume that the user wants to remove the container. So we reset it."""
                logging.error(
                    " [*] Interrupted, Don't pres anything. The program is removing the container"
                )
                self.reset()
                sys.exit(0)
            except ToRaiseException:
                """In case of ToRaiseException, we need to wait for a while and after that we should reset the container and then run the program again"""
                time.sleep(30)
                self.reset()
                continue
            except Exception as e:
                logging.error(f" [*] Program exited with an error: {e}")
                self.reset()
                sys.exit(1)
