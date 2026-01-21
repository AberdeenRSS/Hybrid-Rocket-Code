import numpy as np
import matplotlib.pyplot as plt
import scipy

# Lin-lin liu et. al.
# their fit: a=0.0876 n=0.3953
data = np.array([
    [91,     0.00045],
    [96.22,  0.00054],
    [138.56, 0.00056],
    [171.72, 0.00059],
    [241.74, 0.00078]
])

# stanford
# data = np.array([
#     [100, 0.00219],
#     [100, 0.00253],
#     [104, 0.00215],
#     [150, 0.00289],
#     [194, 0.00295],
#     [198, 0.00246]
# ])


def regression_fun(x, a, n):
    return a*x**n

def regression_fun_fixed(x, a):
    return a*x**0.5

popt, pcov = scipy.optimize.curve_fit(regression_fun, data[:,0], data[:,1])

print(f'a={popt[0]:.7f} n={popt[1]:.5f}')

G = np.linspace(1, 1000)
r = regression_fun(G, popt[0], popt[1])

popt_f, pcov = scipy.optimize.curve_fit(regression_fun_fixed, data[:,0], data[:,1])

print(f'a={popt_f[0]:.7f} n=0.5')

G_f = np.linspace(1, 1000)
r_f = regression_fun_fixed(G, popt_f[0])

plt.plot(data[:, 0], data[:, 1], 'x', label='Experimental values')
plt.plot(G, r, label=f'a={popt[0]:.5f} n={popt[1]:.5f}')
plt.plot(G_f, r_f, label=f'a={popt_f[0]:.5f} n=0.5')
plt.xlabel('G_ox (kg/(m^2)')
plt.ylabel("r' (m/s)")
plt.legend()
# plt.(G, r)

plt.savefig('./output/r2s_2026/linliu_regression_rate.png', bbox_inches='tight')
