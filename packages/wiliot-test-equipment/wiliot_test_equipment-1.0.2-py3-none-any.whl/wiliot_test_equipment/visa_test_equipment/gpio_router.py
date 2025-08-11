import serial # type: ignore
import time

import serial.threaded # type: ignore
import serial.tools # type: ignore
import serial.tools.list_ports # type: ignore

from wiliot_test_equipment.arduino.gpio_router import defines_dict


class GPIORouter(object):
    def __init__(self, baudrate: int = defines_dict['BAUDRATE'], logger=None, print_flag=False):
        self.serial_con: serial.Serial = None
        self.connect(baudrate)

    def __del__(self):
        if self.serial_con:
            self.serial_con.close()

    def log_and_print(self, msg):
        if self.logger:
            self.logger.info(msg)
        if self.print_flag:
            print(msg)

    def connect(self, baudrate):
        ports_list = serial.tools.list_ports.comports()
        for port in ports_list:
            if 'USB VID:PID=2341:0043' in port.hwid:
                try:
                    self.serial_con = serial.Serial(
                        port.device, baudrate, timeout=0, write_timeout=0)
                except serial.SerialException as e:
                    print(e)
                response = self.query(defines_dict['GET_NAME'])
                if (defines_dict['GPIO_ROUTER_NAME'] in response):
                    self.version = self.query(defines_dict['GET_VERSION'])
                    if self.version != defines_dict['GPIO_ROUTER_VERSION']:
                        raise ValueError(f'expected GPIO_Router version is {self.version}, instead got version {
                            defines_dict["GPIO_ROUTER_VERSION"]}')

                    self.serial_con.flushInput()
                    return
                else:
                    if self.serial_con != None:
                        self.serial_con.close()
        raise ConnectionError('could not find GPIO_Router in com ports')

    def query(self, cmd):
        """Send the input cmd string via COM Socket and return the reply string"""
        if self.serial_con.isOpen():
            pass
        else:
            self.serial_con.open()
            time.sleep(0.1)
        self.serial_con.flushInput()
        time.sleep(0.5)
        try:
            self.serial_con.write(str.encode(cmd))
            time.sleep(0.5)
            data = self.serial_con.readlines()
            if data:
                value = data[0].decode("utf-8")
                # Cut the last character as the device returns a null terminated string
                value = value[:-2]
            else:
                value = ''
        except serial.SerialException as e:
            print(e)
            value = ''
        return value

    def get_gpio_state(self):
        return self.query(defines_dict['GET_GPIO'])

    def set_gpio_state(self, gpio_state):
        is_valid = len(gpio_state) == 4 and set(gpio_state) <= {"0", "1"}
        if not is_valid:
            raise ValueError(f'set_gpio_state bad input {
                             gpio_state},  it should be length 4 and contain only 0 and 1')

        return self.query(defines_dict['SET_GPIO'] + gpio_state)


if __name__ == '__main__':
    gr = GPIORouter()
    print(gr.get_gpio_state())
    print(gr.set_gpio_state('1010'))
    print(gr.get_gpio_state())
