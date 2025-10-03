import argparse
import grib2io
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import os 
import xarray as xr
from netCDF4 import Dataset


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



def plot_nc_difference(file1in, file2in, file3in, varin, output_file,
                           title1="SoilDA-Control", title2="SoilDAnoliau-Control") -> None:
    """
    
    """
    
    # Load datasets
    file1 = xr.open_dataset(file1in)
    file2 = xr.open_dataset(file2in)
    file3 = xr.open_dataset(file3in)
    
    # Extract soilt1 for time=0 and coordinates
    soilt1_file1 = file1[varin].isel(time=0)
    soilt1_file2 = file2[varin].isel(time=0)
    soilt1_file3 = file3[varin].isel(time=0)
    
    #lat = file1['grid_yt']
    #lon = file1['grid_xt']
    
    # Use 2D lat/lon grids for axes
    lat = file1['lat']      # shape: (grid_yt, grid_xt)
    lon = file1['lon']      # shape: (grid_yt, grid_xt)

    #lon[lon>180]=lon[lon>180] - 360.

    # Calculate differences
    diff_file2_file1 = soilt1_file2 - soilt1_file1
    diff_file3_file1 = soilt1_file3 - soilt1_file1
    
    # Mask invalid values
    diff_file2_file1_masked = np.ma.masked_invalid(diff_file2_file1)
    diff_file3_file1_masked = np.ma.masked_invalid(diff_file3_file1)
    
    std_21 = np.nanstd(diff_file2_file1)
    vmin_21 = -3 * std_21
    vmax_21 = 3 * std_21

    std_31 = np.nanstd(diff_file3_file1)
    vmin_31 = -3 * std_31
    vmax_31 = 3 * std_31

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), subplot_kw={'projection': ccrs.PlateCarree()}, constrained_layout=True)
    
    # Subplot 1: file2 - file1
    pc1 = axes[0].pcolormesh(lon, lat, diff_file2_file1_masked,cmap='coolwarm', shading='auto', vmin=vmin_21, vmax=vmax_21, transform=ccrs.PlateCarree())
    axes[0].set_title(f'{title1}')
    axes[0].coastlines()
    #axes[0].add_feature(cfeature.BORDERS, linestyle=':')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    fig.colorbar(pc1, ax=axes[0], orientation='horizontal')
    
    # Subplot 2: file3 - file1
    pc2 = axes[1].pcolormesh(lon, lat, diff_file3_file1_masked, cmap='coolwarm', shading='auto', vmin=vmin_31, vmax=vmax_31, transform=ccrs.PlateCarree())
    axes[1].set_title(f'{title2}')
    axes[1].coastlines()
    #axes[1].add_feature(cfeature.BORDERS, linestyle=':')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    fig.colorbar(pc2, ax=axes[1], orientation='horizontal')
    
    plt.show()

    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()


def plot_3inc(file1in, file2in, file3in, varin, output_file,
                           title1="fhr003", title2="fhr006", title3="fhr009") -> None:
    """
    
    """

    # Load datasets
    file1 = Dataset(file1in)
    file2 = Dataset(file2in)
    file3 = Dataset(file3in)

    # Extract soilt1 for time=0 and coordinates
    soilt1_file1 = file1[varin][:] #.isel(time=0)
    soilt1_file2 = file2[varin][:] #.isel(time=0)
    soilt1_file3 = file3[varin][:] #.isel(time=0)

    #lat = file1['grid_yt']
    #lon = file1['grid_xt']

    # Use 2D lat/lon grids for axes
    lat = file1['latitude'][:]      # shape: (grid_yt, grid_xt)
    lon = file1['longitude'][:]      # shape: (grid_yt, grid_xt)
    
    file1.close()
    file2.close()
    file3.close()

    #lon[lon>180]=lon[lon>180] - 360.

    # Mask invalid values
    file1_masked = np.ma.masked_invalid(soilt1_file1)
    file2_masked = np.ma.masked_invalid(soilt1_file2)
    file3_masked = np.ma.masked_invalid(soilt1_file3)

    std_1 = np.nanstd(file1_masked)
    vmin_1 = -3 * std_1
    vmax_1 = 3 * std_1

    std_2 = np.nanstd(file2_masked)
    vmin_2 = -3 * std_2
    vmax_2 = 3 * std_2

    std_3 = np.nanstd(file3_masked)
    vmin_3 = -3 * std_3
    vmax_3 = 3 * std_3

    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(10, 15), subplot_kw={'projection': ccrs.PlateCarree()}, constrained_layout=True)

    # Subplot 1: file2 - file1
    pc0 = axes[0].pcolormesh(lon, lat, file1_masked,cmap='coolwarm', shading='auto', vmin=vmin_1, vmax=vmax_1, transform=ccrs.PlateCarree())
    axes[0].set_title(f'{title1}')
    axes[0].coastlines()
    #axes[0].add_feature(cfeature.BORDERS, linestyle=':')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    fig.colorbar(pc0, ax=axes[0], orientation='vertical', fraction=0.046, pad=0.04)
    
    pc1 = axes[1].pcolormesh(lon, lat, file2_masked,cmap='coolwarm', shading='auto', vmin=vmin_2, vmax=vmax_2, transform=ccrs.PlateCarree())
    axes[1].set_title(f'{title2}')
    axes[1].coastlines()
    #axes[0].add_feature(cfeature.BORDERS, linestyle=':')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    fig.colorbar(pc1, ax=axes[1], orientation='vertical', fraction=0.046, pad=0.04)

    # Subplot 2: file3 - file1
    pc2 = axes[2].pcolormesh(lon, lat, file3_masked, cmap='coolwarm', shading='auto', vmin=vmin_3, vmax=vmax_3, transform=ccrs.PlateCarree())
    axes[2].set_title(f'{title3}')
    axes[2].coastlines()
    #axes[1].add_feature(cfeature.BORDERS, linestyle=':')
    axes[2].set_xlabel('Longitude')
    axes[2].set_ylabel('Latitude')
    fig.colorbar(pc2, ax=axes[2], orientation='vertical', fraction=0.046, pad=0.04)

    plt.show()

    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()


def plot_3fc_diff(file1in, file2in, file3in, file1o, file2o, file3o, varin, output_file,
                           title1="fhr003", title2="fhr006", title3="fhr009") -> None:
    """
    
    """

    # Load datasets
    file1 = Dataset(file1in)
    file2 = Dataset(file2in)
    file3 = Dataset(file3in)

    # Extract soilt1 for time=0 and coordinates
    soilti_file1 = file1[varin][0, :, :] #.isel(time=0)
    soilti_file2 = file2[varin][0, :, :] #.isel(time=0)
    soilti_file3 = file3[varin][0, :, :] #.isel(time=0)

    # Use 2D lat/lon grids for axes
    lat = file1['lat'][:]      # shape: (grid_yt, grid_xt)
    lon = file1['lon'][:]      # shape: (grid_yt, grid_xt)
    
    file1.close()
    file2.close()
    file3.close()

    file1 = Dataset(file1o)
    file2 = Dataset(file2o)
    file3 = Dataset(file3o)

    # Extract soilt1 for time=0 and coordinates
    soilto_file1 = file1[varin][0, :, :] #.isel(time=0)
    soilto_file2 = file2[varin][0, :, :] #.isel(time=0)
    soilto_file3 = file3[varin][0, :, :] #.isel(time=0)
                             
    file1.close()
    file2.close()
    file3.close()

    soilt1_file1 = soilto_file1 - soilti_file1
    soilt1_file2 = soilto_file2 - soilti_file2
    soilt1_file3 = soilto_file3 - soilti_file3

    # Mask invalid values
    file1_masked = np.ma.masked_invalid(soilt1_file1)
    file2_masked = np.ma.masked_invalid(soilt1_file2)
    file3_masked = np.ma.masked_invalid(soilt1_file3)

    std_1 = np.nanstd(file1_masked)
    vmin_1 = -3 * std_1
    vmax_1 = 3 * std_1

    std_2 = np.nanstd(file2_masked)
    vmin_2 = -3 * std_2
    vmax_2 = 3 * std_2

    std_3 = np.nanstd(file3_masked)
    vmin_3 = -3 * std_3
    vmax_3 = 3 * std_3

    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(10, 15), subplot_kw={'projection': ccrs.PlateCarree()}, constrained_layout=True)

    # Subplot 1: file2 - file1
    pc0 = axes[0].pcolormesh(lon, lat, file1_masked,cmap='coolwarm', shading='auto', vmin=vmin_1, vmax=vmax_1, transform=ccrs.PlateCarree())
    axes[0].set_title(f'{title1}')
    axes[0].coastlines()
    #axes[0].add_feature(cfeature.BORDERS, linestyle=':')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    fig.colorbar(pc0, ax=axes[0], orientation='vertical', fraction=0.046, pad=0.04)
    
    pc1 = axes[1].pcolormesh(lon, lat, file2_masked,cmap='coolwarm', shading='auto', vmin=vmin_2, vmax=vmax_2, transform=ccrs.PlateCarree())
    axes[1].set_title(f'{title2}')
    axes[1].coastlines()
    #axes[0].add_feature(cfeature.BORDERS, linestyle=':')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    fig.colorbar(pc1, ax=axes[1], orientation='vertical', fraction=0.046, pad=0.04)

    # Subplot 2: file3 - file1
    pc2 = axes[2].pcolormesh(lon, lat, file3_masked, cmap='coolwarm', shading='auto', vmin=vmin_3, vmax=vmax_3, transform=ccrs.PlateCarree())
    axes[2].set_title(f'{title3}')
    axes[2].coastlines()
    #axes[1].add_feature(cfeature.BORDERS, linestyle=':')
    axes[2].set_xlabel('Longitude')
    axes[2].set_ylabel('Latitude')
    fig.colorbar(pc2, ax=axes[2], orientation='vertical', fraction=0.046, pad=0.04)

    plt.show()

    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()




workdir="/lfs/h2/emc/da/noscrub/tseganeh.gichamo/PLT/"

contdir="/lfs/h2/emc/ptmp/tseganeh.gichamo/contr/"
dadir="/lfs/h2/emc/ptmp/tseganeh.gichamo/soilda/"
noldir="/lfs/h2/emc/ptmp/tseganeh.gichamo/noliau/"

os.chdir(workdir)


file1i=contdir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf003.ensmean.nc"
file2i=contdir+"enkfgdas.20220501/06/ensstat/model/atmos/history//enkfgdas.t06z.sfcf006.ensmean.nc"
file3i=contdir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf009.ensmean.nc"

file1o=dadir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf003.ensmean.nc"
file2o=dadir+"enkfgdas.20220501/06/ensstat/model/atmos/history//enkfgdas.t06z.sfcf006.ensmean.nc"
file3o=dadir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf009.ensmean.nc"

plot_3fc_diff(file1i, file2i, file3i, file1o, file2o, file3o, "soilt1", "stc1_da_cont.png",
                            title1="Diff (DA-Control) enkfgdas.20220501/06/ensstat/sfcf003.ensmean soilt1 fhr003", title2="Diff stc1 fhr006", title3="Diff stc1 fhr009")

file1o=noldir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf003.ensmean.nc"
file2o=noldir+"enkfgdas.20220501/06/ensstat/model/atmos/history//enkfgdas.t06z.sfcf006.ensmean.nc"
file3o=noldir+"enkfgdas.20220501/06/ensstat/model/atmos/history/enkfgdas.t06z.sfcf009.ensmean.nc"
plot_3fc_diff(file1i, file2i, file3i, file1o, file2o, file3o, "soilt1", "stc1_nol_cont.png",
                            title1="Diff (DAnoliau-Control) enkfgdas.20220501/06/ensstat/sfcf003.ensmean soilt1 fhr003", title2="Diff stc1 fhr006", title3="Diff stc1 fhr009")
exit(0)

file1=dadir+"enkfgdas.20220501/06/ensstat/analysis/atmos/enkfgdas.t06z.sfci003.nc"
file2=dadir+"enkfgdas.20220501/06/ensstat/analysis/atmos/enkfgdas.t06z.sfci006.nc"
file3=dadir+"enkfgdas.20220501/06/ensstat/analysis/atmos/enkfgdas.t06z.sfci009.nc"

plot_3inc(file1, file2, file3, "soilt1_inc", output_file="stc1inc.png",
                           title1="enkfgdas.20220501/06/ensstat stc inc fhr003", title2="stc inc fhr006", title3="stc inc fhr009")

file1=contdir+"gdas.20220501/06/model/atmos/history/gdas.t06z.sfcf003.nc"
file2=dadir+"gdas.20220501/06/model/atmos/history/gdas.t06z.sfcf003.nc"
file3=noldir+"gdas.20220501/06/model/atmos/history/gdas.t06z.sfcf003.nc"


#plot_nc_difference(file1, file2, file3, "soilt1", output_file="stc1_3.png", title1="soilt1 (SoilDA-Control) 2022050106f03", title2="soilt1 (SoilDAnoliau-Control) 2022050106f03")

