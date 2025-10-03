import argparse
import grib2io
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import os 


def plot_grib_difference(file1: str, file2: str, 
                           variable: str,
                           level: str,
                           output_file: str = None,
                           title_prefix: str = "GRIB Difference") -> None:
    """
    Plot the difference between two GRIB files for a specified  variable.
    
    Args:
        file1 (str): Path to first GRIB file
        file2 (str): Path to second GRIB file
        variable (str):  variable name (e.g., 'dust_bin1', 'sulfate', etc.)
        level (int): Level index to plot (0-based)
        output_file (str): Output filename for the plot
        title_prefix (str): Prefix for the plot title
    """
    # open the grib files for reading
    grb1 = grib2io.open(file1)
    grb2 = grib2io.open(file2)

    # get grid information from first message of first file, assumes grids are the same
    first_msg = grb1[0]
    lats, lons = first_msg.grid()
    msg1 = grb1.select(shortName=variable, level=level)[0]
    valid_time = first_msg.validDate
    lead_time = first_msg.leadTime
    msg2 = grb2.select(shortName=variable, level=level)[0]
    data1 = msg1.data
    data2 = msg2.data
    diff_data = data2 - data1

    # Create the plot
    fig = plt.figure(figsize=(15, 10))
    
    # Use PlateCarree projection for global data
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
    ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
    
    # Calculate statistics for color scaling
    diff_min = np.nanmin(diff_data)
    diff_max = np.nanmax(diff_data)
    diff_std = np.nanstd(diff_data)
    diff_mean = np.nanmean(diff_data)
    
    # Set symmetric color limits based on data range
    vmax = max(abs(diff_min), abs(diff_max))
    if vmax == 0:
        vmax = diff_std if diff_std > 0 else 1e-10

    # Create contour plot
    levels_plot = np.linspace(-vmax, vmax, 21)
    #contour = ax.contourf(lons, lats, diff_data, levels=levels_plot, cmap='coolwarm', extend='both')
    
    pcm = ax.pcolormesh(lons, lats, diff_data, cmap='coolwarm', shading='auto', transform=ccrs.PlateCarree(),vmin=-3*diff_std, vmax=3*diff_std)
    cbar = plt.colorbar(pcm, ax=ax, orientation='horizontal', pad=0.02)
    cbar.set_label(f'Difference ({msg1.units})')
    ax.set_title(f'{title_prefix}: {variable} at {level} (Valid: {valid_time}, Lead: {lead_time})')

    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()



workdir="/lfs/h2/emc/da/noscrub/tseganeh.gichamo/PLT/"

contdir="/lfs/h2/emc/ptmp/tseganeh.gichamo/contr/"
dadir="/lfs/h2/emc/ptmp/tseganeh.gichamo/soilda/"
noldir="/lfs/h2/emc/ptmp/tseganeh.gichamo/noliau/"

os.chdir(workdir)


file1=contdir+"gdas.20220501/06/products/atmos/grib2/0p25/gdas.t06z.pgrb2.0p25.f003"
file2=dadir+"gdas.20220501/06/products/atmos/grib2/0p25/gdas.t06z.pgrb2.0p25.f003"
file3=noldir+"gdas.20220501/06/products/atmos/grib2/0p25/gdas.t06z.pgrb2.0p25.f003"

plot_grib_difference(file1, file2, "TMP", "1000 mb", title_prefix="Diff (SoilDA-Control)", output_file="fig1_f3.png")
plot_grib_difference(file1, file3, "TMP", "1000 mb", title_prefix="Diff (SoilDAnoliau-Control)", output_file="fig2_f3.png")

