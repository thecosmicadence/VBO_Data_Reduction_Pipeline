# Required Libraries 

import astropy.io.fits as pyfits
from pyraf import iraf
import os 
import glob 
import fnmatch 
import itertools

# Change the current working directory to the one that has data

print("Current working directory:{0}".format(os.getcwd()))
os.chdir('/home/luciferat022/Documents/GitHub/VBT_Data_Reduction_Pipeline/02jan2025') # To where the data is located
print("Working directory changed to:{0}".format(os.getcwd()))


# To remove existing logfiles 

for x in glob.glob('*_t*'):
    os.remove(x)

for x in glob.glob('*_tb*'):
    os.remove(x)

for x in glob.glob('*_tbf*'):
    os.remove(x)

for x in glob.glob('*master*'):
    os.remove(x)

for x in glob.glob('*.ms.fits'):
    os.remove(x)

for x in glob.glob('*c.fits'):
    os.remove(x)

for file in sorted(os.listdir()):
    if (os.path.exists("all")):
        os.remove("all")
    elif (os.path.exists('all_t')):
        os.remove('all_t')
    elif (os.path.exists("logfile")):
        os.remove("logfile")
    elif (os.path.exists("bias.in")):
        os.remove('bias.in')
    elif (os.path.exists('bs.in')):
        os.remove('bs.in')
    elif (os.path.exists('bs.out')):
        os.remove('bs.out')
    elif (os.path.exists("flat.in")):
        os.remove('flat.in')
    elif (os.path.exists('flatf.in')):
        os.remove('flatf.in')
    elif (os.path.exists('flatf.out')):
        os.remove('flatf.out')
    elif (os.path.exists('disp.in')):
        os.remove('disp.in')
    elif (os.path.exists('disp.out')):
        os.remove('disp.out')
    elif (os.path.exists('final.in')):
        os.remove('final.in')
    elif (os.path.exists('final.out')):
        os.remove('final.out')

# Initializing required IRAF packages

iraf.imutil(_doprint=0)
iraf.noao(_doprint = 0)
iraf.imred(_doprint = 0)
iraf.ccdred(_doprint = 0)
iraf.specred(_doprint = 0)

# Changing the Pixel Type

iraf.chpixtype.setParam('input','*.fits')
iraf.chpixtype.setParam('output','*.fits')
iraf.chpixtype.setParam('newpixtype','ushort')
iraf.chpixtype.setParam('oldpixtype','all')
iraf.chpixtype.setParam('verbose','yes')
iraf.chpixtype()

# Changing the Dispersion Axis

iraf.ccdhedit.setParam('images','*.fits')
iraf.ccdhedit.setParam('parameter','DISPAXIS')
iraf.ccdhedit.setParam('value','1')
iraf.ccdhedit.setParam('type','string')
iraf.ccdhedit()

# Creating list of files

for file in sorted(os.listdir()):
    with open('all', mode='a') as all:
        if file.endswith('.fits'):
            f = os.path.join(file)
            all.write(str(f) + os.linesep)
            all.close()
        
with open ('all','r') as file:
    filedata = file.read()
    filedata = filedata.replace('.fits','_t.fits')
    
with open ('all_t', 'w') as all_t:
    all_t.write(filedata)
    all_t.close()

# Trimming and Removing Bad Pixels

iraf.ccdproc.setParam('images','@all')
iraf.ccdproc.setParam('output','@all_t')
iraf.ccdproc.setParam('trim','yes')
iraf.ccdproc.setParam('zerocor','no')
iraf.ccdproc.setParam('flatcor','no')
iraf.ccdproc.setParam('fixfile','badpix')
iraf.ccdproc.setParam('biassec','image')
iraf.ccdproc.setParam('trimsec','[15:1325, 15:385]') 

iraf.ccdproc()

# Getting Files Ready for Bias Correction

files = sorted(glob.glob('*bias*t.fits'))

with open('bias.in', 'w') as bias:
    bias.write(os.linesep.join(files))

with open('bs.in', 'w') as f_out:
    for pattern in ['*obj*t.fits', '*comp*t.fits', '*dft*t.fits']:
        for file in sorted(glob.glob(pattern)):
            f_out.write(file + os.linesep)

with open('bs.in', 'r') as f_in, open('bs.out', 'w') as f_out:
    for line in f_in:
        f_out.write(line.replace('.fits', 'b.fits'))

# Removing Bad Bias Frames

iraf.imstat.setParam('images','@bias.in')
iraf.imstat()
input('Press Enter to Continue...')

# Bias list editing
var1 = 'bias.in'
os.system('gedit '+var1)

# Creating Master Bias Frame

iraf.zerocombine.setParam('input','@bias.in')
iraf.zerocombine.setParam('output','master_bias.fits')
iraf.zerocombine.setParam('combine','average')
iraf.zerocombine.setParam('reject','minmax')
iraf.zerocombine.setParam('ccdtype','zero')
iraf.zerocombine.setParam('rdnoise','4.8')
iraf.zerocombine.setParam('gain','1.22')

iraf.zerocombine()

# Bias Correction

iraf.ccdproc.setParam('images','@bs.in')
iraf.ccdproc.setParam('output','@bs.out')
iraf.ccdproc.setParam('trim','no')
iraf.ccdproc.setParam('zerocor','yes')
iraf.ccdproc.setParam('flatcor','no')
iraf.ccdproc.setParam('zero','master_bias.fits')

iraf.ccdproc()

# Getting Files Ready for Flat Correction

files = sorted(glob.glob('*dft*tb.fits'))

with open('flat.in', 'w') as flat:
    flat.write(os.linesep.join(files))

with open('flatf.in', 'w') as f_out:
    for pattern in ['*obj*tb.fits']:
        for file in sorted(glob.glob(pattern)):
            f_out.write(file + os.linesep)

with open('flatf.in', 'r') as f_in, open('flatf.out', 'w') as f_out:
    for line in f_in:
        f_out.write(line.replace('.fits', 'f.fits'))

# Removing Bad Flat Frames

iraf.imstat.setParam('images','@flat.in')
iraf.imstat()
input('Press Enter to Continue...')

# Bias list editing
var2 = 'flat.in'
os.system('gedit '+var2)

# Creating Master Flat Frame
iraf.flatcombine.setParam('input','@flat.in')
iraf.flatcombine.setParam('output','master_flat.fits')
iraf.flatcombine.setParam('combine','average')
iraf.flatcombine.setParam('reject','avsigclip')
iraf.flatcombine.setParam('ccdtype','flat')
iraf.flatcombine.setParam('rdnoise','4.8')
iraf.flatcombine.setParam('gain','1.22')

iraf.flatcombine()

# Normalised Flat Frame 

iraf.response.setParam('calibration','master_flat.fits')
iraf.response.setParam('normalization','master_flat.fits')
iraf.response.setParam('response','nmaster_flat.fits')
iraf.response.setParam('interactive','yes')
iraf.response.setParam('threshold','INDEF')
iraf.response.setParam('sample','*')
iraf.response.setParam('function','spline3')
iraf.response.setParam('order','3')

iraf.response()


# Flat Correction

iraf.ccdproc.setParam('images','@flatf.in')
iraf.ccdproc.setParam('output','@flatf.out')
iraf.ccdproc.setParam('trim','no')
iraf.ccdproc.setParam('zerocor','no')
iraf.ccdproc.setParam('flatcor','yes')
iraf.ccdproc.setParam('flat','nmaster_flat.fits')

iraf.ccdproc()

# Extracting the Aperture of Star Frames

iraf.apall.setParam('nfind','1')
iraf.apall.setParam('background','median')
iraf.apall.setParam('weights','variance')
iraf.apall.setParam('clean','yes')
iraf.apall.setParam('saturation','60000')
iraf.apall.setParam('readnoise','4.8')
iraf.apall.setParam('gain','1.22')

for pattern in ['*obj*tbf.fits','*comp*tb.fits']:
    for file in sorted(glob.glob(pattern)):
        prompt = 'yes'
        while prompt=='yes':
            iraf.apall.setParam('input', file)
            iraf.apall()  
            prompt = input('Do you want to reselect aperture? (yes/no):')

# Line Identification

for x in glob.glob('*tb.ms*'):
    iraf.identify(images=x) 

# Mapping reference spectral lines to star frames

for x in glob.glob('*tbf.ms*'):
    iraf.refspectra.eParam()

# Dispersion correction (or) Wavelength Calibration

with open('disp.in', 'w') as d_out:
    for pattern in ['*comp*ms*','*obj*ms*']:
        for file in sorted(glob.glob(pattern)):
            d_out.write(file + os.linesep)

with open('disp.in', 'r') as d_in, open('disp.out', 'w') as d_out:
    for line in d_in:
        d_out.write(line.replace('.ms.fits', 'w.ms.fits'))

iraf.dispcor.setParam('input','@disp.in')
iraf.dispcor.setParam('output','@disp.out')
iraf.dispcor()

# Normalizing the Reduced Spectra

with open('final.in', 'w') as final_out:
    for pattern in ['*obj*tbfw.ms*']:
        for file in sorted(glob.glob(pattern)):
            final_out.write(file + os.linesep)

with open('final.in', 'r') as final_in, open('final.out', 'w') as final_out:
    for line in final_in:
        d_out.write(line.replace('tbfw.ms.fits', 'c.fits'))

iraf.continuum.setParam('input','@final.in')
iraf.continuum.setParam('output','@final.out')
iraf.continuum.setParam('naverage','3')
iraf.continuum.setParam('order','6')
iraf.continuum.setParam('high_reject','2')
iraf.continuum()

print('UAGS Spectroscopic Data Reduction Completed Successfully!')
