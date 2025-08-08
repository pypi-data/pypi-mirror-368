from enum import Enum


class FixtureStatus(str, Enum):
    P = "Played"
    U = "Unplayed"
    F = "Forfeit"
    A = "Abandoned"
    D = "Postponed"


class FixtureResult(str, Enum):
    W = "Win"
    D = "Draw"
    L = "Loss"
    F = "Forfeit"
    S = "Suspended"
    N = "None"


class Category(str, Enum):
    """League categories."""

    MEN = "men"
    WOMEN = "women"
    COED = "coed"


class Division(str, Enum):
    """League divisions."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"


class MatchDay(str, Enum):
    """Day of week."""

    MON = "Monday"
    TUE = "Tuesday"
    WED = "Wednesday"
    THU = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"
    SUN = "Sunday"


class Gender(str, Enum):
    """Gender."""

    M = "Male"
    F = "Female"
    NB = "Non-Binary"
    T = "Transgender"
    O = "Other"  # noqa: E741
    P = "Prefer not to say"
    N = "N/A"


class Field(str, Enum):
    """Field of play."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"  # noqa: E741
    J = "J"
    K = "K"
    L = "L"


class ScheduleType(str, Enum):
    ROUNDROBIN = "Round Robin"
    ROUNDROBIN_PLAYOFF = "Round Robin Playoff"
    TOURNAMENT = "Tournament"
    BRACKET = "Bracket"
    LADDER = "Ladder"
