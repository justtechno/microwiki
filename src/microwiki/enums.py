from enum import Enum

class WriteStatus(Enum):
    SUCCESS = "file succesfully writen"
    WRITE_NOT_PERMITTED = "writing this file is not permitted"
    IS_DIRERCTORY = "tried to write to the directory"
    NOT_ENOUGH_PLACE = "there are not enough place on disk to write changes"
    FAILED = "unexcepted error occured writing file"
    OS_FAILED = "unexcepted os error occured writing file"

