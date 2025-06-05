# Required Libraries 

import astropy.io.fits as pyfits
from pyraf import iraf
import os 
import glob 
import fnmatch 

print("Current working directory:{0}".format(os.getcwd()))
os.chdir('') # To where the data is located
print("Working directory changed to:{0}".format(os.getcwd()))


# To remove existing logfiles 

for x in glob.glob('*_t'):
    os.remove(x)
for file in sorted(os.listdir()):
    if (os.path.exists("all")):
        os.remove("all")
    elif (os.path.exists("logfile")):
        os.remove("logfile")

iraf.imutil(_doprint=0)
iraf.noao(_doprint = 0)
iraf.imred(_doprint = 0)
iraf.ccdred(_doprint = 0)
iraf.specred(_doprint = 0)

# Changing the Pixel Type

iraf.chpixtype.setParam('input','*.fits')
iraf.chpixtype.setParam('output','*.fits')
iraf.chpixtype.setParam('newpixtype','ushort')
iraf.chpixtype.setParam('(oldpixtype)','all')
iraf.chpixtype.setParam('(verbose)','yes')

# Changing the Dispersion Axis

iraf.ccdhedit.setParam('images','*.fits')
iraf.ccdhedit.setParam('parameter','DISPAXIS')
iraf.ccdhedit.setParam('value','1')
iraf.ccdhedit.setParam('type','string')

# Creating list of files



# Trimming and Removing Bad Pixels

iraf.ccdproc.setParam('input')







