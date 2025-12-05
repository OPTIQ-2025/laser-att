from integra import INTEGRA
power = INTEGRA("COM3")
power.set_pwc(int(633))
power.send_command("*CAU")
power.read_line()
print(power.reply)