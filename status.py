
def format5(value):
    """ Convert a int in a 5 characters string long.
    This conversion is needed for *PWC for multiple monitor.
    """
    return "{0:5d}".format(value)


def format8(value):
    """ Convert a float in a string 8 chararacters long.
    This conversion is needed for *MUL, *OFF.
    """

    if round(value, 0) <= -100000: return "{:.0f}.".format(round(value, 0))
    if round(value, 1) <= -10000:  return "{:.1f}".format(round(value, 1))
    if round(value, 2) <= -1000:   return "{:.2f}".format(round(value, 2))
    if round(value, 3) <= -100:    return "{:.3f}".format(round(value, 3))
    if round(value, 4) <= -10:     return "{:.4f}".format(round(value, 4))
    if round(value, 5) < 0:        return "{:.5f}".format(round(value, 5))
    if round(value, 6) < 1:        return "{:.6f}".format(round(value, 6))
    if round(value, 6) < 10:       return "{:.6f}".format(round(value, 6))
    if round(value, 5) < 100:      return "{:.5f}".format(round(value, 5))
    if round(value, 4) < 1000:     return "{:.4f}".format(round(value, 4))
    if round(value, 3) < 10000:    return "{:.3f}".format(round(value, 3))
    if round(value, 2) < 100000:   return "{:.2f}".format(round(value, 2))


class Status:
    """ Status of a monitor """
    def __init__(self):
        self.mode = 0
        self.scale_max = 0
        self.scale_min = 0
        self.scale_cur = 0
        self.wavelength_max = 0
        self.wavelength_min = 0
        self.wavelength_cur = 0
        self.att_available = 0
        self.att_present = 0
        self.detector_name = ""
        self.detector_serial = ""
        self.version_sw = ""
        self.version_fw = ""
        self.version_hw = ""

    def print_status(self):
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
        print(f"attenuator available: {self.att_available}")
        print(f"attenuator present: {self.att_present}")

    def decode(self, input):
        # decode the status
        self.mode = int(f"0x{input[0x05][6:10]}{input[0x04][6:10]}", base=16)
        self.scale_cur = int(f"0x{input[0x07][6:10]}{input[0x06][6:10]}",
                             base=16)
        self.scale_max = int(f"0x{input[0x09][6:10]}{input[0x08][6:10]}",
                             base=16)
        self.scale_min = int(f"0x{input[0x0B][6:10]}{input[0x0A][6:10]}",
                             base=16)
        self.wavelength_cur = int(f"0x{input[0x0D][6:10]}{input[0x0C][6:10]}",
                                  base=16)
        self.wavelength_max = int(f"0x{input[0x0F][6:10]}{input[0x0E][6:10]}",
                                  base=16)
        self.wavelength_min = int(f"0x{input[0x11][6:10]}{input[0x10][6:10]}",
                                  base=16)
        self.att_available = int(f"0x{input[0x13][6:10]}{input[0x12][6:10]}",
                                 base=16)
        self.att_present = int(f"0x{input[0x15][6:10]}{input[0x14][6:10]}",
                               base=16)

        # decode name
        name = ""
        for i in range(0x1A, 0x24):
            name = name + input[i][6:10]

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

        sn = ""
        for i in range(0x2A, 0x2D):
            sn = sn + input[i][6:10]

        for i in range(0, len(sn), 4):
            if sn[i+2:i+4] != "CC":
                self.detector_serial = self.detector_serial + chr(int(
                    sn[i+2:i+4],
                    base=16)
                )

            if sn[i:i+2] != "CC":
                self.detector_serial = self.detector_serial + chr(int(
                     sn[i:i+2],
                     base=16)
                )
