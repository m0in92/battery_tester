import pyvisa
import time
import pandas as pd
from e_load import E_load


class PSU:
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
    def __init__(self, id, delay = 0.05, init_delay = 0.3):
        self.id = id
        self.delay = delay
        self.init_delay = init_delay

        rm = pyvisa.ResourceManager()
        self.supply = rm.open_resource(self.id)
        self.supply.write_termination = '\n'
        self.supply.read_termination = '\n'

    def set_psu_VI(self, V_upper, I_charge):
        # Set the channel's voltage and current
        time.sleep(0.05)
        self.supply.write(f'VOLTage {V_upper}')
        time.sleep(0.05)
        self.supply.write(f'CURRent {I_charge}')
        time.sleep(0.05)

    def turn_psu_on(self):
        time.sleep(self.delay)
        self.supply.write('OUTP CH1,ON')

    def turn_psu_off(self):
        time.sleep(self.delay)
        self.supply.write('OUTP CH1,OFF')

    def hex_to_bin(self, hex_string):
        return bin(int(hex_string, 16)).zfill(8)

    def CC_or_CV(self, bin_string):
        if int(bin_string[-1]) == 0:
            return 'CV'
        else:
            return 'CC'

    def measureV(self):
        self.supply.write('MEASure:VOLTage?')
        time.sleep(self.delay)
        V = float(self.supply.read())
        time.sleep(self.delay)
        return V

    def measureI(self):
        self.supply.write('MEASure:CURRent?')
        time.sleep(self.delay)
        I = float(self.supply.read())
        time.sleep(self.delay)
        return I

    def measureW(self):
        self.supply.write('MEASure:POWEr?')
        time.sleep(self.delay)
        W = float(self.supply.read())
        time.sleep(self.delay)
        return W

    def readStatus(self):
        self.supply.write('SYSTem:STATus?')
        time.sleep(self.delay)
        status = self.supply.read()
        return status

    def cycle(self, dt, V_upper, I_charge, I_cut):
        # Set the channel's voltage and current
        self.set_psu_VI(V_upper, I_charge)

        # Initialization of measuring parameters
        t_list, V_list, I_list, W_list, status_list = [],[],[],[],[]
        cap_charge_list, cap_discharge_list = [], []

        #Turn the power supply on and start charging
        self.turn_psu_on()
        t_start = time.time()
        time.sleep(self.init_delay)
        I = I_charge
        cap_charge = 0
        counter = 0
        while I >= I_cut:
            #time
            if counter == 0:
                t_last = 0
            else:
                t_last = t
            t = time.time() - t_start
            #V
            #----------------------------------------
            V = self.measureV()
            #I
            #------------------------------------------
            I = self.measureI()
            # W
            #---------------------------------------------
            W = self.measureW()
            #Status
            #------------------------------------------------
            status = self.readStatus()
            status = self.hex_to_bin(status) #convert hexadecimal number to binary
            status = self.CC_or_CV(status) #Determine if CC or CV mode
            status = f'{status}_charge'
            #capacities
            #-------------------------------------------------------
            cap_charge += I * (t - t_last)/3600
            cap_discharge = 0

            #Update list
            print(t, V, I, W, status, cap_charge, cap_discharge)
            t_list.append(t)
            V_list.append(V)
            I_list.append(I)
            W_list.append(W)
            status_list.append(status)
            cap_charge_list.append(cap_charge)
            cap_discharge_list.append(cap_discharge)
            #Wait for the next time increment
            time.sleep(dt - 5*self.delay - self.init_delay)
            counter += 1

        #Turn off the power supply
        self.turn_psu_off()

        return t_list,V_list,I_list,W_list, status_list, cap_charge_list, cap_discharge_list


    def CC_charge(self, dt, V_upper, I_charge, measuring_instr = 'same', return_output = True):
        """
        Instructs the psu to perform the CC_charging step
        :param dt: time increment where the measurements should be taken
        :param V_upper: The battery's upper terminal voltage
        :param I_charge: The battery's charging current
        :param measuring_instr: Determines whether the measuring instrument is the psu or another instrument.
        Acceptable arguments are 'same' or other instrument's id.
        :param return_output: If or not to return the charging cycle information
        :return: pandas DataFrame containing current, voltage, power, status, and capacities
        """

        # Set channel's charging current and upper battery terminal voltage
        #-------------------------------------------------------------------------------
        self.set_psu_VI(V_upper=V_upper, I_charge=I_charge)

        #initialize list containing measuring quantities and an empty pandas DataFrame
        #-------------------------------------------------------------------------------
        if return_output:
            t_list, I_list, V_list, status_list = [],[],[],[]
            cap_charge_list = []
            cap_discharge_list = []

        if measuring_instr != 'same':
            measur_instr = E_load(measuring_instr) # create an instance of the measuring instrument's class

        #turn on the power supply and wait for the initial delay time
        #-------------------------------------------------------------------------------
        self.turn_psu_on() # turn on psu
        time.sleep(self.init_delay) #init delay otherwise there would be some issues reading values from Siglent
        t_start = time.time()  # start timer

        # Start charging until upper terminal voltage criteria is met
        #------------------------------------------------------------------------------
        V = self.measureV() # create a current voltage variable
        cap_charge = 0 # initialize the charge capacity
        counter = 0
        t_prev = 0 # intialize a variable that contains the previous time step's time needed for cap measurements
        while V <= V_upper:
            t = time.time() - t_start  # variable that holds the current time in seconds
            if measuring_instr == 'same':
                V = self.measureV()
            else:
                V = measur_instr.measureV()
            I = self.measureI() # Measure current
            # status
            status = self.readStatus()
            status = self.hex_to_bin(status)  # convert hexadecimal number to binary
            status = self.CC_or_CV(status)  # Determine if CC or CV mode
            status = f'{status}_charge'
            #measure capacity
            cap_charge += (t - t_prev) * I / 3600
            cap_discharge = 0

            if return_output:
                #update lists
                t_list.append(t)
                V_list.append(V)
                I_list.append(I)
                status_list.append(status)
                cap_charge_list.append(cap_charge)
                cap_discharge_list.append(cap_discharge)


            # Wait for the next time increment
            time.sleep(dt - 12 * self.delay)

            #Update relevant variables for next iteration
            t_prev = t  # Update the previous time
            counter += 1  # Update counter

            # Print on the console
            print(t, I, V, status, cap_charge, cap_discharge)

        # Turn off the power supply
        self.turn_psu_off()

        # Create a pandas DataFrame
        if return_output:
            df = pd.DataFrame({
                't': t_list,
                'I': I_list,
                'V': V_list,
                'W': W_list,
                'status': status_list,
                'cap_charge': cap_charge_list,
                'cap_discharge': cap_discharge_list
            })
            return df
