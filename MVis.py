import sys
from src.MultiplyVis import MultiplyVis

"""
To run the MULTIPLY visualisation with default data, type the following:

> import MVis
> MVis.show()

To use a bespoke directory, type:
> MVis.show(os.path.abspath('path/to/directory')

"""

def show(directory=None, kaska=False, port=None):

    if directory:

        MultiplyVis(directory, kaska, port)

    else:

        MultiplyVis(kaska=kaska, port=port)


if __name__ == "__main__":

    #MultiplyVis()

    if len(sys.argv) == 2 :
        show(sys.argv[1], sys.argv[2].lower() == 'true')
    elif len(sys.argv) == 3 :
        show(sys.argv[1], sys.argv[2].lower()=='true', sys.argv[3])
    else:
        show()
