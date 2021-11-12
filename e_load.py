import time
import pyvisa


class E_load:
    """
    The discharging algorithm
    1. Input parameters (t_wait, V_stop, dt, I_dis)
    2. Wait for t_wait while measuring the voltage every dt
    3. Start CC discharging until V_cut, while measuring time, current, voltage
    4. Start CC discharging until I_cut, while measuring time, current, voltage
    5. Wait for t_wait while measuring voltage
    """
    def __init__(self, id):
        self.id = id

    @property
    def load(self):
        rm = pyvisa.ResourceManager()
        return rm.open_resource(self.id)

    def turn_on_load(self):
        self.load.write(':SOURce:INPut:STATe 1')

    def turn_off_load(self):
        self.load.write(':SOURce:INPut:STATe 0')

    def set_CC(self, I_dis):
        self.load.write(':SOURce:FUNCtion CURRent')
        self.load.write(f':SOURce:CURRent:LEVel:IMM {I_dis}')

    def set_CV(self, V_cut):
        self.load.write(':SOURce:FUNCtion VOLTage')
        self.load.write(f':SOURce:VOLTage:LEVel:IMM {V_cut}')

    def measureV(self):
        return float(self.load.query('MEASure:VOLTage?'))

    def measureI(self):
        return float(self.load.query('MEASure:CURRent?'))

    def update_lists(self,
                     t_list, t,
                     V_list, V,
                     I_list, I,
                     status_list, status,
                     cap_charge_list, cap_charge,
                     cap_discharge_list, cap_discharge):
        t_list.append(t)
        V_list.append(V)
        I_list.append(I)
        status_list.append(status)
        cap_charge_list.append(cap_charge)
        cap_discharge_list.append(cap_discharge)

    def cycle(self, t_wait, V_cut, I_cut, I_dis, dt, cap_charge_init):
        t = 0
        t_list, V_list, I_list, status_list = [], [], [], []
        cap_charge_list, cap_discharge_list = [], []
        t_start = time.time()
        cap_discharge = 0
        counter = 0
        # Initial wait
        # -------------------------------------
        while t < t_wait:
            if counter == 0:
                t_last = 0
            else:
                t_last = t
            t = time.time() - t_start
            V = self.measureV()
            I = 0
            cap_charge = cap_charge_init
            cap_discharge += I*(t - t_last)/3600
            status = 'wait_between'
            # Update list
            print(t, V, I, status, cap_charge, cap_discharge)
            self.update_lists(t_list, t,
                              V_list, V,
                              I_list, I,
                              status_list, status,
                              cap_charge_list, cap_charge,
                              cap_discharge_list, cap_discharge)
            # Meaurement break
            time.sleep(dt)

        # CC discharge
        #-----------------------------------------------
        self.set_CC(I_dis)
        self.turn_on_load()
        while V >= V_cut:
            t_last = t
            t = time.time() - t_start
            V = self.measureV()
            I = self.measureI()
            status = 'CC_discharge'
            cap_charge = cap_charge_init
            cap_discharge += I*(t - t_last)/3600
            # Update list
            print(t, V, I, status, cap_charge, cap_discharge)
            self.update_lists(t_list, t,
                              V_list, V,
                              I_list, I,
                              status_list, status,
                              cap_charge_list, cap_charge,
                              cap_discharge_list, cap_discharge)
            #Meauring break
            time.sleep(dt)
        self.turn_off_load()

        # CV Discharge
        #----------------------------------------------------------
        self.set_CV(V_cut)
        self.turn_on_load()

        while I >= I_cut:
            t_last = t
            t = time.time() - t_start
            V = self.measureV()
            I = self.measureI()
            status = 'CV_discharge'
            cap_charge = cap_charge_init
            cap_discharge += I*(t - t_last)/3600
            # Update list
            print(t, V, I, status, cap_charge, cap_discharge)
            self.update_lists(t_list, t,
                              V_list, V,
                              I_list, I,
                              status_list, status,
                              cap_charge_list, cap_charge,
                              cap_discharge_list, cap_discharge)
            #Measuring break
            time.sleep(dt)
        self.turn_off_load()

        #Last waiting period
        t_end = t
        while t < t_wait + t_end:
            t_last = t
            t = time.time() - t_start
            V = self.measureV()
            I = 0
            status = 'wait_end'
            cap_charge = cap_charge_init
            cap_discharge += I*(t - t_last)/3600
            # Update list
            print(t, V, I, cap_charge, cap_discharge)
            # Measuring break
            self.update_lists(t_list, t,
                              V_list, V,
                              I_list, I,
                              status_list, status,
                              cap_charge_list, cap_charge,
                              cap_discharge_list, cap_discharge)
            # Measurement break
            time.sleep(dt)

        return t_list, V_list, I_list, status_list, cap_charge_list, cap_discharge_list