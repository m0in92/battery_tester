import pyvisa
import time

"""
------------------------------
Class for the power supply for CC_CV charging.
------------------------------
Steps:
1. Input V_upper, charg_curr, I_cut, dt
2. Open pyvisa's resource manager and set the termination values
2. Set the channel's voltage and current values
3. Initialize measured time, current, voltage list
3. Charge and record time, current, voltage values at regular intervals (dt)
    * Use of while loop which terminates when the current reaches cut-off current (I_cut)
    * Append the time, current, and voltage lists
------------------------------
Note:
The name of the Aglient SPD power supply is 'USB0::0xF4EC::0x1410::SPD13DCQ4R0571::INSTR'.
The above can be found by using the following command:
rm = pyvisa.ResourceManager()
print(rm.list_resources())
"""

#Input parameters
dt = 10
V_upper = 3.65
I_charge = 1.5
I_cut = 0.075

#Open Resource and change the command terminations
rm = pyvisa.ResourceManager()
supply = rm.open_resource('USB0::0xF4EC::0x1410::SPD13DCQ4R0571::INSTR')
supply.write_termination='\n'
supply.read_termination='\n'

#Set the channel's voltage and current
time.sleep(0.05)
supply.write(f'VOLTage {V_upper}')
time.sleep(0.05)
supply.write(f'CURRent {I_charge}')
time.sleep(0.05)

# Initialization of measuring parameters
t_list, V_list, I_list, W_list, status_list = [],[],[],[],[]

#Turn the power supply on
t_delay = 0.05
t_init_delay = 0.2
supply.write('OUTP CH1,ON')
t_start = time.time()
time.sleep(t_init_delay)
I = I_charge
while I >= I_cut:
    #time
    t = time.time() - t_start
    #V
    supply.write('MEASure:VOLTage?')
    time.sleep(t_delay)
    V = float(supply.read())
    time.sleep(t_delay)
    #I
    supply.write('MEASure:CURRent?')
    time.sleep(t_delay)
    I = float(supply.read())
    # I
    supply.write('MEASure:POWEr?')
    time.sleep(t_delay)
    W = float(supply.read())
    #Status
    supply.write('SYSTem:STATus?')
    time.sleep(t_delay)
    status = supply.read()
    #convert hexadecimal number to binary
    status = bin(int(status, 16)).zfill(8)
    #Determine if CC or CV mode
    if int(status[-1]) == 0:
        status = 'CV'
    else:
        status = 'CC'
    #Update list
    print(t, V, I, W, status)
    t_list.append(t)
    V_list.append(V)
    I_list.append(I)
    W_list.append(W)
    status_list.append(status)
    #Wait for the next time increment
    time.sleep(dt - 5*t_delay - t_init_delay)

#Turn off the power supply
time.sleep(0.04)
supply.write('OUTP CH1,OFF')



# #Let it run for some time
# time.sleep(3)
#
# #Query current and voltage values
# supply.write('MEASure:VOLTage?')
# time.sleep(0.1)
# volt_value = supply.read()
# supply.write('MEASure:CURRent?')
# time.sleep(0.1)
# curr_value = supply.read()
#
# #Set the voltage
# time.sleep(3)

# #Turn off the power supply
# time.sleep(0.04)
# supply.write('OUTP CH1,OFF')










# time.sleep(2)
# supply.write('OUTP CH1,OFF')
# time.sleep(2)
# supply.write('*IDN?')
# time.sleep(1)
# qStr = supply.read()
# print(str(qStr))
# supply.close()


# #Setup PSU
# supply.query('*IDN?')