import pyvisa
import time



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
    def __init__(self, id, dt, V_upper, I_charge, I_cut, delay = 0.05, init_delay = 0.3):
        self.id = id
        self.dt = dt
        self.V_upper = V_upper
        self.I_charge = I_charge
        self.I_cut = I_cut
        self.delay = delay
        self.init_delay = init_delay

        rm = pyvisa.ResourceManager()
        self.supply = rm.open_resource(self.id)
        self.supply.write_termination = '\n'
        self.supply.read_termination = '\n'

    def set_psu_VI(self):
        # Set the channel's voltage and current
        time.sleep(0.05)
        self.supply.write(f'VOLTage {self.V_upper}')
        time.sleep(0.05)
        self.supply.write(f'CURRent {self.I_charge}')
        time.sleep(0.05)

    def turn_psu_on(self, delay = 0.04):
        time.sleep(delay)
        self.supply.write('OUTP CH1,ON')

    def turn_psu_off(self, delay = 0.04):
        time.sleep(delay)
        self.supply.write('OUTP CH1,OFF')

    def hex_to_bin(self, hex_string):
        return bin(int(hex_string, 16)).zfill(8)

    def CC_or_CV(self, bin_string):
        if int(bin_string[-1]) == 0:
            return 'CV'
        else:
            return 'CC'

    def cycle(self):
        # Set the channel's voltage and current
        self.set_psu_VI()

        # Initialization of measuring parameters
        t_list, V_list, I_list, W_list, status_list = [],[],[],[],[]

        #Turn the power supply on and start charging
        self.turn_psu_on()
        t_start = time.time()
        time.sleep(self.init_delay)
        I = self.I_charge
        while I >= self.I_cut:
            #time
            t = time.time() - t_start
            #V
            self.supply.write('MEASure:VOLTage?')
            time.sleep(self.delay)
            V = float(self.supply.read())
            time.sleep(self.delay)
            #I
            self.supply.write('MEASure:CURRent?')
            time.sleep(self.delay)
            I = float(self.supply.read())
            time.sleep(self.delay)
            # I
            self.supply.write('MEASure:POWEr?')
            time.sleep(self.delay)
            W = float(self.supply.read())
            time.sleep(self.delay)
            #Status
            self.supply.write('SYSTem:STATus?')
            time.sleep(self.delay)
            status = self.supply.read()
            status = self.hex_to_bin(status) #convert hexadecimal number to binary
            status = self.CC_or_CV(status) #Determine if CC or CV mode

            #Update list
            print(t, V, I, W, status)
            t_list.append(t)
            V_list.append(V)
            I_list.append(I)
            W_list.append(W)
            status_list.append(status)
            #Wait for the next time increment
            time.sleep(self.dt - 5*self.delay - self.init_delay)

        #Turn off the power supply
        self.turn_psu_off()

        return t_list,V_list,I_list,W_list, status_list