from enum import Enum


class RecordType(str, Enum):
    theory = "theory"
    lab = "lab"


class Status(str, Enum):
    present = "present"
    absent = "absent"
