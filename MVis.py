import sys
from src.MultiplyVis import MultiplyVis

"""
To run the MULTIPLY visualisation with default data, type the following:

> import MVis
> MVis.show()

To use a bespoke directory, type:
> MVis.show(os.path.abspath('path/to/directory')

"""

def show(directory=None):

    if directory:

        MultiplyVis(directory)

    else:

        MultiplyVis()


if __name__ == "__main__":

    #MultiplyVis()

    if len(sys.argv) > 1 :
        show(sys.argv[1])
    else:
        show()
