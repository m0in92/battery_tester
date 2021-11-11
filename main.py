from psu import PSU
import matplotlib.pyplot as plt

#Input parameters
dt = 10
V_upper = 3.65
I_charge = 1.5
I_cut = 0.075
psu_id = 'USB0::0xF4EC::0x1410::SPD13DCQ4R0571::INSTR'
load_id = 'USB0::0x1AB1::0x0E11::DL3A222600541::INSTR'
#Set PSU
siglent = PSU(id = psu_id,
              dt = dt,
              V_upper = V_upper,
              I_charge = I_charge,
              I_cut = I_cut)

#start cycling
t_list,V_list,I_list,W_list, status_list = siglent.cycle()
plt.plot(t_list, V_list)

