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
import random
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
        with open(os.path.join(os.path.dirname(__file__),"transform_config.yaml"), 'r') as t_config:
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
                    filenames = sorted(glob.glob(f'{self.data_directory}/{param}_A???????{var}.tif'))

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
        xarray_unc = xr.open_rasterio(f"{self.data_directory}/{param}_unc_warped.vrt")
        xarray_unc = xarray_unc.rename({'band': 'time', 'x': 'longitude', 'y': 'latitude'})
        xarray_unc.time.values = self.__extract_timesteps_from_gdal(param, '_unc')

        # Calculate min and max values
        xarray_min = xarray_core - xarray_unc
        xarray_max = xarray_core + xarray_unc

        # Store as a DataSet
        dataset = xr.Dataset({'min':xarray_min, 'mean':xarray_core, 'max':xarray_max})

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

        # Extract the numerical part of each name as a datestring
        datestrings = [(re.findall('\d+', file))[0] for file in filelist]

        # Convert these datestrings into datetimes
        datetimes = [dt.datetime.strptime(ds, "%Y%j") for ds in datestrings]

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
        timeseries = self.data[param].sel(latitude=lat, longitude=lon)

        df = timeseries.to_dataframe()

        return df

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
    def __simple_transform(data, coeff):
        """
        Transform data using the simple form of the equations
        :param coeff:
        :return:
        """
        return coeff * data

    # def __extract_filenames(self, parameter, var):
    #     """
    #     Get the filenames of the files for this parameter
    #     :return:
    #     """
    #     # Populate the core filenames list (empty string as is for the filenames)
    #     filenames = sorted(glob.glob(f'{self.data_directory}/{parameter}_A???????{var}.tif'))
    #
    #     # Todo: return sensible error here when filenames are empty
    #
    #     return filenames

    # def load_data(self, parameter):
    #     """
    #     Open up all the geotiffs, transform the data and save the core vlues and uncertainty into an xarray
    #     :param parameter:
    #     :return: xarray
    #     """
    #
    #     # Save the parameter name as an attribute
    #     self.parameter = parameter
    #
    #     # Gather all the filenames for this parameter into a list
    #     self.__extract_filenames()
    #
    #     # Read the data recursively for these files
    #     self.__create_dataset()
    #
    #     # Transform the values
    #     self.__transform_data()
    #
    #     return self.data

    # def __extract_filenames(self, parameter):
    #     """
    #     Get the filenames of the files for this parameter
    #     :return:
    #     """
    #     # Define empty filenames
    #     filenames = {}
    #
    #     # Populate the core filenames list
    #     filenames['core'] = sorted(glob.glob(f'{self.data_directory}/{parameter}_A???????.tif'))
    #
    #     # Poplate the uncertainty filenames list
    #     filenames['unc'] = sorted(glob.glob(f'{self.data_directory}/{parameter}_A???????_unc.tif'))
    #
    #     return filenames

    # def get_timeseries(self, parameter):
    #     """
    #     Extract the datetimes of this dataset
    #     :return:
    #     """
    #     filenames = self.__extract_filenames(parameter)
    #
    #     datestrings = [(re.findall('\d+', fname))[0] for fname in filenames['core']]
    #
    #     dates = [dt.datetime.strptime(datestring, "%Y%j") for datestring in datestrings]
    #
    #     return dates

    # def get_timestep(self, parameter, time=None, step=None):
    #     """
    #     Return datafrma of single datetime of data
    #     :return:
    #     """
    #
    #     # Convert to datestring (which can be found in the files)
    #     if time:
    #         datestring = time.strftime("%Y%j")
    #
    #         # Identify our files
    #         core_file = glob.glob(f'{self.data_directory}/{parameter}_A{datestring}.tif')
    #         unc_file = glob.glob(f'{self.data_directory}/{parameter}_A{datestring}_unc.tif')
    #
    #     elif step is not None:
    #
    #         filenames = self.__extract_filenames(parameter)
    #         core_file = filenames['core'][step]
    #         unc_file = filenames['unc'][step]
    #
    #     else:
    #         raise IOError('unknown time/step for retrieving data')
    #
    #     # Read the data into an xarray
    #     core_data = self.__read_the_data(core_file)
    #
    #     # Read uncertainty values into an xarray
    #     unc_data = self.__read_the_data(unc_file)
    #
    #     # Calculate min and max values
    #     min_data = core_data - unc_data
    #     max_data = core_data + unc_data
    #
    #     # Add min, core(mean) and max values into a dataset for this timestep
    #     data_timestep = xr.Dataset({'mean': core_data, 'min': min_data, 'max': max_data})
    #
    #     # rename dimensions
    #     data_timestep = data_timestep.rename({'band': 'time', 'x': 'longitude', 'y': 'latitude'})
    #
    #     # add time coordinate
    #     #data_timestep.time.values = [timestep_dt]
    #
    #     # Transform
    #     data = self.__transform_data(parameter, data_timestep)
    #
    #     # Convert to a dataframe
    #     df = data.to_dataframe()
    #
    #     return df

    # def __create_dataset(self, filenames):
    #     """
    #     Create an xarray dataset of the data required
    #     :return:
    #     """
    #
    #     # Extract the datestrings from the core filenames:
    #     datestrings = [(re.findall('\d+', fname))[0] for fname in filenames['core']]
    #
    #     # Set flag to be false so that a new xarray is created the first time around
    #     first_timestep_complete = False
    #
    #     # Loop over datestrings, do this instead of siply looping over filenames, so that we make sure uncertainty
    #     # and core are in sync
    #     for datestring in datestrings:
    #
    #         # Define filenames:
    #         fname_core = [f for f in filenames['core'] if datestring in f][0]
    #         fname_unc = [f for f in filenames['unc'] if datestring in f][0]
    #
    #         # Read the data into an xarray
    #         core_data = self.__read_the_data(fname_core)
    #
    #         # Read uncertainty values into an xarray
    #         unc_data = self.__read_the_data(fname_unc)
    #
    #         # Calculate min and max values
    #         min_data = core_data - unc_data
    #         max_data = core_data + unc_data
    #
    #         # Add min, core(mean) and max values into a dataset for this timestep
    #         data_timsetep = xr.Dataset({'mean':core_data, 'min':min_data, 'max':max_data})
    #
    #         # rename dimensions
    #         data_timsetep = data_timsetep.rename({'band': 'time', 'x': 'longitude', 'y': 'latitude'})
    #
    #         # Extract the date from the filename and create time coordinate
    #         date = dt.datetime.strptime(datestring, "%Y%j")
    #         data_timsetep.time.values = [date]
    #
    #         # Either create the self.data dataset, or concatenate.
    #         if not first_timestep_complete:
    #
    #             self.data = data_timsetep
    #             first_timestep_complete = True
    #
    #         # For runs >1, concatenate to the existing output variable
    #         else:
    #             self.data = xr.concat([self.data, data_timsetep], dim='time')

    # @staticmethod
    # def __read_the_data(fname):
    #     """
    #     Open the geotiff and read data into an xarray
    #
    #     :return:
    #     """
    #
    #     # Generate a temporary filename
    #     tmp_file = f'tmp_{random.randint(1,100)}.vrt'
    #
    #     # convert to lat/lon
    #     gd = gdal.Warp(
    #         srcDSOrSrcDSTab=fname,
    #         destNameOrDestDS=tmp_file,
    #         format='VRT',
    #         dstSRS='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs') #remove this to use native coordinates
    #     gd = None  # flush the file
    #
    #     # open the data set
    #     dataarray = xr.open_rasterio(tmp_file)
    #
    #     # Delete the temporary file
    #     os.remove(tmp_file)
    #
    #     return dataarray

    # def __transform_data(self):
    #     """
    #     Use transform coefficients to convert data into real values
    #
    #     :return:
    #     """
    #     # Identify the type of transform that we're doing
    #     if self.transform_parameters[self.parameter]['t_type'] == 'simple':
    #         transform_func = self.__simple_transform
    #     elif self.transform_parameters[self.parameter]['t_type'] == 'exponential':
    #         transform_func = self.__exponential_transform
    #     elif self.transform_parameters[self.parameter]['t_type'] == 'none':
    #         transform_func = lambda x, y: x # just return the data and don't do anything with the coefficents
    #     else:
    #         raise IOError(f"unrecognised transform type for {self.parameter} in transform_config.yaml")
    #
    #     # extract coefficients
    #     coeff = self.transform_parameters[self.parameter]['t_coeff']
    #
    #     # Transform all the values (core, minimum and maximum)
    #     for param in ['max', 'mean', 'min']:
    #         self.data[param].values = transform_func(self.data[param].values, coeff)