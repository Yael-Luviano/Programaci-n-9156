# -*- coding: utf-8 -*-
"""Proyecto 1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_M2HHUB7vZzfHQ7z3NfusvuId42bJDyw
"""

#Alumno: Luviano Real José Yael.  N.Cuenta: 321013725
import pandas as pd
import os

class Project:
    def __init__(self, actividades):
        self.actividades = actividades
        self.agregar_nodos_ficticios()

    def agregar_nodos_ficticios(self):
        inicio_ficticio = '0'
        fin_ficticio = str(max(map(int, self.actividades.keys())) + 1)
        self.actividades[inicio_ficticio] = {'Precedentes': [], 'Duración': 0, 'Siguientes': []}
        for id, actividad in self.actividades.items():
            if not actividad['Precedentes']:
                actividad['Precedentes'].append(inicio_ficticio)
        self.actividades[fin_ficticio] = {'Precedentes': [], 'Duración': 0, 'Siguientes': []}
        for id in self.actividades:
            if all(fin_ficticio not in self.actividades[otro]['Precedentes'] for otro in self.actividades if otro != id):
                self.actividades[id]['Siguientes'].append(fin_ficticio)
        self.actividades[fin_ficticio]['Precedentes'] = [id for id in self.actividades if id != fin_ficticio and not self.actividades[id]['Siguientes']]

    def calcular_tiempos_inicio_mas_temprano(self):
        tiempos_inicio_temprano = {}
        for id in self.actividades:
            tiempos_inicio_temprano[id] = self._calcular_inicio_mas_temprano(id)
        return tiempos_inicio_temprano

    def _calcular_inicio_mas_temprano(self, actividad_id, visitados=None):
        if visitados is None:
            visitados = set()
        if actividad_id in visitados:
            raise ValueError(f"Se detectó una dependencia cíclica en la actividad {actividad_id}!")
        visitados.add(actividad_id)
        dependencias = self.actividades[actividad_id]['Precedentes']
        if not dependencias:
            return 0
        tiempos = []
        for dep in dependencias:
            if dep == '0':  # Nodo ficticio de inicio
                continue
            tiempo_dep = self._calcular_inicio_mas_temprano(dep, visitados.copy())
            tiempo_dep += self.actividades[dep]['Duración']
            tiempos.append(tiempo_dep)
        return max(tiempos)

    def calcular_tiempos_inicio_mas_tardio(self, duracion_proyecto):
        tiempos_inicio_tardio = {id: duracion_proyecto for id in self.actividades}
        for id in sorted(self.actividades, key=lambda x: int(x), reverse=True):  # Orden inverso
            tiempos_inicio_tardio[id] = self._calcular_inicio_mas_tardio(id, tiempos_inicio_tardio)
        return tiempos_inicio_tardio

    def _calcular_inicio_mas_tardio(self, actividad_id, tiempos_inicio_tardio):
        sucesores = self.actividades[actividad_id]['Siguientes']
        if not sucesores:
            return tiempos_inicio_tardio[actividad_id] - self.actividades[actividad_id]['Duración']
        tiempos = []
        for succ in sucesores:
            if succ == str(max(map(int, self.actividades.keys())) + 1):  # Nodo ficticio de fin
                continue
            tiempo_succ = tiempos_inicio_tardio[succ] - self.actividades[succ]['Duración']
            tiempos.append(tiempo_succ)
        return min(tiempos)

    def identificar_ruta_critica(self, tiempos_inicio_temprano, tiempos_inicio_tardio):
        ruta_critica = [id for id in self.actividades if tiempos_inicio_temprano[id] == tiempos_inicio_tardio[id]]
        ruta_critica = [id for id in ruta_critica if id not in ('0', str(max(map(int, self.actividades.keys())) + 1))]
        return ruta_critica

def leer_archivo_excel(ruta_archivo):
    try:
        df = pd.read_excel(ruta_archivo)
        # Verificar que todas las columnas requeridas existen
        for col in ['Actividad', 'Descripción', 'Precedentes', 'Duración']:
            if col not in df.columns:
                raise ValueError(f"La columna '{col}' no se encontró en el archivo Excel.")
        actividades = {}
        for index, row in df.iterrows():
            id = str(int(row['Actividad']))  # Asegurarse de que el ID es un string.
            dependencias = [str(int(dep.strip())) for dep in str(row['Precedentes']).split(',') if pd.notnull(row['Precedentes'])]  # Elimina espacios y convierte a string.
            actividades[id] = {
                'Descripción': row['Descripción'],
                'Duración': row['Duración'],
                'Precedentes': dependencias,
                'Siguientes': []
            }
        return actividades
    except ValueError as e:
        print(f"Error en el archivo Excel: {e}")
        raise

def escribir_informe_proyecto(project, tiempos_inicio_temprano, tiempos_inicio_tardio, ruta_critica, ruta_archivo):
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        for id in sorted(project.actividades, key=lambda x: int(x)):  # Ordena las actividades por su ID numérico.
            if id in ['0', str(max(map(int, project.actividades.keys())) + 1)]:
                continue  # Omitir los nodos ficticios en el informe.
            archivo.write(f"Actividad {id}: {project.actividades[id]['Descripción']}\n")
            archivo.write(f"Duración: {project.actividades[id]['Duración']} minutos\n")
            archivo.write(f"Tiempo de Inicio Más Temprano: {tiempos_inicio_temprano[id]} minutos\n")
            archivo.write(f"Tiempo de Inicio Más Tardío: {tiempos_inicio_tardio[id]} minutos\n")
            archivo.write(f"Precedentes: {', '.join(project.actividades[id]['Precedentes'])}\n\n")
        archivo.write(f"Ruta Crítica: {' -> '.join(ruta_critica)}\n")
        duracion_proyecto = max(tiempos_inicio_temprano.values()) + max(project.actividades[id]['Duración'] for id in ruta_critica)
        archivo.write(f"Duración Total del Proyecto: {duracion_proyecto} minutos\n")

def obtener_ruta_archivo_excel():
    ruta_archivo = input("Ingrese la ruta al archivo Excel con las actividades del proyecto: ")
    if not os.path.isfile(ruta_archivo) or not ruta_archivo.endswith(('.xlsx', '.xls')):
        raise ValueError("El archivo proporcionado no es un archivo Excel válido.")
    return ruta_archivo

def main():
    try:
        ruta_archivo_excel = obtener_ruta_archivo_excel()
        actividades = leer_archivo_excel(ruta_archivo_excel)
        proyecto = Project(actividades)
        tiempos_inicio_temprano = proyecto.calcular_tiempos_inicio_mas_temprano()
        duracion_proyecto = max(tiempos_inicio_temprano.values()) + max(actividad['Duración'] for actividad in proyecto.actividades.values())
        tiempos_inicio_tardio = proyecto.calcular_tiempos_inicio_mas_tardio(duracion_proyecto)
        ruta_critica = proyecto.identificar_ruta_critica(tiempos_inicio_temprano, tiempos_inicio_tardio)
        ruta_informe = 'informe_proyecto.txt'
        escribir_informe_proyecto(proyecto, tiempos_inicio_temprano, tiempos_inicio_tardio, ruta_critica, ruta_informe)
        print(f"El informe del proyecto se ha escrito en {ruta_informe}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()