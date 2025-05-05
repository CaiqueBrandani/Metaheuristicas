from enum import Enum


# Matérias com esses status recebem o valor 0 no .csv
class ApprovedStatus(Enum):
    APR = "APR"
    APRN = "APRN"
    CUMP = "CUMP"
    DISP = "DISP"
    TRANS = "TRANS"
    INCORP = "INCORP"


# Matérias com esses status recebem o valor 1 no .csv
class PendingStatus(Enum):
    MATR = "MATR"
    CANC = "CANC"
    TRANC = "TRANC"


# Matérias com esses status recebem o valor 2 no .csv
class FailedStatus(Enum):
    REP = "REP"
    REPF = "REPF"
    REPMF = "REPMF"
    REPN = "REPN"
    REPNF = "REPNF"
    REC = "REC"
