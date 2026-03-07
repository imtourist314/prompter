from enum import Enum


class FileStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERRORED = "ERRORED"
