import os
import numpy as np
import matplotlib.pyplot as plt
from common.cira_atmosphere_model import CiraAtmosphereModel

OUT = 'output/r2s_2026'

os.makedirs(f'./{OUT}', exist_ok=True)

cira_model = CiraAtmosphereModel()
cira_model.import_data('./data/atmosphere/cira_nhant.txt', 14)

h = np.linspace(0, 150000, 200)

plt.semilogy(h/1000, cira_model.get_density_interpolated(h, 67))
plt.xlabel('Height (km)')
plt.ylabel('Air density (kg/m^3)')
plt.savefig(f'{OUT}/cira_density.png', bbox_inches='tight')