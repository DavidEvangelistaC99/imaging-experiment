#!/usr/bin/env python
import os, sys, json

from schainpy.controller import Project

desc = "Imaging Experiment"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

startDate = '2026/08/11'
endDate =  '2026/08/11'
startTime =  '15:00:00' # 10:00:00
endTime =  '21:00:00'   # 17:20:00
#dpath = '/mnt/150kM_img/150kM/'
# dpath = '/mnt/minotauro/2025_09/150kM-Perpendicular/main_radar/rawdata'
dpath = '/mnt/compartido4/imaging'

# plots = '/mnt/data10tb/christianP_proc/150km_Imaging/Sep23_9s_150m_cleanedall'
plots = '/home/david/Documents/DATA-2/Imaging/10_Aug_26/pdata'

ppath = plots
#plots = '/mnt/data10tb/150kM/offline/img/plots/'
#mpath = '/mnt/data10tb/150kM/main/hdf5/'
online = 0
delay = 30
walk=1
dB_range= ['3', '15']
dB_range= ['33', '53']
dB_range= ['0', '60'] # 20,30
#dB_range= ['17', '27']
dB=['-20','-10']
tiempo=['7', '18']
tiempo=['0', '24']
altura_1=['1350', '1450']
altura_1=['0', '200.0']
altura_2=['125.0', '185.0']
velocidad=['-50', '50']
sw=[0,10]
pwr=[-55,-48]
title='Perpendicular'
exp_code='216'

exp = '150EEJ'
mode_fit = 1

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=dpath,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            delay=delay,
                                            online=online,
                                            getByBlock=0,
                                            #server="tcp://10.10.10.85:5556",
                                            walk=walk)

######################## MP #############################################
procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())


opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
opObj11.addParameter(name='minHei', value='65.0', format='float')
opObj11.addParameter(name='maxHei', value='200.0', format='float')

# opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
# opObj11.addParameter(name='minHei', value='.0', format='float') #120.0
# opObj11.addParameter(name='maxHei', value='200.0', format='float') #200.0

'''
channels=[0,1]
#channels=[4,5,6,7]
opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value=channels, format='list')
'''
#cc32 = [[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1],[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1]]
#cc64 = [[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1,1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1],[1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1,-1,-1,-1,1,-1,-1,1,-1,-1,-1,-1,1,1,1,-1,1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1]] #CC64 A,B
'''cc64=[[1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1], 
      [1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1],  
      [-1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1], 
      [-1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1], ]  # A, B, -A, -B
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=cc64)
opObj11.addParameter(name='nCode', value='4', format='int')
opObj11.addParameter(name='nBaud', value='64', format='int')'''
#opObj11.addParameter(name='osamp', value='2', format='int')

#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='minHei', value='130.0', format='float') #130
#opObj11.addParameter(name='maxHei', value='170.0', format='float') # 170 

#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='minHei', value='65.0', format='float')
#opObj11.addParameter(name='maxHei', value='200.0', format='float')

#opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
#opObj11.addParameter(name='window', value='1') # 2 for march 2025

# 2000 profiles for 2025 experiment

# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value=4, format='int') # 500 profiles


# opObj11 = procUnitConfObj0.addOperation(name='ToLilBlock')
# opObj11.addParameter(name='nProfilesOut', value='20') # 20 profiles in 25 intervals

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nProfiles', value='20', format='int')
procUnitConfObj1.addParameter(name='nFFTPoints', value='20', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
							(1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
							(2,3),(2,4),(2,5),(2,6),(2,7), \
							(3,4),(3,5),(3,6),(3,7), \
							(4,5),(4,6),(4,7), \
							(5,6),(5,7), \
							(6,7)')
#procUnitConfObj1.addParameter(name='pairsList', value=((0,0),(1,1)),format='list')

'''
opObj11 = procUnitConfObj1.addOperation(name='removeDC')
opObj11.addParameter(name='mode', value='2', format='int')
opObj11 = procUnitConfObj1.addOperation(name='removeInterference')
'''
#opObj11 = procUnitConfObj1.addOperation(name='IncohInt') # (n*ToLilIntervals) 10 * 25

opObj11 = procUnitConfObj1.addOperation(name='IncohInt')
opObj11.addParameter(name='n', value='45', format='float')

'''opObj11 = procUnitConfObj1.addOperation(name='IntegrationFaradaySpectraNoLags')
opObj11.addParameter(name='n', value='75', format='float')   # 20 for experiment
#opObj11.addParameter(name='n', value='5', format='float')   # 5 for maintenance'''

'''opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='zmin', value=dB_range[0], format='int')
opObj11.addParameter(name='zmax', value=dB_range[1], format='int')
#opObj11.addParameter(name='ymin', value=altura_1[0], format='float')
#opObj11.addParameter(name='ymax', value=altura_1[1], format='float')
#opObj11.addParameter(name='xmin', value=velocidad[0], format='float')
#opObj11.addParameter(name='xmax', value=velocidad[1], format='float')
opObj11.addParameter(name='xaxis', value='velocity', format='str')
opObj11.addParameter(name='showprofile', value=1, format='int')
opObj11.addParameter(name='save', value=plots, format='str')'''



opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='external')
opObj11.addParameter(name='path', value=ppath)
opObj11.addParameter(name='blocksPerFile', value='120', format='int')


'''
writer = procUnitConfObj1.addOperation(name='HDFWriter')
writer.addParameter(name='path', value=ppath)
writer.addParameter(name='blocksPerFile', value='15', format='int')
writer.addParameter(name='dataList', value='utctime,data_spc,data_cspc,data_dc', format='int')
'''
'''
opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='zmin', value=dB_range[0], format='int')
opObj11.addParameter(name='zmax', value=dB_range[1], format='int')
#opObj11.addParameter(name='ymin', value=altura_1[0], format='float')
#opObj11.addParameter(name='ymax', value=altura_1[1], format='float')
opObj11.addParameter(name='xmin', value=velocidad[0], format='float')
opObj11.addParameter(name='xmax', value=velocidad[1], format='float')
opObj11.addParameter(name='xaxis', value='velocity', format='str')
opObj11.addParameter(name='showprofile', value=1, format='int')
opObj11.addParameter(name='save', value=plots, format='str')
'''
'''
opObj11.addParameter(name='exp_code', value=exp_code, format='int')
opObj11.addParameter(name='server', value='10.10.120.138:4444', format='str')
opObj11.addParameter(name='tag', value= 'jicamarca', format='str')
'''
'''
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='xmin', value=tiempo[0], format='float')
opObj11.addParameter(name='xmax', value=tiempo[1], format='float')
#opObj11.addParameter(name='ymin', value=altura_1[0], format='float')
#opObj11.addParameter(name='ymax', value=altura_1[1], format='float')
opObj11.addParameter(name='zmin', value=dB_range[0], format='int')
opObj11.addParameter(name='zmax', value=dB_range[1], format='int')
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='save', value=plots, format='str')
'''
'''
opObj11.addParameter(name='exp_code', value=exp_code, format='int')
opObj11.addParameter(name='server', value='10.10.120.138:4444', format='str')
opObj11.addParameter(name='tag', value= 'jicamarca', format='str')
'''
'''
opObj11 = procUnitConfObj1.addOperation(name='NoisePlot')
opObj11.addParameter(name='wintitle', value=title, format='str')
opObj11.addParameter(name='xmin', value=tiempo[0], format='float')
opObj11.addParameter(name='xmax', value=tiempo[1], format='float')
opObj11.addParameter(name='ymin', value=dB_range[0], format='int')
opObj11.addParameter(name='ymax', value=dB_range[1], format='int')
opObj11.addParameter(name='save', value=plots, format='str')


opObj11.addParameter(name='exp_code', value=exp_code, format='int')
opObj11.addParameter(name='server', value='10.10.120.138:4444', format='str')
opObj11.addParameter(name='tag', value= 'jicamarca', format='str')
'''

controllerObj.start()
