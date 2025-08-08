# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import logging
from queue import Queue
from threading import Thread
from time import sleep

from substrateinterface import SubstrateInterface


class ThreadWorker(Thread):

    queue: Queue = Queue()

    def __init__(self, *args, **kwargs):
        """
        Init a SubstrateInterface client adapter instance as a thread

        :param args: Positional arguments
        :param kwargs: Keywords arguments
        """
        super().__init__(*args, **kwargs)

    def run(self):
        """
        Started asynchronously with Thread.start()

        :return:
        """
        while True:
            # print("loop...")
            call, args, result = self.queue.get()
            result_ = dict()
            # print(call, args, result)
            if call == "--close--":
                logging.debug("Close queue thread on substrate_interface")
                break

            try:
                # logging.debug(f"threadsafe call to rpc method {method}")
                result_ = call(*args)
            except Exception as exception:
                logging.error(args)
                # logging.exception(exception)
                result.put(exception)
            # print(call.__name__, " put result ", result_)
            result.put(result_)
            # print("reloop...")

        logging.debug("SubstrateInterface connection closed and thread terminated.")

    def close(self):
        """
        Close connection

        :return:
        """
        # Closing the connection
        self.queue.put(("--close--", (), None))


class ThreadSafeSubstrateInterface(SubstrateInterface):
    """
    Override substrate_interface client class with a queue to be thread safe

    """

    # keep alive ping interval in seconds
    KEEP_ALIVE_INTERVAL = 30

    def __init__(self, *args, **kwargs):
        """
        Init a SubstrateInterface client adapter instance as a thread

        :param args: Positional arguments
        :param kwargs: Keywords arguments
        """
        # create and start thread before calling parent init (which makes a rpc_request!)
        self.thread = ThreadWorker()
        self.thread.start()
        self.subscription_pending = False

        try:
            super().__init__(*args, **kwargs)
        except ConnectionRefusedError as exception:
            self.thread.close()
            logging.exception(exception)
        else:
            self.keep_alive_flag = True
            self.keep_alive_interval_time = self.KEEP_ALIVE_INTERVAL
            # start keep alive thread
            self.keep_alive_thread = Thread(target=self.keep_alive_ping)
            self.keep_alive_thread.start()

    def keep_alive_ping(self):
        """
        Send a ping message to server to keep alive the websocket connection

        :return:
        """
        while self.keep_alive_flag is True:
            sleep(self.KEEP_ALIVE_INTERVAL / 100)
            self.keep_alive_interval_time -= self.KEEP_ALIVE_INTERVAL / 100
            if self.keep_alive_flag is False:
                logging.debug("Stop websocket keep alive thread")
                break
            if self.keep_alive_interval_time <= 0:
                self.keep_alive_interval_time = self.KEEP_ALIVE_INTERVAL
                result: Queue = Queue()
                logging.debug("Send websocket keep alive ping...")
                self.thread.queue.put(
                    (self.websocket.send, (json.dumps({"ping": 1}),), result)
                )
                logging.debug("Websocket keep alive pong %s received", result.get())

    def rpc_request(self, method, params, result_handler=None) -> dict:
        """
        Override rpc_request method to use threadsafe queue

        :param method: Name of the RPC method
        :param params: Params of the RPC method
        :param result_handler: Optional variable to receive results, default to None
        :return:
        """
        # print("queued rpc_request call !!")
        # if subscription...
        if result_handler is not None:
            # if no subscription in queue...
            if self.subscription_pending is False:
                # set flag
                self.subscription_pending = True
        else:
            if self.subscription_pending is True:
                return super().rpc_request(method, params, result_handler)

        # reset keep alive timer
        self.keep_alive_interval_time = self.KEEP_ALIVE_INTERVAL

        result: Queue = Queue()
        self.thread.queue.put(
            (super().rpc_request, (method, params, result_handler), result)
        )
        # print(self.thread.queue.get())
        # print('done calling %s' % method)
        return_ = result.get()
        # if request was with subscription...
        if self.subscription_pending is True:
            # end of subscription
            self.subscription_pending = False
        if isinstance(return_, Exception):
            raise return_
        return return_

    def close(self):
        logging.debug("Close RPC connection thread")
        self.keep_alive_flag = False
        self.thread.close()
