# Crowdpurr results generation script for Gateaway 2018

To run this yourself, just clone the repo, install the Python dependencies (I recommend using the Anaconda Python distro), then run the script
against the data file in the data directory from Sep 29, 2018.

To install the dependencies using the Anaconda distro, I think this should do it:

`conda create -n pydata pandas numpy scipy seaborn ipython-notebook python=3`

`pip install reportlab`


# Run the script

To run with a 20% trimmed mean:

`./crowdpurr.py --trim 0.2 data/CrowdActivityExport_09292018_10-41AM.csv`

You will now have a bunch of .png and .pdf files in the directory. To open them on an OSX laptop:

`open *.pdf`

