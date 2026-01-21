import os
import pandas as pd
import matplotlib.pyplot as plt

from nitrous_engine_sim.propep_3_parser import import_simulation_results, add_nes_units, export_as_nes_propep

dfs = list()
start_index = 0
for f in os.listdir('./data/nox_petrolium_runs'):
    df = import_simulation_results(f'./data/nox_petrolium_runs/{f}', start_index)
    start_index += len(df)
    dfs.append(df)

propep_data = pd.concat(dfs)

print(propep_data.head())
# propep_data = propep_data.drop(propep_data[propep_data['P_CHAMBER_PSI'] == 0].index)
add_nes_units(propep_data, 'nitrous_oxide', 'petroleum_jelly')
propep_data = propep_data.dropna()

print(propep_data.columns)
print(propep_data[propep_data['run_id'] == 30])

chamber_pressures = list(set(propep_data['P_CHAMBER_BAR']))
plotted_pressures = [x for (i, x) in enumerate(chamber_pressures) if (i % 5 == 0) and x < 60]

# for p in reversed(plotted_pressures):

#     series =  propep_data[propep_data['P_CHAMBER_BAR'] == p]

#     of_ratio = series['ox_percentage']/series['fuel_percentage']

#     plt.plot(of_ratio, series['FROZEN_IMPULSE'], label=f'{p:.2f} bar')

# plt.legend()
# plt.xlabel('O/F ratio')
# plt.ylabel('Specific Impulse (s)')
# plt.xlim(0, 15)
# plt.savefig('./output/chemistry/paraffin_petrogel_OF_.png', bbox_inches='tight')

for p in reversed(plotted_pressures):

    series =  propep_data[propep_data['P_CHAMBER_BAR'] == p]
    of_ratio = series['ox_percentage']/series['fuel_percentage']
    plt.plot(of_ratio, series['T_CHAMBER_K'], label=f'{p:.2f} bar')

plt.legend()
plt.xlabel('O/F ratio')
plt.ylabel('T (K)')
plt.xlim(0, 15)
plt.savefig('./output/chemistry/paraffin_petrogel_OF_T.png', bbox_inches='tight')