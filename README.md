![image](https://github.com/patternizer/pha-prepare/blob/master/stationlistmap.png)

# pha-prepare

Python pre-processor to generate input station files and station list file for NOAA's PHA v52i algorithm for pairwise homogenisation of land surface air temperature monitoring station subsets from CRUTEM5 in the [GloSAT](https://www.glosat.org) project:

* python input file generation code

## Contents

* `pha-prepare.py` - python code to generate station list and station input files + subset map
* `rate-of-station-loss.py` - python code to calculate the rate of station loss as a fnuction of minimum years of data requirement

The first step is to clone the latest pha-prepare code and step into the check out directory: 

    $ git clone https://github.com/patternizer/pha-prepare.git
    $ cd pha-prepare

### Using Standard Python

The code should run with the [standard CPython](https://www.python.org/downloads/) installation and was tested in a conda virtual environment running a 64-bit version of Python 3.8+.

pha-prepare scripts can be run from sources directly on input data from CRUTEM.

Run with:

    $ python pha-prepare.py
    $ python rate-of-station-loss.py

For your PHA v52i set up:

* Copy the world1_stnlist.tavg file to your run directory: /pha_v52i/data/benchmark/world1/meta/ 
* Copy the station files [stationid].raw.tavg to your run directory: /pha_v52i/data/benchmark/world1/monthly/raw/

## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)

