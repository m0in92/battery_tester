from psu import PSU
from e_load import E_load
import matplotlib.pyplot as plt
import pandas as pd
from cycling import Cycling


#Input parameters
#--------------------------------------------------------
dt = 10
V_upper = 3.65
I_charge = 1.5
I_cut = 0.075
t_wait = 5
V_cut = 2
I_dis = 2
t_wait_init= 5
cycles = 1

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
df = cycle1.cycle()
df.to_csv('data/test_discharge.csv', index = False)