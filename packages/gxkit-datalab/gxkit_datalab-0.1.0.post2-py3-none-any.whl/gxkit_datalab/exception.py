"""
datalab 事件层
Version 0.1.0
"""
from enum import IntEnum


class ErrorCode(IntEnum):
    GENERAL = 2000
    CHECK = 2001
    CONVERT = 2002
    ALIGN = 2003
    MARK = 2004
    DETECT = 2005
    INTERP = 2006


class DataLabError(Exception):

    def __init__(self, message: str, *, code: int = ErrorCode.GENERAL):
        self.code = code
        self.message = message
        super().__init__(message)


class CheckError(DataLabError):
    def __init__(self, source: str, message: str = "check error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.CHECK)


class ConvertError(DataLabError):
    def __init__(self, source: str, message: str = "covert error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.CONVERT)


class AlignError(DataLabError):
    def __init__(self, source: str, message: str = "Data align error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.ALIGN)


class MarkError(DataLabError):
    def __init__(self, source: str, message: str = "Data mark error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.ALIGN)


class DetectError(DataLabError):
    def __init__(self, source: str, message: str = "Data detect error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.DETECT)


class InterpolateError(DataLabError):
    def __init__(self, source: str, message: str = "Data interpolate error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.INTERP)
