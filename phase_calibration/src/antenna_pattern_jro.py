

def ndgrid(*args, **kwargs):
	import numpy
	same_dtype = kwargs.get("same_dtype", True)
	V = [numpy.array(v) for v in args] 
	shape = [len(v) for v in args] 
	result = []
	for i, v in enumerate(V):
		zero = numpy.zeros(shape, dtype=v.dtype)
		thisshape = numpy.ones_like(shape)
		thisshape[i] = shape[i]
		result.append(zero + v.reshape(thisshape))
	if same_dtype:
		return numpy.array(result) 
	else:
		return result 



def sign(x):
	from numpy import arctan2
	if x > 0 or (x == 0 and arctan2(x, -1.) > 0.):
		return 1
	else:
		return -1


def diric_deg(x,N):
	import numpy
	y = numpy.sin(x/2*numpy.pi/180)
	yy=y.T.reshape((y.size))
	i=numpy.nonzero(yy)
	j=numpy.where(yy == 0)
	xx=x.T.reshape((x.size))
	xx.shape
	yy.shape
	yy[i]=(numpy.sin(N*xx[i]*numpy.pi/360)) / (N*yy[i])
	yy[j]=numpy.sign(numpy.cos((N+1)*xx[j]*numpy.pi/360))
	yy = yy.reshape([y.shape[0],y.shape[1]])
	return yy.T


def antenna_pattern_jro (phase,ues,mask,*args):
	"""
	ANTENNA_PATTERN_JRO computes the radiation pattern of Jicamarca's antenna
	array composed of 8x8 antenna modules and two orthogonal polarizations.

	Syntax:
		antenna_pattern_jro(phase,ues,mask,pol,phi,N,graph)
		antenna_pattern_jro(phase,ues,mask,pol,phi,cosx,cosy,graph)
	
	Inputs:
		phase: 8x8 array of phase increments added to each antenna module measured
			in cable units (1 unit = 1/4*lambda)
		ues: 4x1 vector of phase increments added to each antenna quarter measured
			in cable units
		mask: 8x8 binary array indicating active modules
		pol: antenna polarization ('DN' or 'UP'), if set computes the radiation
			 pattern considering the orientation of the dipoles
		phi: angle of rotation [deg[ of the system of coordinates on the plane of
			 the antenna array
		N: [Nx,Ny] number of x and y points used to compute the radiation pattern
		cosx, cosy: user-defined direction cosines with respect to x and y
		graph: enables plotting the radiation pattern

	Outputs:
		Gain: normalized gain (radiation pattern) of the antenna array
		cosx, cosy: direction cosines with respect to x and y
		FAnt: antenna factor (Gain = FAnt.*conj(FAnt))
	
	Author:
		Marco A. Milla
	
	Revisions:
		Jan 20, 2008: We still have to test the accuracy of the algorithm and its
		performance. Note that functions [cosd,sind] are much slower than [cos,sin].
		Review the plotting options.
		May 29, 2008: The computation of the pattern should be much faster (review
		the algorithm).
		Aug 05, 2008: According to Ochs (1965), the array of dipoles is at a
		distance of 0.3 lambda from the ground reflector. A more careful revision is
		needed.
	"""
	import numpy
	import matplotlib.pyplot as plt
	from JroUtils import sind, cosd

#	matplotlib.use('GTKAgg')
#	from matplotlib.backends.backend_agg import RendererAgg

#	Checking the number of input variables
#	Checking the number of input variables
	if (len(args) == 4):
		# print "Numero de Parametros = 4\n" ,args
		(pol,phi,N,graph) = args
		setcosxy = 0
	elif (len(args) == 5):
		# print "Numero de Parametros = 5\n" , args
		(pol,phi,cosx,cosy,graph) = args 
		setcosxy = 1 
	else :
		# print "Numero de PARAMETROS INVALIDO"
		1
		
	num_dip = 12
	
#	Antenna Configuration:
#	[ North ] [ East  ]
#	[ West  ] [ South ]
#
#	U's comfiguration:
#	[ WW  NN  EE  SS ]
	
#	Recalculating phase increments including the Ues
	phase = numpy.vstack((  
					   numpy.hstack((phase[0:4,0:4]+ues[1],phase[0:4][:,4:8]+ues[2]))
					   , 
					   numpy.hstack((phase[4:8][:,0:4]+ues[0],phase[4:8][:,4:8]+ues[3]))
					   ))

	
# 	phase[0:4,0:4] = phase[0:4,0:4] + ues[1]
# 	phase[0:4,4:8] = phase[0:4,4:8] + ues[2]
# 	phase[4:8,0:4] = phase[4:8,0:4] + ues[0]
# 	phase[4:8,4:8] = phase[4:8,4:8] + ues[3]

	phase = phase[::-1,:]
	mask = mask[::-1,:]
	
#	Recalculating phase increments including the Ues
	if setcosxy:
		Nx = len(cosx)
		Ny = len(cosy)
	else:
		NN = args[2]
		NN = numpy.array([NN,NN])
		Nx = NN[0]
		Ny = NN[1]
		dcx = 2.0/Nx
		dcy = 2.0/Ny
		cosx = dcx*(numpy.arange(0,Nx)-numpy.floor(Nx/2.))
		cosy = dcy*(numpy.arange(0,Ny)-numpy.floor(Ny/2.))
		
	[Cx0,Cy0] = ndgrid(cosx,cosy)
	Cz2 = 1-(Cx0**2+Cy0**2)
	# CHANGE MADE BY IAN COLLET ON JUNE 17 2016 A.D.
	Cz2 = numpy.absolute(Cz2)
	epsilon = numpy.finfo(float).eps
	Cz2[Cz2<epsilon] = numpy.nan	  #	float('nan')
	Cz = numpy.sqrt(Cz2)
	
#	Antenna axes in the rotated coordinate system
#	Cx = Cx0*numpy.cos(phi*numpy.pi/180)-Cy0*numpy.sin(phi*numpy.pi/180)
#	Cy = Cx0*numpy.sin(phi*numpy.pi/180)+Cy0*numpy.cos(phi*numpy.pi/180)
	Cx = Cx0*cosd(phi)-Cy0*sind(phi)
	Cy = Cx0*sind(phi)+Cy0*cosd(phi)
	
#	Defining the half-wave dipole pattern for DN or UP polarizations
#	Note: The electric field of a half-wave dipole in spherical coordinates
#	is given by:
#	   E_theta = exp(-1i*k*r)*cos(pi/2*cos(theta))/sin(theta)
#	where k is the wavenumber, r is the distance from the center of the dipole,
#	and theta is the angle between the propagation direction and the dipole
#	orientation.
	if pol=='DN':   #	x-polarization
		sinth = numpy.sqrt(1-Cx**2)
		sinth[(sinth<epsilon)] = numpy.nan
		FDip = cosd(90*Cx)/sinth
	elif pol=='UP': #	y-polarization
		sinth = numpy.sqrt(1-Cy**2)
		sinth[(sinth<epsilon)] = numpy.nan
		FDip = cosd(90*Cy)/sinth
	elif pol=='':
		FDip = 1
		
#	Defining the antenna factor due to a PEC placed below the antenna array
#	at a distance d (in lambda units).
#	Note: Using image theory the antenna factor resultant after placing a PEC
#	below a horizontally oriented dipole antenna is given by
#		F_ground = 2i*sin(k*d*cos(theta))
#	where theta is the angle between the propagation direction and the z-axis		
	ground = 1 
	if pol=='DN':
		d = 0.3-0.005
	elif pol=='UP':
		d = 0.3+0.005
	elif pol=='':
		d = 0.3
	if ground:
		FGround = 2j*sind(360*d*Cz)
	else:
		FGround = 1
	
		
#	Calculating radiation pattern including module pattern and gap between quarters
#	If the rotation angle is 0 and the direction cosines were not defined by the
#	user, the radiation pattern is computed using 2D-FFT, otherwise the summation
#	of the contribution of each module is carried out explicitly.		
	gap = 1 
	if (phi==0.0) and not(setcosxy) : ## La negacion de setcosxy es TRUE (~setcosxy=1) 
#		Calculating phase increments (in deg)
#		Note: phaserad = k*phase*lambda/4, where k is the wavenumber, phase is the
#		matrix of phase increments added to each module (measured in lambda/4 units)
		phasedeg = 360.0*phase/4
#		ephase = numpy.cos(phasedeg*numpy.pi/180)+1j*numpy.sin(phasedeg*numpy.pi/180)
		ephase = cosd(phasedeg)+1j*sind(phasedeg)
		
#		Expanding the size of the phase-increment matrix to account for the number
#		of dipoles in each module		
		ephase = ephase * mask 
		ephase_tmp = numpy.zeros([8*num_dip,8*num_dip])+1j*numpy.zeros([8*num_dip,8*num_dip])
		for i in range(0,8):
			for j in range(0,8):
				for l1 in range(0,num_dip):
					for l2 in range(0,num_dip):
						indx = l1+i*num_dip
						indy = l2+j*num_dip				
						ephase_tmp[indx,indy] = ephase[i,j]
		
		ephase = ephase_tmp
		
		
		# Compensating for the gaps between antenna quarters		
		if gap:
			gap_vert = numpy.zeros((8*num_dip,1))
			gap_horz = numpy.zeros((1,8*num_dip+1))
			ephase = numpy.hstack((ephase[:,0:4*num_dip],gap_vert,ephase[:,4*num_dip:]))
			ephase = numpy.vstack((ephase[0:4*num_dip,:], gap_horz , ephase[4*num_dip:,:]))

		# Computing the array factor of the array of modules
		# Note: The array factor of the array of modules is given by
		#   exp(-1i*alpharad).*conj(fftshift(fft2(exp(1i*phaserad),Nx,Ny)))
		# where phaserad is the matrix of phase increments (in radians) and
		# alphara d = k*d*(n-1)/2*(Cx+Cy). In addition, k is the wavenumber, d is
		# the dipole separation, and n the number of dipoles. Above,
		# exp(-1i*alpharad) is applied so that the array factor is evaluated with
		# respect to the center of the whole antenna.
		
		# alpharad = numpy.pi*(8*num_dip-1+gap)/2*(Cx+Cy)
		# Array = (numpy.cos(alpharad)-1j*numpy.sin(alpharad)) * (numpy.conj(numpy.fft.fftshift(numpy.fft.fft2(ephase.T,[Nx,Ny]))))	 
		alphadeg = 180*(8*num_dip)/2*(Cx+Cy)
		FArray = (cosd(alphadeg)-1j*sind(alphadeg)) * (numpy.conj(numpy.fft.fftshift(numpy.fft.fft2(ephase.T,[Nx,Ny]))))
	
	else : 
		
		# Computing the array factor of one antenna module
		# Note: The array factor of a square array of nxn dipoles is given by
		# F_module = (n^2)*(diric(k*d*Cx,n).*diric(k*d*Cy,n))
		# where n is the number of dipoles, k is the wavenumber, and d is the
		# separation between dipoles (lambda/2 in this case). In addition,
		# Cx and Cy are the direction cosines of the array.
		# Above, diric is the Dirichlet function (or discrete sinc) defined as
		#   diric(x,n) = sin(n*x/2)/(n*sin(x/2))

		FModule = (num_dip**2)*((diric_deg(180*Cx,num_dip))* (diric_deg(180*Cy,num_dip)))
		
		# Computing the array factor of the array of modules
		FArray=0+0j
		L = num_dip*numpy.arange(0,8)-(7*num_dip+gap)/2.0  
		L[4:8] = L[4:8]+gap
		for ir in range(0,8):
			for ic in range(0,8):
				if mask[ir,ic] != 0:
					
					# Calculating phase increments (in deg)
					# phasedeg = 180*(Cx*L(ic)+Cy*L(ir)-phase(ir,ic)/2);
					# exy = complex(cosd(phasedeg),sind(phasedeg));
					phaserad = (numpy.pi*L[ic])*Cx + (numpy.pi*L[ir])*Cy - numpy.pi*phase[ir,ic]/2.0
					exy = mask[ir,ic]*(numpy.cos(phaserad)+1j*numpy.sin(phaserad))
					# Computing array factor
					FArray = FArray + exy
					
		# Computing the array factor of the full array					
		FArray = FArray * FModule

	# Computing the antenna factor taking into account the dipole orientation and
	# a reflecting ground.		
	FAnt = FArray * FDip * FGround
	
	FAnt[numpy.isnan(FAnt)] = 0
	
	# Defining the differential solid angle	
	domg = 1./Cz 
	domg[~numpy.isfinite(domg)] = 0
	
	# Computing normalized antenna gain (radiation pattern)	
	# Gain = numpy.multiply(numpy.abs(FAnt),numpy.abs(FAnt))
	Gain = numpy.abs(FAnt)**2
	
	if setcosxy:
		Gain = (4*numpy.pi/(numpy.trapz(cosy,numpy.trapz(cosx,Gain*domg))))*Gain
	else:
		Gain = (4*numpy.pi/((dcx*dcy)*numpy.sum(numpy.sum(Gain*domg))))*Gain 
		
		
#		Plotting the radiation pattern
	if graph:
		crange = numpy.array([-40,0])
		angrange = numpy.array([-5,5])*numpy.pi/180
		Gain_max = numpy.max(Gain[numpy.isfinite(Gain)])
		Gdiv = Gain/Gain_max
		# I added this line so that the code would work...
		Gdiv[Gdiv == 0] = epsilon
		GaindB = 10*numpy.log10(Gdiv)
		Gain_maxdB = 10*numpy.log10(Gain_max)
		title = '1-Way Directivity: %.2f dB' %Gain_maxdB  # title is changed this way

		plt.pcolormesh(cosx,cosy,GaindB.T,shading='flat', vmin=crange[0], vmax=crange[1]) # pcolor
		plt.axis('scaled') # changed from 'equal' to 'scaled'
		plt.grid()
		plt.xlim(angrange)
		plt.ylim(angrange)
		plt.colorbar()
		plt.xlabel(r'$\theta_{x}$')
		plt.ylabel(r'$\theta_{y}$')
		plt.title(title) 
		plt.show()
		
	return Gain, cosx, cosy