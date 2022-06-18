import sys
import os
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

matplotlib.use('Agg')

from pywfm import IWFMBudget

def read_filename_from_commandline(args):
    """ Read the budget hdf file name from the commandline
    """
    if len(args) == 1:
        input("Provide name of budget HDF file: ")
    
    elif len(args) > 2:
        raise ValueError("Too many values provided on command line")

    else:
        file_name = args[1]
        if not os.path.exists(file_name):
            raise FileNotFoundError("File provided {} was not found".format(file_name))
        
        if not file_name.endswith('hdf'):
            raise ValueError("Budget files must be HDF format")

        return file_name

def date_to_water_year(month, year):
    if month > 9:
        return int(year + 1)
    else:
        return int(year)

if __name__ == '__main__':


    gw_budget_file = read_filename_from_commandline(sys.argv)
    
    with IWFMBudget(gw_budget_file) as bud:
        locations = bud.get_location_names()
        for i, l in enumerate(locations, start=1):

            print("Plotting Groundwater Budget for {}".format(l))

            gw = bud.get_values(
                i,
                output_interval='1YEAR',
                area_conversion_factor=1/43560,
                area_units='Acres',
                volume_conversion_factor=1/43560,
                volume_units='AF'
            )
            
            gw['Loss to Stream (-)'] = np.where(gw['Gain from Stream (+)'].to_numpy() < 0, -1*gw['Gain from Stream (+)'].to_numpy(), 0)
            gw['Gain from Stream (+)'] = np.where(gw['Gain from Stream (+)'].to_numpy() >= 0, gw['Gain from Stream (+)'].to_numpy(), 0)

            gw['Net Subsurface Outflow (-)'] = np.where(gw['Net Subsurface Inflow (+)'].to_numpy() < 0, -1*gw['Net Subsurface Inflow (+)'].to_numpy(), 0)
            gw['Net Subsurface Inflow (+)'] = np.where(gw['Net Subsurface Inflow (+)'].to_numpy() >= 0, gw['Net Subsurface Inflow (+)'].to_numpy(), 0)

            gw['Loss to Lake (-)'] = np.where(gw['Gain from Lake (+)'].to_numpy() < 0, -1*gw['Gain from Lake (+)'].to_numpy(), 0)
            gw['Gain from Lake (+)'] = np.where(gw['Gain from Lake (+)'].to_numpy() >= 0, gw['Gain from Lake (+)'].to_numpy(), 0)

            gw['Rebound (-)'] = np.where(gw['Subsidence (+)'].to_numpy() < 0, -1*gw['Subsidence (+)'].to_numpy(), 0)
            gw['Subsidence (+)'] = np.where(gw['Subsidence (+)'].to_numpy() >= 0, gw['Subsidence (+)'].to_numpy(), 0)


            width = 0.35

            fig, ax = plt.subplots(figsize=(20,6))
            ax.bar(
                gw.index - width/2, 
                gw['Deep Percolation (+)'],
                width,
                color='#C35ABC',
                label='Deep Percolation (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Recharge (+)'],
                width,
                bottom=gw['Deep Percolation (+)'],
                color='#61B74F',
                label='Recharge (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Boundary Inflow (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'],
                color='#7561CF',
                label='Boundary Inflow (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Gain from Stream (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'] + gw['Boundary Inflow (+)'],
                color='#B4B445',
                label='Gain from Stream (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Gain from Lake (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'] + gw['Boundary Inflow (+)'] + gw['Gain from Stream (+)'],
                color='#787EC7',
                label='Gain from Lake (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Subsidence (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'] + gw['Boundary Inflow (+)'] + gw['Gain from Stream (+)'] + gw['Gain from Lake (+)'],
                color='#D68B31',
                label='Subsidence (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Net Subsurface Inflow (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'] + gw['Boundary Inflow (+)'] + gw['Gain from Stream (+)'] + gw['Gain from Lake (+)'] + gw['Subsidence (+)'],
                color='#4FACD8',
                label='Net Subsurface Inflow (Inflow)'
            )
            
            ax.bar(
                gw.index - width/2, 
                gw['Subsurface Irrigation (+)'],
                width,
                bottom=gw['Deep Percolation (+)'] + gw['Recharge (+)'] + gw['Boundary Inflow (+)'] + gw['Gain from Stream (+)'] + gw['Gain from Lake (+)'] + gw['Subsidence (+)'] + gw['Net Subsurface Inflow (+)'],
                color='#CA4C39',
                label='Subsurface Irrigation (Inflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Pumping (-)'],
                width,
                color='#50B897',
                label='Pumping (Outflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Loss to Stream (-)'],
                width,
                bottom=gw['Pumping (-)'],
                color='#D14074',
                label='Loss to Stream (Outflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Loss to Lake (-)'],
                width,
                bottom=gw['Pumping (-)'] + gw['Loss to Stream (-)'],
                color='#4E8345',
                label='Loss to Lake (Outflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Net Subsurface Outflow (-)'],
                width,
                bottom=gw['Pumping (-)'] + gw['Loss to Stream (-)'] + gw['Loss to Lake (-)'],
                color='#BD6C90',
                label='Net Subsurface Outflow (Outflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Rebound (-)'],
                width,
                bottom=gw['Pumping (-)'] + gw['Loss to Stream (-)'] + gw['Loss to Lake (-)'] + gw['Net Subsurface Outflow (-)'],
                color='#81762E',
                label='Rebound (Outflow)'
            )
            
            ax.bar(
                gw.index + width/2, 
                gw['Tile Drain Outflow (-)'],
                width,
                bottom=gw['Pumping (-)'] + gw['Loss to Stream (-)'] + gw['Loss to Lake (-)'] + gw['Net Subsurface Outflow (-)'] + gw['Rebound (-)'],
                color='#C8815C',
                label='Tile Drain Outflow (Outflow)'
            )
            
            ax2 = ax.twinx()
            
            ax2.plot(
                gw.index,
                (gw['Ending Storage (-)'] - gw['Beginning Storage (+)']).cumsum(),
                'k'
            )
            
            ax.set_xticks(gw.index.tolist(), gw['Time'].dt.year.tolist())
            for label in ax.get_xticklabels():
                label.set_rotation(90)
                
            ax.grid()
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + 0.25 * box.height, box.width, box.height * 0.75])
            
            # Put a legend below the current axis
            ax.legend(loc='lower center', ncol=7, fontsize=8, bbox_to_anchor=(0.5, -0.35), frameon=False)
            
            ax.set_ylabel('Annual Volume (AF)')
            ax2.set_ylabel('Cumulative Change in Storage (AF)')
            ax.set_xlabel('Water Year')
            ax.set_title('Groundwater Budget\nfor Subregion {}'.format(i))
            plt.savefig('{}_GW.png'.format(l))
            plt.close()

    print("Processing Complete!")