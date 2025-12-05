import serial
import serial.tools.list_ports
import time

class PortSerial:
    """Class to facilitate the serial port object for Gentec-EO devices"""

    def __init__(self, comPort=""):
        """ Ask to select a com port if none is specified
            _comPort: the selected port name Ex.: COM6
        """
        self.reply = ""
        self.custom_delay = 0.02
        self.comPort = comPort
        self.serialPort = serial.Serial()
        self.verbose = True  # flag
        self.port_select = True

        if self.comPort != "":
            self.port_open(comPort)
        else:
            # if port select is true ask for port selection
            if self.port_select:
                self.quit = PortSerial.port_select(self)*-1+1

    def port_list(self):
        """ Display available port."""
        ports = list(serial.tools.list_ports.comports())
        if len(ports) == 0:
            print("None. Check your connection.")
            return 0
        for p in ports:
            print(p)

    def port_select(self):
        """ Display all available ports on the computer and ask the port to connect to """
        self.comPort = ""  # reset the comPort
        if self.serialPort.is_open:
            self.serialPort.close()  # close the port

        print("Port(s) available:\r\n")
        if self.port_list() == 0:
            return 0

        while not self.serialPort.is_open:
            promptPort = input("\r\nPlease enter a COM port (ex.: COM3). Enter Q to quit:")
            if promptPort:
                if promptPort == "Q":
                    return 0
                self.comPort = promptPort.upper()
                self.port_open()
        return 1

    def is_open(self):
        """ Indicate if the port is open """
        return self.serialPort.is_open

    def port_close(self):
        """ Close the selected port """
        self.serialPort.close()

    def port_open(self, _comport=""):
        """ Open the selected port
            _comport: the selected port name
        """
        if _comport != "":
            self.comPort = _comport

        if not self.serialPort.is_open:
            try:
                self.serialPort = serial.Serial(port=self.comPort,
                                                baudrate=115200,
                                                timeout=2)
            except serial.serialutil.PortNotOpenError:
                print(f"Unable to open port {self.comPort}")
            except serial.serialutil.SerialException:
                print(f"Unable to open port {self.comPort}")
                self.port_select

    def send_command(self, command, arg=""):
        """
        Send a command and argument to the selected port:
            : command: The command sent to the device
            : arg:     The argument of that command
        """
        self.reply = ""
        for c in command:
            self.serialPort.write(c.encode('ascii'))
            time.sleep(self.custom_delay)

        for c in arg:
            self.serialPort.write(c.encode('ascii'))
            time.sleep(self.custom_delay)

        if self.verbose:
            if arg:
                print(f"< {command}[{arg}]")
            else:
                print(f"< {command}")

    def read_line(self):
        """ Read one line from selected port"""
        self.reply = self.serialPort.readline().decode("ascii")
        if self.verbose:
            print(f"> {self.reply}")

    def read_lines(self, eot):
        """ Read line until eot "end of transmission" is reached
            eot: end of transmission to search for
        """
        self.reply = ""
        while self.reply != eot:
            self.reply = self.serialPort.readline().decode("ascii")
            if self.verbose:
                print(f"> {self.reply}")

    def read(self, length):
        """ Read a fixed length of characters
        length : nb of char to read
        """
        self.reply = self.serialPort.read(length).decode("ascii")
        if self.verbose:
            print(self.reply)


# def main():
#     """ main fonction to test the class """
#     p = PortSerial()

#     print(f"{p.comPort} is open")

#     p.send_command("*VER")
#     p.read_line()

#     p.send_command('*GFW')
#     p.read_line()

#     p.send_command("*PWC", "00555")
#     p.read_line()

#     p.send_command("*CAU")
#     p.read_lines(20)

#     p.read(5)

#     p.send_command("*CSU")
#     p.read_line()

# if __name__ == "__main__":
#     main()
