from psu import PSU
from e_load import E_load
import time
import numpy as np
import pandas as pd

class Cycling:
    def __init__(self, t_wait_init, psu_id, e_load_id,
                 cycles, dt, V_upper, I_charge, I_cut, t_wait, V_cut, I_dis):
        self.t_wait_init = t_wait_init
        self.psu_id = psu_id
        self.e_load_id = e_load_id
        self.cycles = cycles
        self.dt = dt
        self.V_upper = V_upper
        self.I_charge = I_charge
        self.I_cut = I_cut
        self.t_wait = t_wait
        self.V_cut = V_cut
        self.I_dis = I_dis

    def cycle(self):
        """
        Cycling Steps (CC-CV):
        1. Wait for some time (t_wait_init)
        2. CC and CV charge
        3. Wait for some time (t_wait)
        4. CC-CV discharge
        5. Wait for some time (t_wait)
        6. Repeat steps 2-5 for n cycles
        :return:
        """
        #Define instruments
        siglent = PSU(id= self.psu_id)

        rigol = E_load(self.e_load_id)

        #Step 1
        time.sleep(self.t_wait_init)

        # initialize empty dataframe
        df = pd.DataFrame({
            'cycle_no': [],
            'status': [],
            't [s]': [],
            'V [V]': [],
            'I [A]': [],
            'cap_charge [Ahr]': [],
            'cap_discharge [Ahr]': []
        })
        for cycle in range(1,self.cycles + 1):

            t_start = time.time() # Start_timer
            #Step 2 (CC_CV charging)
            #----------------------------------------------------------------------------
            t_list,V_list,I_list,W_list, status_list, cap_charge_list, cap_discharge_list = siglent.cycle(
                self.dt,
                self.V_upper,
                self.I_charge,
                self.I_cut)
            df_charge = pd.DataFrame({
                'cycle_no': cycle * np.ones(len(t_list)),
                'status': status_list,
                't [s]': t_list,
                'V [V]': V_list,
                'I [A]': I_list,
                'cap_charge [Ahr]': cap_charge_list,
                'cap_discharge [Ahr]': cap_discharge_list
            })

            df = df.append(df_charge, ignore_index= True)
            del df_charge

            time_elapsed = time.time() - t_start  #time elasped since timer was started
            #Step 3,4,5,6
            #---------------------------------------------------------------------------
            t_list, V_list, I_list, status_list, cap_charge_list, cap_discharge_list = rigol.cycle(
                self.t_wait,
                self.V_cut,
                self.I_cut,
                self.I_dis,
                self.dt,
                cap_charge_list[-1])
            df_discharge = pd.DataFrame({
                'cycle_no': cycle * np.ones(len(t_list)),
                'status': status_list,
                't [s]': t_list,
                'V [V]': V_list,
                'I [A]': I_list,
                'cap_charge [Ahr]': cap_charge_list,
                'cap_discharge [Ahr]': cap_discharge_list
            })
            df_discharge['t [s]'] = df_discharge['t [s]'] + time_elapsed #Add charging time to discharge times
            df = df.append(df_discharge, ignore_index= True)
            del df_discharge
        return df

    def discharge(self, return_ouput = True):
        rigol = E_load(self.e_load_id)

        # Step 1
        time.sleep(self.t_wait_init)
        # Step 2 (CC-CV discharge)
        t_list, V_list, I_list = rigol.cycle(self.t_wait,
                                             self.V_cut,
                                             self.I_cut,
                                             self.I_dis,
                                             self.dt)
        df_discharge = pd.DataFrame({
            't [s]': t_list,
            'V [V]': V_list,
            'I [A]': I_list,
            'status': status_list
        })
        if return_ouput:
            return df_discharge

    def charge(self, return_output = True):
        siglent = PSU(self.psu_id)

        t_list, V_list, I_list, W_list, status_list = siglent.cycle(self.dt,
                                                                    self.V_upper,
                                                                    self.I_charge,
                                                                    self.I_cut)
        df_charge = pd.DataFrame({
            't [s]': t_list,
            'V [V]': V_list,
            'I [A]': I_list,
            'status': status_list
        })
        if return_output:
            return df_charge

    def charge_CC(self, measuring_instrument, return_output):
        siglent = PSU(self.psu_id)

        if measuring_instrument == 'eload':
            measuring_instr = self.e_load_id
        else:
            measuring_instr = 'same'

        df = siglent.CC_charge(dt= self.dt,
                               V_upper= self.V_upper,
                               I_charge= self.I_charge,
                               measuring_instr= measuring_instr,
                               return_output = return_output)

        if return_output:
            return df

    def discharge_CC(self, return_output):

        rigol = E_load(self.e_load_id)

        df = rigol.CC_discharge(dt = self.dt,
                                V_lower= self.V_cut,
                                I_dis= self.I_dis,
                                return_output = return_output)

        if return_output:
            return df






