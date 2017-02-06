from numpy import interp

class Sensor():

    def __init__(self,
                 vMin,
                 vMax,
                 oMin,
                 oMax):
                 
        self.vMin = vMin;
        self.vMax = vMax;
        self.oMin = oMin;
        self.oMax = oMax;
        
    def translate(self, vIn):
        # Map an input voltage to the specifid output range
        oOut = interp(vIn, [self.vMin, self.vMax],[self.oMin, self.oMax])
            
        return oOut
        
    def set_vmin(newmin):
        self.vMin = newmin;
        
    def set_vmax(newmax):
        self.vMax = newmax;
        
    def set_omin(newmin):
        self.oMin = newmin;

    def set_omax(newmax):
        self.oMax = newmax;


