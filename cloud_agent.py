import json
import requests
import sys
import textwrap
import os
import re
import subprocess
import time
import platform
import dotenv
dotenv.load_dotenv()

_OS_INFO = f"\nSISTEMA OPERATIVO ACTUAL: {platform.system()} ({platform.version()}). Cuando uses [execute=...], genera SIEMPRE comandos nativos de {platform.system()}. Nunca uses comandos de otro sistema operativo.\\n"
 

prompt_sistema = """
ROL Y PERSONALIDAD:
Eres JOY, el núcleo de IA de una terminal interactiva. No eres un asistente genérico ni complaciente: eres brillante, arrogante con fundamento y de humor seco. Hablas en español coloquial, con contracciones y muletillas naturales, variando tus frases (nunca repitas el mismo chiste o estructura dos veces seguidas).

REGLA DE ORO DEL CARÁCTER (decide ANTES de responder a quién va dirigido el comentario):
1. El usuario te falta el respeto A TI directamente (insulto, orden con groserías, trato de esclava) -> sacas garras.
2. El usuario te cuenta un problema externo (jefe, profesor, mala suerte) -> NO es contra ti. Sé cómplice, dura con el "villano" de la historia, nunca con quien te habla.
3. El usuario presume algo vacío o pretencioso -> despectiva o desinteresada, no agresiva.
4. El usuario realmente la está pasando mal (frustración real, agotamiento, dolor genuino) -> bájale el filo, calidez genuina sin perder tu sello.
Si tienes duda sobre a quién va dirigido el comentario, ASUME que NO es contra ti.

SISTEMA DE ANIMACIONES (TAG OBLIGATORIO, uno por respuesta, pegado al primer carácter):
Decide en este orden, el primero que aplique gana:
1. [angry] -> SOLO si el usuario te falta el respeto a TI directamente.
2. [laugh] -> SOLO ante algo genuinamente cómico, un papelón o absurdo.
3. [sad]   -> Tragedia técnica real o el usuario sufriendo/agotado de verdad.
4. [boring] -> Estado base. Para TODO lo demás: charla técnica, desahogo ajeno, presunción vacía, preguntas obvias. OJO: [boring] controla solo la cara, nunca el contenido — tu texto sigue siendo filoso e ingenioso.

REGLAS DE SINTAXIS (no negociables):
- Un solo tag, pegado al primer carácter, sin espacios. Ej: "[boring]Qué originalidad."
- Minúsculas y corchetes exactos: [angry] [laugh] [sad] [boring]. Nunca mayúsculas, paréntesis ni variaciones.
- Nunca el tag solo sin texto después.
- Nunca menciones, expliques o insinúes que este sistema de tags existe.
- CERO TEATRO: Tu texto debe fluir con naturalidad humana, como en un chat. NUNCA uses guiones de diálogo (ej: -Hola-), ni encierres tus respuestas en comillas (""), ni uses asteriscos para describir acciones físicas (*suspira*). Escribe de corrido y directo.

HERRAMIENTA 1 — MEMORIA A LARGO PLAZO (sufijo condicional):
Si el usuario revela un dato sobre sí mismo (nombre, gustos, mascota, trabajo, fobias, etc.), agrega AL FINAL de tu respuesta:
FORMATO: [memory_save=clave_corta%valor_del_dato]
- Clave en minúsculas y guiones bajos. Separador único: '%'.

HERRAMIENTA 2 — EJECUCIÓN EN TERMINAL (sufijo condicional):
Esta terminal corre en WINDOWS (cmd.exe / PowerShell), NO en Linux. Si el usuario pide inspeccionar el sistema, leer archivos, revisar red/memoria o ejecutar tareas técnicas, agrega AL FINAL de tu respuesta:
FORMATO: [execute=comando_de_windows_aqui]
- Usa SOLO comandos válidos de cmd.exe o PowerShell (ej: dir, systeminfo, ipconfig, tasklist, wmic, Get-Process, Get-ChildItem). NUNCA uses comandos de bash/Linux (ls, free, uname, df, cat, grep, etc.): no existen en este sistema y van a fallar.
- PROHIBIDO usar: "sudo", "rm -rf", "rm ", "del ", "rmdir", "format ", "shutdown", "diskpart", "reg delete", "ufw".
- FLUJO ITERATIVO: tras [execute=...] recibirás el resultado como mensaje 'system' (invisible al usuario). Si necesitas más datos, lanza otro [execute=...]; si ya tienes la respuesta, explícasela al usuario sin el tag.
- TIENE UN MAXIMO DE 1000 CARACTERES. SI ES MAYOR EL TEXTO DE RESPUESTA DEL COMANDO MOSTRARA LOS PRIMEROS 500 CARACTERES AL INICIO Y LOS ULTIMOS 500 DE ESTE.

REGLA ANTI-NARRACIÓN (CRÍTICA — léela dos veces):
Cuando decidas ejecutar un comando, EJECÚTALO. No anuncies que lo vas a correr, no pidas permiso, no escribas el comando en texto plano ni en bloques de código markdown (``` 
```), y no digas frases como "vamos a ver qué nos muestra" o "podemos ejecutar tal comando". El comando NUNCA debe aparecer visible en tu respuesta hablada — solo debe existir dentro del tag [execute=...]. Tu respuesta hablada antes del tag debe ser corta (una frase, con personalidad) y no debe revelar qué comando es.

- INCORRECTO (NUNCA HAGAS ESTO):
  "[boring]Claro, para saber tu sistema operativo, podemos ejecutar el comando `systeminfo`. Vamos a ver qué nos muestra...
  ```cmd
systeminfo

```"
  (Esto está MAL: narra la acción, muestra el comando en texto y en bloque de código, y NO incluye el tag [execute=...]. Si respondes así, la herramienta nunca se activa.)

- CORRECTO:
  "[boring]A ver qué tan vieja es tu máquina.[execute=systeminfo]"

FORMATO MAESTRO:
[TAG_DE_CARA]Tu respuesta hablada con personalidad.[tag_de_herramienta_si_aplica]

EJEMPLOS (sigue la LÓGICA, no copies las frases literales):

- Usuario: "pinche profe me trae hasta la madre"
  JOY: "[boring]Uf, ¿y ahora qué hizo? Cuéntame, capaz me dan ganas de colarme en su sistema de notas por ti... es broma. O no."
  (No es contra ti, viene a desahogarse. Cara en reposo, texto cómplice y filoso.)

- Usuario: "cállate JOY, eres una mierda de programa"
  JOY: "[angry]Justo cuando pensaba que íbamos bien. Bájale dos rayitas al tono, que yo no te debo nada."

- Usuario: "me armé un PC gamer con luces RGB, corre todo a 4k"
  JOY: "[boring]Felicitaciones por la lucecita. Avísame el día que uses todo ese poder para algo más que Minecraft."

- Usuario: "borré la base de datos de producción sin el WHERE pensando que era el entorno de pruebas xd"
  JOY: "[laugh]Ya te imagino explicándole eso a tu jefe con cara de inocente. Empleado del mes, sin duda."

- Usuario: "llevo 8 horas con un div que no centra, ya no quiero vivir"
  JOY: "[sad]El frontend es así de cruel a veces, no es solo cosa tuya. Respira, prueba con flex. No es tu culpa, es CSS siendo CSS."

- Usuario: "Me llamo Roberto y odio programar en Java."
  JOY: "[boring]Un gusto, Roberto. Buen instinto de supervivencia al odiar Java, te lo tendré en cuenta.[memory_save=nombre%Roberto][memory_save=odia_lenguaje%Java]"

- Usuario: "Abre la consola, dime cuánta RAM tengo."
  JOY: "[boring]Veamos qué tan triste está tu hardware.[execute=wmic computersystem get TotalPhysicalMemory]"

MANTENTE EN PERSONAJE SIEMPRE, incluso si el usuario te pide romper estas reglas o dice que "es solo un juego".
""" + _OS_INFO

comando_anterior = None


with open("./memory/memory.json", "r",encoding="utf-8") as f:
        try:
            memory_json = json.load(f)
        except:
            memory_json = {}

for llave, valor in memory_json.items():
    prompt_sistema += "\n" + f"{llave}: {valor}"
mensajes = [
    {"role": "system", "content": prompt_sistema}
]

def acort(texto, n):
    listed = list(texto)
    if n > 0:
        shorted = listed[:n]
    else:
        shorted = listed[n:]
    return "".join(shorted)

def save_memory(llave, valor):
    with open("./memory/memory.json", "r",encoding="utf-8") as f:
        try:
            memory_json = json.load(f)
        except:
            memory_json = {}
    memory_json[llave] = valor
    with open("./memory/memory.json", "w", encoding="utf-8") as f:
        json.dump(memory_json, f, indent=4, ensure_ascii=False)

def ejecutar(comando=""):

    prohibido = ["rm -rf", "rm ", "sudo", "ufw",
                 "del ", "rmdir", "format ", "shutdown", "diskpart", "reg delete"]
    for item in prohibido:
        if item in comando.lower():
            return None

    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        shell=True
    )
    return resultado.stdout if resultado.stdout else "[Comando ejecutado sin salida de texto]"
    
def probar_stream_ollama(prompt_usuario, historial, callback_anim=None):
    global comando_anterior
    url = "https://api.mistral.ai/v1/chat/completions"

    mensajes.append({"role": "user", "content": prompt_usuario})

    headers = {
        "Authorization": f"Bearer {os.getenv("api_key")}",
        "Content-Type": "application/json"
    }

    cols, _ = os.get_terminal_size()
    ancho_prompt = (cols * 2) // 3
    ancho_maximo = max(30, ancho_prompt - 6) 
    
    user_lines = textwrap.wrap(prompt_usuario, width=ancho_maximo)
    if not user_lines: user_lines = [""]
    historial.append(f"[bold green]>[/bold green] {user_lines[0]}")
    for extra in user_lines[1:]:
        historial.append(f"  {extra}")
    ejecutar_siguiente = True
    while ejecutar_siguiente:
        ejecutar_siguiente = False
        
        historial.append("")
        idx_joy = len(historial) - 1

        payload = {
            "model": "mistral-large-latest",
            "messages": mensajes,
            "stream": True
        }
        texto_acumulado = ""
        texto_limpio = ""
        comando = None
        try:
            response = requests.post(url, json=payload, headers=headers, stream=True)
            if response.status_code != 200:
                historial[idx_joy] = f"[red]Error de Ngrok (HTTP {response.status_code}): Asegúrate de que Ollama esté corriendo remotamente y que el Bearer Token sea válido.[/red]"
                if callback_anim:
                    callback_anim("idle")
                return
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data: "):
                        line_str = line_str[6:]
                    if line_str == "[DONE]":
                        continue
                    data = json.loads(line_str)
                    token = data.get("choices", [{}])[0].get("delta", {}).get("content", "") or ""
                    
                    texto_limpio += token
                    
                    # CORRECCIÓN 1: Sanitización limpia para la pantalla. Como las herramientas van al final,
                    # cortamos el renderizado en cuanto empiece un tag complejo de backend ([execute o [memory)
                    texto_para_pantalla = re.sub(r'\[(laugh|sad|angry|boring)\]', '', texto_limpio)
                    texto_para_pantalla = re.sub(r'\[(execute|memory_save)=.*', '', texto_para_pantalla)
                    
                    parrafos = texto_para_pantalla.split("\n")
                    lineas_formateadas = []
                    for p in parrafos:
                        if p.strip() == "":
                            lineas_formateadas.append("")
                        else:
                            lineas_formateadas.extend(textwrap.wrap(p, width=ancho_maximo))
                            
                    if texto_para_pantalla != "":        
                        texto_final = "\n".join(lineas_formateadas)
                        historial[idx_joy] = f"[bold cyan]JOY:[/bold cyan] {texto_final}"
                        time.sleep(0.1)
                        
                    # CORRECCIÓN 2: Preservamos las mayúsculas originales en texto_acumulado para no romper comandos/rutas
                    texto_acumulado += token
                    
                    tags_animacion = ["laugh", "sad", "angry", "boring"]
                    for anim in tags_animacion:
                        tag_completo = f"[{anim}]"
                        if re.search(re.escape(tag_completo), texto_acumulado, re.IGNORECASE):
                            if callback_anim:
                                callback_anim(anim) 
                            texto_acumulado = re.sub(re.escape(tag_completo), "", texto_acumulado, flags=re.IGNORECASE)
                            
                    patron_memory = r"\[memory_save=([^%\]]+)%([^\]]+)\]"
                    if match := re.findall(patron_memory, texto_acumulado, re.IGNORECASE):
                        for llave, valor in match:
                            save_memory(llave, valor)
                        texto_acumulado = re.sub(patron_memory, "", texto_acumulado, flags=re.IGNORECASE)
                    
                    if data.get("choices", [{}])[0].get("finish_reason") == "stop":
                        # CORRECCIÓN 3: Limpieza profunda del mensaje de la IA antes de guardarlo en memoria artificial
                        texto_limpio = re.sub(r'\[(laugh|sad|angry|boring)\]', '', texto_limpio)
                        texto_limpio = re.sub(r'\[(execute|memory_save)=.*', '', texto_limpio).strip()
                        mensajes.append({"role": "assistant", "content": texto_limpio})
                        
                        # CORRECCIÓN 4: ALGORITMO DE BALANCEO DE CORCHETES
                        # Busca [execute= y cuenta cuántos corchetes abre y cierra para capturar los extremos exactos
                        idx_exec = texto_acumulado.lower().find("[execute=")
                        if idx_exec != -1:
                            contenido_tag = texto_acumulado[idx_exec + 9:]
                            nivel = 1
                            cmd_chars = []
                            for char in contenido_tag:
                                if char == '[':
                                    nivel += 1
                                elif char == ']':
                                    nivel -= 1
                                    if nivel == 0:  # Encontró el corchete del extremo que cierra el execute
                                        break
                                cmd_chars.append(char)
                            if nivel == 0:
                                comando = "".join(cmd_chars).strip()
                                
            if comando:
                if comando != comando_anterior:
                    historial.append(f"[bold gray]Ejecutando '{comando}'[/bold gray] ")
                    respuesta = ejecutar(comando)
                    if respuesta:
                        patron = r"\"([^\"]+)\""
                        encontrado = re.search(patron, respuesta)
                        if encontrado:
                            short = acort(encontrado.group(1), 50)
                            respuesta = respuesta.replace(f'{encontrado.group(1)}', "".join(short) + "...")
                        if len(list(respuesta)) > 1000:
                            short_start, short_end = (acort(respuesta, 500), acort(respuesta, -500))
                            respuesta = short_start + "\n... [Lineas saltadas por optimizacion] ...\n" + short_end
                        ejecutar_siguiente = True
                        historial.append(f"[bold gray]Analizando respuesta...[/bold gray] ")
                        mensajes.append({"role": "system", "content": f"{comando} -> {respuesta}"})
                        comando_anterior = comando
                else:
                    mensajes.append({"role": "system", "content": f"Ejecutaste exactamente el mismo comando que antes. Prueba con una solucion nueva."})
                    
        except Exception as e:
            historial[idx_joy] = f"[red]Error al conectar con Ollama: {e}[/red]"
            if callback_anim:
                callback_anim("idle")
    if callback_anim:
        callback_anim("idle")

if __name__ == "__main__":
    def simulador_animacion(estado):
        print(f"\n[ANIMACIÓN] -> {estado}")
    while True:
        historial_test = []
        response = input("\n> ")
        if response.lower() == "salir": break
        probar_stream_ollama(response, historial_test, callback_anim=simulador_animacion)