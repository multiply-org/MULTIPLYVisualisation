#######################################################
#
# MultiplyVis.py
# Orchestrator class for the multiply Visualisation
#
# Created on:      12-Jun-2019
# Original author: Bethan Perkins
#
#######################################################

from src.GenerateView import GenerateView
import os

class MultiplyVis:
    """
    This is the wrapper/orchestrator class for the MULTIPLY visualisation
    """
    def __init__(self):
        """
        This should start up on initialisation.

        Could potentially give it a directory to work from in the future - depends on how the use cases work out.
        """
        data_directory = os.path.abspath('../data/')

        app = GenerateView(data_directory)

        app.run_server(debug=True)