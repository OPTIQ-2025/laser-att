from nicegui import ui

#Classes imaginaires pour le contrôle du moteur et la mesure de puissance
class MotorController:
    def __init__(self):
        self.current_angle = 0.0

    def go_to_angle(self, angle: float):
        """Déplacement instantané pour simplification."""
        self.current_angle = angle

class PowerMeter:
    def measure(self):
        import random
        return 5 + random.random() * 15  # 5 à 20 mW

motor = MotorController()
pm = PowerMeter()

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

    # Photodiode et moteur
    with ui.row().classes('w-full md:w-2/3 gap-6').style('flex-wrap: wrap'):

        # Photodiode
        with ui.card().classes(
            'flex flex-col items-center bg-blue-50 hover:bg-blue-100 cursor-pointer min-w-[250px] md:w-5/12'
        ).props('outlined') as pd_card:
            ui.label('Photodiode').classes('text-xl font-bold text-blue-700 mb-2')
            pd_power = ui.label(f'{pm.measure():.2f} mW').classes('text-lg mb-4')
            with ui.element('div').style(
                'width:40px; height:150px; border:1px solid #007BFF; background:#e0f0ff; position:relative; margin-bottom:10px;'
            ) as power_bar:
                power_fill = ui.element('div').style(
                    'position:absolute; bottom:0; width:100%; background:#007BFF; height:50%;'
                )

            # Timer pour mise à jour automatique
            def update_power():
                value = pm.measure()
                pd_power.set_text(f'{value:.2f} mW')
                height_percent = min(max(value / 20 * 100, 0), 100)
                power_fill.style(
                    f'position:absolute; bottom:0; width:100%; background:#007BFF; height:{height_percent}%;'
                )
                return True  # permet à ui.timer de répéter l'appel

            ui.timer(1.0, update_power)


         # CONTRÔLE MOTEUR 
        with ui.card().classes(
            'flex flex-col items-center bg-green-50 min-w-[250px] md:w-5/12'
        ).props('outlined') as motor_card:
            ui.label('Contrôle Moteur').classes('text-xl font-bold text-green-700 mb-2')
            
            # Affichage Position
            current_angle_init = motor.current_angle if motor else 0.0
            motor_angle_display = ui.label(f'{current_angle_init:.1f}°').classes('text-lg mb-2')
            
            # Cadran Visuel
            with ui.element('div').style(
                'width:100px; height:100px; border:2px solid #28a745; border-radius:50%; position:relative; margin-bottom:10px;'
            ) as motor_circle:
                motor_needle = ui.element('div').style(
                    f'width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; '
                    f'transform-origin:bottom center; transform:rotate({current_angle_init}deg); transition: transform 0.5s;'
                )

            #ONGLETS POUR CHOISIR LE MODE
            with ui.tabs().classes('w-full') as tabs:
                manual_tab = ui.tab('Angle').classes('text-green-700')
                power_tab = ui.tab('Puissance').classes('text-blue-700')

            with ui.tab_panels(tabs, value=manual_tab).classes('w-full bg-transparent'):
                
                # MODE 1 : ANGLE MANUEL 
                with ui.tab_panel(manual_tab):
                    angle_input = ui.number(
                        min=-180, max=180, value=current_angle_init, step=1.0,
                        label='Angle (-180° à +180°)'
                    ).classes('w-full')

                    def move_motor_angle(preset_angle=None):
                        if preset_angle is not None:
                            angle_input.set_value(preset_angle)
                        
                        if angle_input.value is None: return
                        target = float(f'{angle_input.value:.1f}')
                        
                        print(f"Déplacement manuel vers {target}°")
                        if motor:
                            motor.go_to_angle(target)
                            # Update UI
                            new_ang = motor.current_angle
                            motor_angle_display.set_text(f'{new_ang:.1f}°')
                            motor_needle.style(f'transform:rotate({new_ang}deg); width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; transform-origin:bottom center;')

                    angle_input.on('keydown.enter', lambda: move_motor_angle())
                    
                    with ui.row().classes('justify-center gap-2 mt-2'):
                        ui.button('0°', on_click=lambda: move_motor_angle(0)).props('outline size=sm')
                        ui.button('22.5°', on_click=lambda: move_motor_angle(22.5)).props('outline size=sm')
                        ui.button('45°', on_click=lambda: move_motor_angle(45)).props('outline size=sm')

                # MODE 2 : PUISSANCE CIBLE 
                with ui.tab_panel(power_tab):
                    # Calibration (Puissance Max du Laser)
                    ui.label('Calibration (P max)').classes('text-xs text-gray-500')
                    p_max_input = ui.number(value=20.0, min=0.1, step=0.1, suffix='mW').props('dense outlined').classes('w-full mb-2')
                    
                    # Cible
                    target_power_input = ui.number(
                        label='Puissance souhaitée', suffix='mW', min=0, step=0.1
                    ).classes('w-full')

                    def move_motor_power():
                        P_target = target_power_input.value
                        P_max = p_max_input.value
                        
                        if P_target is None or P_max is None: return
                        
                        if P_target > P_max:
                            ui.notify(f'Impossible : Demande ({P_target} mW) > Max ({P_max} mW)', type='warning')
                            return
                        
                        if P_target < 0: P_target = 0


                        ratio = P_target / P_max
                        # si ratio > 1 à cause d'un arrondi
                        ratio = min(ratio, 1.0)
                        
                        angle_rad = 0.5 * math.acos(math.sqrt(ratio))
                        angle_deg = math.degrees(angle_rad)
                        
                        #  Une lame lambda/2 atténue de Max à 0 entre 0° et 45°.
                        print(f"Puissance demandée: {P_target}mW -> Angle calculé: {angle_deg:.2f}°")
                        
                        if motor:
                            motor.go_to_angle(angle_deg)
                            # Update UI visu
                            new_ang = motor.current_angle
                            motor_angle_display.set_text(f'{new_ang:.1f}°')
                            motor_needle.style(f'transform:rotate({new_ang}deg); width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; transform-origin:bottom center;')
                            ui.notify(f'Réglé à {angle_deg:.1f}° pour {P_target} mW')

                    target_power_input.on('keydown.enter', move_motor_power)
                    ui.button('Régler Puissance', on_click=move_motor_power).classes('w-full mt-2 bg-blue-600 text-white')

ui.run()