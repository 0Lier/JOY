import os
import sys
import random
import platform
from time import sleep
from datetime import datetime
from threading import Thread
from contextlib import contextmanager
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich import print
import handler_animo
import cloud_agent as agent

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt
else:
    import select
    import tty
    import termios

def verificar_pantalla(min_cols, min_rows):
    cols, rows = os.get_terminal_size()
    if cols < min_cols or rows < min_rows:
        print(f"Error: Terminal too small.")
        sys.exit(1)

verificar_pantalla(115, 16)

estados = handler_animo.obtener_animo()

layout = Layout()
console = Console()
layout.split_row(
    Layout(name="face", ratio=1),
    Layout(name="prompt", ratio=2)
)
animo_actual = "Vacio"


def set_idle():
    global estados, animo_actual
    animo_actual = "idle"
    frames = handler_animo.animate("idle", estados["idle"])
    current = "up"
    value = 1
    max_value = len(frames) - 1 if isinstance(frames, list) else len(frames)
    min_value = 0 if isinstance(frames, list) else 1
    sleep_value = 0.5
    while animo_actual == "idle":
        frame = frames[value]
        align_face = Align.center(frame, vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        pasado = 0.0
        while pasado < sleep_value:
            if animo_actual != "idle":
                return 
            sleep(0.1)
            pasado += 0.1
        sleep_value = random.randint(5, 15)
        if current == "up":
            if value < max_value:
                value += 1
            else:
                current = "down"
                value -= 1
        else: 
            if value > min_value:
                value -= 1
            else:
                current = "up"
                value += 1
                sleep_value = 0.3

def set_laugh():
    global estados, animo_actual
    animo_actual = "laugh"
    frames = handler_animo.animate("laugh", estados["laugh"])
    current = "up"
    value = 1
    tiempo_de_vida = 0.0
    max_value = len(frames) - 1 if isinstance(frames, list) else len(frames)
    min_value = 0 if isinstance(frames, list) else 1
    while animo_actual == "laugh":
        frame = frames[value]
        align_face = Align.center(frame, vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        sleep(0.3)
        tiempo_de_vida += 0.3
        if tiempo_de_vida > 5.0:
            Thread(target=set_idle, daemon=True).start()
            return
        if current == "up":
            if value < max_value:
                value += 1
            else:
                current = "down"
                value -= 1
        else: 
            if value > min_value:
                value -= 1
            else:
                current = "up"
                value += 1

def set_angry():
    global estados, animo_actual
    animo_actual = "angry"
    frames = handler_animo.animate("angry", estados["angry"])
    
    # SI SOLO HAY 1 SPRITE: Lo dibuja una vez y mantiene el bucle sin mover índices
    if len(frames) == 1:
        align_face = Align.center(frames[0], vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        tiempo_de_vida = 0.0
        while animo_actual == "angry":
            sleep(0.3)
            tiempo_de_vida += 0.3
            if tiempo_de_vida > 5.0:
                Thread(target=set_idle, daemon=True).start()
                return
        return

    current = "up"
    value = 0
    tiempo_de_vida = 0.0
    max_value = len(frames) - 1
    min_value = 0
    while animo_actual == "angry":
        frame = frames[value]
        align_face = Align.center(frame, vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        sleep(0.3)
        tiempo_de_vida += 0.3
        if tiempo_de_vida > 5.0:
            Thread(target=set_idle, daemon=True).start()
            return
        if current == "up":
            if value < max_value:
                value += 1
            else:
                current = "down"
                value -= 1
        else: 
            if value > min_value:
                value -= 1
            else:
                current = "up"
                value += 1

def set_boring():
    global estados, animo_actual
    animo_actual = "boring"
    frames = handler_animo.animate("boring", estados["boring"])
    current = "up"
    value = 1
    tiempo_de_vida = 0.0
    max_value = len(frames) - 1 if isinstance(frames, list) else len(frames)
    min_value = 0 if isinstance(frames, list) else 1
    while animo_actual == "boring":
        frame = frames[value]
        align_face = Align.center(frame, vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        sleep(0.3)
        tiempo_de_vida += 0.3
        if tiempo_de_vida > 5.0:
            Thread(target=set_idle, daemon=True).start()
            return
        if current == "up":
            if value < max_value:
                value += 1
            else:
                current = "down"
                value -= 1
        else: 
            if value > min_value:
                value -= 1
            else:
                current = "up"
                value += 1

def set_sad():
    global estados, animo_actual
    animo_actual = "sad"
    frames = handler_animo.animate("sad", estados["sad"])
    current = "up"
    value = 1
    tiempo_de_vida = 0.0
    max_value = len(frames) - 1 if isinstance(frames, list) else len(frames)
    min_value = 0 if isinstance(frames, list) else 1
    while animo_actual == "sad":
        frame = frames[value]
        align_face = Align.center(frame, vertical="middle")
        layout["face"].update(Panel(align_face, title="JOY"))
        sleep(0.3)
        tiempo_de_vida += 0.3
        if tiempo_de_vida > 5.0:
            Thread(target=set_idle, daemon=True).start()
            return
        if current == "up":
            if value < max_value:
                value += 1
            else:
                current = "down"
                value -= 1
        else: 
            if value > min_value:
                value -= 1
            else:
                current = "up"
                value += 1

# ── LECTURA DE TECLADO ──────────────────────────────────────────────────────
# En Windows: msvcrt no bloquea y mapea las flechas a las mismas secuencias
# que ya chequea el loop principal (\x1b[A / \x1b[B), así todo el resto
# del código queda idéntico entre plataformas.
def leer_teclas_de_golpe():
    if IS_WINDOWS:
        chars = ""
        while msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):   # Prefijo de tecla especial en Windows
                ch2 = msvcrt.getwch()
                if ch2 == 'H':           # Flecha Arriba  → mismo código que Linux
                    chars += '\x1b[A'
                elif ch2 == 'P':         # Flecha Abajo   → mismo código que Linux
                    chars += '\x1b[B'
            else:
                # ¡ESTO FALTABA! Captura letras, números, espacios y ENTER (\r)
                chars += ch
        return chars if chars else None
    else:
        if select.select([sys.stdin], [], [], 0.05)[0]:
            return os.read(sys.stdin.fileno(), 10).decode('utf-8', errors='ignore')
        return None

# ── CONTEXTO DE TERMINAL ─────────────────────────────────────────────────────
# En Linux ponemos stdin en modo raw (setcbreak) y lo restauramos al salir.
# En Windows msvcrt ya lee sin eco y sin esperar Enter, no hace falta nada.
@contextmanager
def setup_terminal():
    if IS_WINDOWS:
        yield
    else:
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            yield
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

input_buffer = ""
historial = []
scroll_offset = 0
ia_pensando = False  

def controlador_de_cara(estado):
    global animo_actual, ia_pensando
    if estado == "laugh" and animo_actual != "laugh":
        Thread(target=set_laugh, daemon=True).start()
    elif estado == "angry" and animo_actual != "angry":
        Thread(target=set_angry, daemon=True).start()
    elif estado == "sad" and animo_actual != "sad":
        Thread(target=set_sad, daemon=True).start()
    elif estado == "boring" and animo_actual != "boring":
        Thread(target=set_boring, daemon=True).start()
    elif estado == "idle":
        ia_pensando = False  

texto_usuario = "Ninguno"

Thread(target=set_idle, daemon=True).start()

with setup_terminal():
    with Live(layout, refresh_per_second=20):
        while True:
            _, rows = os.get_terminal_size()
            max_lineas = max(3, rows - 7) 

            # Procesamos las líneas reales subdivididas por el cloud_agente
            todas_las_lineas = []
            for bloque in historial:
                todas_las_lineas.extend(bloque.split("\n"))

            # --- DETECCIÓN MEJORADA DE FLECHAS (Evita pérdidas de secuencia) ---
            teclas = leer_teclas_de_golpe()
            if teclas:
                if '\x1b[A' in teclas:     # Flecha Arriba detectada de forma segura
                    scroll_offset += 1
                elif '\x1b[B' in teclas:   # Flecha Abajo detectada de forma segura
                    scroll_offset -= 1
                elif teclas.startswith('\x1b'): 
                    pass 
                else:
                    if not ia_pensando:
                        salir_del_programa = False
                        for c in teclas:
                            if c in ("\n", "\r"):
                                texto_usuario = input_buffer
                                input_buffer = ""
                                scroll_offset = 0  
                                
                                if texto_usuario.lower() == "salir":
                                    salir_del_programa = True
                                    break
                                
                                if texto_usuario.strip():
                                    ia_pensando = True  
                                    Thread(
                                        target=agent.probar_stream_ollama, 
                                        args=(texto_usuario, historial, controlador_de_cara), 
                                        daemon=True
                                    ).start()

                            elif c in ("\x7f", "\b"):  
                                input_buffer = input_buffer[:-1]
                            elif c.isprintable(): 
                                input_buffer += c
                                
                        if salir_del_programa:
                            break

            # Bounding reactivo inmediato posterior a la pulsación
            limite_scroll = max(0, len(todas_las_lineas) - max_lineas)
            if scroll_offset > limite_scroll: 
                scroll_offset = limite_scroll
            if scroll_offset < 0: 
                scroll_offset = 0

            inicio = max(0, len(todas_las_lineas) - max_lineas - scroll_offset)
            fin = inicio + max_lineas
            pantalla_historial = "\n".join(todas_las_lineas[inicio:fin])

            if ia_pensando:
                linea_input = "[bold yellow]⏳ JOY está pensando...[/bold yellow]"
            else:
                linea_input = f"👉 Escribe algo: [bold cyan]{input_buffer}█[/bold cyan]"

            layout["prompt"].update(Panel(
                f"{pantalla_historial}\n\n"
                f"{linea_input}", 
                title="Consola (↑/↓ para scrollear)"
            ))
            
            sleep(0.02)