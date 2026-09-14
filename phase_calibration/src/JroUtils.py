import numpy

def sind(x):
	"""
	%SIND   Sine of argument in degrees.
	%   SIND(X) is the sine of the elements of X, expressed in degrees.
	%   For integers n, sind(n*180) is exactly zero, whereas sin(n*pi)
	%   reflects the accuracy of the floating point value of pi.
	%
	%   Class support for input X:
	%	  float: double, single
	%
	%   See also ASIND, SIN.

	%   Copyright 1984-2004 The MathWorks, Inc. 
	%   $Revision: 1.1.6.3 $  $Date: 2004/06/25 18:52:06 $
	"""
	#if ~isreal(x)
	#	error('MATLAB:sind:ComplexInput', 'Argument should be real.');
	#end

	n = numpy.round(x/90);
	x = x - n*90;
	m = numpy.mod(n,4);

	if numpy.isscalar(x):
		if m==0:
			x = numpy.sin(numpy.pi/180*x);
		elif m==1:
			x = numpy.cos(numpy.pi/180*x);
		elif m==2:
			x = -numpy.sin(numpy.pi/180*x);
		elif m==3:
			x = -numpy.cos(numpy.pi/180*x); 
	else:
		x[m==0] = numpy.sin(numpy.pi/180*x[m==0]);
		x[m==1] = numpy.cos(numpy.pi/180*x[m==1]);
		x[m==2] = -numpy.sin(numpy.pi/180*x[m==2]); 
		x[m==3] = -numpy.cos(numpy.pi/180*x[m==3]); 

	return x


def cosd(x):
	"""
	%COSD   Cosine of argument in degrees.
	%   COSD(X) is the cosine of the elements of X, expressed in degrees.
	%   For odd integers n, cosd(n*90) is exactly zero, whereas cos(n*pi/2)
	%   reflects the accuracy of the floating point value for pi.
	%
	%   Class support for input X:
	%	  float: double, single
	%
	%   See also ACOSD, COS.
	
	%   Copyright 1984-2004 The MathWorks, Inc. 
	%   $Revision: 1.1.6.3 $  $Date: 2004/06/25 18:51:50 $
	"""
	# if ~isreal(x)
	#	error('MATLAB:cosd:ComplexInput', 'Argument should be real.');
	#end

	n = numpy.round(x/90);
	x = x - n*90;
	m = numpy.mod(n,4);

	if numpy.isscalar(x):
		if m==0:
			x = numpy.cos(numpy.pi/180*x);
		elif m==1:
			x = -numpy.sin(numpy.pi/180*x);
		elif m==2:
			x = -numpy.cos(numpy.pi/180*x);
		elif m==3:
			x = numpy.sin(numpy.pi/180*x); 
	else:
		x[m==0] = numpy.cos(numpy.pi/180*x[m==0]);
		x[m==1] = -numpy.sin(numpy.pi/180*x[m==1]);
		x[m==2] = -numpy.cos(numpy.pi/180*x[m==2]); 
		x[m==3] = numpy.sin(numpy.pi/180*x[m==3]); 

	return x
