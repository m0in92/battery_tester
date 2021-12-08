from cycling import Cycling


#Input parameters
#--------------------------------------------------------
dt = 30
V_upper = 3.65 # battery upper terminal voltage
C_rate = 1.5
I_charge = I_dis = C_rate/3 #Discharge and charge currents
I_cut = 0.1
t_wait = 2*60*60 #Wait period in between the charge and discharge steps within cycle
V_cut = 2 # battery lower terminal voltage
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
Step 1:
--------------------------------------------------------------
Fully charge the cell
"""
cycle1.charge(return_output=False)

"""
Step 2: Pulse charging
------------------------------------------------------------------
1. Let cell rest for 5 minutes
2. Let the cell discharge at constant currrent for 15 miuntes
3. Let cell rest for 20 minutes
** potential and current are measured at each steps at suitable intervals
"""