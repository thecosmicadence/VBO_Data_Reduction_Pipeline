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

# Sorting files based on IMAGETYP ; Obtaining the Read Noise and Gain information from Header

obj = []
bias = []
comp = []
dft = []
x = sorted(glob.glob('*.fits'))
index = 0

print("\nObtaining the Read Noise and Gain information from Header...")

for i in range(len(x)):
    hdulist = pyfits.open(x[i])
    if hdulist[0].header['IMAGETYP'] == 'object':
        readnoise = hdulist[0].header['RDNOISE']
        gain = hdulist[0].header['GAIN']
        index = i
        obj.append(x[i])   # append filename
    elif hdulist[0].header['IMAGETYP'] == 'zero':
        bias.append(x[i])  # append filename
    elif hdulist[0].header['IMAGETYP'] == 'comp':
        comp.append(x[i])  # append filename
    elif hdulist[0].header['IMAGETYP'] == 'flat':
        dft.append(x[i])   # append filename
    hdulist.close()
    

print("\nBias Frames:", bias)
print("\nObject Frames:", obj)
print("\nComparison Frames:", comp)
print("\nFlat Frames:", dft)

# To specify the region of trimming

print("\nPlease examine the image and specify the region to be trimmed")
hdulist = pyfits.open(x[index])
d = pyds9.DS9()
d.set('file '+str(x[index]))
x1, x2, y1, y2 = map(int, input("Enter the coordinates (x1 x2 y1 y2) to be trimmed: ").split())
hdulist.close()

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

bias = [f.replace('.fits', '_t.fits') for f in bias]
obj  = [f.replace('.fits', '_t.fits') for f in obj]
comp = [f.replace('.fits', '_t.fits') for f in comp]
dft  = [f.replace('.fits', '_t.fits') for f in dft]

print("\nBias Frames after trimming:", bias)
print("\nObject Frames after trimming:", obj)
print("\nComparison Frames after trimming:", comp)
print("\nFlat Frames after trimming:", dft)

# Getting Files Ready for Bias Correction

with open('bias.in', 'w') as b:
    for file in sorted([f for f in bias if f.endswith('_t.fits')]):
        b.write(file + os.linesep)

with open('bs.in', 'w') as b_out:
    for file in sorted([f for f in (obj + comp + dft) if f.endswith('_t.fits')]):
        b_out.write(file + os.linesep)

with open('bs.in', 'r') as b_in, open('bs.out', 'w') as b_out:
    for line in b_in:
        b_out.write(line.strip().replace('.fits', 'b.fits') + os.linesep)

# Removing Bad Bias Frames

print("\nRemove bias file names based on image statistics:")
iraf.imstat.setParam('images','@bias.in')
iraf.imstat()
input('Press Enter to Continue...')
print("\nPlease edit the bias.in file to remove bad bias frames."
      " After editing, save and close the file to continue.")

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

obj  = [f.replace('.fits', 'b.fits') for f in obj]
comp = [f.replace('.fits', 'b.fits') for f in comp]
dft  = [f.replace('.fits', 'b.fits') for f in dft]

# Getting Files Ready for Flat Correction

with open('flat.in', 'w') as flat:
    for file in sorted([f for f in dft if f.endswith('tb.fits')]):
        flat.write(file + os.linesep)

with open('flatf.in', 'w') as f_out:
    for file in sorted([f for f in obj if f.endswith('tb.fits')]):
        f_out.write(file + os.linesep)

with open('flatf.in', 'r') as f_in, open('flatf.out', 'w') as f_out:
    for line in f_in:
        f_out.write(line.strip().replace('.fits', 'f.fits') + os.linesep)

# Removing Bad Flat Frames

print("\nRemove flat file names based on image statistics:")
iraf.imstat.setParam('images','@flat.in')
iraf.imstat()
input('Press Enter to Continue...')
print("\nPlease edit the flat.in file to remove bad flat frames."
      " After editing, save and close the file to continue.")

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

print("\nFlat-fielding the star frames...")
iraf.ccdproc.setParam('images','@flatf.in')
iraf.ccdproc.setParam('output','@flatf.out')
iraf.ccdproc.setParam('trim','no')
iraf.ccdproc.setParam('zerocor','no')
iraf.ccdproc.setParam('flatcor','yes')
iraf.ccdproc.setParam('flat','nmaster_flat.fits')

iraf.ccdproc()
print("\nFlat-fielded the star frames successfully!")

obj  = [f.replace('.fits', 'f.fits') for f in obj]

# Extracting the Aperture of Star Frames

print("\nAperture extraction:")
iraf.apall.setParam('nfind','1')
iraf.apall.setParam('background','median')
iraf.apall.setParam('weights','variance')
iraf.apall.setParam('clean','yes')
iraf.apall.setParam('saturation','60000')
iraf.apall.setParam('readnoise',readnoise)
iraf.apall.setParam('gain',gain)

for file in sorted([f for f in obj if f.endswith('tbf.fits')] + [f for f in comp if f.endswith('tb.fits')]):
    prompt_apall = 'yes'
    while prompt_apall == 'yes':
        print("\nAperture extraction for " + str(file))
        iraf.apall.setParam('input', file)
        iraf.apall()
        prompt_apall = input('\nDo you want to reselect aperture for current file? (yes/no):')

obj  = [f.replace('.fits', '.ms.fits') for f in obj]
comp  = [f.replace('.fits', '.ms.fits') for f in comp]

# Line Identification 

tb_ms_files = sorted(
    [f for f in obj if 'tbf.ms' in f] +
    [f for f in comp if 'tb.ms' in f]
)

prompt_line = 'yes'
for x in comp:
    if prompt_line.lower() != 'yes':  # Check if user wants to stop
        break
    print("\nLine identification for "+str(x))
    iraf.identify(images=x) 
    prompt_line = input("\nDo you want to continue?(yes/no):")

# Mapping reference spectral lines to star frames

prompt_ref = 'yes'
reference_file = input("Enter the reference spectrum filename: ")

for x in obj:
    if prompt_ref.lower() != 'yes':  # Check if user wants to stop
        break
    iraf.refspectra.setParam('input', x)
    iraf.refspectra.setParam('references', reference_file)
    iraf.refspectra()
    prompt_ref = input("\nDo you want to continue?(yes/no):")

# Dispersion correction (or) Wavelength Calibration

print("\nPerforming Dispersion Correction for selected files...")

with open('disp.in', 'w') as d_out:
    for file in tb_ms_files:
        d_out.write(file + os.linesep)

with open('disp.in', 'r') as d_in, open('disp.out', 'w') as d_out:
    for line in d_in:
        d_out.write(line.strip().replace('.ms.fits', 'w.ms.fits') + os.linesep)

var3 = 'disp.in'
os.system('gedit '+var3)
var4 = 'disp.out'
os.system('gedit '+var4)
print("\nUpdated successfully!")

iraf.dispcor.setParam('input','@disp.in')
iraf.dispcor.setParam('output','@disp.out')
iraf.dispcor()

obj  = [f.replace('.ms.fits', 'w.ms.fits') for f in obj]

# Normalizing the Reduced Spectra

print("\nNormalizing the reduced spectra...")

with open('final.in', 'w') as final_out:
    for file in sorted([f for f in obj if 'tbfw.ms' in f]):
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