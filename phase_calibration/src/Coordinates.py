'''
@author $Author: dsuarez $
@version $Id: Coordinates.py 16 2012-06-13 06:37:03Z dsuarez $
'''

import numpy
from scipy.optimize import leastsq
from JroUtils import *


def jro2xyz(cosx,cosy,rrange):
	"""
	JRO2XYZ transforms Jicamarca On-Axis coordinates to Geocentric (cartesian)
	coordinates.

	Syntax:
	[x,y,z,uk] = jro2xyz(cosx,cosy,rrange)
	
	Inputs:
		cosx, cosy: Direction cosine coordinates of target point given wrt
					Jicamarca On-Axis frame of reference
		rrange: Distance of target point from center of Jicamarca antenna array [km]
	
	Outputs:
		x, y, z: Geocentric (cartesian) coordinates
		uk: Unit wave propagation vector
	
	Revisions:
		Author: Marco A. Milla
		Mar 22, 2011: This routine needs to be tested
	"""
	
#	Location of JRO in geodetic coordinates (WGS84)
#	jro_lat,jro_lon,jro_h: JRO latitude, longitude, and height
#	ue,un,uv: Unit vectors pointing to the East, North and Zenith of JRO
#	ux,uy,uo: Orthonormal basis vectors of JRO On-Axis frame of reference
	[jro_lat,jro_lon,jro_h,ue,un,uv,ux,uy,uo] = jroCoordinates("IGP-2011")
	
#	Location of JRO in geocentric (cartesian) coordinates wrt Greenwich
	[jro_x,jro_y,jro_z] = llh2xyz(jro_lat,jro_lon,jro_h);
	
#	Unit wave propagation vector for a given [cosx,cosy] direction
	cosz = numpy.sqrt(1-(cosx**2+cosy**2)); 
	
	N = cosx.size
	uk = ux.reshape((3,1))*cosx.reshape((1,N)) + \
		 uy.reshape((3,1))*cosy.reshape((1,N)) + \
		 uo.reshape((3,1))*cosz.reshape((1,N))
		
#	Geocentric (cartesian) coordinates of target point [cosx,cosy,rrange]	
	x = jro_x + uk[0,:]*rrange
	y = jro_y + uk[1,:]*rrange
	z = jro_z + uk[2,:]*rrange
	
#	Reshaping output variables
	sz = numpy.shape(cosx)

	x = numpy.reshape(x,sz)
	y = numpy.reshape(y,sz)
	z = numpy.reshape(z,sz)
	
	if sz[0]==1:
		#sz[0] = 3
		sz = (3,)+sz[1:]
	else:
		sz = (3,)+sz
		
	uk = numpy.reshape(uk,sz)
	
	return [x,y,z,uk]


def llh2xyz(glat,glon,ghei):
#	import earth_models
	"""
	LLH2XYZ: transforms geodetic (WGS84) coordinates [latg,long,heig] of a
	location into geocentric coordinates [x,y,z].

	Inputs:
		glat: Geodetic latitude [deg]
		glon: Geodetic longitude [deg]
		ghei: Geodetic height above local ellipsoid [km]
	
	Outputs:
		x,y,z: Geocentric cartesian coordinates wrt Greenwich [km]
	
	Revisions:
		Author: Marco Milla
		Apr 05, 2008: Done.
	"""
	
#	Equatorial radius and Earth flatness (WGS84)
	[a,fl] = earth_models('wgs84')
	e2 = fl*(2-fl); # Earth Eccentricity (e^2)
	
	lat_rad = numpy.deg2rad(glat)
	lon_rad = numpy.deg2rad(glon)
	
	sinlat = numpy.sin(lat_rad)
	coslat = numpy.cos(lat_rad)
	
#	Radius of curvature in the prime vertical
	n = a/numpy.sqrt(1-e2*sinlat**2)
	
#	Cartesian Geocentric Coordinates wrt Greenwich
	x = numpy.multiply(numpy.multiply((n+ghei),coslat),numpy.cos(lon_rad))
	y = numpy.multiply(numpy.multiply((n+ghei),coslat),numpy.sin(lon_rad))
	z = numpy.multiply((n*(1-e2)+ghei),sinlat)
	
#	return numpy.array((x,y,z))
	return [x,y,z]


def xyz2llh(x,y,z):
	"""
	XYZ2LLH: transforms geocentric coordinates [x,y,z] of a location
	into geodetic (WGS84) coordinates [latg,long,heig].
	
	Inputs:
		x,y,z: Geocentric coordinates wrt Greenwich [km]
	
	Outputs:
		glat: Geodetic latitude [deg]
		glon: Geodetic longitude [deg]
		ghei: Geodetic height above local ellipsoid [km]
	
	Revisions:
		Author: Marco Milla
		Apr 07, 2008: Compare coordinates with other results.
	
	"""

	# Equatorial radius and Earth flatness (WGS84)
	[a,fl] = earth_models('wgs84');

	#b = a*(1-fl); % Polar radius [km]
	e2 = fl*(2-fl); # Earth Eccentricity (e^2)

	# Geodetic longitude
	p = numpy.sqrt(x**2+y**2);
	glon = numpy.atan2(y,x)*180/numpy.pi;

	# Iterating to compute Geodetic latitude
	plat = numpy.atan2(z,p)*180/numpy.pi;

	for [] in range(10):
		sinlat = numpy.sin(numpy.pi*plat/180);
		n = a/numpy.sqrt(1-e2*sinlat**2);
		nh0 = numpy.sqrt(p**2+(z+e2*n*sinlat)**2);
		nh1 = numpy.sqrt((p-e2*n*numpy.cos(numpy.pi*plat/180))**2+z**2);
		glat = numpy.atan2(z*nh0,p*nh1)*180/numpy.pi;
#		if abs(glat-plat) < numpy.finfo(float).eps(glat):
		if abs(glat-plat) < numpy.finfo(float).eps(glat):
			break
		plat = glat;

	# Computing Geodetic height
	sinlat = numpy.sin(numpy.pi*glat/180);
	n = a/numpy.sqrt(1-e2*sinlat**2);
	nh0 = numpy.sqrt(p**2+(z+e2*n*sinlat)**2);
	ghei = nh0 - n;

	return [glat, glon, ghei]


def cart2sph(x,y,z):

	az = numpy.arctan2(y,x)
	el = numpy.arctan2(z,numpy.sqrt(x**2+y**2))
	r = numpy.sqrt(x**2+y**2+z**2)
	
	return [az, el, r]


def jroCoordinates(survey):
	"""
	jroCoordinates provides the latitude, longitude, and altitude of the
	main antenna at the Jicamarca Radio Observatory. The coordinates
	correspond to different surveys taken over the years.

	Inputs:
		survey: Name of the survey of the antenna coordinates.

	Outputs:
		lat, lon, h: Latitude, longitude, and altitude of the main antenna.
		ue, un, uv: Unit vectors pointing to the local east, north, and zenith.
		ux, uy, uz: Unit vectors of the JRO On-Axis frame of reference.

	Revisions:
		Author: Marco Milla
		Mar 22, 2011: First version
	"""
	
	if survey == "Ochs":	# Ochs Manual (1960)
		lat = -(11.0 + 57./60)  # Latitude  [deg]
		lon = -(76.0 + 52./60)  # Longitude [deg]
		h = 0.5					# Local height above reference ellipsoid [km]
		phi = 6 + 1./60
		tilt = 2.6/100
	elif survey == "Kudeki":	# Kudeki GPS (2005)
		lat = -11.947917	# Latitude  [deg]
		lon = -76.872306	# Longitude [deg]
		h = 0.463			# Local height above reference ellipsoid [km]
		phi = 6 + 1./60
		tilt = 2.6/100;
	elif survey == "Google":	# Google Earth
		lat = -(11.0 + 57./60 + 05.47/3600)	# Latitude  [deg]
		lon = -(76.0 + 52./60 + 27.53/3600)	# Longitude [deg]
		h = 0.510							# Local height above reference ellipsoid [km]
		phi = 6 + 1./60
		tilt = 2.6/100
	elif survey == "IGP-2009":  #	IGP GPS 2009
		lat = -11.951472523	 #	(11d 57m 05.30s S) Latitude  [deg]
		lon = -76.874362201	 #	(76d 52m 27.70s W) Longitude [deg]
		h = 0.5366			  #	Local height above reference ellipsoid [km]
		phi = 6 + 1./60
		tilt = 2.6/100
	else:
#		[lat,lon,h,phi,tilt,elat,elon,eh,ephi,etilt] = jroIgpGps2011()
#		[lat,lon,h,phi,tilt] = jroIgpGps2011()
		lat = -11.951481
		lon = -76.874383
		h = 0.533253887
		phi = 6.166710
		tilt = 2.598179/100

	#	JRO East, North, and Vertical directions wrt local Earth ellipsoid (WGS84)
	[ue,un,uv] = uvecll(lat,lon)
		
	deg = 180/numpy.pi # converts from radians to degree
	rad = numpy.pi/180  #		  from degrees to radians
	
	beta = deg * numpy.arctan(tilt)					#	Tilt angle
	alpha = deg*numpy.arctan(1/numpy.cos(rad*beta))+phi   #	Diagonal angle
	
	#	Orthonormal basis vectors after rotation around the zenith direction
	ux1 = (numpy.cos(rad*alpha))*ue - numpy.sin(rad*alpha)*un
	uy1 = numpy.sin(rad*alpha)*ue + numpy.cos(rad*alpha)*un
	uz1 = uv
		
	#	Orthonormal basis vectors of Jicamarca On-Axis frame of reference
	ux = ux1
	uy = rad*(uz1*deg*(numpy.sin(rad*beta)) + uy1*deg*(numpy.cos(rad*beta)))
	uz = rad*(uz1*deg*(numpy.cos(rad*beta)) - uy1*deg*(numpy.sin(rad*beta)))
	
	return [lat,lon,h,ue,un,uv,ux,uy,uz] 


def jroIgpGps2011():
	"""
	JRO_IGP_GPS2011: This function computes the coordinates of the JRO
	antenna based on GPS measurements conducted on January 2011.
	"""
#	GPS measurements, coordinates of the antenna center and corners.
#	The antenna corners were measured 2 m above ground and the center
#	was measured 1 m above ground
	coord = [
			 [ -11.949651218, -76.874182221, (539.10-2)*1E-3 ], 
			 [ -11.953310691, -76.874583710, (531.51-2)*1E-3 ], 
			 [ -11.951679171, -76.872524559, (538.92-2)*1E-3 ], 
			 [ -11.951282503, -76.876240741, (531.55-2)*1E-3 ], 
			 [ -11.951466233, -76.874363005, (534.27-1)*1E-3 ] 
			 ] 
	coord = numpy.array(coord)
	coord = coord.T
	
#	GPS measurements, converting geodetic to geocentric cartesian coordinates
	[x,y,z] = llh2xyz(coord[0,:],coord[1,:],coord[2,:])
	
	xyz = numpy.vstack(numpy.array([x,y,z]))
	xyz = xyz[:]
	
#	Initial Guess (taken from Ochs Manual)
	lat = -(11.0 + 57./60) # Latitude  [deg]
	lon = -(76.0 + 52./60) # Longitude [deg]
	h = 0.5			   # Height above reference ellipsoid [km]
	phi = 6 + 1./60	   # Antenna diagonal angle NE [km]
	tilt = 2.6/100		#Antenna plane tilt

	x0 = numpy.array([lat,lon,h,phi,tilt])

#	Standard deviation of GPS measurements
	sige = 0.05	 #  About 5 cm
	
#	(xf,cov_x) = leastsq(fitGps2011,x0,args=(xyz,sige),col_deriv=1,full_output=1)
	xf,cov_x = leastsq(fitGps2011,x0,args=(xyz,sige),full_output=True)

#	fitted results
	lat = xf[0]	 #	Latitude [deg]
	lon = xf[1]	 #	Longitude [deg]
	h   = xf[2]	 #	Height above reference ellipsoid [km]
	phi = xf[3]	 #	 Antenna diagonal angle NE [deg]
	if (numpy.shape(xf)[0]==5):
		tilt = x0[4]	#	Antenna plane tilt
		
#	return xf, cov_x
	return [lat,lon,h,phi,tilt]

def fitGps2011(x0,xyz,sige):
	"""
	FIT_GPS2011 : This function model the GPS measurements of the JRO antenna coordinates
	"""
	lat = x0[0] # Latitude [deg]
	lon = x0[1] # Longitude [deg]
	h = x0[2]   # Altitude [m]
	phi = x0[3] #Antenna Diagonal Angle NE [deg]
	
#	Antenna Plane Tild
	if (numpy.shape(x0)[0]==5):
		tilt = x0[4]
	else:
		tilt = 2.6/100
		
#	Location of JRO in geocentric (cartesian) coordinates WRF Greenwich
	[xj,yj,zj] = llh2xyz(lat,lon,h)
	jro = numpy.array([xj,yj,zj]).T
	
#	print "[xj,yj,zj]",[xj,yj,zj] 
#	print 
#	print
#	print "jro",jro
	
#	JRO East, North, and vertical directions WRT local Earth Ellipsoid (WGS84)
	[ue,un,uv] = uvecll(lat,lon);
	
	beta = 180/numpy.pi*numpy.arctan(tilt) # Tilt angle
	alpha = 180/numpy.pi*numpy.arctan(1/numpy.cos((numpy.pi/180)*beta))+phi # Diagonal angle
	
#	Orthonormal basis vectors after rotation around the zenith direction
#	ux1 = numpy.cos((numpy.pi/180)*alpha)*ue - numpy.sin((numpy.pi/180)*alpha)*un
#	uy1 = numpy.sin((numpy.pi/180)*alpha)*ue + numpy.cos((numpy.pi/180)*alpha)*un	
#############	alpha y beta ya estan en unidades degrees 

	alpha = numpy.deg2rad(alpha)
	ux1 = numpy.cos(alpha)*ue - numpy.sin(alpha)*un
	uy1 = numpy.sin(alpha)*ue + numpy.cos(alpha)*un
	uz1 = uv;
	
#	Orthonormal basis vectors of Jicamarca On-Axis frame of reference
	ux = ux1
	beta = numpy.deg2rad(beta)
	uy = uz1*numpy.sin(beta) + uy1*numpy.cos(beta)

#	Relative positions of the GPS measured points
#	Dipole posts at each corner (N,S,E,W) and pilar at the center.
	xl = numpy.array([-144, 144, 144,-144,   0])/1E3
	yl = numpy.array([ 144,-144, 144,-144, 2.6])/1E3
	
#	Calculating the error between GPS positions and antenna model
	xyz1 = numpy.zeros((3,5))	
	
	for i in numpy.arange(0,5):
		xyz1[:,i] = jro + xl[i]*ux + yl[i]*uy
	
	e = (xyz1[:]-xyz[:])*(1E3/sige)
	
	#print numpy.size(e)
	
	return e
