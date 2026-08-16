#!/usr/bin/env python
import os, sys, json
from schainpy.controller import Project


desc = "Hydra Phase - Imaging"
controllerObj = Project()
controllerObj.setup(id = '191', name='test01', description=desc)


# DOY = 222
startDate = '2026/08/10'
endDate =  '2026/08/10'
startTime =  '12:00:00'
endTime =  '12:15:00'


# dpath -> rawdata
# JRO
# dpath = '/home/david/Documents/DATA/Imaging/10_Aug_26/hydra/'
# MSI
dpath = '/home/david/Documents/DATA/Imaging/10_Aug_26/hydra/'


# pptah -> processed data
ppath = '/home/david/Documents/DATA-2/Imaging/10_Aug_26/hydra-pdata-5'

plots = ppath
mpath = ppath
delay = 30
walk=1
dB_range= ['15', '40']


velocidad=['-10', '10']
velocidad_cross=['-50', '50']
sw=[0,10]
pwr=[-55,-48]
title='Perpendicular'
exp_code='130'
exp = '150EEJ'
mode_fit = 1


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=dpath,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            delay=delay,
                                            online=0,
                                            getByBlock=0,
                                            #server="tcp://10.10.10.85:5556",
                                            walk=walk)


procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())


opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
opObj11.addParameter(name='minHei', value='50.0', format='float')
opObj11.addParameter(name='maxHei', value='200.0', format='float')


'''
#channels=[0,1,2,3]
channels=[4,5,6,7]
opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value=channels, format='list')'''


#code = [[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1],[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1],[-1,-1,-1,1,-1,-1,1,-1,-1,-1,-1,1,1,1,-1,1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1],[-1,-1,-1,1,-1,-1,1,-1,-1,-1,-1,1,1,1,-1,1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1]]
'''cc32 = [[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1],[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1]]
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=cc32)
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='32', format='int')
opObj11.addParameter(name='osamp', value='2', format='int')'''


opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value=2, format='int')


'''opObj11 = procUnitConfObj0.addOperation(name='ToLilBlock')
opObj11.addParameter(name='nProfilesOut', value='500')'''


procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nProfiles', value='20', format='int') # 2000 by default
procUnitConfObj1.addParameter(name='nFFTPoints', value='20', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
							(1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
							(2,3),(2,4),(2,5),(2,6),(2,7), \
							(3,4),(3,5),(3,6),(3,7), \
							(4,5),(4,6),(4,7), \
							(5,6),(5,7), \
							(6,7)')


#procUnitConfObj1.addParameter(name='pairsList', value=((0,0),(1,1)),format='list')


'''opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='zmin', value=dB_range[0], format='int')
opObj11.addParameter(name='zmax', value=dB_range[1], format='int')
#opObj11.addParameter(name='ymin', value='0', format='float')
#opObj11.addParameter(name='ymax', value='500', format='float')
opObj11.addParameter(name='xaxis', value='velocity', format='str')
opObj11.addParameter(name='showprofile', value=1, format='int')
opObj11.addParameter(name='save', value=plots, format='str')'''


'''
opObj11 = procUnitConfObj1.addOperation(name='removeDC')
opObj11.addParameter(name='mode', value='2', format='int')
'''

opObj11 = procUnitConfObj1.addOperation(name='IntegrationFaradaySpectraNoLags')
opObj11.addParameter(name='n', value='45', format='float')   # 20 for experiment
#opObj11.addParameter(name='n', value='5', format='float')   # 5 for maintenance

# nIncohInt 45 -> 3s
'''opObj11 = procUnitConfObj1.addOperation(name='IncohInt')
opObj11.addParameter(name='n', value='45', format='float')'''


'''op9 = procUnitConfObj1.addOperation(name='RTIPlot')
op9.addParameter(name='id', value='20')
op9.addParameter(name='wintitle', value='RTI')
op9.addParameter(name='xmin', value=12.00)
op9.addParameter(name='xmax', value=13.20)
op9.addParameter(name='zmin', value=dB_range[0])
op9.addParameter(name='zmax', value=dB_range[1])
op9.addParameter(name='showprofile', value='1')
op9.addParameter(name='timerange', value=str(24))
op9.addParameter(name='save', value=plots)'''


opObj11 = procUnitConfObj1.addOperation(name='PhasePlot', optype='other')
opObj11.addParameter(name='id', value='102', format='int')
opObj11.addParameter(name='wintitle', value='Phase RTI', format='str')
opObj11.addParameter(name='phase_cmap', value='jet', format='str')
opObj11.addParameter(name='xmin', value=12.0, format='float')
opObj11.addParameter(name='xmax', value=12.50, format='float')
opObj11.addParameter(name='save', value=plots, format='str')


opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='external')
opObj11.addParameter(name='path', value=ppath)
opObj11.addParameter(name='blocksPerFile', value='20', format='int')


'''opObj11 = procUnitConfObj1.addOperation(name='CoherencePlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='Coherence RTI', format='str')
opObj11.addParameter(name='coherence_cmap', value='jet', format='str')
opObj11.addParameter(name='xmin', value=9.0, format='float')
opObj11.addParameter(name='xmax', value=9.6, format='float')
opObj11.addParameter(name='save', value=plots, format='str')'''


'''
opObj32 = procUnitConfObj1.addOperation(name='PhasePlot', optype='other')
opObj32.addParameter(name='id', value='201', format='int')
opObj32.addParameter(name='wintitle', value='PhaseCalibration', format='str')
opObj32.addParameter(name='save', value='1', format='bool')
opObj32.addParameter(name='xmin', value='0', format='float')
opObj32.addParameter(name='xmax', value='24', format='float')
opObj32.addParameter(name='ymin', value='-180', format='float')
opObj32.addParameter(name='ymax', value='180', format='float')
opObj32.addParameter(name='figpath', value=pathfig, format='str')'''


'''writer = procUnitConfObj1.addOperation(name='HDFWriter')
writer.addParameter(name='path', value=ppath)
writer.addParameter(name='blocksPerFile', value='20', format='int')
writer.addParameter(name='dataList', value='utctime,data_spc,data_cspc,data_dc')'''


'''opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='zmin', value=dB_range[0], format='int')
opObj11.addParameter(name='zmax', value=dB_range[1], format='int')
#opObj11.addParameter(name='ymin', value=altura_1[0], format='float')
#opObj11.addParameter(name='ymax', value=altura_1[1], format='float')
opObj11.addParameter(name='xmin', value=velocidad_cross[0], format='float')
opObj11.addParameter(name='xmax', value=velocidad_cross[1], format='float')
opObj11.addParameter(name='xaxis', value='velocity', format='str')
opObj11.addParameter(name='save', value=plots, format='str')'''


'''
opObj11.addParameter(name='exp_code', value=exp_code, format='int')
opObj11.addParameter(name='server', value='10.10.120.138:4444', format='str')
opObj11.addParameter(name='tag', value= 'jicamarca', format='str')'''


controllerObj.start()
