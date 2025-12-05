from port import PortSerial
from scope import Scope
from status import *


class INTEGRA(PortSerial, Scope, Status):
    """ Class to connect to an integra """

    def __init__(self, comPort=""):
        """ Default constructor """
        PortSerial.__init__(self, comPort)
        Status.__init__(self)
        Scope.__init__(self)

    def get_version(self):
        """ Get the versions of the device:
            VER, GFW and GHW
        """
        self.send_command("*VER")
        self.read_line()
        self.version_sw = self.reply.rstrip()

        self.send_command("*GFW")
        self.read_line()
        self.version_fw = self.reply.rstrip()

        self.send_command("*GHW")
        self.read_line()
        self.version_hw = self.reply.rstrip()

    def set_pwc(self, pwc):
        """
        Set the pwc
            : pwc: the desired wavelength
        """
        s = "{:05d}".format(pwc)

        if len(s) == 5:
            print("PWC: OK")
        else:
            print("PWC: Wrong length")
            return

        self.send_command("*PWC" + s)
        self.read_line()

    def set_user_multiplier(self, value):
        s = format8(value)
        n = 0
        if len(s) == 8:
            print("UserMultiplier: OK[", n, "] ", s, "for:", value)
        else:
            n += 1
            print("UserMultiplier: Wrong length:", s, "for:", value)

    def get_data(self):
        """ Read the line and convert the output into data """
        self.read_line()
        try:
            self.set_value(float(self.reply))
        except ValueError:
            self.set_value(0)

    def get_status(self):
        """ Request the status from the device and decode it"""
        self.send_command("*STS")
        self.verbose = False
        replys = []

        while self.reply[0:2] != ":1":
            self.read_line()
            replys.append(self.reply)

        self.read_line()  # read the ACK

        # decode the status
        self.mode = int(f"0x{replys[0x05][6:10]}{replys[0x04][6:10]}",
                        base=16)
        self.scale_cur = int(f"0x{replys[0x07][6:10]}{replys[0x06][6:10]}",
                             base=16)
        self.scale_max = int(f"0x{replys[0x09][6:10]}{replys[0x08][6:10]}",
                             base=16)
        self.scale_min = int(f"0x{replys[0x0B][6:10]}{replys[0x0A][6:10]}",
                             base=16)
        self.wavelength_cur = int(
            f"0x{replys[0x0D][6:10]}{replys[0x0C][6:10]}",
            base=16)
        self.wavelength_max = int(
            f"0x{replys[0x0F][6:10]}{replys[0x0E][6:10]}",
            base=16)
        self.wavelength_min = int(
            f"0x{replys[0x11][6:10]}{replys[0x10][6:10]}",
            base=16)
        self.att_available = int(f"0x{replys[0x13][6:10]}{replys[0x12][6:10]}",
                                 base=16)
        self.att_present = int(f"0x{replys[0x15][6:10]}{replys[0x14][6:10]}",
                               base=16)

        # decode name
        name = ""
        for i in range(0x1A, 0x24):
            name = name + replys[i][6:10]

        for i in range(0, len(name), 4):
            if name[i+2:i+4] != "CC":
                self.detector_name = self.detector_name + chr(int(
                    name[i+2:i+4],
                    base=16)
                )

            if name[i:i+2] != "CC":
                self.detector_name = self.detector_name + chr(int(
                    name[i:i+2],
                    base=16)
                )

    def print_status(self):
        """ Display the status of the device """
        
        print(f"sw: {self.version_sw}")
        print(f"fw: {self.version_fw}")
        print(f"hw: {self.version_hw}")
        print(f"Name: {self.detector_name}")
        print(f"Serial: {self.detector_serial}")
        print(f"Mode: {self.mode}")
        print(f"Scale Cur: {self.scale_cur}")
        print(f"Scale Min: {self.scale_min}")
        print(f"Scale Max: {self.scale_max}")
        print(f"Wavelength cur: {self.wavelength_cur}")
        print(f"Wavelength min: {self.wavelength_min}")
        print(f"Wavelength max: {self.wavelength_max}")
        print(f"Attenuator available: {self.att_available}")
        print(f"Attenuator present: {self.att_present}")

    def test_integra_D(self):
        """ Test to validate the scale_min of STS command """

        self.port.get_status()
        scale = True

        while scale:
            self.port.send_command("*GCR")
            self.port.read_line()
            valeur_1 = self.port.reply.rstrip()[7:]
            print("Valuer_1", valeur_1)
            self.port.send_command("*SSD")
            self.port.send_command("*GCR")
            self.port.read_line()
            valeur_2 = self.port.reply.rstrip()[7:]
            print("Valeur_2:", valeur_2)

            if valeur_2 == valeur_1:
                scale = False
                self.assertEqual(int(valeur_1), self.port.scale_min)

    def show_validscale(self):
        """Show the valid scales"""

        self.send_command("*DVS")
        self.verbose = False
        finish = 0

        while finish != 1:
            self.read_line()
            if self.reply == "":
                finish = 1
            else:
                print(self.reply)

    def set_range(self, range):
        """Set the current scale
            range: index of the scale"""

        s = "{0:2d}".format(range)

        if len(s) == 2:
            print("Scale: OK")
        else:
            print("Scale: Wrong length")
            return

        self.verbose = True
        self.send_command("*SCS" + s)


def main():
    """ Functions manager for user """

    integra = INTEGRA()
    if integra.quit == 1:
        return
    rep = ""
    while rep != "5":
        integra.verbose = True
        print("-"*30)
        rep = input("Menu:\n\n\
1. Display detector/Monitor info\n\
2. Change the wavelength\n\
3. Change the range\n\
4. Display measurement\n\
5. Quit\n\n Your choice: ")
        print("-"*30)

        if rep == "1":
            integra.get_status()
            integra.print_status()

        elif rep == "2":
            pwc = input("Enter the desired wavelength: ")
            integra.set_pwc(int(pwc))

        elif rep == "3":
            integra.show_validscale()
            range = input("Enter the desired scale: ")
            integra.set_range(int(range))

        elif rep == "4":
            integra.verbose = False
            integra.sleepDelay = 0
            integra.restart()
            integra.send_command("*CAU")
            integra.read_line()
            print("Close window or enter \"Ctrl C\" to stop the measurement.")
            end = 0
            while not end:
                try:
                    integra.get_data()
                    integra.update()
                except (KeyboardInterrupt, IndexError):
                    end = 1

            integra.send_command("*CSU")
            integra.read_line()

        elif rep != "5":
            print("Choose a valid option (1 to 5).")


if __name__ == "__main__":

    main()
