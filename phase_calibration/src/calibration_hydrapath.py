# Calibrate antenna modules with the fringe fitting approach by using the radio star Hydra's signal

import sys
import os

# External libraries
import numpy
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
import ephem
from antenna_pattern_jro import *

# Signal chain
from schainpy.model import *
from schainpy.admin import SchainWarning

def hydrapath(timeobj, N, step):
    """
    Calculates the position of hydra in the antenna plane.
    This routine is based on http://www.stargazing.net/kepler/altaz.html
    Input: Start time from data, number of steps, step size in seconds
    Output: Vectors of directional cosines relative to the antenna plane
    """
    # Now, let's calculate the position of Hydra
    # First, some constants
    lat = numpy.deg2rad(-11.951481)
    lon = -76.874383 # don't need to do trig with this one
    ra = numpy.deg2rad((9. + 17./60 + 6./3600)*15)
    dec = numpy.deg2rad(-(12. + 5./60))
       
    # Grab time data from the first block
    year = timeobj.year
    doy = float(timeobj.timetuple().tm_yday)
    hour = float(timeobj.hour)
    minute = float(timeobj.minute)
    second = float(timeobj.second)
    hod0 = hour + minute/60 + second/3600
    hodf = hod0 + (step/3600)*N
    
    # create a vector of time values for all of the data
    hod = numpy.arange(hod0, hodf, step/3600)
    # change to UTC... if the timestamps aren't already UTC?
    hod += 5
    
    # calculate days since j2000 epoch
    year_count = 2000
    jdate = -1.5
    
    while year_count < year:
        jdate += 365 + int(not(year_count % 4))
        year_count += 1
        
    jdate += doy + hod/24
    
    # calculate local sidereal time
    lst = ((18.697374558 + 24.06570982441908*jdate)*15 + lon) % 360
    lst = numpy.deg2rad(lst)
    # calculate hour angle
    ha = lst - ra
    # calculate altitude and azimuth (horizontal coordinates)
    t1 = (numpy.sin(dec)*numpy.sin(lat)
          +numpy.cos(dec)*numpy.cos(lat)*numpy.cos(ha))
    alt = numpy.arcsin(t1)
    # print alt
    t2 = ((numpy.sin(dec)-numpy.sin(alt)*numpy.sin(lat))
          /(numpy.cos(alt)*numpy.cos(lat)))
    a = numpy.arccos(t2)
    az = numpy.zeros(N)
    for i in range(0, N):
        if numpy.sin(ha[i]) < 0:
            az[i] = a[i]
        else:
            az[i] = 2*numpy.pi - a[i]
    
    # now change to standard spherical coords
    th = numpy.pi/2 - alt
    phi = numpy.pi/2 - az
    
    # now change to (normalized) cartesian
    x = numpy.sin(th)*numpy.cos(phi)
    y = numpy.sin(th)*numpy.sin(phi)
    z = numpy.cos(th)
    
    # rotate the y axis to NE (x axis to SE)
    # I need to check the validity of this still
    rot = numpy.deg2rad(45 + 6.166710)
    xnew = x*numpy.cos(rot) - y*numpy.sin(rot)
    ynew = x*numpy.sin(rot) + y*numpy.cos(rot)
    
    # rotate about the new x-axis by antenna tilt
    # because the NE side tilts up
    tilt = numpy.deg2rad(1.488312)
    # tilt = numpy.deg2rad(15.)
    x = xnew
    # y = ynew*numpy.cos(tilt) - z*numpy.sin(tilt)
    y = ynew*numpy.cos(tilt) + z*numpy.sin(tilt)
    
    # we are in normalized cartesian coordinates
    # so x and y are actually the direction cosines
    return x, y

def hydrapathnew(timeobj, N, step):
    """
    Calculates the position of Hydra in the antenna plane.
    This routine uses the PyEphem module to track Hydra's path.
    Input: Start time from data, number of steps, step size in seconds
    Output: Vectors of directional cosines relative to the antenna plane
    """

    hydra = ephem.FixedBody()
    hydra._ra = '9:17:0'
    hydra._dec = '-12:5:0'

    #hydra._ra = '9:27:35'
    #hydra._dec = '-8:39:31'

    obs = ephem.Observer()
    obs.date = ephem.date(timeobj)
    # Convert to UTC
    obs.date = ephem.date(obs.date + 5*ephem.hour)
    # Latitude, longitude, and elevation of the antenna center
    obs.lat = ephem.degrees('-11.951481')
    obs.lon = ephem.degrees('-76.874383')
    obs.elevation = 533.253887
     
    alt = numpy.zeros(N)
    az = numpy.zeros(N)
    for i in range(0, N):
        hydra.compute(obs)
        alt[i] = float(repr(hydra.alt))
        az[i] = float(repr(hydra.az))
        obs.date = ephem.date(obs.date + step*ephem.second)
    
    # now change to standard spherical coords
    th = numpy.pi/2 - alt
    phi = numpy.pi/2 - az
    
    # now change to (normalized) cartesian
    x = numpy.sin(th)*numpy.cos(phi)
    y = numpy.sin(th)*numpy.sin(phi)
    z = numpy.cos(th)
    
    # rotate the y axis to NE (x axis to SE)
    rot = numpy.deg2rad(45 + 6.166710) # 45 + 6.166710
    xnew = x*numpy.cos(rot) - y*numpy.sin(rot)
    ynew = x*numpy.sin(rot) + y*numpy.cos(rot)
    
    # rotate about the new x-axis by antenna tilt
    # because the NE side tilts up
    tilt = numpy.deg2rad(1.488312)
    x = xnew
    y = ynew*numpy.cos(tilt) + z*numpy.sin(tilt)
    
    # we are in normalized cartesian coordinates
    # so x and y are actually the direction cosines
    return x, y

def separation(a1, a2):
    """
    Calculate the antenna separation along the x and y directions, in meters.
    Input: numbers of two different antennas
    Output: separation between the two antennas (dx and dy)
    rx=127.5, 91.5, 127.5, 19.5, 91.5, -127.5, -55.5, -220.824
    ry=127.5, 91.5, 91.5, 55.5, -19.5, -127.5, -127.5, -322.294
    """
    apos = numpy.array([[127.50,127.50],[91.50,91.50],[127.50,91.50],
                        [19.50,55.50],[91.50,-19.50],[-127.50,-127.50],
                        [-55.50,-127.50],[-220.824,-322.294]])
    dx = apos[a1, 0] - apos[a2, 0]
    dy = apos[a1, 1] - apos[a2, 1]
    return dx, dy
 
def fit1(t, f, dx, dy, gpath, thx, thy, aguess, ct1guess, ct2guess):
    """
    Fits the cross spectral data to the model.
    Fitting parameters: amplitude, phase, complex offset (antenna crosstalk terms ct1 & ct2)

    t: time
    f: cross spectra
    dx,dy: antenna separation
    gpath: gain of antenna in Hydra path
    thx, thy: directional cosines of Hydra
    aguess: amplitude guess
    ct1guess, ct2guess: real and imaginary cross spectra guess (averaged)

    OUTPUT
    amp, ph, ct1, ct2, fitted
    """
    def model1(t, amp, ph, ct1, ct2):
        # array index variable
        ti = numpy.linspace(0, size-1, num=size).astype(int)
        # define our function f(t)
        f = amp*gpath*numpy.exp(1j*k*(dx*thx[ti]+dy*thy[ti])+1j*ph) + ct1 + 1j*ct2
        f = numpy.repeat(f,2)
        f = f[::2]
        f = f.astype(numpy.complex64)
        #print("f", f)
        return f
 
    def residual1(params, t, f):
        amp, ph, ct1, ct2 = params
        r = model1(t, amp, ph, ct1, ct2) - f
        #print("r", r)
        f1d = numpy.zeros(f.size*2, dtype=numpy.float64)
        f1d[0:f1d.size:2] = r.real
        f1d[1:f1d.size:2] = r.imag
        return f1d
    
    # Guess initial parameters
    # Guess of pi for phase restricts phase to [0,2*pi]
    pguess = numpy.array([aguess, numpy.pi, ct1guess, ct2guess])
    #print("aguess pguess", pguess, aguess)
    params, cov = leastsq(residual1, pguess, args=(t,f))
    amp, ph, ct1, ct2 = params
    #print("amp*gpath", amp, gpath)
    fitted = amp*gpath*numpy.exp(1j*k*(dx*thx+dy*thy)+1j*(ph)) + ct1 + 1j*ct2
    #print ct1
    return amp, ph, ct1, ct2, fitted

def fit2(t, f, dx, dy, gpath, thx, thy, aguess, ct1guess, ct2guess):
    """
    Fits the cross spectral data of an antenna pair to the model.
    Fitting parameters: amplitude, phase, complex offset (antenna crosstalk terms ct1 & ct2),
    errors in the antenna separations (called edx and edy)
    """
    def model2(t, amp, ph, ct1, ct2, edx, edy):
        # array index variable
        ti = numpy.linspace(0, size-1, num=size).astype(int)
        # define our function f(t)
        f = amp*gpath*numpy.exp(1j*k*((dx+edx)*thx[ti]+(dy+edy)*thy[ti])+1j*ph) + ct1 + 1j*ct2
        f = numpy.repeat(f,2)
        f = f[::2]
        f = f.astype(numpy.complex64)
        return f
 
    def residual2(params, t, f):
        amp, ph, ct1, ct2, edx, edy = params
        r = model2(t, amp, ph, ct1, ct2, edx, edy) - f
        f1d = numpy.zeros(f.size*2, dtype=numpy.float64)
        f1d[0:f1d.size:2] = r.real
        f1d[1:f1d.size:2] = r.imag
        return f1d
    
    pguess = numpy.array([aguess, numpy.pi, ct1guess, ct2guess, 0.0, 0.0])
    params, cov = leastsq(residual2, pguess, args=(t,f))
    amp, ph, ct1, ct2, edx, edy = params
    fitted = amp*gpath*numpy.exp(1j*k*((dx+edx)*thx+(dy+edy)*thy)+1j*ph) + ct1 + 1j*ct2
    return amp, ph, ct1, ct2, edx, edy, fitted




#----------------------------------------------
#   MAIN SCRIPT
#----------------------------------------------

# JRO
# main_dir = '/home/david/Documents/DATA-2/Imaging/10_Aug_26/phase-calibration-4'

# MSI
main_dir = '/home/david/Documents/DATA-2/Imaging/10_Aug_26/phase-calibration-5'

# Edit path to the data here!
dir_ = '/home/david/Documents/DATA-2/Imaging/10_Aug_26/hydra-pdata-5'
path = dir_ 
# path = '/home/soporte01/Desktop/ian'

# Loop through the data specified by the path
# Choose the appropriate dates and times for your data
startDate = datetime.date(2026,8,10)
endDate = datetime.date(2026,8,10)
startTime = datetime.time(12,0,0)
endTime = datetime.time(12,30,0)

weights_mode = None
#weights_mode = 1



####
arr = numpy.zeros((28,0), dtype=numpy.complex)
zeros = numpy.zeros((28,1), dtype=numpy.complex)
j = 0

# Global variables
c = 299792456. # speed of light
f = 49.92*(10**6) # antenna frequency
wl = c/f # wavelength
k = (2*numpy.pi)/wl # wave number (used in fitting routines)


# Schain reading
spectradataObj = SpectraReader()

spectradataObj.setup(path=path,
            startDate=startDate,
            endDate=endDate,
           startTime=startTime,
           endTime=endTime,
           getByBlock=1,
            walk=True)

start = None

while True:
    try:
        spectradataObj.getData()
    except SchainWarning: break

    if spectradataObj.dataOut.flagNoData or spectradataObj.flagNoMoreFiles: break
    if start is None: start = spectradataObj.dataOut.datatime

    # Add cross spectral data to the array for each unique antenna pair

    arr = numpy.append(arr, zeros, axis=1)
    for i in range(0, 28):
        # Average over doppler bins and range gates
        # arr[i, j] = numpy.mean(spectradataObj.data_cspc[i,:,200:470])
        arr[i, j] = numpy.mean(spectradataObj.dataOut.data_cspc[i, :, :]) # 250:400 #100:900 # 
        # arr[i, j] = numpy.mean(spectradataObj.dataOut.data_cspc[i, :, 50:200]) # 250:400 #100:900 # 
        #print(numpy.shape(spectradataObj.dataOut.data_cspc[i, :, :]))

    j += 1  # increment the counter


# Delete extra array entry generated by the loop above
#arr = numpy.delete(arr, -1, 1)
# The size of the data sets the size of the rest of the vectors used
size = arr[0].size

# Time difference between two consecutive PDATA
#start = spectradataObj.datetimeList[0]
#print start
print(numpy.shape(arr))
print(start)
dt = spectradataObj.dataOut.timeInterval #spectradataObj.datetimeList[1] - spectradataObj.datetimeList[0]
print("dt", dt)
# Find the step size between each block
step = float(dt)
#print step
tot = j*step # total number of seconds elapsed
#print tot
print(tot)
# Find the vectors of directional cosines of Hydra in the antenna plane
thx, thy = hydrapathnew(start, size, step)
print("AA", start, size, step, thx, thy)
# Custom define date time object to find where Hydra will be at a later time
# time = datetime.datetime(2016,07,14,13,8,21)
# thx, thy = hydrapathnew(time, 300, 30.)

# Some constants for the antenna pattern
phase = numpy.zeros((8,8))
ues = numpy.zeros((4,1))
# Number of grid points
N = 2000
mask = numpy.zeros((8,8))
# Find antenna pattern for a single module (it's the same for each one)



##############################################################################################
mask[0,0] = 1
gain, cosx, cosy = antenna_pattern_jro(phase, ues, mask, '', 0.0, N, 0)

# Plot Hydra's path over the antenna pattern, just for looks
epsilon = numpy.finfo(float).eps
crange = numpy.array([-40,0])
srange = numpy.array([-1,1])
gain_max = numpy.max(gain[numpy.isfinite(gain)])
Gdiv = gain/gain_max
# Make sure nothing is zero to avoid problems with the logarithm
Gdiv[Gdiv == 0] = epsilon
GaindB = 10*numpy.log10(Gdiv)
Gain_maxdB = 10*numpy.log10(gain_max)
plt.pcolormesh(cosx,cosy,GaindB.T, shading='auto', vmin=crange[0], vmax=crange[1])
plt.axis('scaled')
plt.grid()
plt.xlim(srange)
plt.ylim(srange)
plt.colorbar()
plt.title("Hydra's path starting at {}".format(start))
plt.xlabel(r'$\theta_{x}$')
plt.ylabel(r'$\theta_{y}$')
plt.plot(thx, thy, linewidth=1.0, color='k')
############################################################################################


dir___ = main_dir

if not os.path.exists(dir___):
    os.makedirs(dir___)

plt.savefig(
    dir___ + '/hydra-pass_init.png',
    dpi=300,
    bbox_inches='tight'
)

#plt.show()
#plt.gcf().clear()

# Directional cosines in terms of array index for full antenna pattern
thxi = numpy.around((thx+1.)*0.5*N).astype(int)
thyi = numpy.around((thy+1.)*0.5*N).astype(int)
# Calculate antenna cut
gpath = gain[thxi, thyi]
#gpath = numpy.roll(gpath, -35)
gpathN = gpath/gain_max


#--------------------------------------------
# Grafica del paso de Hydra
#--------------------------------------------

gpath = gain[thxi, thyi]
#gpath = numpy.roll(gpath, -35)

# Tiempo asociado a cada muestra
t = numpy.arange(size) * step

# -------------------------------------------------
# Máximo de ganancia durante el paso de Hydra
# -------------------------------------------------

imax = numpy.argmax(gpath)

# Ganancia máxima alcanzada por Hydra
gain_max_path = gpath[imax]

# Tiempo en el que ocurre el máximo
time_max = t[imax]

# Hora correspondiente al máximo
datetime_max = start + datetime.timedelta(
    seconds=float(time_max)
)

# -------------------------------------------------
# Ganancia normalizada respecto al máximo de Hydra
# -------------------------------------------------

gpathN = gpath / gain_max_path

# -------------------------------------------------
# Convertir a dB
# -------------------------------------------------

gpath_dB = 10 * numpy.log10(gpathN)

# El máximo será exactamente 0 dB
gain_max_dB = 0.0

# Nivel de -3 dB
gain_3db = -3.0

# -------------------------------------------------
# Gráfica
# -------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    t,
    gpath_dB,
    linewidth=2.0,
    label='Antenna gain'
)

# Punto máximo = 0 dB
plt.plot(
    time_max,
    gain_max_dB,
    'o',
    markersize=7,
    label='Maximum (0 dB)'
)

# Línea horizontal de -3 dB
plt.axhline(
    gain_3db,
    linestyle='--',
    linewidth=1.5,
    label='-3 dB'
)

# -------------------------------------------------
# Anotación del máximo
# -------------------------------------------------

plt.annotate(
    '{}\n0 dB'.format(
        datetime_max.strftime('%H:%M:%S')
    ),
    xy=(time_max, gain_max_dB),
    xytext=(10, 15),
    textcoords='offset points',
    arrowprops=dict(arrowstyle='->')
)

# -------------------------------------------------
# Etiquetas
# -------------------------------------------------

plt.xlabel(
    'Seconds after {}'.format(
        start.strftime('%Y-%m-%d %H:%M:%S')
    )
)

plt.ylabel('Relative antenna gain (dB)')

plt.title(
    "Hydra passage through antenna pattern"
)

plt.grid()
plt.legend()
plt.tight_layout()

# -------------------------------------------------
# Guardar figura
# -------------------------------------------------

dir___ = main_dir

if not os.path.exists(dir___):
    os.makedirs(dir___)

plt.savefig(
    dir___ + '/hydra-pass.png',
    dpi=300,
    bbox_inches='tight'
)

#plt.show()
#plt.close()

# plt.plot(gpath)
# plt.show()

# Now loop over every antenna pair and store fit values
# Create vectors to store all of the fitting parameters
fitted = numpy.zeros((28, size), dtype=numpy.complex128)
amp = numpy.zeros(28)
ph = numpy.zeros(28)
ct1 = numpy.zeros(28)
ct2 = numpy.zeros(28)
edx = numpy.zeros(28)
edy = numpy.zeros(28)

# t = numpy.linspace(0.0, tot/(3600), num=size)
t = numpy.linspace(0.0, tot/(1), num=size)
# Keep track of which number pair it's on (total count)
tc = 0
for a1 in range(0, 7):
    for a2 in range(a1+1, 8):
        dx, dy = separation(a1,a2)
        #print(a1,a2, dx, dy)
        f = arr[tc]
        aguess = (numpy.mean(numpy.absolute(arr[tc].real))/numpy.amax(gpath))
        ct1guess = numpy.mean(arr[tc].real)
        ct2guess = numpy.mean(arr[tc].imag)
        # Use the fit2 function if you want to allow uncertainty in antenna separation
        #amp[tc], ph[tc], ct1[tc], ct2[tc], edx[tc], edy[tc], fitted[tc] = fit2(t, f, dx, dy, gpath, thx, thy, aguess, ct1guess, ct2guess)
        # Otherwise, use the fit1 function
        print('{}_{}'.format(a1, a2))
        amp[tc], ph[tc], ct1[tc], ct2[tc], fitted[tc] = fit1(t, f, dx, dy, gpath, thx, thy, aguess, ct1guess, ct2guess)
        #print(amp[tc])
        #print(aguess)
        # Plot just to check it out
        plt.plot(t, f.real, '.') # Experimental point
        plt.plot(t, fitted[tc].real, linewidth=2.0, color='r')  # fitting
        plt.plot(t, gpath*amp[tc] + ct1[tc], t, -gpath*amp[tc] + ct1[tc], linestyle='dashed', linewidth=2.0, color='g') #envelope
        plt.title('Cross-correlation of antennas {} and {}'.format(a1, a2))
        plt.xlabel('Number of seconds after {}'.format(start))

        dir__ = main_dir
        if not os.path.exists(dir__):
            os.makedirs(dir__)


        plt.savefig(dir__+'/csc{}_{}.png'.format(a1, a2))
        #plt.show()
        plt.gcf().clear()
        tc += 1

# Now let's find the best phases by solving a huge overdetermined linear system...
# Note: I've defined the phase ph_ij as ph_j-ph_i
# First, I have to ensure that the phases are in the proper range to work in the linear system
# It's hard to explain but I promise it works!!  
tc = 7
tol = numpy.pi/2
for a1 in range(1,7):
    for a2 in range(a1+1, 8):
        if (((ph[a2-1]-ph[a1-1]) < tol) and ((ph[a2-1]-ph[a1-1]) > -tol)) and (ph[tc] > (2*numpy.pi - tol)):
            ph[tc] = ph[tc] - 2*numpy.pi
        if (ph[a2-1]-ph[a1-1]) <= -tol:
            ph[tc] = ph[tc] - 2*numpy.pi
        tc += 1

# Next we need to construct this crazy big matrix!
# Start with a 7x7 identity on top of a bunch of zeros
M = numpy.zeros((28,7))
M[0:7, :] = numpy.identity(7)
# Now loop through and fill the rest!!
row = 7
for i in range(1,7):
    m = numpy.zeros((7-i, 7))
    m[:, i-1] = -numpy.ones(7-i)
    m[:, i:7] = numpy.identity(7-i)
    M[row:(row+(7-i)), :] = m
    row += (7-i)
print("MATRIX: ", M)

## Least Square Overdeterminated
# phase = ((M_t*M)^(-1))*M_t*ph (least squares solution)
# phase = ((M_t*W*M)^(-1))*M_t*W*ph (least squares solution with weights)
M_t = numpy.asmatrix(numpy.transpose(M))
M = numpy.asmatrix(M)

if weights_mode is None:
    inv = numpy.linalg.inv(M_t * M)
    print("FINAL MATRIX: ", (inv*M_t))
    phase = numpy.dot((inv * M_t), ph)

else:
    from weights import get_weights
    w = get_weights(mode=1, N=M.shape[0])

    W = numpy.diag(w)
    print("Weights applied:", W)

    M_t = numpy.asmatrix(M.T)
    M   = numpy.asmatrix(M)
    W   = numpy.asmatrix(W)

    inv = numpy.linalg.inv(M_t * W * M)
    print("FINAL MATRIX: ", (inv*M_t))
    phase = numpy.dot(inv * M_t * W, ph)


# The results are the least squares phase solutions in the range [0,2*pi]
# It's possible that some phases could be slightly out of range because of discrepancies between the real and measured values
phase = phase % (2*numpy.pi)
#print ph
print("phase_1")
print(phase)
# I used a different definition of phase, so I change it to be ph_i-ph_j instead
phase = 2*numpy.pi - phase
# Now put it in the range of -pi to pi like in the imaging configuration files
phase = ((phase+numpy.pi) % (2*numpy.pi )) - numpy.pi

# Next, let's solve for the errors in the antenna positions
# Start with a 28x8 matrix of zeros and fill it in
Mxy = numpy.zeros((28,8))
row = 0
for i in range(1,8):
    m = numpy.zeros((8-i, 8))
    m[:, i-1] = numpy.ones(8-i)
    m[:, i:8] = -numpy.identity(8-i)
    Mxy[row:(row+(8-i)), :] = m
    row += (8-i)

# Now solve the overdetermined linear system for the error in antenna position
# The position, on the other hand is defined as x_ij = x_j-x_i
Mxy_t = numpy.asmatrix(numpy.transpose(Mxy))
Mxy = numpy.asmatrix(Mxy)
inv = numpy.linalg.inv(Mxy_t*Mxy)
ex = numpy.asarray(numpy.dot((inv*Mxy_t), edx))
ey = numpy.asarray(numpy.dot((inv*Mxy_t), edy))

# x and y coordinates of the antenna modules
x = numpy.array([[127.50, 91.50, 127.50, 19.50, 91.50, -127.50, -55.50, -220.824]])
y = numpy.array([[127.50, 91.50, 91.50, 55.50, -19.50, -127.50, -127.50, -322.294]])
xnew = x + ex
ynew = y + ey
plt.scatter(x, y, c='r', marker='+', s=50)
plt.scatter(xnew, ynew, c='b', marker='+', s=50)
plt.show()
#plt.gcf().clear()

#print ex, ey
#print xnew, ynew
print("phase_2")
print(phase)

# Save in a .txt file

