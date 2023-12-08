class Fix:
    def __init__(self, tstmp, coords, elev, index):
        self.tstmp  = tstmp
        self.coords = coords
        self.elev   = elev
        self.index  = index
        
    def assign(self, other):
        self.tstmp  = other.tstmp
        self.coords = other.coords
        self.elev   = other.elev
        self.index  = other.index