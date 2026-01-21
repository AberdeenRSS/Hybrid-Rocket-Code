import numpy as np
import matplotlib.pyplot as plt

from mach_corrected_drag import mjollnir_rocket_drag


mach_number = np.linspace(0.01, 4, 100)

plt.plot(mach_number, mjollnir_rocket_drag(mach_number))
plt.xlabel('Mach number')
plt.ylabel('Drag coefficient')
plt.savefig('./output/r2s_2026/mjollnir_drag.png')