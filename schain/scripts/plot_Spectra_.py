import os, sys 

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

controllerObj = Project()
controllerObj.setup(id = '005', name='script05', description="Spectra Plot")

#--------------------------------------    Setup    -----------------------------------------
#Verificar estas variables

#Path donde estan los archivos HDF5 de meteoros
path = '/home/david/Documents/DATA/Imaging'
figpath = '/home/david/Documents/DATA-2/test-2/RTI-SPC'
#Fechas para busqueda de archivos
startDate = '2009/11/4'
endDate = '2009/11/4'
#Horas para busqueda de archivos
startTime = '00:00:00' #'05:30:00'
endTime = '23:59:59' # '06:30:00'

#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            walk=1)
#--------------------------------------------------------------------------------------------------

procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())

op1 = procUnitConfObjSpectraBeam0.addOperation(name='selectChannels', optype='self')
op1.addParameter(name='channelList', value='0,2,5')# , format='intlist')
#RemoveDc
#opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='removeDC')

#Noise Estimation
#opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
#opObj11.addParameter(name='minHei', value='100', format='float')
#opObj11.addParameter(name='maxHei', value='280', format='float')

#SpectraPlot
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='external')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='wintitle', value='Imaging Beam 0', format='str')
opObj11.addParameter(name='zmin', value=-5, format='int')
opObj11.addParameter(name='zmax', value=5, format='int')
opObj11.addParameter(name='save', value=figpath, format='str')

dB_range= ['22', '26']

# RTI
op9 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot')
op9.addParameter(name='id', value='20')
op9.addParameter(name='wintitle', value='RTI')
op9.addParameter(name='xmin', value='18')
op9.addParameter(name='xmax', value='24')
op9.addParameter(name='zmin', value=dB_range[0])
op9.addParameter(name='zmax', value=dB_range[1])
op9.addParameter(name='showprofile', value='1')
op9.addParameter(name='timerange', value=str(24))
op9.addParameter(name='save', value=figpath, format='str')


#--------------------------------------------------------------------------------------------------

controllerObj.start()
