# -*- coding: utf-8 -*-
import logging

__all__ = ("MarkdownFormatter", "HtmlFormatter")


class BaseFormatter(logging.Formatter):
    """⭐"""

    EMOJI_MAP = {
        logging.CRITICAL: '⚫',
        logging.ERROR: '🔴',
        logging.WARNING: '🟠',
        logging.INFO: '🔵',
        logging.DEBUG: '⚪',
        logging.NOTSET: '⚪'
    }

    def __init__(self, *args, **kwargs):
        """⭐"""
        super().__init__(*args, **kwargs)

    @staticmethod
    def escape_html(text):
        """⭐"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def format(self, record):
        """⭐"""
        super().format(record)
        if record.funcName:
            record.funcName = self.escape(str(record.funcName))
        if record.name:
            record.name = self.escape(str(record.name))
        if record.msg:
            record.msg = self.escape(record.getMessage())
        emoji = self.EMOJI_MAP[record.levelno]
        record.levelname = emoji + " #" + record.levelname
        return self._style.format(record)

    def formatException(self, *args, **kwargs):
        """⭐"""
        return f"{self.BLOCK_L}{self.escape(self.formatException(*args, **kwargs))}{self.BLOCK_R}"

    def formatStack(self, *args, **kwargs):
        """⭐"""
        return f"{self.BLOCK_L}{self.escape(self.formatStack(*args, **kwargs))}{self.BLOCK_R}"


class MarkdownFormatter(BaseFormatter):
    """⭐"""

    BLOCK_L = BLOCK_R = "```"

    @staticmethod
    def escape(s):
        """⭐"""
        return s


class HtmlFormatter(BaseFormatter):
    """⭐"""

    BLOCK_L, BLOCK_R = "<pre>", "</pre>"

    @staticmethod
    def escape(s):
        """⭐"""
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
