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


        # Moteur
        with ui.card().classes(
            'flex flex-col items-center bg-green-50 hover:bg-green-100 cursor-pointer min-w-[250px] md:w-5/12'
        ).props('outlined') as motor_card:
            ui.label('Moteur').classes('text-xl font-bold text-green-700 mb-2')
            motor_angle_display = ui.label(f'{motor.current_angle:.1f}°').classes('text-lg mb-2')
            with ui.element('div').style(
                'width:150px; height:150px; border:2px solid #28a745; border-radius:50%; position:relative; margin-bottom:10px;'
            ) as motor_circle:
                motor_needle = ui.element('div').style(
                    'width:2px; height:70px; background:#28a745; position:absolute; bottom:50%; left:50%; '
                    'transform-origin:bottom center; transform:rotate(0deg);'
                )
            angle_input = ui.number(min=0, max=180, value=motor.current_angle, step=0.1, label='Angle souhaité').classes('w-full mb-2')

            # Déplacement instantané sur bouton
            def move_motor():
                target_angle = float(f'{angle_input.value:.1f}')
                motor.go_to_angle(target_angle)
                motor_angle_display.set_text(f'{motor.current_angle:.1f}°')
                motor_needle.style(
                    f'width:2px; height:70px; background:#28a745; position:absolute; bottom:50%; left:50%; '
                    f'transform-origin:bottom center; transform:rotate({motor.current_angle}deg);'
                )

            ui.button("Aller à l'angle", on_click=move_motor).classes('mt-2')
ui.run()