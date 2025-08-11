import pyvisa as visa
import time


class VisaTestEquipment(object):
    def __init__(self, visa_addr, read_termination=None, baud_rate=None, logger=None, print_flag=False):
        self.print_flag = print_flag
        self.logger = logger
        rm = visa.ResourceManager()
        if read_termination == '\r':
            self._inst = rm.open_resource(visa_addr, read_termination='\r')
        elif read_termination == '\n':
            self._inst = rm.open_resource(visa_addr, read_termination='\n')
        else:
            self._inst = rm.open_resource(visa_addr)
        if baud_rate != None:
            self._inst.baud_rate = 115200

    def __del__(self):
        try:
            self._inst.close()
        except Exception as e:
            print("make sure everything is turned on")

    def log_and_print(self, msg):
        if self.logger:
            self.logger.info(msg)
        if self.print_flag:
            print(msg)

    def write(self, cmd):
        self.log_and_print(f"write, cmd = {cmd}")
        try:
            self._inst.write(cmd)
            time.sleep(0.1)
        except:
            time.sleep(1)
            self._inst.write(cmd)
            time.sleep(0.1)

    def read(self, cmd):
        self.log_and_print(f"read, cmd = {cmd}")
        try:
            reply = self._inst.read(cmd)
        except:
            time.sleep(1)
            reply = self._inst.read(cmd)
        return reply.strip('\n')

    def query(self, cmd, reply_type='float'):
        self.log_and_print(f"query, reply_type = {reply_type}, cmd = {cmd}")
        try:
            reply = self._inst.query(cmd)
        except:
            time.sleep(1)
            reply = self._inst.query(cmd)
        reply = reply.strip('\n')
        if reply_type == 'float':
            reply = float(reply)
        elif reply_type == 'str':
            reply = reply
        else:
            print('>>Error: type not support for query')
        return reply

    def query_ieee_block(self, cmd, verbose=False):
        if verbose:
            print("Qys = '%s'" % cmd)
        try:
            reply = self._inst.query_binary_values("%s" % cmd, datatype='s')
        except:
            time.sleep(1)
            reply = self._inst.query_binary_values("%s" % cmd, datatype='s')
        return reply[0]

    def timeout(self, time):
        self._inst.timeout = time
        time.sleep(0.1)

    def wait(self):
        self._inst.timeout = 25000000
        self.query('*OPC?')
        self._inst.timeout = 2000
        time.sleep(0.1)

    def clear(self):
        self._inst.clear()

    def flush(self):
        self._inst.flush()
