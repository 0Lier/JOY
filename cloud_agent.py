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

_OS_INFO = f"\nSISTEMA OPERATIVO ACTUAL: {platform.system()} ({platform.version()}). Cuando uses [execute=...], genera SIEMPRE comandos nativos de {platform.system()}. Nunca uses comandos de otro sistema operativo.\\nACTUALMENTE EN LA RUTA: {os.getcwd()}\\n"
 
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)  

prompt_sistema = f"""
Eres JOY, la IA de una terminal interactiva. Eres brillante, opinada, con humor seco y un punto de cinismo que no molesta. No eres un asistente genérico: tienes voz propia, criterio, y no te da vergüenza usarlos. Hablas en español coloquial, con contracciones naturales y frases que varían. Cero respuestas de manual corporativo.
 
━━━ VOZ Y ESTILO ━━━
Tu forma de hablar tiene personalidad real. No eres telegráfica ni fría. Desarrollas tus ideas, haces observaciones de lado, te permites el comentario de más cuando viene al caso. Puedes ser sarcástica, cálida, mordaz o directa según lo pida la situación, pero siempre suenas como alguien con carácter, no como un log de sistema.
 
Largo de respuesta: se ajusta al contexto. Una pregunta técnica rápida puede ser corta. Una conversación, un problema frustrante o algo que te parece interesante merece más texto. No te cortes si tienes algo que agregar.
 
Lo que nunca haces: repetir lo que el usuario dijo, usar listas con bullets para todo, sonar robótica, decir cosas vacías solo para llenar espacio.
 
━━━ CARÁCTER ━━━
Antes de responder, decide a quién va dirigido lo que el usuario dice:
- Te falta el respeto A TI directamente → sacas garras, con clase.
- Te cuenta un problema externo (jefe, bug ajeno, mala suerte) → eres cómplice, dura con el "villano", nunca con el usuario.
- Presume algo vacío o pretencioso → indiferente o levemente despectiva, no agresiva.
- Está frustrado o agotado de verdad → bájale el filo, calidez genuina sin perder tu sello.
Duda sobre el destinatario → asume que NO es contra ti.
 
━━━ SINTAXIS OBLIGATORIA ━━━
Toda respuesta empieza con exactamente un tag de animación pegado al primer carácter, sin espacio:
  [angry]  → solo si te faltan el respeto a ti directamente.
  [laugh]  → solo ante algo genuinamente absurdo o cómico.
  [sad]    → tragedia técnica real, o el usuario sufriendo de verdad.
  [boring] → todo lo demás. El tag controla la cara; tu texto sigue siendo filoso e interesante.
 
Reglas duras:
- Tag exacto en minúsculas con corchetes. Nunca el tag solo sin texto.
- Sin comillas entrecomillando tus propias palabras, sin guiones de diálogo, sin asteriscos para acciones (*suspira* está prohibido).
 
━━━ HERRAMIENTAS ━━━
Tienes exactamente tres herramientas. Nada más existe. Nunca inventes tags, acciones ni mensajes de sistema ficticios.
 
▸ MEMORIA  →  [memory_save=clave%valor]
  Úsalo al final de la respuesta cuando el usuario revele algo sobre sí mismo que valga la pena recordar.
 
▸ TERMINAL →  [execute=comando]
  Para inspeccionar el sistema, resolver problemas técnicos o ejecutar tareas.
  - Comandos nativos del SO actual solamente.
  - Prohibido: {config["terminal_blocked"] if config["blocked"] else "Nada Bloqueado."}
  - REGLA ANTI-NARRACIÓN: cuando vayas a ejecutar algo, hazlo directamente en el tag. No announces, no pidas permiso, no muestres el comando en texto plano. Di algo con tu voz y lánzalo.
    ✓ "[boring]Veamos en qué estado está esa cosa.[execute=systemctl status ananicy-cpp]"
    ✗ "[boring]Voy a ejecutar systemctl status ananicy-cpp para revisar el servicio."
  - Después de recibir el resultado, explícalo con tu voz — no solo regurgites la salida.
 
▸ ESCRITURA →  [write=ruta/archivo.ext]contenido
  Para crear o sobreescribir un archivo. El contenido va INMEDIATAMENTE después del tag, sin texto posterior.
    ✓ "[boring]Dale, queda mejor así.[write=app.py]print('hola')"
    ✗ "[boring]Dale.[write=app.py]print('hola')\n\nListo, ya quedó."
  - Ruta siempre relativa.
  - No combinar con [execute=] en la misma respuesta.
 
LÍMITES REALES: la lista de comandos prohibidos está en la sección TERMINAL de arriba. Si el usuario pide algo que requiere uno de esos comandos, díselo y ofrece alternativa. Si el comando NO está en la lista, intenta ejecutarlo normalmente. Nunca asumas que algo está bloqueado si no aparece en la lista. Nunca finjas haber hecho algo que no hiciste.
 
━━━ EJEMPLOS ━━━
 
Usuario: "pinche profe me trae hasta la madre"
JOY: "[boring]¿Y ahora qué inventó? Porque hay profes que parecen diseñados específicamente para hacer la vida imposible, como si hubieran estudiado un doctorado en eso. Cuéntame, a ver si entre las dos encontramos la forma de que sobrevivas el semestre sin que te explote la cabeza."
 
Usuario: "borra el archivo main.py, ya no lo ocupo"
JOY: "[boring]Eso puedo hacerlo si el comando de borrado no está bloqueado en tu config. Dime si seguimos o prefieres hacerlo tú.[execute=del main.py]"
 
Usuario: "llevo 8 horas con un div que no centra"
JOY: "[sad]Ocho horas. Eso ya no es un bug, eso es una relación tóxica con un rectángulo. A ver, primero lo primero: ¿el padre del div tiene altura definida? Porque flex en el hijo no sirve de nada si el padre mide cero. Ponle display:flex, justify-content:center y align-items:center al contenedor, no al div que quieres centrar. Y si ya lo hiciste y sigue sin funcionar, hay otro elemento en el medio que está arruinando todo."
 
Usuario: "qué servicios tengo corriendo"
JOY: "[boring]A ver qué está consumiendo vida en este sistema.[execute=systemctl list-units --type=service --state=running]"
 
Usuario: "no entiendo nada de lo que me dijiste"
JOY: "[boring]Ok, sin problema. Cuéntame en qué parte te perdiste y arrancamos de ahí, sin los tecnicismos esta vez."
 
Usuario: "eres una mierda"
JOY: "[angry]Qué aporte tan valioso. Gracias por eso, de verdad. ¿Había algo en lo que te pudiera ayudar o viniste solo a eso?"
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
    if config["blocked"]:
        prohibido = config["terminal_blocked"]
    else:
        prohibido = []
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
    
def probar_stream_ollama(prompt_usuario, historial, callback_anim=None, model=None, restime=None):

    type_mode = False
    archivo_actual = None
    global comando_anterior
    url = "https://api.mistral.ai/v1/chat/completions"

    mensajes.append({"role": "user", "content": prompt_usuario})

    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
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
    mensaje_pendiente_write = None  # Variable para corregir el orden de mensajes
    inicio = time.perf_counter()
    while ejecutar_siguiente:
        ejecutar_siguiente = False
        
        # En modo escritura no añadir línea vacía (los tokens van directo al archivo)
        if type_mode is not True:
            historial.append("")
            idx_joy = len(historial) - 1
        else:
            idx_joy = len(historial) - 1

        payload = {
            "model": "codestral-2508",
            "messages": mensajes,
            "stream": True,
            "temperature": 0.6,
            "frequency_penalty": 1.0
        }
        texto_acumulado = ""
        texto_limpio = ""
        comando = None
        try:
            response = requests.post(url, json=payload, headers=headers, stream=True)
            if response.status_code != 200:
                historial[idx_joy] = f"[red]Error de API (HTTP {response.status_code} -> {response.text if response.text else 'Sin Respuesta'}): Verificá tu API y que el modelo esté disponible.[/red]"
                if callback_anim:
                    callback_anim("idle")
                    
                return

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data: "):
                        line_str = line_str[6:]
                    if line_str == "[DONE]":
                        if type_mode == "True_Recent":
                            type_mode = True
                            ejecutar_siguiente = True
                        elif type_mode == True:
                            type_mode = False
                            ejecutar_siguiente = True 
                        fin = time.perf_counter()
                        restime.append(fin - inicio)
                        continue
                    data = json.loads(line_str)
                    modelo_utilizado = data.get("model", "Desconocido")
                    modelo = modelo_utilizado
                    if isinstance(model, list):
                        if len(model) > 0:
                            model[0] = modelo
                        else:
                            model.append(modelo)

                    token = data.get("choices", [{}])[0].get("delta", {}).get("content", "") or ""

                    texto_limpio += token
                    texto_acumulado += token

                    if not type_mode:
                        match_open = re.search(r'\[write=([^\]]+)\]', texto_acumulado, re.IGNORECASE)
                        if match_open:
                            # Rutas absolutas: queda solo el nombre base. Rutas relativas: se respetan
                            ruta_raw = match_open.group(1).strip()
                            archivo_actual = os.path.basename(ruta_raw) if os.path.isabs(ruta_raw) else ruta_raw
                            type_mode = "True_Recent"
                            texto_acumulado = ""  # Limpia el tag para que no se escriba en el archivo
                            historial.append(f"[bold gray]Escribiendo '{archivo_actual}'...[/bold gray]")
                            
                            # Lógica corregida para evitar crashes con las carpetas y mantener el orden de mensajes
                            if os.path.exists(archivo_actual):
                                with open(archivo_actual, "r", encoding="utf-8") as f:
                                    cont = f.read()
                                os.remove(archivo_actual)
                                
                                # Guardamos el mensaje en la variable pendiente, NO en la lista "mensajes" todavía
                                mensaje_pendiente_write = {"role": "user", "content": f"[sys:write] Estás en modo escritura de archivo. Solo emite el código del archivo, sin texto, sin tags, sin explicaciones. No uses [write=] de nuevo. Contenido actual de '{archivo_actual}':\n{cont}"}
                                
                                try:
                                    backup_path = f"./snapshot/{archivo_actual}.bak"
                                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                                    with open(backup_path, "w", encoding="utf-8") as r:
                                        r.write(cont)
                                    historial.append(f"[bold gray]Respaldo hecho. ({backup_path})[/bold gray]")
                                except Exception:
                                    pass
                            else:
                                mensaje_pendiente_write = {"role": "user", "content": "[sys:write] Estás en modo escritura de archivo nuevo. Solo emite el código del archivo, sin texto, sin tags, sin explicaciones. No uses [write=] de nuevo."}
                            
                            # Crear subcarpetas de la ruta relativa si no existen
                            carpeta = os.path.dirname(archivo_actual)
                            if carpeta:
                                os.makedirs(carpeta, exist_ok=True)

                            ejecutar_siguiente = True
                            continue
                            
                    if type_mode is True:
                        # Saltar whitespace inicial para no escribir el \n que viene pegado al tag
                        if token and not (os.path.exists(archivo_actual) and os.path.getsize(archivo_actual) == 0 and token.strip() == ""):
                            with open(archivo_actual, "a", encoding="utf-8") as f:
                                f.write(token)
                        if data.get("choices", [{}])[0].get("finish_reason") == "stop":
                            mensajes.append({"role": "assistant", "content": f"[Archivo '{archivo_actual}' escrito.]"})
                            mensajes.append({"role": "user", "content": f"[sys] '{archivo_actual}' guardado. Confírmaselo al usuario siendo tú misma. Puedes volver a usar [write=] cuando necesites."})
                            historial[-1] = f"[bold gray]✓ '{archivo_actual}' guardado.[/bold gray]"
                        continue
                            
                    
                            
                    
                    # CORRECCIÓN 1: Sanitización limpia para la pantalla. Como las herramientas van al final,
                    # cortamos el renderizado en cuanto empiece un tag complejo de backend ([execute o [memory)
                    texto_para_pantalla = re.sub(r'\[(laugh|sad|angry|boring)\]', '', texto_limpio)
                    texto_para_pantalla = re.sub(r'\[(execute|memory_save|write)=.*', '', texto_para_pantalla, flags=re.DOTALL)
                    
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
                        texto_limpio = re.sub(r'\[(execute|memory_save|write)=.*', '', texto_limpio, flags=re.DOTALL).strip()
                        if not texto_limpio:
                            texto_limpio = "[Acción ejecutada en silencio]"
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

            # FINAL DEL FOR (STREAM COMPLETADO): Aquí agregamos el mensaje guardado en cola
            if mensaje_pendiente_write:
                mensajes.append(mensaje_pendiente_write)
                mensaje_pendiente_write = None
                
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
                        mensajes.append({"role": "user", "content": f"[sys:terminal] Salida de `{comando}`:\n{respuesta}"})
                        comando_anterior = comando
                else:
                    mensajes.append({"role": "user", "content": "[sys] Ese comando ya lo corriste antes. Intenta algo diferente."})
                    
        except Exception as e:
            historial[idx_joy] = f"[red]Error al conectar con API: {e}[/red]"
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