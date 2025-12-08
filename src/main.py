from nicegui import ui
from emulation import PMEmulation, EmulatedMotor
#from integra import Integra  # classe réelle
#from motor_arduino import ArduinoMotor  # classe réelle



# Interface principale

with ui.column().classes('w-full items-center gap-6 mt-4'):

   
    # Schéma optique
   
    with ui.card().classes('w-full md:w-2/3 p-6 items-center bg-blue-50'):
        ui.label('SYSTÈME OPTIQUE').classes('text-2xl font-bold text-blue-700')
        with ui.row().classes('justify-center items-center gap-4 mt-4'):
            ui.label('P_in').classes('text-lg font-semibold')
            ui.label('→').classes('text-lg font-semibold')
            with ui.card().classes('p-2 text-center border-2 border-blue-500 rounded-lg bg-white'):
                ui.label('Lame demi-onde + Polariseur').classes('text-lg')
            ui.label('→').classes('text-lg font-semibold')
            ui.label('P_out').classes('text-lg font-semibold')

   
    # PowerMeter et MotorController
   
    with ui.row().classes('w-full md:w-2/3 gap-6').style('flex-wrap: wrap'):

        
        # PowerMeter
       
        with ui.card().classes(
            'flex flex-col items-center bg-blue-50 hover:bg-blue-100 cursor-pointer min-w-[250px] md:w-5/12 p-4'
        ).props('outlined') as pd_card:

            ui.label('PowerMeter').classes('text-xl font-bold text-blue-700 mb-2')

            # Sélecteur et statut
            mode_select = ui.select(['emulation', 'integra'], value='emulation', label='Mode').classes('w-full mb-1')
            status_label = ui.label("Non connecté").classes('text-sm mb-2')

            def connect_powermeter():
                global pm, powermeter_mode
                powermeter_mode = mode_select.value
                try:
                    if powermeter_mode == 'emulation':
                        pm = PMEmulation()
                        status_label.set_text("Simulation activée")
                    elif powermeter_mode == 'integra':
                        
                        pm = Integra()
                        status_label.set_text(" Powermeter Integra connecté")
                    ui.notify(f"Powermeter connecté en mode {powermeter_mode}", color="green")
                except Exception as e:
                    pm = PMEmulation()
                    status_label.set_text(f"Erreur: {e}, Simulation activée")
                    ui.notify(f"Erreur connexion Powermeter : {e}", color="red")

            ui.button("Connect", on_click=connect_powermeter).classes('w-full mb-2')

            # Affichage puissance
            pd_power = ui.label('0.00 mW').classes('text-lg font-mono mb-2')
            with ui.element('div').style(
                'width:40px; height:150px; border-radius:6px; border:1px solid #007BFF; background:#e0f0ff; position:relative; margin-bottom:10px; overflow:hidden;'
            ) as power_bar:
                power_fill = ui.element('div').style(
                    'position:absolute; bottom:0; width:100%; background:#007BFF; height:0%; transition: height 0.5s;'
                )

            def update_power():
                if pm:
                    value = pm.measure()
                    pd_power.set_text(f'{value:.2f} mW')
                    height_percent = min(max(value / 20 * 100, 0), 100)
                    power_fill.style(f'position:absolute; bottom:0; width:100%; background:#007BFF; height:{height_percent}%; transition: height 0.5s;')
                return True

            ui.timer(1.0, update_power)

       
        # MotorController
        
        with ui.card().classes(
            'flex flex-col items-center bg-green-50 hover:bg-green-100 cursor-pointer min-w-[250px] md:w-5/12 p-4'
        ).props('outlined') as motor_card:

            ui.label('MotorController').classes('text-xl font-bold text-green-700 mb-2')

            motor_mode_select = ui.select(['emulation', 'arduino'], value='emulation', label='Mode').classes('w-full mb-1')
            motor_status_label = ui.label("Non connecté").classes('text-sm mb-2')

            def connect_motor():
                global motor, motor_mode
                motor_mode = motor_mode_select.value
                try:
                    if motor_mode == 'emulation':
                        motor = EmulatedMotor()
                        motor_status_label.set_text("Simulation activée")
                    elif motor_mode == 'arduino':
                       
                        motor = ArduinoMotor()
                        motor_status_label.set_text("Moteur Arduino connecté")
                    ui.notify(f"Moteur connecté en mode {motor_mode}", color="green")
                except Exception as e:
                    motor = EmulatedMotor()
                    motor_status_label.set_text(f"Erreur: {e}, Simulation activée")
                    ui.notify(f"Erreur connexion moteur : {e}", color="red")

            ui.button("Connect", on_click=connect_motor).classes('w-full mb-2')

            motor_angle_display = ui.label('0.0°').classes('text-lg font-mono mb-2')
            with ui.element('div').style(
                'width:150px; height:150px; border-radius:50%; border:2px solid #28a745; position:relative; margin-bottom:10px; overflow:hidden;'
            ) as motor_circle:
                motor_needle = ui.element('div').style(
                    'width:2px; height:70px; background:#28a745; position:absolute; bottom:50%; left:50%; transform-origin:bottom center; transform:rotate(0deg); transition: transform 0.5s;'
                )

            angle_input = ui.number(min=0, max=180, value=0.0, step=0.1, label='Angle souhaité').classes('w-full mb-2')

            def move_motor():
                if motor:
                    target_angle = float(f'{angle_input.value:.1f}')
                    motor.go_to_angle(target_angle)
                    current_angle = motor.read_angle()
                    motor_angle_display.set_text(f'{current_angle:.1f}°')
                    motor_needle.style(
                        f'width:2px; height:70px; background:#28a745; position:absolute; bottom:50%; left:50%; '
                        f'transform-origin:bottom center; transform:rotate({current_angle}deg); transition: transform 0.5s;'
                    )

            ui.button("Aller à l'angle", on_click=move_motor).classes('mt-2 w-full')


ui.run()
