import os, random, time

def obtener_animo():
    animo = {}
    for dir, path, files in os.walk("./model"):
        for file in files:
            sin_ext = file.split(".")
            name = sin_ext[0].split("_")
            if name[0] in animo:
                animo[name[0]] = animo[name[0]] + 1
            else:
                animo[name[0]] = 1
    return animo 

def animate(mood, count):
    frames = []
    for i in range(count):
        with open(f"./model/{mood}_{i+1}.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
            frames.append(contenido)
    return frames