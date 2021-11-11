import time
import pyvisa


"""
The discharging algorithm
1. Input parameters (t_wait, V_stop, dt, I_dis)
2. Wait for t_wait while measuring the voltage every dt
3. Start CC discharging until V_cut, while measuring time, current, voltage
4. Start CC discharging until I_cut, while measuring time, current, voltage 
"""

#Parameters
t_wait = 60
V_cut = 2
I_cut = 0.075
I_dis = 1
dt = 10

rm = pyvisa.ResourceManager()
load = rm.open_resource('USB0::0x1AB1::0x0E11::DL3A222600541::INSTR')

t_list, V_list, I_list = [],[],[]

t_start = time.time()
#Step 2
#-------------------------------------
t = 0
while t < t_wait:
    t = time.time() - t_start
    V = float(load.query('MEASure:VOLTage?'))
    I = 0
    #Update list
    print(t, V, I)
    t_list.append(t)
    V_list.append(V)
    I_list.append(I)
    time.sleep(dt)

#Step 3
#-------------------------------------------
load.write(':SOURce:FUNCtion CURRent')
load.write(f':SOURce:CURRent:LEVel:IMM {I_dis}')
load.write(':SOURce:INPut:STATe 1')
while V >= V_cut:
    t = time.time() - t_start
    V = float(load.query('MEASure:VOLTage?'))
    I = float(load.query('MEASure:CURRent?'))
    #Update list
    print(t, V, I)
    t_list.append(t)
    V_list.append(V)
    I_list.append(I)
    time.sleep(dt)
load.write(':SOURce:INPut:STATe 0')

#Step 4
#------------------------------------------------
load.write(':SOURce:FUNCtion VOLTage')
load.write(f':SOURce:VOLTage:LEVel:IMM {V_cut}')
load.write(':SOURce:INPut:STATe 1')

while I >= I_cut:
    t = time.time() - t_start
    V = float(load.query('MEASure:VOLTage?'))
    I = float(load.query('MEASure:CURRent?'))
    # Update list
    print(t, V, I)
    t_list.append(t)
    V_list.append(V)
    I_list.append(I)
    time.sleep(dt)
load.write(':SOURce:INPut:STATe 0')





# load.write(':SOUR:BATT:LEV:IMM 1A')
# load.write(':SOURCE:BATT:RANG 4A')
# load.write(':SOUR:BATT:VST 2')
# load.write('SOURCE:BATT:VEN 1')
#
# t_start = time.time()
# load.write('SOUR:INPut:STATe 0')
# time.sleep(10)
# print(time.time()-t_start, load.query('MEASure:VOLTage?'), load.query('MEASure:CURRent?'))