import math
from typing import TypeVar, cast

import numpy as np

k1 = 0.657 
k2 = -0.151 
k3 = 0.00979
k4 = 0.440 
k5 = -0.164
k6 = 0.0740 
k7 = 72.1 
k8 = 0.985 

T = TypeVar('T', float, np.ndarray)

def mjollnir_rocket_drag(mach_number: T) -> T:
    '''
    Taken from https://kth.diva-portal.org/smash/get/diva2:1881325/FULLTEXT01.pdf
    '''

    exp = np.exp(-k7*(mach_number - k8))

    return cast(T, ((k1 + k2*mach_number + k3*mach_number**2) + (k4 + k5*mach_number + k6*mach_number**2)*exp)/(1 + exp))


