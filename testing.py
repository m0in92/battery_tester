import pyvisa
from cycling import Cycling
from psu import PSU

dt = 10
V_upper = 3.65 # battery upper terminal voltage
C_rate = 1.5
I_charge = I_dis = C_rate #Discharge and charge currents
I_cut = 0.1
t_wait = 5 #Wait period in between the charge and discharge steps within cycle
V_cut = 2 # battery lower terminal voltage
t_wait_init= 5 #intial wait in seconds
cycles = 1
filename_charge = "20211203_ECM_OCV_charge"
filename_discharge = "20211203_ECM_OCV_discharge"

psu_id = 'USB0::0xF4EC::0x1410::SPD13DCQ4R0571::INSTR'
load_id = 'USB0::0x1AB1::0x0E11::DL3A222600541::INSTR'

siglent = PSU(id = psu_id)
siglent.set_psu_VI(V_upper=V_upper, I_charge=I_charge)
print(type(siglent.measureV()))
siglent.CC_charge(dt = dt, V_upper= V_upper, I_charge= I_charge, return_output= False)
