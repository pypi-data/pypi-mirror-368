import logging
import logging.handlers
import time
from io import BytesIO
from queue import Queue

import requests

__all__ = ("StandaloneHandler", "ThreadedHandler")


class BaseHandler(logging.Handler):
    """⭐"""

    def __init__(self):
        """⭐"""
        super().__init__()

    def _request(self, method, **kwargs):
        """⭐"""
        try:
            response = self.session.post(self.url_template.format(method=method), **kwargs)
            response.raise_for_status()
        except Exception as exc:
            print("Can't send log telegram message: ", exc)

    def _send(self, text_content, **data):
        """⭐"""
        if len(text_content) < 4096:
            self._request("sendMessage", json={'text': text_content, **data})
        else:
            self._request(
                "sendDocument",
                data={"caption": text_content[:self.max_message_slice], **data},
                files={"document": (self.document_name, BytesIO(text_content.encode("UTF-8")), "text/plain")}
                )

    def _wait(self):
        """⭐"""

    def handle(self, record):
        """⭐"""
        record = self.format(record)
        self.emit(record)

    def emit(self, record):
        """⭐"""
        for chat_id in self.chat_ids:
            self._send(record, **{"chat_id": chat_id, **self.rq_data, **self.rq_params})
            self._wait()


class ThreadedSlaveHandler(BaseHandler):
    """⭐"""

    def __init__(
        self,
        token,
        chat_ids,
        disable_web_page_preview,
        disable_notification,
        parse_mode,
        max_message_slice,
        rps_limit,
        document_name,
        **rq_params
        ):
        """⭐"""
        self.chat_ids = chat_ids
        self.rq_params = rq_params
        self.max_message_slice = max_message_slice
        self.document_name = document_name
        self.rps_limit = rps_limit
        self.url_template = "https://api.telegram.org/bot{token}".format(token=token) + "/{method}"
        self.rq_data = {
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "parse_mode": parse_mode
            }
        self.session = requests.Session()
        super().__init__()

    def _wait(self):
        """⭐"""
        time.sleep(self.rps_limit)


class StandaloneHandler(BaseHandler):
    """⭐"""

    def __init__(
        self,
        token,
        chat_ids,
        disable_web_page_preview=False,
        disable_notification=False,
        parse_mode="html",
        max_message_slice=1024,
        rps_limit=0.03,
        document_name="log.txt",
        **rq_params
        ):
        """⭐"""
        self.chat_ids = chat_ids
        self.rq_params = rq_params
        self.max_message_slice = max_message_slice
        self.document_name = document_name
        self.rps_limit = rps_limit
        self.url_template = "https://api.telegram.org/bot{token}".format(token=token) + "/{method}"
        self.rq_data = {
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "parse_mode": parse_mode
            }
        self.session = requests.Session()
        super().__init__()


class ThreadedHandler(logging.handlers.QueueHandler):
    """⭐"""

    def __init__(
        self,
        token,
        chat_ids,
        disable_web_page_preview=False,
        disable_notification=False,
        parse_mode="html",
        max_message_slice=1024,
        rps_limit=0.03,
        document_name="log.txt",
        **rq_params
        ):
        """⭐"""
        queue: Queue = Queue()
        super().__init__(queue)
        handler = ThreadedSlaveHandler(
            token, chat_ids, disable_web_page_preview, disable_notification,
            parse_mode, max_message_slice, rps_limit, document_name, **rq_params
            )
        listener = logging.handlers.QueueListener(queue, handler)
        listener.start()
