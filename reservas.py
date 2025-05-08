#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, time, timedelta
from colorama import Fore, Back, Style, init

# Inicializar colorama
init(autoreset=True)

# Constantes
ARCHIVO_RESERVAS = "reservas.json"
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
HORA_INICIO = time(8, 0)
HORA_FIN = time(16, 0)

# Diccionario de salas
SALAS = {
    "5": "Sala Piso 5 - Vista Panorámica",
    "4": "Sala Piso 4 - Sala de Conferencias"
}

class Reserva:
    def __init__(self, sala, persona, dia, hora_inicio, duracion):
        self.sala = sala
        self.persona = persona
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.duracion = duracion

def cargar_reservas():
    if os.path.exists(ARCHIVO_RESERVAS):
        with open(ARCHIVO_RESERVAS, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return [Reserva(**reserva) for reserva in datos]
    return []

def guardar_reservas(reservas):
    with open(ARCHIVO_RESERVAS, 'w', encoding='utf-8') as f:
        datos = [vars(reserva) for reserva in reservas]
        json.dump(datos, f, ensure_ascii=False, indent=2)

def mostrar_menu_principal():
    print(Fore.YELLOW + "\n" + "="*50)
    print(Fore.CYAN + " SISTEMA DE RESERVA DE SALAS".center(50))
    print(Fore.YELLOW + "="*50)
    print(Fore.GREEN + "\n1. Reservar sala")
    print(Fore.GREEN + "2. Ver disponibilidad")
    print(Fore.GREEN + "3. Ver todas las reservas")
    print(Fore.BLUE + "4. Modificar reserva")
    print(Fore.RED + "5. Cancelar reserva")
    print(Fore.MAGENTA + "6. Salir")
    print(Fore.YELLOW + "="*50)

def mostrar_dias_disponibles():
    print(Fore.CYAN + "\nDías disponibles para reserva:")
    for i, dia in enumerate(DIAS_SEMANA, 1):
        print(Fore.GREEN + "{0}. {1}".format(i, dia))

def mostrar_salas():
    print(Fore.CYAN + "\nSalas disponibles:")
    for clave, valor in SALAS.items():
        print(Fore.GREEN + "{0}. {1}".format(clave, valor))

def validar_hora(hora_str):
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
        if hora < HORA_INICIO or hora >= HORA_FIN:
            print(Fore.RED + "La hora debe estar entre {0} y {1}".format(
                HORA_INICIO.strftime("%H:%M"), HORA_FIN.strftime("%H:%M")))
            return None
        return hora
    except ValueError:
        print(Fore.RED + "Formato de hora inválido. Use HH:MM (ej. 09:30)")
        return None

def validar_duracion(duracion_str):
    try:
        duracion = int(duracion_str)
        if duracion < 1:
            print(Fore.RED + "La duración mínima es 1 hora")
            return None
        return duracion
    except ValueError:
        print(Fore.RED + "Duración inválida. Debe ser un número entero de horas")
        return None

def obtener_horas_reservadas(reservas, sala, dia):
    horas_reservadas = []
    for reserva in reservas:
        if reserva.sala == sala and reserva.dia == dia:
            hora_fin = (datetime.combine(datetime.today(), 
                       datetime.strptime(reserva.hora_inicio, "%H:%M").time()) + 
                       timedelta(hours=reserva.duracion)).time()
            horas_reservadas.append((datetime.strptime(reserva.hora_inicio, "%H:%M").time(), hora_fin))
    return horas_reservadas

def mostrar_disponibilidad(sala, dia, reservas):
    horas_reservadas = obtener_horas_reservadas(reservas, sala, dia)
    horas_reservadas.sort()
    
    print(Fore.CYAN + "\nDisponibilidad para {0} el {1}:".format(SALAS[sala], dia))
    print(Fore.YELLOW + "-"*50)
    
    hora_actual = HORA_INICIO
    while hora_actual < HORA_FIN:
        disponible = True
        for inicio, fin in horas_reservadas:
            if inicio <= hora_actual < fin:
                disponible = False
                break
        
        if disponible:
            print(Fore.GREEN + "{0} - Disponible".format(hora_actual.strftime("%H:%M")))
        else:
            print(Fore.RED + "{0} - Reservado".format(hora_actual.strftime("%H:%M")))
        
        hora_actual = (datetime.combine(datetime.today(), hora_actual) + 
                      timedelta(minutes=30)).time()

def reservar_sala(reservas):
    mostrar_salas()
    sala = input(Fore.CYAN + "\nIngrese el número de la sala (4 o 5): ")
    if sala not in SALAS:
        print(Fore.RED + "Sala inválida")
        return
    
    mostrar_dias_disponibles()
    try:
        dia_idx = int(input(Fore.CYAN + "\nSeleccione el día (1-5): ")) - 1
        if dia_idx < 0 or dia_idx >= len(DIAS_SEMANA):
            raise ValueError
        dia = DIAS_SEMANA[dia_idx]
    except ValueError:
        print(Fore.RED + "Día inválido")
        return
    
    mostrar_disponibilidad(sala, dia, reservas)
    
    hora = None
    while hora is None:
        hora_str = input(Fore.CYAN + "\nIngrese la hora de inicio (HH:MM): ")
        hora = validar_hora(hora_str)
    
    duracion = None
    while duracion is None:
        duracion_str = input(Fore.CYAN + "Ingrese la duración en horas: ")
        duracion = validar_duracion(duracion_str)
    
    # Verificar disponibilidad
    horas_reservadas = obtener_horas_reservadas(reservas, sala, dia)
    hora_fin_reserva = (datetime.combine(datetime.today(), hora) + 
                       timedelta(hours=duracion)).time()
    
    conflicto = False
    for inicio, fin in horas_reservadas:
        if (hora >= inicio and hora < fin) or (hora_fin_reserva > inicio and hora_fin_reserva <= fin):
            conflicto = True
            break
    
    if conflicto:
        print(Fore.RED + "\n¡Conflicto de horario! Esa hora ya está reservada.")
        return
    
    persona = input(Fore.CYAN + "Ingrese su nombre: ").strip()
    
    nueva_reserva = Reserva(sala, persona, dia, hora.strftime("%H:%M"), duracion)
    reservas.append(nueva_reserva)
    guardar_reservas(reservas)
    
    print(Fore.GREEN + "\n¡Reserva exitosa!")
    print(Fore.YELLOW + "-"*50)
    print(Fore.CYAN + "Sala: {0}".format(SALAS[sala]))
    print(Fore.CYAN + "Día: {0}".format(dia))
    print(Fore.CYAN + "Hora: {0} por {1} horas".format(hora.strftime("%H:%M"), duracion))
    print(Fore.YELLOW + "-"*50)

def ver_disponibilidad(reservas):
    mostrar_salas()
    sala = input(Fore.CYAN + "\nIngrese el número de la sala (4 o 5): ")
    if sala not in SALAS:
        print(Fore.RED + "Sala inválida")
        return
    
    mostrar_dias_disponibles()
    try:
        dia_idx = int(input(Fore.CYAN + "\nSeleccione el día (1-5): ")) - 1
        if dia_idx < 0 or dia_idx >= len(DIAS_SEMANA):
            raise ValueError
        dia = DIAS_SEMANA[dia_idx]
    except ValueError:
        print(Fore.RED + "Día inválido")
        return
    
    mostrar_disponibilidad(sala, dia, reservas)

def ver_todas_reservas(reservas, mostrar_indices=False):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.YELLOW + " TODAS LAS RESERVAS ".center(50))
    print(Fore.CYAN + "="*50)
    
    if not reservas:
        print(Fore.MAGENTA + "\nNo hay reservas registradas")
        return
    
    for idx, reserva in enumerate(reservas, 1):
        print(Fore.YELLOW + "-"*50)
        if mostrar_indices:
            print(Fore.CYAN + "ID: {0}".format(idx))
        print(Fore.GREEN + "Sala: {0}".format(SALAS[reserva.sala]))
        print(Fore.GREEN + "Reservado por: {0}".format(reserva.persona))
        print(Fore.GREEN + "Día: {0}".format(reserva.dia))
        print(Fore.GREEN + "Hora: {0} por {1} horas".format(reserva.hora_inicio, reserva.duracion))
    
    print(Fore.YELLOW + "-"*50)

def seleccionar_reserva(reservas):
    ver_todas_reservas(reservas, mostrar_indices=True)
    try:
        idx = int(input(Fore.CYAN + "\nSeleccione el ID de la reserva: ")) - 1
        if idx < 0 or idx >= len(reservas):
            raise ValueError
        return idx
    except ValueError:
        print(Fore.RED + "\nID inválido")
        return None

def modificar_reserva(reservas):
    if not reservas:
        print(Fore.RED + "\nNo hay reservas para modificar")
        return
    
    idx = seleccionar_reserva(reservas)
    if idx is None:
        return
    
    reserva_original = reservas[idx]
    reserva_modificada = Reserva(
        reserva_original.sala,
        reserva_original.persona,
        reserva_original.dia,
        reserva_original.hora_inicio,
        reserva_original.duracion
    )
    
    print(Fore.CYAN + "\nReserva seleccionada:")
    print(Fore.YELLOW + "-"*50)
    print(Fore.GREEN + "1. Sala: {0}".format(SALAS[reserva_modificada.sala]))
    print(Fore.GREEN + "2. Persona: {0}".format(reserva_modificada.persona))
    print(Fore.GREEN + "3. Día: {0}".format(reserva_modificada.dia))
    print(Fore.GREEN + "4. Hora: {0}".format(reserva_modificada.hora_inicio))
    print(Fore.GREEN + "5. Duración: {0} horas".format(reserva_modificada.duracion))
    print(Fore.YELLOW + "-"*50)
    
    try:
        opcion = int(input(Fore.CYAN + "\n¿Qué desea modificar? (1-5): "))
        if opcion < 1 or opcion > 5:
            raise ValueError
    except ValueError:
        print(Fore.RED + "\nOpción inválida")
        return
    
    if opcion == 1:
        mostrar_salas()
        nueva_sala = input(Fore.CYAN + "\nIngrese el nuevo número de sala (4 o 5): ")
        if nueva_sala in SALAS:
            reserva_modificada.sala = nueva_sala
        else:
            print(Fore.RED + "\nSala inválida")
            return
    elif opcion == 2:
        nueva_persona = input(Fore.CYAN + "\nIngrese el nuevo nombre: ").strip()
        reserva_modificada.persona = nueva_persona
    elif opcion == 3:
        mostrar_dias_disponibles()
        try:
            dia_idx = int(input(Fore.CYAN + "\nSeleccione el nuevo día (1-5): ")) - 1
            if dia_idx < 0 or dia_idx >= len(DIAS_SEMANA):
                raise ValueError
            reserva_modificada.dia = DIAS_SEMANA[dia_idx]
        except ValueError:
            print(Fore.RED + "\nDía inválido")
            return
    elif opcion == 4:
        nueva_hora = None
        while nueva_hora is None:
            hora_str = input(Fore.CYAN + "\nIngrese la nueva hora de inicio (HH:MM): ")
            nueva_hora = validar_hora(hora_str)
        reserva_modificada.hora_inicio = nueva_hora.strftime("%H:%M")
    elif opcion == 5:
        nueva_duracion = None
        while nueva_duracion is None:
            duracion_str = input(Fore.CYAN + "\nIngrese la nueva duración en horas: ")
            nueva_duracion = validar_duracion(duracion_str)
        reserva_modificada.duracion = nueva_duracion
    
    # Verificar disponibilidad excluyendo la reserva original
    horas_reservadas = []
    for i, reserva in enumerate(reservas):
        if i != idx and reserva.sala == reserva_modificada.sala and reserva.dia == reserva_modificada.dia:
            hora_inicio = datetime.strptime(reserva.hora_inicio, "%H:%M").time()
            hora_fin = (datetime.combine(datetime.today(), hora_inicio) + 
                       timedelta(hours=reserva.duracion)).time()
            horas_reservadas.append((hora_inicio, hora_fin))
    
    hora_inicio_nueva = datetime.strptime(reserva_modificada.hora_inicio, "%H:%M").time()
    hora_fin_nueva = (datetime.combine(datetime.today(), hora_inicio_nueva) + 
                     timedelta(hours=reserva_modificada.duracion)).time()
    
    conflicto = False
    for inicio, fin in horas_reservadas:
        if (hora_inicio_nueva < fin and hora_fin_nueva > inicio):
            conflicto = True
            break
    
    if conflicto:
        print(Fore.RED + "\n¡Conflicto de horario! La modificación no es posible.")
        print(Fore.RED + "Existe una reserva entre {0} y {1}".format(
            inicio.strftime("%H:%M"), fin.strftime("%H:%M")))
        return
    
    # Actualizar la reserva original con los cambios
    reservas[idx] = reserva_modificada
    guardar_reservas(reservas)
    print(Fore.GREEN + "\n¡Reserva modificada exitosamente!")

def cancelar_reserva(reservas):
    if not reservas:
        print(Fore.RED + "\nNo hay reservas para cancelar")
        return
    
    idx = seleccionar_reserva(reservas)
    if idx is None:
        return
    
    reserva = reservas[idx]
    print(Fore.CYAN + "\nReserva seleccionada para cancelar:")
    print(Fore.YELLOW + "-"*50)
    print(Fore.GREEN + "Sala: {0}".format(SALAS[reserva.sala]))
    print(Fore.GREEN + "Persona: {0}".format(reserva.persona))
    print(Fore.GREEN + "Día: {0}".format(reserva.dia))
    print(Fore.GREEN + "Hora: {0} por {1} horas".format(reserva.hora_inicio, reserva.duracion))
    print(Fore.YELLOW + "-"*50)
    
    confirmacion = input(Fore.RED + "\n¿Está seguro que desea cancelar esta reserva? (s/n): ").lower()
    if confirmacion == 's':
        del reservas[idx]
        guardar_reservas(reservas)
        print(Fore.GREEN + "\n¡Reserva cancelada exitosamente!")
    else:
        print(Fore.BLUE + "\nCancelación abortada")

def main():
    reservas = cargar_reservas()
    
    while True:
        mostrar_menu_principal()
        opcion = input(Fore.CYAN + "\nSeleccione una opción (1-6): ")
        
        if opcion == "1":
            reservar_sala(reservas)
        elif opcion == "2":
            ver_disponibilidad(reservas)
        elif opcion == "3":
            ver_todas_reservas(reservas)
        elif opcion == "4":
            modificar_reserva(reservas)
        elif opcion == "5":
            cancelar_reserva(reservas)
        elif opcion == "6":
            print(Fore.MAGENTA + "\n¡Hasta pronto!")
            break
        else:
            print(Fore.RED + "\nOpción inválida. Por favor seleccione 1-6")

if __name__ == "__main__":
    main()
