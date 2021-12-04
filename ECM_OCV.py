from cycling import Cycling
import time

#Input parameters
#--------------------------------------------------------
dt = 10
V_upper = 3.4 # battery upper terminal voltage
C_rate = 1.5
I_charge = I_dis = C_rate #Discharge and charge currents
I_cut = 0.1
t_wait = 1 #Wait period in between the charge and discharge steps within cycle
V_cut = 3.3 # battery lower terminal voltage
t_wait_init= 5 #intial wait in seconds
cycles = 1
filename_charge = "20211203_ECM_OCV_charge"
filename_discharge = "20211203_ECM_OCV_discharge"

psu_id = 'USB0::0xF4EC::0x1410::SPD13DCQ4R0571::INSTR'
load_id = 'USB0::0x1AB1::0x0E11::DL3A222600541::INSTR'

cycle1 = Cycling(t_wait_init= t_wait_init,
                 psu_id= psu_id,
                 e_load_id = load_id,
                 cycles = cycles,
                 dt = dt,
                 V_upper = V_upper,
                 I_charge= I_charge,
                 I_cut= I_cut,
                 t_wait= t_wait,
                 V_cut= V_cut,
                 I_dis= I_dis)

"""
Step 1: Discharge step 
##Fully discharge the battery at C/30 after waiting for 2 hours
"""
time.sleep(t_wait)
cycle1.discharge_CC(return_output= False)

"""
Step 2: CC-charging
##Fully charge battery at C/30 after waiting for 2 hours
"""
time.sleep(t_wait)
df = cycle1.charge_CC(measuring_instrument= 'eload',return_output= True)
df.to_csv(f'data/{filename_charge}.csv', index= False)

"""
Step 3: CC-discharging
##Fully discharge battery after waiting for 2 hours
"""
time.sleep(t_wait)
df = cycle1.discharge_CC(return_output= True)
df.to_csv(f'data/{filename_discharge}.csv', index= False)

