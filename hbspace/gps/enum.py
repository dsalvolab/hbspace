class TripDirection:
    X2X = 0
    H2D = 1     # home to destination
    H2X = 2     # home to x
    D2H = 3     # destination to home
    D2X = 4     # destination to X
    X2H = 5     # x to home
    X2D = 6     # x to destination

class GPSState:
    STATIONARY = 0
    MOTION     = 1
    PAUSE      = 2
    MOTION_NOT_TRIP = -1
