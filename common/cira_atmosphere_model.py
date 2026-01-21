
import math
import numpy as np


class CiraAtmosphereModel():
    '''
    Assumes cira data from https://data.ceda.ac.uk/badc/cira/data/
    '''

    def import_data(self, file_location: str, line: int, max_rows=None):

        self.data = np.loadtxt(file_location, skiprows=line, ndmin=2, max_rows=max_rows)

    def get_pressure_interpolated(self, h):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        return np.interp(h/1000, np.flip(self.data[:, 2]), np.flip(self.data[:, 1]))
    
    def get_temp_interpolated(self, h, lat):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        lat_i = math.floor(lat/5)

        if lat_i > 18:
            lat_i = 18
        
        return np.interp(h/1000, np.flip(self.data[:, 2]), np.flip(self.data[:, 3 + lat_i]))
    
    def get_density_interpolated(self, h, lat):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        M_Air = 0.0289647 #kg/mol
        R = 8.314
        
        p = self.get_pressure_interpolated(h)
        T = self.get_temp_interpolated(h, lat)

        return p * M_Air/ (R * T)
