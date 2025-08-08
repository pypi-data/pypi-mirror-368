class Data:
    def __init__(self, X, Y, Z=None):
        self.X = X
        self.Y = Y
        self.Z = Z
        
        # Validate that all provided arrays have the same length
        if len(X) != len(Y):
            raise ValueError(f"X and Y must have the same length. Got X: {len(X)}, Y: {len(Y)}")
        
        if Z is not None and len(Z) != len(X):
            raise ValueError(f"Z must have the same length as X and Y. Got Z: {len(Z)}, X: {len(X)}")

    def unpack(self):
        if self.Z is not None:
            return {'X': self.X, 'Y': self.Y, 'Z': self.Z}
        else:
            return {'X': self.X, 'Y': self.Y}
