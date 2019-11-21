#!/usr/bin/env python

import logging
import os
import datetime as dt
import numpy as np
import gdal
import osr
from shutil import copyfile
import scipy.sparse as sp
import _pickle as cPickle

# from multiply.inference-engine blah blah blah
try:
    from multiply_prior_engine import PriorEngine
except ImportError:
    pass


import kafka
from kafka.input_output import Sentinel2Observations, KafkaOutput
from kafka import LinearKalman
from kafka.inference.narrowbandSAIL_tools import propagate_LAI_narrowbandSAIL
from kafka.inference import create_prosail_observation_operator
from kafka.inference.narrowbandSAIL_tools import SAILPrior
from kafka.inference.temporal_prior import TemporalSAILPrior
from kafka.inference.propagate_phenology import TrajectoryFromPrior
'''
def reproject_image(source_img, target_img, dstSRSs=None):
    """Reprojects/Warps an image to fit exactly another image.
    Additionally, you can set the destination SRS if you want
    to or if it isn't defined in the source image."""
    g = gdal.Open(target_img)
    geo_t = g.GetGeoTransform()
    x_size, y_size = g.RasterXSize, g.RasterYSize
    xmin = min(geo_t[0], geo_t[0] + x_size * geo_t[1])
    xmax = max(geo_t[0], geo_t[0] + x_size * geo_t[1])
    ymin = min(geo_t[3], geo_t[3] + y_size * geo_t[5])
    ymax = max(geo_t[3], geo_t[3] + y_size * geo_t[5])
    xRes, yRes = abs(geo_t[1]), abs(geo_t[5])
    if dstSRSs is None:
        dstSRS = osr.SpatialReference()
        raster_wkt = g.GetProjection()
        dstSRS.ImportFromWkt(raster_wkt)
    else:
        dstSRS = dstSRSs
    g = gdal.Warp('', source_img, format='MEM',
                  outputBounds=[xmin, ymin, xmax, ymax], xRes=xRes, yRes=yRes,
                  dstSRS=dstSRS)
    return g


class KafkaOutputMemory(object):
    """A very simple class to output the state."""
    def __init__(self, parameter_list):
        self.parameter_list = parameter_list
        self.output = {}
    def dump_data(self, timestep, x_analysis, P_analysis, P_analysis_inv,
                state_mask):
        solution = {}
        for ii, param in enumerate(self.parameter_list):
            solution[param] = x_analysis[ii::7]
        self.output[timestep] = solution
'''
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == exc.errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main():

    # Set up logging
    Log = logging.getLogger(__name__+".kafka_test_x.py")

    runname = 'Barrax_Q1_noprior_S2'  #Used in output directory as a unique identifier

    logging.basicConfig(level=logging.getLevelName(logging.DEBUG),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename="logfiles/{}.log".format(runname))

    Qfactor = 1

    # To run without propagation set propagator to None and set a
    # prior in LinearKalman.
    # If propagator is set to propagate_LAI_narrowbandSAIL then the
    # prior in LinearKalman must be set to None because this propagator
    # includes a prior
    propagator = propagate_LAI_narrowbandSAIL

    parameter_list = ['n', 'cab', 'car', 'cbrown', 'cw', 'cm',
                      'lai', 'ala', 'bsoil', 'psoil']

    Log.info("propagator = {}".format(propagator))
    Log.info("Qfactor = {}".format(Qfactor))

    path = "/home/npounder/output/kafka/MULTIPLY/barrax/S2/kafkaout_{}".format(runname)
    if not os.path.exists(path):
        mkdir_p(path)
    Log.info("output path = {}".format(path))
    # copy relevant files across for records:
    copyfile("local_kafka_test_S2.py", path+'/run_script.py')

    #emulator_folder = "/home/ucfafyi/DATA/Multiply/emus/sail/"
    emulator_folder = "/home/glopez/Multiply/src/py36/emus/sail"
    #emulator_folder = "/data/archive/emulators/s2_prosail"

    ## Barrax
    state_mask = "./Barrax_pivots.tif"
    data_folder = "/data/001_planet_sentinel_study/sentinel/30/S/WJ"
    start_time = "2017001"
    time_grid_start = dt.datetime(2017, 1, 1)
    num_days = 366
    laiprior = "default"
    transformed_prior = False
    prior_unc = None

    ## California
    #start_time = "2017121"
    #time_grid_start = dt.datetime(2017, 5, 1)
    #time_grid_start = dt.datetime(2017, 3, 1)
    #data_folder = "/data/001_planet_sentinel_study/sentinel/11/S/KA"
    ##state_mask = "/data/001_planet_sentinel_study/planet/utm11n_sur_ref/field_sites.tif"
    ##state_mask = "/home/npounder/repositories/python3/KaFKA-InferenceEngine/dataCleansing/Window200Pix.tif"
    #state_mask = "/home/npounder/repositories/python3/KaFKA-InferenceEngine/dataCleansing/GoodFieldMask.tif"
    #num_days = 250

    ##  Quzhou
    #start_time = "2017001"
    #time_grid_start = dt.datetime(2017, 1, 1)
    #data_folder = "/data/Sentinel2/quizou/2017/to_correct_secondary/"
    ##state_mask = "/home/acornelius/KaFKA-InferenceEngine/quizou_100by100_mask.tif"
    ##state_mask = "/home/npounder/AlexCode/Quzou_WangzhuangSTB_mask.tif"
    #state_mask = "/home/npounder/AlexCode/Quzhou_WangzhuangSTB_mask_bigger.tif"
    #num_days = 365
    ##laiprior = "default"
    ##laiprior = "/media/DataShare/Alex/wofost/quizou_lai_WOFOST.pkl"
    ##laiprior = "/media/DataShare/Alex/wofost/quizou_lai_wofost_site_s01HB.pkl"
    #laiprior = "/home/npounder/repositories/python3/wofost_calibration/wofostPriors/Quzhou_wofost_lai_newhengshuical.pkl"
    #prior_unc = 0.5

    ##  Henan
    #start_time = "2016289"
    #time_grid_start = dt.datetime(2016, 10, 16)
    #data_folder = "/data/Sentinel2/henan/T49SGU/corrected2/"
    #state_mask = "/home/npounder/AlexCode/Henan_mask.tif"
    #num_days = 365
    ##laiprior = "default"
    ##laiprior = "/media/DataShare/Alex/wofost/henan_lai_wofost_site_s01HB.pkl"
    ##laiprior = "/home/npounder/repositories/python3/wofost_calibration/wofostPriors/henan_wofost_lai_newhengshuical.pkl"
    #laiprior = "/home/npounder/repositories/python3/wofost_calibration/wofostPriors/Mean_TLAI_HenanCal_site1.pkl"
    #transformed_prior=True
    #prior_unc = 0.5
    #prior_unc = "/home/npounder/repositories/python3/wofost_calibration/wofostPriors/SD_TLAI_HenanCal_site1.pkl"


    ##  Hengshui
    #start_time = "2016245"
    #time_grid_start = dt.datetime(2016, 9, 1)
    #data_folder = "/data/Sentinel2/China/~ucfafyi/S2_data/50/S/LG/"
    #state_mask = "/home/npounder/AlexCode/HS01_mask.tif"
    #num_days = 500
    #laiprior = "default"
    #laiprior = "/media/DataShare/Nicola/NplusIntegration/hengshui_lai_wofost.pkl"
    #prior_unc = 2.0

    Log.info("start_time = {}".format(start_time))

    s2_observations = Sentinel2Observations(data_folder,
                                            emulator_folder,
                                            state_mask)
    s2_observations.check_mask()
    projection, geotransform = s2_observations.define_output()

    output = KafkaOutput(parameter_list, geotransform,
                         projection, path)

    # If using a separate prior then this is passed to LinearKalman
    # Otherwise this is just used to set the starting state vector.
    if laiprior == "default":
        # Original SAIL prior
        the_prior = SAILPrior(parameter_list, state_mask)
    else:
        # Temporal prior. laiprior should be a pickled dictionary
        lai = cPickle.load(open(laiprior, 'rb'), encoding='bytes')
        if transformed_prior:
            t_lai = {key.date(): val for key, val in lai.items()}
        else:
            try:
                # WOFOST prior stored as a dictionary
                t_lai = {key: np.exp(-val / 2.) for key, val in lai.items()
                         if val is not None}
            except AttributeError:
                # WOFOST prior stored as two lists
                t_lai = {key: np.exp(-val / 2.) for key, val in zip(*lai)
                         if val is not None}

        try:
            t_lai_unc = cPickle.load(open(prior_unc, 'rb'), encoding='bytes')
        except TypeError:
            if transformed_prior:
                t_lai_unc = prior_unc
            else:
                t_lai_unc = {key: (-0.5 * prior_unc * t_val) for key, t_val in t_lai.items()}
        t_lai_unc_invcov = {key: 1.0 / unc**2 for key, unc in t_lai_unc.items()}

        the_prior = TemporalSAILPrior(parameter_list, state_mask, t_lai, t_lai_unc_invcov)


    g = gdal.Open(state_mask)
    mask = g.ReadAsArray().astype(np.bool)

    # prior = None when using propagate_LAI_narrowbandSAIL
    kf = LinearKalman(s2_observations, output, mask,
                      create_prosail_observation_operator,
                      parameter_list,
                      state_propagation=propagator,
                      prior=None, #the_prior,
                      linear=False)

    # This determines the time grid of the retrieved state parameters
    time_grid = list((time_grid_start + dt.timedelta(days=x)
                     for x in range(0, num_days, 1)))
    # Get starting state... We can request the prior object for this
    x_forecast, P_forecast_inv = the_prior.process_prior(time_grid[0])

    # Inflation amount for propagation
    Q = np.zeros_like(x_forecast)
    Q[6::10] = Qfactor

    #dates_traj_prior = sorted(t_lai)
    #t_lai_traj_prior = [t_lai[d] for d in dates_traj_prior]
    #trajectory_model = TrajectoryFromPrior(dates_traj_prior, t_lai_traj_prior)
    kf.set_trajectory_model()  # Defaults to identitiy matrix (today like yesterday)
    #kf.set_trajectory_model(trajectory_model.M_matrix)
    kf.set_trajectory_uncertainty(Q)

    kf.run(time_grid, x_forecast, None, P_forecast_inv,
           iter_obs_op=True)


if __name__ == "__main__":
    main()
