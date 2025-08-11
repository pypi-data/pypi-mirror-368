import pandas as pd
import numpy as np
import time

from wiliot_test_equipment import HardwareError
from wiliot_test_equipment.visa_test_equipment.visa_test_equipment import VisaTestEquipment


class SMU(VisaTestEquipment):
    # https://www.keysight.com/il/en/assets/9921-01285/programming-guides/B2900B-BL-Series-Precision-Source-Measure-Unit-SCPI-Command-Reference.pdf
    # https://www.keysight.com/il/en/assets/9921-01284/programming-guides/B2900B-BL-Series-Precision-Source-Measure-Unit-Programming-Guide.pdf?success=true
    def __init__(self, visa_addr, logger=None, print_flag=False):
        self.print_flag = print_flag
        super().__init__(visa_addr=visa_addr, logger=logger, print_flag=print_flag)
        self.smu_type = self.query('*IDN?', 'str')
        print(self.smu_type)
        self.all_data = pd.DataFrame()
        self.time_offset = 0.0
        self.max_buffer_size = 0.90

    def config_volt_source(self, channel, volt_v, current_limit_mA=1, reset=False):

        if reset:
            self.write('*RST')

        self.write(':FORM ASC')
        self.write(':FORM:ELEM:SENS CURR')

        self.write(':SENS%s:FUNC:ON "VOLT","CURR"' % channel)
        self.write(':SENS%s:VOLT:RANG:AUTO ON' % channel)
        self.write(':SENS%s:CURR:RANG:AUTO ON' % channel)

        self.write(':OUTP%s:STAT ON' % channel)

        self.write(':SOUR%s:VOLT:MODE FIX' % channel)
        self.write(':SOUR%s:VOLT %s' % (channel, volt_v))
        self.write(':SENS%s:CURR:PROT %s' % (channel, current_limit_mA / 1000))

        self.write(':OUTP%s:ON:AUTO 1')

        self.write(':SOUR%s:FUNC:MODE VOLT' % channel)

    def update_volt_source(self, channel, volt_v):

        self.write(':SOUR%s:VOLT %s' % (channel, volt_v))

    def config_current_source(self, channel, current_mA=0, volt_limit_mV=1400, reset=False):

        if reset:
            self.write('*RST')

        self.write(':FORM ASC')
        self.write(':FORM:ELEM:SENS VOLT')

        self.write(':SENS%s:FUNC:ON "VOLT","CURR","RES"' % channel)
        self.write(':SENS%s:VOLT:RANG:AUTO ON' % channel)
        self.write(':SENS%s:CURR:RANG:AUTO ON' % channel)

        self.write(':OUTP%s:STAT ON' % channel)

        self.write(':SOUR%s:CURR %s' % (channel, current_mA / 1000))
        self.write(':SENS%s:VOLT:PROT %s' % (channel, volt_limit_mV / 1000))

        self.write(':OUTP%s:ON:AUTO 1')

        self.write(':SOUR%s:FUNC:MODE CURR' % channel)

    def set_func_mode(self, channel, func_mode='VOLTAGE'):
        if func_mode.upper() == 'VOLTAGE':
            self.write(':SOUR%s:FUNC:MODE VOLT' % channel)
        elif func_mode.upper() == 'CURRENT':
            self.write(':SOUR%s:FUNC:MODE CURR' % channel)
        else:
            raise ("SMU: Invalid function mode configuration")

    def set_output_state(self, channel, output_state='OFF'):
        if output_state.upper() == 'ON':
            self.write(':OUTP%s:STAT ON' % channel)
        elif output_state.upper() == 'OFF':
            self.write(':OUTP%s:STAT OFF' % channel)
        else:
            raise HardwareError("SMU: Invalid output state configuration")

    def meas(self, channel, meas, units=1, num_repetitions=1):
        """
        channel: SMU channel number
        meas: 'Current', 'Voltage'
        units: uV,uA:1e-6, mV,mA:1e-3
        num_repetitions: number of measurement queries to perform
        """

        meas_result = []
        for _ in range(num_repetitions):
            if meas == 'Current':
                reply = self.query(':MEAS:CURR? (@%d)' % channel)
            elif meas == 'Voltage':
                reply = self.query(':MEAS:VOLT? (@%d)' % channel)

            # TODO: handle empty reply
            meas_result.append(reply)
            if num_repetitions > 1:
                time.sleep(0.1)

        meas_result = [float(i) / units for i in meas_result]
        if num_repetitions > 1:
            return [
                np.mean(meas_result), np.max(meas_result), np.min(meas_result),
                np.std(meas_result)]

        else:
            return meas_result[0]

    def configure_current_sampling(self, channel=1, volt_v=1.4, current_limit_mA=0.3, delay_us=0, samp_interval_us=20,
                                   num_points=10000, reset=False):
        """
        channel: SMU channel number
        volt_v: source voltage in volts
        current_limit_mA: current limit (compliance) in mA
        delay_us: acquire measurement delay time in micro-sec
        samp_interval_us: sampling interval in micro-sec (min is 20 us, max is 100 ks)
        num_points: number of data points (min is 1, max is 100k)
        """

        if reset:
            self.write('*RST')

        # allowed values
        if samp_interval_us < 20:
            print(">> SMU: sampling interval is too low, sets to 20 us")
        if samp_interval_us > 100e9:
            print(">> SMU: sampling interval is too high, sets to 100 ks")

        if num_points > 30e3:
            print(
                ">> SMU: Warning! number of points could be too high. Recommended max value is 30k")
            if num_points > 100e3:
                print(">> SMU: Number of data points is too high, sets to 100 ks")

        # configurations setting
        self.write(":SOUR%s:FUNC:MODE VOLT" % channel)
        self.write(":SOUR%s:VOLT:TRIG %s" % (channel, volt_v))
        self.write(":SENS%s:FUNC ""CURR""" % channel)
        self.write(":SENS%s:CURR:NPLC 0.1" % channel)
        self.write(":SENS%s:CURR:PROT %s" % (channel, current_limit_mA / 1e3))
        self.write(":TRIG%s:ACQ:DEL %s" % (channel, delay_us / 1e6))
        self.write(":TRIG%s:SOUR TIM" % channel)
        self.write(":TRIG%s:TIM %s" % (channel, samp_interval_us / 1e6))
        self.write(":TRIG%s:COUN %s" % (channel, num_points))

        # turn on output
        self.write(":OUTP%s ON" % channel)

    def configure_voltage_sampling(self, channel=1, current_mA=0, volt_limit_V=1.4, delay_us=0, samp_interval_us=20,
                                   num_points=10000, reset=False):
        """
        channel: SMU channel number
        current_mA: source current in mA
        volt_limit_V: voltage limit (compliance) in volts
        delay_us: acquire measurement delay time in micro-sec
        samp_interval_us: sampling interval in micro-sec (min is 20 us, max is 100 ks)
        num_points: number of data points (min is 1, max is 100k)
        """

        if reset:
            self.write('*RST')

        # allowed values
        if samp_interval_us < 20:
            print(">> SMU: sampling interval is too low, sets to 20 us")
        if samp_interval_us > 100e9:
            print(">> SMU: sampling interval is too high, sets to 100 ks")

        if num_points > 30e3:
            print(
                ">> SMU: Warning! number of points could be too high. Recommended max value is 40k")
            if num_points > 100e3:
                print(">> SMU: Number of data points is too high, sets to 100 ks")

        # configurations setting
        self.configure_param(param=f":SOUR{channel}:FUNC:MODE", value='CURR')
        self.configure_param(
            param=f":SOUR{channel}:CURR:TRIG", value=current_mA / 1e3)

        self.configure_param(param=f":SENS{channel}:FUNC", value="""VOLT""")
        self.configure_param(
            # protection
            param=f":SENS{channel}:VOLT:PROT", value=volt_limit_V)

        self.configure_param(param=f":TRIG{channel}:ACQ:SOUR", value="TIM")
        self.configure_param(
            param=f":TRIG{channel}:ACQ:TIM", value=(samp_interval_us / 1e6))

        # delay time after trigger was set (e.g. for sweep if you want to have time between the change in the current till the measurement)
        self.configure_param(
            param=f":TRIG{channel}:ACQ:DEL", value=(delay_us / 1e6))
        # delay time after trigger was set (e.g. for sweep if you want to have time between the change in the current till the measurement)
        self.configure_param(
            param=f":TRIG{channel}:ACQ:COUN", value=num_points)

        # turn on output
        self.write(":OUTP%s ON" % channel)

    def configure_param(self, param, value=None):
        cmd = param
        cmd += f' {value}' if value is not None else ''
        self.write(cmd)
        rsp = self.query(f'{param}?', reply_type='str')
        if value is not None and str(rsp) != str(value):
            print(
                f'CHECK SMU CONFIGURATION error for param: {param} with value: {value}. current configuration is {rsp}')

    def run(self, channel=1, continuous=False):
        if continuous:
            self.write(f':ARM{channel}:ACQ:COUN 2147483647')
            self.time_offset = 0.0
        self.write(f":INIT{channel}")

    def reset_device(self):
        self.write('*RST')

    def config_data_format(self, channel=1):

        self.configure_param(param=f":FORM:ELEM:SENS", value='VOLT,CURR,TIME')
        self.configure_param(param=f":TRAC{channel}:FEED", value='SENS')

        # init the trace, the trace config cannot be change once the mode is on NEXT
        self.configure_param(param=f":TRAC{channel}:FEED:CONT", value='NEXT')

    def check_data_buffer(self, channel):
        rsp = self.query(f":TRAC{channel}:FREE?", 'str')
        print(f'trace: available, total{rsp}')
        rsp_list = [int(x) for x in rsp.split(',')]
        if (1 - (rsp_list[0] / rsp_list[1])) > self.max_buffer_size:
            # stop data to trace buffer
            print('RESET TRACE BUFFER!!!')
            t_start = time.time()
            self.configure_param(
                param=f":TRAC{channel}:FEED:CONT", value='NEV')
            self.write(f":TRAC{channel}:CLE")
            rsp = self.query(f":TRAC{channel}:FREE?", 'str')
            rsp_list = [int(x) for x in rsp.split(',')]
            if rsp_list[0] != rsp_list[1]:
                raise Exception('could not clean the buffer')

            # init the trace buffer again
            self.configure_param(
                param=f":TRAC{channel}:FEED:CONT", value='NEXT')
            dt = time.time() - t_start
            self.time_offset = self.all_data['time'].iloc[-1] + dt

    def set_max_buffer_size_percentage(self, max_size=0.90):
        self.max_buffer_size = max_size

    def is_data_available(self, channel):
        # TODO once the clear buffer will work need to add here the relevant logic
        return int(self.query(f":TRAC{channel}:POIN:ACT?", reply_type='str')) > len(self.all_data)

    def read_continuous_data(self, channel=1, n_fields=3):
        # :FORM:ELEM:SENS SOUR,CURR,VOLT,RES,TIME,STAT
        new_data = pd.DataFrame()
        if not self.is_data_available(channel=channel):
            return new_data
        rsp = self.query(
            f":TRAC{channel}:DATA? {len(self.all_data)}", reply_type='str')
        all_data = np.array([float(x) for x in rsp.split(",")])

        try:
            n_samples = int(np.floor(float(len(all_data)) / n_fields))
            all_data_to_save = all_data[:(n_samples*n_fields)]
            all_data_to_save = all_data_to_save.reshape(
                (n_samples, n_fields)).transpose()
            voltage_list_float = all_data_to_save[0].tolist()
            current_list_float = all_data_to_save[1].tolist()
            time_list_float = (all_data_to_save[2] + self.time_offset).tolist()
            new_data = pd.DataFrame(
                {'time': time_list_float, 'current': current_list_float, 'voltage': voltage_list_float})
        except Exception as e:
            print(f'could not split data due to: {e}')

        self.all_data = pd.concat([self.all_data, new_data], ignore_index=True)
        self.check_data_buffer(channel=channel)

        return new_data

    def get_all_data(self):
        return self.all_data

    def read_sampling(self, channel=1):
        time_list_str = self.query(
            ":FETC:ARR:TIME? (@%d)" % channel, reply_type='str')
        time_list_float = [float(x) for x in time_list_str.split(",")]
        current_list_str = self.query(
            ":FETC:ARR:CURR? (@%d)" % channel, reply_type='str')
        current_list_float = [float(x)
                              for x in current_list_str.split(",")]
        voltage_list_str = self.query(
            ":FETC:ARR:VOLT? (@%d)" % channel, reply_type='str')
        voltage_list_float = [float(x)
                              for x in voltage_list_str.split(",")]

        return time_list_float, current_list_float, voltage_list_float

    def configure_filter(self, filter_onoff='ON', auto_onoff='ON', tau_or_f_cutoff='tau', tau_sec=5e-6,
                         f_cutoff_Hz=31.831e3, channel=1):
        """
        auto_onoff: enables the automatic filter function. If this function is enabled, the
                    instrument automatically sets the output filter which provides the optimized filter.
        tau_or_f_cutoff: choose to set tau or cutoff frequency - tau = 1 / (2 * pi * f_cutoff)
        tau_sec: time constant in seconds. 5 us to 5 ms.
        f_cutoff_Hz: cutoff frequency in Hz. 31.830 Hz to 31.831 kHz.
        """

        if filter_onoff.upper() == 'ON':
            self.write(":OUTP%s:FILT:STAT ON" % channel)
            if auto_onoff.upper() == 'ON':
                self.write(":OUTP%s:FILT:AUTO ON" % channel)
            elif auto_onoff.upper() == 'OFF':
                self.write(":OUTP%s:FILT:AUTO OFF" % channel)
                if tau_or_f_cutoff.lower() == 'tau':
                    self.write(":OUTP%s:FILT:TCON %s" % (channel, tau_sec))
                elif tau_or_f_cutoff.lower() == 'f_cutoff':
                    self.write(":OUTP%s:FILT:FREQ %s" % (channel, f_cutoff_Hz))
                else:
                    print(">> SMU: Invalid mode, remaining in default setup")
            else:
                print(">> SMU: Invalid mode, remaining in default setup")
        elif filter_onoff.upper() == 'OFF':
            self.write(":OUTP%s:FILT:STAT OFF" % channel)
            self.write(":OUTP%s:FILT:AUTO OFF" % channel)
        else:
            print(">> SMU: Invalid mode, remaining in default setup")

        # print configurations
        if self.query(":OUTP%s:FILT:LPAS:STAT?" % channel) == 1:
            stat_log = 'ON'
        else:
            stat_log = 'OFF'
        if self.query(":OUTP%s:FILT:LPAS:AUTO?" % channel) == 1:
            auto_log = 'ON'
        else:
            auto_log = 'OFF'
        config_log = (">> SMU: Filter cofigurations: \n" +
                      "    >> Filter: " + stat_log + "\n" +
                      "    >> Auto: " + auto_log + "\n" +
                      "    >> tau_sec: " + str(self.query(":OUTP%s:FILT:LPAS:TCON?" % channel)) + "\n" +
                      "    >> f_cutoff_Hz: " + str(self.query(":OUTP%s:FILT:LPAS:FREQ?" % channel)) + "\n")
        print(config_log)

    def configure_voltage_sweep(self, channel=1, staircase_or_pulse='STAIRCASE', voltage_list=None, direction='DOWN',
                                start_voltage_V=1,
                                stop_voltage_V=1.4, current_limit_mA=1, delay_us=0, samp_interval_us=20,
                                num_points=1000, reset=False):

        ######################
        # still in progress
        ######################
        """
        channel: SMU channel number
        current_mA: source current in mA
        volt_limit_V: voltage limit (compliance) in volts
        delay_us: acquire measurement delay time in micro-sec
        samp_interval_us: sampling interval in micro-sec (min is 20 us, max is 100 ks)
        num_points: number of data points (min is 1, max is 100k)
        """

        if reset:
            self.write('*RST')

        # allowed values
        if samp_interval_us < 20:
            print(">> SMU: sampling interval is too low, sets to 20 us")
        if samp_interval_us > 100e9:
            print(">> SMU: sampling interval is too high, sets to 100 ks")

        if num_points > 30e3:
            print(
                ">> SMU: Warning! number of points could be too high. Recommended max value is 40k")
            if num_points > 100e3:
                print(">> SMU: Number of data points is too high, sets to 100 ks")

        # configurations setting
        self.write(":SOUR%s:FUNC:MODE VOLT" % channel)
        if voltage_list is None:
            self.write(":SOUR%s:VOLT:MODE SWE" % channel)
            self.write(":SOUR%s:VOLT:STAR %s" % (channel, start_voltage_V))
            self.write(":SOUR%s:VOLT:STOP %s" % (channel, stop_voltage_V))
            self.write(":SOUR%s:VOLT:POIN %s" % (channel, num_points))

            self.write((":SOUR%s:SWE:DIR " + direction.upper()) % channel)
        else:
            voltage_list_str = np.array2string(np.array(voltage_list), separator=',')[
                1:-1].replace('\n', '')
            self.write(":SOUR%s:VOLT:MODE LIST" % channel)
            self.write((":SOUR%s:LIST:VOLT " + voltage_list_str) % channel)
            num_points = len(voltage_list)

        self.write(":SENS%s:FUNC ""CURR""" % channel)
        self.write(":SENS%s:CURR:NPLC 0.1" % channel)
        self.write(":SENS%s:CURR:PROT %s" % (channel, current_limit_mA / 1e3))

        self.write(":TRIG%s:SOUR AINT" % channel)
        self.write(":TRIG%s:ACQ:DEL %s" % (channel, delay_us / 1e6))
        self.write(":TRIG%s:SOUR TIM" % channel)
        self.write(":TRIG%s:TIM %s" % (channel, samp_interval_us / 1e6))
        self.write(":TRIG%s:COUN %s" % (channel, num_points))

        # turn on output
        self.write(":OUTP%s ON" % channel)

    def configure_current_sweep(self, channel=1, staircase_or_pulse='STAIRCASE', current_list=None, direction='DOWN',
                                start_current_uA=0.1,
                                stop_current_uA=0.2, voltage_limit_V=2.5, delay_us=0, samp_interval_us=20,
                                num_points=1000, reset=False):

        ######################
        # still in progress
        ######################
        """
        channel: SMU channel number
        current_mA: source current in mA
        volt_limit_V: voltage limit (compliance) in volts
        delay_us: acquire measurement delay time in micro-sec
        samp_interval_us: sampling interval in micro-sec (min is 20 us, max is 100 ks)
        num_points: number of data points (min is 1, max is 100k)
        """

        if reset:
            self.write('*RST')

        # allowed values
        if samp_interval_us < 20:
            print(">> SMU: sampling interval is too low, sets to 20 us")
        if samp_interval_us > 100e9:
            print(">> SMU: sampling interval is too high, sets to 100 ks")

        if num_points > 30e3:
            print(
                ">> SMU: Warning! number of points could be too high. Recommended max value is 40k")
            if num_points > 100e3:
                print(">> SMU: Number of data points is too high, sets to 100 ks")

        # configurations setting
        self.write(":SOUR%s:FUNC:MODE CURR" % channel)
        if current_list is None:
            self.write(":SOUR%s:CURR:MODE SWE" % channel)
            self.write(":SOUR%s:CURR:STAR %s" %
                       (channel, start_current_uA / 1e6))
            self.write(":SOUR%s:CURR:STOP %s" %
                       (channel, stop_current_uA / 1e6))
            self.write(":SOUR%s:CURR:POIN %s" % (channel, num_points))

            # self.write((":SOUR%s:SWE:DIR " + direction.upper()) % channel)
        else:
            if isinstance(current_list[2], str):
                current_list_str = np.array2string(np.array(current_list), separator=',')[1:-1].replace("'",
                                                                                                        '').replace(
                    '\n', '')
            else:
                current_list_str = np.array2string(np.array(current_list), separator=',')[
                    1:-1].replace('\n', '')
            self.write(":SOUR%s:CURR:MODE LIST" % channel)
            self.write((":SOUR%s:LIST:CURR " + current_list_str) % channel)
            num_points = len(current_list)

        self.write(":SENS%s:FUNC ""VOLT""" % channel)
        self.write(":SENS%s:VOLT:NPLC 0.1" % channel)
        self.write(":SENS%s:VOLT:PROT %s" % (channel, voltage_limit_V))

        self.write(":TRIG%s:SOUR AINT" % channel)
        self.write(":TRIG%s:ACQ:DEL %s" % (channel, delay_us / 1e6))
        self.write(":TRIG%s:SOUR TIM" % channel)
        self.write(":TRIG%s:TIM %s" % (channel, samp_interval_us / 1e6))
        self.write(":TRIG%s:COUN %s" % (channel, num_points))

        # turn on output
        self.write(":OUTP%s ON" % channel)

    def read_sweep(self, channel=1):
        time_list_str = self.query(
            ":FETC:ARR:TIME? (@%d)" % channel, reply_type='str')
        time_list_float = [float(x) for x in time_list_str.split(",")]
        current_list_str = self.query(
            ":FETC:ARR:CURR? (@%d)" % channel, reply_type='str')
        current_list_float = [float(x)
                              for x in current_list_str.split(",")]
        voltage_list_str = self.query(
            ":FETC:ARR:VOLT? (@%d)" % channel, reply_type='str')
        voltage_list_float = [float(x)
                              for x in voltage_list_str.split(",")]

        return time_list_float, current_list_float, voltage_list_float

    def run_and_read_current_sweep(self, **kwargs):
        self.configure_current_sweep(**kwargs)
        self.run()
        wait_time = kwargs['samp_interval_us'] * kwargs['num_points'] / 1e6
        time.sleep(wait_time + 0.1)
        return self.read_sweep()


if __name__ == '__main__':
    # smu = SMU(visa_addr='TCPIP0::192.168.48.83::inst0::INSTR')
    import pandas as pd
    import time
    from pathlib import Path

    downloads_path = str(Path.home() / "Downloads")
    test_time = 60  # sec
    num_points = 100

    smu = SMU(visa_addr='TCPIP0::192.168.48.88::inst0::INSTR', print_flag=True)
    smu.configure_voltage_sampling(
        reset=True, num_points=num_points, samp_interval_us=1000)
    smu.config_data_format()
    # smu.set_max_buffer_size_percentage(0.5)
    smu.run(continuous=True)
    time_list_all = []
    current_list_all = []
    voltage_list_list_all = []
    start_time = time.time()
    file_path = f"{downloads_path}\\my_test_{str(time.time()).replace('.', '_')}.csv"
    first = True
    while (time.time() - start_time) < test_time:
        try:
            time.sleep(0.100)
            new_data = smu.read_continuous_data()
            if first:
                new_data.to_csv(file_path, index=False)
            else:
                new_data.to_csv(file_path, mode='a', index=False, header=False)
            first = False
        except Exception as e:
            print(f'could not get measurements due to {e}')
            break
    smu.reset_device()
    print('done')
