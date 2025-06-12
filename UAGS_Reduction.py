# Required Libraries 

import astropy.io.fits as pyfits
from pyraf import iraf
import os 
import glob 
import shutil
import pyds9

# Change the current working directory to the one that has data

print("Current working directory:{0}".format(os.getcwd()))
directory = input("Enter the path to directory where the data is located:")
os.chdir(directory) # To where the data is located
print("Working directory changed to:{0}".format(os.getcwd()))

# Obtaining the Read Noise and Gain information from Header
# To specify the region of trimming

x = sort(glob.glob('*obj*.fits'))
print(x[0])
hdulist = pyfits.open(x[0])
readnoise = hdulist[0].header['RDNOISE']
gain = hdulist[0].header['GAIN']

d = pyds9.DS9()
d.set('file '+str(x[0]))
x1, x2, y1, y2 = map(int, input("Enter the coordinates (x1 x2 y1 y2) to be trimmed: ").split())
hdulist.close()


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
    elif os.path.exists('database'):  # New condition for directory
        shutil.rmtree('database')  

# Initializing required IRAF packages

iraf.imutil(_doprint=0)
iraf.noao(_doprint = 0)
iraf.imred(_doprint = 0)
iraf.ccdred(_doprint = 0)
iraf.specred(_doprint = 0)

# Changing the Pixel Type

print("\n Pixel type being changed to 'ushort'...")
iraf.chpixtype.setParam('input','*.fits')
iraf.chpixtype.setParam('output','*.fits')
iraf.chpixtype.setParam('newpixtype','ushort')
iraf.chpixtype.setParam('oldpixtype','all')
iraf.chpixtype.setParam('verbose','yes')
iraf.chpixtype()
print("\nSuccessfully changed the pixel type!")

# Changing the Dispersion Axis

print("\n Dispersion axis being updated to '1'...")
iraf.ccdhedit.setParam('images','*.fits')
iraf.ccdhedit.setParam('parameter','DISPAXIS')
iraf.ccdhedit.setParam('value','1')
iraf.ccdhedit.setParam('type','string')
iraf.ccdhedit()
print("\n Dispersion Axis update successful!")

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

trimmed = f"[{x1}:{x2},{y1}:{y2}]"
print("\n Unwanted regions in the frame are being trimmed...")
iraf.ccdproc.setParam('images','@all')
iraf.ccdproc.setParam('output','@all_t')
iraf.ccdproc.setParam('trim','yes')
iraf.ccdproc.setParam('zerocor','no')
iraf.ccdproc.setParam('flatcor','no')
iraf.ccdproc.setParam('fixfile','badpix')
iraf.ccdproc.setParam('biassec','image')
iraf.ccdproc.setParam('trimsec', trimmed) 

iraf.ccdproc()
print("\nTrimmed successfully!")

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

print("\nRemove bias file names based on image statistics:")
iraf.imstat.setParam('images','@bias.in')
iraf.imstat()
input('Press Enter to Continue...')

# Bias list editing

var1 = 'bias.in'
os.system('gedit '+var1)
print("\nUpdated bias files for zerocombine successfully!")

# Creating Master Bias Frame

print("\nMaster Bias being created...")
iraf.zerocombine.setParam('input','@bias.in')
iraf.zerocombine.setParam('output','master_bias.fits')
iraf.zerocombine.setParam('combine','average')
iraf.zerocombine.setParam('reject','minmax')
iraf.zerocombine.setParam('ccdtype','zero')
iraf.zerocombine.setParam('rdnoise',readnoise)
iraf.zerocombine.setParam('gain',gain)

iraf.zerocombine()
print("\nMaster Bias created successfully")
iraf.imstat('master_bias.fits')

# Bias Correction

print("Subtracting masterbias from other frames...")
iraf.ccdproc.setParam('images','@bs.in')
iraf.ccdproc.setParam('output','@bs.out')
iraf.ccdproc.setParam('trim','no')
iraf.ccdproc.setParam('zerocor','yes')
iraf.ccdproc.setParam('flatcor','no')
iraf.ccdproc.setParam('zero','master_bias.fits')

iraf.ccdproc()
print("\nBias subtraction successful!")

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

print("\nRemove flat file names based on image statistics:")
iraf.imstat.setParam('images','@flat.in')
iraf.imstat()
input('Press Enter to Continue...')

# Flat list editing

var2 = 'flat.in'
os.system('gedit '+var2)
print("\nUpdated flat files for zerocombine successfully!")

# Creating Master Flat Frame

print("\nMaster Flat being created...")
iraf.flatcombine.setParam('input','@flat.in')
iraf.flatcombine.setParam('output','master_flat.fits')
iraf.flatcombine.setParam('combine','average')
iraf.flatcombine.setParam('reject','avsigclip')
iraf.flatcombine.setParam('ccdtype','flat')
iraf.flatcombine.setParam('rdnoise',readnoise)
iraf.flatcombine.setParam('gain',gain)

iraf.flatcombine()
print("\nMaster Flat created successfully")

# Normalised Flat Frame 

print("\nCreating Normalized Flat frame...")
iraf.response.setParam('calibration','master_flat.fits')
iraf.response.setParam('normalization','master_flat.fits')
iraf.response.setParam('response','nmaster_flat.fits')
iraf.response.setParam('interactive','yes')
iraf.response.setParam('threshold','INDEF')
iraf.response.setParam('sample','*')
iraf.response.setParam('function','spline3')
iraf.response.setParam('order','3')

iraf.response()
print("\nNormalized Flat Frame created successfully!")

# Flat Correction

print("Flat-fielding the star frames...")
iraf.ccdproc.setParam('images','@flatf.in')
iraf.ccdproc.setParam('output','@flatf.out')
iraf.ccdproc.setParam('trim','no')
iraf.ccdproc.setParam('zerocor','no')
iraf.ccdproc.setParam('flatcor','yes')
iraf.ccdproc.setParam('flat','nmaster_flat.fits')

iraf.ccdproc()
print("Flat-fielded the star frames successfully!")

# Extracting the Aperture of Star Frames

print("Aperture extraction:")
iraf.apall.setParam('nfind','1')
iraf.apall.setParam('background','median')
iraf.apall.setParam('weights','variance')
iraf.apall.setParam('clean','yes')
iraf.apall.setParam('saturation','60000')
iraf.apall.setParam('readnoise',readnoise)
iraf.apall.setParam('gain',gain)

for pattern in ['*obj*tbf.fits','*comp*tb.fits']:
    for file in sorted(glob.glob(pattern)):
        prompt_apall = 'yes'
        while prompt_apall=='yes':
            print("\nAperture extraction for "+str(file))
            iraf.apall.setParam('input', file)
            iraf.apall()  
            prompt_apall = input('\nDo you want to reselect aperture for current file? (yes/no):')

# Line Identification 

prompt_line = 'yes'
for x in sorted(glob.glob('*tb.ms*')):
    if prompt_line.lower() != 'yes':  # Check if user wants to stop
        break
    print("\nLine identification for "+str(x))
    iraf.identify(images=x) 
    prompt_line = input("\nDo you want to continue?(yes/no):")

# Mapping reference spectral lines to star frames

prompt_ref = 'yes'
for x in sorted(glob.glob('*tb.ms*')):
    if prompt_ref.lower() != 'yes':  # Check if user wants to stop
        break
    print("\nReferring comparison spectra to "+str(x))
    iraf.refspectra(images=x) 
    prompt_ref = input("\nDo you want to continue?(yes/no):")

# Dispersion correction (or) Wavelength Calibration

print("Performing Dispersion Correction for selected files...")

with open('disp.in', 'w') as d_out:
    for pattern in ['*comp*ms*','*obj*ms*']:
        for file in sorted(glob.glob(pattern)):
            d_out.write(file + os.linesep)

with open('disp.in', 'r') as d_in, open('disp.out', 'w') as d_out:
    for line in d_in:
        d_out.write(line.replace('.ms.fits', 'w.ms.fits'))

var3 = 'disp.in'
os.system('gedit '+var3)
var4 = 'disp.out'
os.system('gedit '+var4)
print("\nUpdated successfully!")

iraf.dispcor.setParam('input','@disp.in')
iraf.dispcor.setParam('output','@disp.out')
iraf.dispcor()

# Normalizing the Reduced Spectra

print("Normalizing the reduced spectra...")

with open('final.in', 'w') as final_out:
    for pattern in ['*obj*tbfw.ms*']:
        for file in sorted(glob.glob(pattern)):
            final_out.write(file + os.linesep)

with open('final.in', 'r') as final_in, open('final.out', 'w') as final_out:
    for line in final_in:
        final_out.write(line.replace('tbfw.ms.fits', 'c.fits'))

iraf.continuum.setParam('input','@final.in')
iraf.continuum.setParam('output','@final.out')
iraf.continuum.setParam('naverage','3')
iraf.continuum.setParam('order','6')
iraf.continuum.setParam('high_reject','2')
iraf.continuum()

print('UAGS Spectroscopic Data Reduction Completed Successfully!')
