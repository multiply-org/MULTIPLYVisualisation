#######################################################
#
# DataHandling.py
# Python implementation of the Class DataHandling
# Generated by Enterprise Architect
# Created on:      11-Jun-2019 16:42:03
# Original author: Bethan
#
#######################################################
import xarray as xr
import glob
import yaml
import os
import numpy as np
import datetime as dt
import re
import gdal
import pandas as pd


class DataHandling:
    """This class pre-processes the data requested by the user. It transforms the data
    and keeps a copy of the values and the uncertainties in memory.
    """

    def __init__(self, directory):
        """
        Set this directory to be the source
        :param directory:
        """
        # Save the directory
        self.data_directory = directory

        # Ingest transform data from config
        with open(os.path.join(os.path.dirname(__file__),
                               "transform_config.yaml"), 'r') as t_config:
            self.transform_parameters = yaml.safe_load(t_config)

        # Extract available parameters
        self.parameters = self.get_available_parameters()

        # Create VRT for all the datasets if they don't exist
        self.__build_vrts()

        # Load the data as xarrays into memory
        self.__load_all_data()

    def __build_vrts(self):
        """
        Generate VRT files to bind together the individual geotiffs so that we can reference them all together
        in xarrays

        :return:
        """
        # define universal options for the VRT files
        vrt_options = gdal.BuildVRTOptions(separate=True)

        for param in self.parameters:

            for var in ['', '_unc']:

                # define the name for the vrt file
                vrt_filename = f"{self.data_directory}/{param}{var}.vrt"

                # check to see whether the file already exists
                if not os.path.isfile(vrt_filename):

                    # Get an ordered list of all the filenames
                    # Todo test that the system is robust to these values not being sorted.
                    filenames = sorted(glob.glob(f'{self.data_directory}/{param}*_A???????{var}.tif'))

                    if len(filenames) == 0:
                        continue

                    # BUild the file
                    gd = gdal.BuildVRT(vrt_filename, filenames, options=vrt_options)
                    gd = None# flush

                else:
                    # File exists already
                    pass

                # As a second step, produce warped VRTs
                vrt_filename_warp = f"{self.data_directory}/{param}{var}_warped.vrt"

                # check to see whether the file already exists
                if not os.path.isfile(vrt_filename_warp):

                    # convert to lat/lon
                    gd = gdal.Warp(
                        srcDSOrSrcDSTab=vrt_filename,
                        destNameOrDestDS=vrt_filename_warp,
                        format='VRT',
                        dstSRS='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')  # remove this to use native coordinates
                    gd = None  # flush the file

                else:
                    # File exists already
                    pass

    def get_available_parameters(self):
        """
        Parse the filenames and return the parameters available for selection

        :return:
        """
        # Extract all the possible paths
        all_filepaths = sorted(glob.glob(f'{self.data_directory}/*_A???????.tif'))

        # Discard all but the filenames
        all_files = [fp.split('/')[-1] for fp in all_filepaths]

        # Discard all but the parameter names
        parameters_with_duplication = [f.split('_')[0] for f in all_files]

        # Remove duplicates
        parameters = sorted(list(set(parameters_with_duplication)))

        return parameters

    def __load_all_data(self):
        """
        Open up all the geotiffs, transform the data and save the core vlues and uncertainty into an xarray
        :param parameter:
        :return: xarray
        """

        self.data = {}

        for param in self.parameters:

            # Read the data recursively for these files
            data_raw = self.__build_dataset(param)

            # Transform the values
            data_transformed = self.__transform_data(param, data_raw)

            # Add to dictionary of all datasets
            self.data[param] = data_transformed

            # Compute key statistics for visulaisation
            self.data[param].attrs['vis_stats'] = \
                self.__add_vis_stats(self.data[param])

        return self.data

    def __build_dataset(self, param):
        """
        Create an xarray dataset of the data required
        :return:
        """

        # Load core values
        xarray_core = xr.open_rasterio(f"{self.data_directory}/{param}_warped.vrt")
        xarray_core = xarray_core.rename({'band': 'time', 'x': 'longitude', 'y': 'latitude'})
        xarray_core.time.values = self.__extract_timesteps_from_gdal(param, '')

        # Load uncertainty values
        unc_file = f"{self.data_directory}/{param}_unc_warped.vrt"
        if os.path.exists(unc_file):
            xarray_unc = xr.open_rasterio(unc_file)
            xarray_unc = xarray_unc.rename({'band': 'time', 'x': 'longitude', 'y': 'latitude'})
            xarray_unc.time.values = self.__extract_timesteps_from_gdal(param, '_unc')
        else:
            xarray_unc = xarray_core.copy(deep=True)
            xarray_unc *= 0.2

        # Calculate min and max values
        xarray_min = xarray_core - xarray_unc
        xarray_max = xarray_core + xarray_unc

        # Store as a DataSet
        dataset = xr.Dataset({'min': xarray_min, 'mean': xarray_core,
                              'max': xarray_max})

        return dataset

    def __extract_timesteps_from_gdal(self, param, var):
        """
        Use the Source Filenames from gdal to extract the timestep values. We do it this way to ensure that there is no
        mis-placing of time. Gdal stores these filenames in the same order that they are applied to bands.
        :param param:
        :param var:
        :return:
        """

        # Open the dataset
        gdata = gdal.Open(f"{self.data_directory}/{param}{var}.vrt")

        # Extract all filenames (discaring the first, which is the name of this file)
        filelist = gdata.GetFileList()[1:]

        # Extract the filename from each ful path
        filenames = [f.split('/')[-1] for f in filelist]

        # Extract the numerical part of each name as a datestring
        datestrings = [(re.findall('\d+', file))[-1] for file in filenames]

        # Convert these datestrings into datetimes
        try:
            datetimes = [dt.datetime.strptime(ds, "%Y%j") for ds in datestrings]
        except ValueError:
            raise Exception (f'Unable to determine datetime for {param}')

        return datetimes

    def get_timesteps(self, param):
        """
        Extract the datetimes of this dataset
        :return:
        """
        timesteps_np64 = self.data[param].time.values

        timesteps = [pd.to_datetime(time) for time in timesteps_np64]

        return timesteps

    def get_timestep(self, param, time=None, step=None):
        """
        Return dataframe of single datetime of data
        :return:
        """

        if time:
            scene = self.data[param].sel(time=time)
        elif step:
            scene = self.data[param].isel(step=step)
        else:
            raise IOError('unknown time/step for retrieving data')

        # Convert to a dataframe
        df = scene.to_dataframe()

        return df

    def get_timeseries(self, param, lat, lon):
        """
        Extract timeseries of this data for a particular lat lon

        :param param:
        :param lat:
        :param lon:
        :return:
        """

        timeseries = self.data[param].sel(latitude=lat, longitude=lon,
                                          method='nearest')

        df = timeseries.to_dataframe()

        return df

    def get_stats(self, param, lats, lons):

        """
        Gets the data for all the lats and lons in the range of the lats and
        lons input from the selected area and returns the data
        :param param:
        :param lats:
        :param lons:
        :return:
        """

        lat_start = lats[0]
        lat_end = lats[-1]

        lon_start = lons[0]
        lon_end = lons[-1]

        timeseries = self.data[param].sel(latitude=slice(lat_start, lat_end),
                                          longitude=slice(lon_start, lon_end))
        timeseries = timeseries.drop(['longitude', 'latitude'])

        df = timeseries.to_dataframe()

        return df

    def __add_vis_stats(self, dataset):
        """
        Calculate some key statistics for defining colourscales in the final
        plots
        :return:
        """
        # Empty dict
        vis_stats = {'unc': {}, 'core': {}}

        # Calculate the uncertainty range, which is what is plotted
        range = np.fabs(dataset['max'] - dataset['min'])

        # Extract max and min,
        # ping nans and Infs
        vis_stats['unc']['max'] = range.\
            where(np.isfinite(range), np.nan).max(skipna=True)
        vis_stats['unc']['min'] = range.\
            where(np.isfinite(range), np.nan).min(skipna=True)
        vis_stats['unc']['mean'] = range.\
            where(np.isfinite(range), np.nan).mean(skipna=True)
        vis_stats['unc']['std'] = range.\
            where(np.isfinite(range), np.nan).std(skipna=True)

        # Extract max and min from core data, skipping nans and Infs
        vis_stats['core']['max'] = dataset['mean'].\
            where(np.isfinite(dataset['mean']), np.nan).max(skipna=True)
        vis_stats['core']['min'] = dataset['mean'].\
            where(np.isfinite(dataset['mean']), np.nan).min(skipna=True)
        vis_stats['core']['mean'] = dataset['mean'].\
            where(np.isfinite(dataset['mean']), np.nan).mean(skipna=True)
        vis_stats['core']['std'] = dataset['mean'].\
            where(np.isfinite(dataset['mean']), np.nan).std(skipna=True)

        return vis_stats

    def get_vis_stats(self, param):
        """
        Extract the statistics required to build consistent colourbars for
        the maps over all timesteps
        :param param:
        :return:
        """

        vis_stats = self.data[param].attrs['vis_stats']

        return vis_stats

    def __transform_data(self, parameter, data):
        """
        Use transform coefficients to convert data into real values

        :return:
        """
        # Identify the type of transform that we're doing
        if self.transform_parameters[parameter]['t_type'] == 'simple':
            transform_func = self.__simple_transform
        elif self.transform_parameters[parameter]['t_type'] == 'exponential':
            transform_func = self.__exponential_transform
        elif self.transform_parameters[parameter]['t_type'] == 'none':
            transform_func = lambda x, y: x # just return the data and don't do anything with the coefficents
        else:
            raise IOError(f"unrecognised transform type for {parameter} in transform_config.yaml")

        # extract coefficients
        coeff = self.transform_parameters[parameter]['t_coeff']

        # Transform all the values (core, minimum and maximum)
        for var in ['max', 'mean', 'min']:
            data[var].values = transform_func(data[var].values, coeff)

        # Swap round the min and the max values for the exponential method,
        # as untransforming switches their magnitudes
        if self.transform_parameters[parameter]['t_type'] == 'exponential':
            data['oldmin'] = data['min']
            data['min'] = data['max']
            data['max'] = data['oldmin']
            data = data.drop('oldmin')

        return data

    @staticmethod
    def __exponential_transform(data, coeff):
        """
        Transform data using the (inverse) exponential form of the equations.
        :param coeff:
        :return:
        """
        return coeff * np.log(data)

    @staticmethod
    def __exponential_transform_uncertainty(unc, data, coeff):
        """
        Transform uncertainty for the (inverse) exponential form of the equations using the first order 
        Taylor expansion approximation (uncertainty propagation). This approximation is only valid when 
        the uncertainty is much smaller than the data. This will produce symmetric uncertanties.
        In reality they are not symmetric especially when the uncertaitny is not much smaller than the data.
        :param coeff:
        :return:
        """
        return np.absolute(coeff * unc / data)
   
    @staticmethod
    def __simple_transform(data, coeff):
        """
        Transform data using the simple form of the equations
        :param coeff:
        :return:
        """
        return coeff * data
   
    @staticmethod
    def __simple_transform_uncertainty(unc, coeff):
        """
        Transform data for the simple form of the equations. This calculation is exact
        :param coeff:
        :return:
        """
        return np.absolute(coeff) * unc
