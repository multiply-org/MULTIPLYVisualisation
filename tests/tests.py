from src.MultiplyVis import MultiplyVis
from src.DataHandling import DataHandling
from src.GenerateView import GenerateView
import os
import xarray as xr
import copy
import numpy as np
import nose.tools as ntools

# def integration_test():
#     """
#     Test of entire setup from a single commandline point
#     """
#     pass

class TestDataHandler:

    def setup(self):
        """
        Set up parameters required
        :return:
        """

        self.data_dir = os.path.abspath("../data")

        self.quick_data = {'min':5, 'mean':10, 'max':15}

        self.dummy_data = xr.Dataset({
            'min': xr.DataArray(self.quick_data['min']),
            'max': xr.DataArray(self.quick_data['max']),
            'mean': xr.DataArray(self.quick_data['mean']),
        })

        self.filenames = {
            "core": [f"{self.data_dir}/lai_A2017156.tif",
                     f"{self.data_dir}/lai_A2017161.tif",
                     f"{self.data_dir}/lai_A2017166.tif",
                     f"{self.data_dir}/lai_A2017171.tif",
                     f"{self.data_dir}/lai_A2017176.tif",
                     f"{self.data_dir}/lai_A2017181.tif"],
            "unc": [f"{self.data_dir}/lai_A2017156_unc.tif",
                            f"{self.data_dir}/lai_A2017161_unc.tif",
                            f"{self.data_dir}/lai_A2017166_unc.tif",
                            f"{self.data_dir}/lai_A2017171_unc.tif",
                            f"{self.data_dir}/lai_A2017176_unc.tif",
                            f"{self.data_dir}/lai_A2017181_unc.tif"]
        }

        # Instantiate data handler for the data directory
        self.dh = DataHandling(self.data_dir)

    def filenames_test(self):
        """
        Make sure that we're picking up the correct filenames
        :return:
        """
        # set parameter
        self.dh.parameter = 'lai'

        # extract the filenames using the datahandler
        self.dh._DataHandling__extract_filenames()

        # Test they are the same
        assert self.filenames == self.dh.filenames

    def transform_test(self):
        """
        Test the transform equations
        :return:
        """

        # Set transform parameters for the test
        self.dh.transform_parameters = {
            'lorem': {
                't_type': 'exponential',
                't_coeff': 100},
            'ipsum': {
                't_type': 'simple',
                't_coeff': 10},
            'dolors': {
                't_type': 'none',
                't_coeff': -999}
        }

        expected_outputs = {
            'lorem': {k:100*np.log(v) for k,v in self.quick_data.items()},
            'ipsum': {k:10*v for k,v in self.quick_data.items()},
            'dolors': {k:v for k,v in self.quick_data.items()}
        }

        for param in ['lorem', 'ipsum', 'dolors']:

            # Define the data
            self.dh.data = copy.deepcopy(self.dummy_data)

            # Define the input parameter
            self.dh.parameter = param

            # Transform
            self.dh._DataHandling__transform_data()

            # Check all three parameters
            assert self.dh.data['min'].values == expected_outputs[param]['min']
            assert self.dh.data['max'].values == expected_outputs[param]['max']
            assert self.dh.data['mean'].values == expected_outputs[param]['mean']


    def create_dataset_test(self):
        """
        Test that we can load the dataset
        :return:
        """

        # Add in filenames
        self.dh.filenames = self.filenames

        # Load the dataset into an xarray
        self.dh._DataHandling__create_dataset()

        # Check that the type is a dataset
        ntools.assert_is_instance(self.dh.data, xr.Dataset)

        # Check that the variable names are correct
        ds_content = list(self.dh.data.variables.mapping.keys())
        assert len(ds_content) == 6
        assert 'latitude' in ds_content
        assert 'longitude' in ds_content
        assert 'time' in ds_content
        assert 'mean' in ds_content
        assert 'min' in ds_content
        assert 'max' in ds_content

    def integration_load_data_test(self):
        """
        Check the load data function in its entirety
        :return:
        """

        self.dh.load_data('lai')

        # Check that the type is a dataset
        ntools.assert_is_instance(self.dh.data, xr.Dataset)

class TestViewGenerator:
    """
    Test elements of the view generator
    """

    def setup(self):
        """
        setup for these tests
        :return:
        """
        # create generate view object
        self.gv = GenerateView(os.path.abspath("../data"))

        # Load dummy data based on the LAI profile in the 'data' directory
        self.gv.data = xr.open_dataset('dummy_data_lai.nc')


    def build_slider_test(self):
        """
        Test that we build a slider
        :return:
        """

        # Build the slider
        self.gv.slider()

        # Assert the id
        assert self.gv.slider.id == 'time-slider'

        # Assert length of time slider
        assert len(self.gv.slider.marks) == 6