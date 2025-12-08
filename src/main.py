from nicegui import ui
from emulation import PMEmulation, EmulatedMotor, IntegraPowerMeter
from integra import INTEGRA  # classe réelle
from motor_half_lambda import MotorController, motor
import math


# Choix du backend moteur : préférence pour `motor` (hardware), sinon bascule vers `EmulatedMotor`
active_motor = None
try:
    if 'motor' in globals() and motor is not None:
        # essayer d'utiliser le moteur matériel s'il expose get_position() ou un attribut d'angle
        try:
            if hasattr(motor, 'get_position'):
                _ = motor.get_position()
                active_motor = motor
            elif hasattr(motor, 'current_angle_lame'):
                active_motor = motor
            else:
                raise Exception('motor sans API de position')
        except Exception:
            # fallback vers simulation
            active_motor = EmulatedMotor()
            print('Motor simulation active (fallback from main)')
    else:
        active_motor = EmulatedMotor()
        print('Motor simulation active (no motor found)')
except Exception as e:
    print(f'Erreur sélection backend moteur: {e} — utilisation simulation')
    active_motor = EmulatedMotor()





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

            mode_select = ui.select(['emulation', 'integra'], value=None, label='Mode').classes('w-full mb-1')
            status_label = ui.label("Non connecté").classes('text-sm mb-2')

            pm = None   # variable globale future

            def connect_powermeter():
                global pm
                mode = mode_select.value

                try:
                    if mode == 'emulation':
                        pm = PMEmulation()
                        status_label.set_text("Simulation activée")

                    elif mode == 'integra':
                        # Utiliser le wrapper IntegraPowerMeter qui encapsule la
                        # classe INTEGRA et fournit detect/measure/zero
                        pm = IntegraPowerMeter()
                        reply = pm.detect()
                        status_label.set_text(f"INTEGRA détecté : {reply}")

                    ui.notify(f"Powermeter connecté en mode {mode}", color="green")

                except Exception as e:
                    pm = PMEmulation()
                    status_label.set_text(f"Erreur: {e}, Simulation activée")
                    ui.notify(f"Erreur connexion Powermeter : {e}", color="red")

            ui.button("Connect", on_click=connect_powermeter).classes('w-full mb-2')

            # Affichage puissance
            pd_power = ui.label('0.00 mW').classes('text-lg font-mono mb-2')
            pd_wavelength = ui.label('λ: -- nm').classes('text-sm text-gray-600 mb-2')
            with ui.element('div').style(
                'width:40px; height:150px; border-radius:6px; border:1px solid #007BFF; background:#e0f0ff; position:relative; margin-bottom:10px; overflow:hidden;'
            ) as power_bar:
                power_fill = ui.element('div').style(
                    'position:absolute; bottom:0; width:100%; background:#007BFF; height:0%; transition: height 0.5s;'
                )

            # BOUTON ZERO
            def zero_powermeter():
                global pm
                if not pm:
                    ui.notify("Powermeter non connecté", color="red")
                    return

                if hasattr(pm, "zero"):
                    reply = pm.zero()
                    status_label.set_text(f"ZERO effectué : {reply}")
                else:
                    status_label.set_text("ZERO simulation effectué")

                pd_power.set_text("0.00 mW")
                power_fill.style(
                    'position:absolute; bottom:0; width:100%; background:#007BFF; height:0%; transition: height 0.5s;'
                )

                ui.notify("Powermeter remis à zéro", color="green")

            ui.button("Zero", on_click=zero_powermeter).classes('w-full bg-red-100 mb-2')

            # Timer mise à jour puissance
            def update_power():
                if pm:
                    value = pm.measure()
                    pd_power.set_text(f'{value:.2f} mW')
                    # longueur d'onde si disponible
                    if hasattr(pm, 'get_wavelength'):
                        try:
                            wl = pm.get_wavelength()
                            if wl:
                                pd_wavelength.set_text(f'λ: {wl:.0f} nm')
                            else:
                                pd_wavelength.set_text('λ: -- nm')
                        except Exception:
                            pd_wavelength.set_text('λ: -- nm')
                    height_percent = min(max(value / 20 * 100, 0), 100)
                    power_fill.style(
                        f'position:absolute; bottom:0; width:100%; background:#007BFF; height:{height_percent}%; transition: height 0.5s;'
                    )
                return True

            ui.timer(1.0, update_power)

       
        # MotorController
        
           # --- BLOC 2 : CONTRÔLE MOTEUR (Vert) ---
        with ui.card().classes(
            'flex flex-col items-center bg-green-50 min-w-[250px] md:w-5/12'
        ).props('outlined') as motor_card:
            ui.label('Contrôle Moteur').classes('text-xl font-bold text-green-700 mb-2')
           
            # Affichage Position
            # Utiliser l'instance `active_motor` (hardware ou simulation)
            current_angle_init = 0.0
            try:
                if hasattr(active_motor, 'get_position'):
                    current_angle_init = float(active_motor.get_position())
                elif hasattr(active_motor, 'current_angle_lame'):
                    current_angle_init = float(active_motor.current_angle_lame)
                elif hasattr(active_motor, 'current_angle'):
                    current_angle_init = float(active_motor.current_angle)
            except Exception:
                current_angle_init = 0.0

            motor_angle_display = ui.label(f'{current_angle_init:.1f}°').classes('text-lg mb-2')
           
            # Cadran Visuel Simple
            with ui.element('div').style(
                'width:100px; height:100px; border:2px solid #28a745; border-radius:50%; position:relative; margin-bottom:10px;'
            ) as motor_circle:
                motor_needle = ui.element('div').style(
                    f'width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; '
                    f'transform-origin:bottom center; transform:rotate({current_angle_init}deg); transition: transform 0.5s;'
                )

            # --- ONGLETS ---
            with ui.tabs().classes('w-full') as tabs:
                manual_tab = ui.tab('Angle')
                power_tab = ui.tab('Puissance')

            with ui.tab_panels(tabs, value=manual_tab).classes('w-full bg-transparent'):
               
                # --- MODE 1 : ANGLE MANUEL ---
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
                        if active_motor:
                            try:
                                active_motor.go_to_angle(target)
                            except Exception:
                                pass
                            # Récupérer la position effective (en degrés lame)
                            try:
                                if hasattr(active_motor, 'get_position'):
                                    new_ang = float(active_motor.get_position())
                                elif hasattr(active_motor, 'read_angle'):
                                    new_ang = float(active_motor.read_angle())
                                elif hasattr(active_motor, 'current_angle_lame'):
                                    new_ang = float(active_motor.current_angle_lame)
                                elif hasattr(active_motor, 'current_angle'):
                                    new_ang = float(active_motor.current_angle)
                                else:
                                    new_ang = target
                            except Exception:
                                new_ang = target
                            motor_angle_display.set_text(f'{new_ang:.1f}°')
                            motor_needle.style(f'transform:rotate({new_ang}deg); width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; transform-origin:bottom center;')

                    angle_input.on('keydown.enter', lambda: move_motor_angle())
                   
                    with ui.row().classes('justify-center gap-2 mt-2'):
                        ui.button('0°', on_click=lambda: move_motor_angle(0)).props('outline size=sm')
                        ui.button('22.5°', on_click=lambda: move_motor_angle(22.5)).props('outline size=sm')
                        ui.button('45°', on_click=lambda: move_motor_angle(45)).props('outline size=sm')

                # --- MODE 2 : PUISSANCE CIBLE ---
                with ui.tab_panel(power_tab):
                    # Calibration
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
                            ui.notify(f'Impossible : {P_target} > {P_max}', type='warning')
                            return
                       
                        if P_target < 0: P_target = 0

                        # Calcul Physique
                        ratio = P_target / P_max
                        ratio = min(ratio, 1.0)
                       
                        angle_rad = 0.5 * math.acos(math.sqrt(ratio))
                        angle_deg = math.degrees(angle_rad)
                       
                        print(f"Puissance demandée: {P_target}mW -> Angle calculé: {angle_deg:.2f}°")
                       
                        if active_motor:
                            try:
                                active_motor.go_to_angle(angle_deg)
                            except Exception:
                                pass
                            try:
                                if hasattr(active_motor, 'get_position'):
                                    new_ang = float(active_motor.get_position())
                                elif hasattr(active_motor, 'read_angle'):
                                    new_ang = float(active_motor.read_angle())
                                elif hasattr(active_motor, 'current_angle_lame'):
                                    new_ang = float(active_motor.current_angle_lame)
                                elif hasattr(active_motor, 'current_angle'):
                                    new_ang = float(active_motor.current_angle)
                                else:
                                    new_ang = angle_deg
                            except Exception:
                                new_ang = angle_deg
                            motor_angle_display.set_text(f'{new_ang:.1f}°')
                            motor_needle.style(f'transform:rotate({new_ang}deg); width:2px; height:45px; background:#28a745; position:absolute; bottom:50%; left:50%; transform-origin:bottom center;')
                            ui.notify(f'Réglé à {angle_deg:.1f}° pour {P_target} mW')

                    target_power_input.on('keydown.enter', move_motor_power)
                    ui.button('Régler Puissance', on_click=move_motor_power).classes('w-full mt-2')


ui.run()
