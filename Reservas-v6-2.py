import os
import json
from datetime import datetime, timedelta

# Configuración
SALAS = ["Sala Piso 4", "Sala Piso 5"]
HORAS = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
DIAS_SEMANA = ["Lu", "Ma", "Mi", "Ju", "Vi"]
ARCHIVO_DATOS = "reservas6.json"

# Caracteres ASCII para la interfaz
BORDE_H = "═"
BORDE_V = "║"
ESQUINA_TL = "╔"
ESQUINA_TR = "╗"
ESQUINA_BL = "╚"
ESQUINA_BR = "╝"
LINEA_H = "─"
LINEA_V = "│"
CRUZ = "┼"

# Colores ANSI
COLOR_TITULO = "\033[1;34m"
COLOR_MENU = "\033[1;92m"
COLOR_RESALTADO = "\033[0;93m"
COLOR_ERROR = "\033[1;31m"
COLOR_EXITO = "\033[1;32m"
COLOR_RESET = "\033[0m"

# Cargar datos
def cargar_datos():
    try:  # Bloque try correctamente colocado
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except (json.JSONDecodeError, AttributeError):  # Coincide con el try
        print(f"{COLOR_ERROR}Error leyendo el archivo. Se creará uno nuevo.{COLOR_RESET}")
    return {sala: {} for sala in SALAS}  # Estructura por defecto
    
# Guardar datos
def guardar_datos(reservas):
    if isinstance(reservas, dict):  # Solo guardar si es diccionario
        with open(ARCHIVO_DATOS, 'w') as f:
            json.dump(reservas, f, indent=2)  # indent=2 para formato legible
            
# Limpiar pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Dibujar marco
def dibujar_marco(ancho=80):
    print(f"{COLOR_TITULO}{ESQUINA_TL}{BORDE_H*(ancho-2)}{ESQUINA_TR}{COLOR_RESET}")

# Menú principal
def mostrar_menu():
    limpiar_pantalla()
    dibujar_marco()
    print(f"{COLOR_TITULO}{BORDE_V}{COLOR_MENU}{' SISTEMA DE RESERVAS '.center(78)}{COLOR_TITULO}{BORDE_V}{COLOR_RESET}")
    dibujar_marco()
    print(f"{COLOR_TITULO}{BORDE_V} {COLOR_MENU}[S]ala  [R]eservar  [U]suarios  [M]odificar  [E]liminar  [V]er  [Q]uit {COLOR_TITULO}{BORDE_V:>7}{COLOR_RESET}")
    dibujar_marco()

# Convertir día abreviado a fecha
def dia_a_fecha(dia_abrev, semana=0):
    dias = {"Lu": 0, "Ma": 1, "Mi": 2, "Ju": 3, "Vi": 4}
    hoy = datetime.now()
    
     # Calcula el próximo día de la semana (ej: si hoy es jueves y piden "Lu", será el lunes de la semana siguiente)
    dia_num = dias[dia_abrev]
    diferencia = (dia_num - hoy.weekday() + 7) % 7
    fecha = hoy + timedelta(days=diferencia + semana * 7)
    
    # Si la fecha calculada es anterior a hoy, sumamos 1 semana (por seguridad)
    if fecha.date() < hoy.date():
        fecha += timedelta(days=7)
    
    return fecha.strftime("%Y-%m-%d")

def mostrar_horarios(sala, reservas, semana=0):
    print(f"\n{COLOR_RESALTADO}{sala.center(30)}{COLOR_RESET}")
    
    # Cabecera de la tabla
    print(f"{COLOR_TITULO}┌────────┬───┬───┬───┬───┬───┐{COLOR_RESET}")
    print(f"{COLOR_TITULO}│ Hora   │{DIAS_SEMANA[0]} │{DIAS_SEMANA[1]} │{DIAS_SEMANA[2]} │{DIAS_SEMANA[3]} │{DIAS_SEMANA[4]} │{COLOR_RESET}")
    print(f"{COLOR_TITULO}├────────┼───┼───┼───┼───┼───┤{COLOR_RESET}")  # Corregido: eliminé el "┼─────" extra
    
    for hora in HORAS:  # Ahora está correctamente indentado
        fila = f"{COLOR_TITULO}│ {COLOR_RESET}{hora.ljust(6)}{COLOR_TITULO} │{COLOR_RESET}"
        for dia in DIAS_SEMANA:
            fecha = dia_a_fecha(dia)
            if reservas.get(sala, {}).get(fecha, {}).get(hora):
                usuario = reservas[sala][fecha][hora]
                fila += f" {COLOR_ERROR}{usuario[:1]}{COLOR_RESET} {COLOR_TITULO}│{COLOR_RESET}"
            else:
                fila += f"   {COLOR_TITULO}│{COLOR_RESET}"
        print(fila)
    print(f"{COLOR_TITULO}└────────┴───┴───┴───┴───┴───┘{COLOR_RESET}")

# Módulo de reserva
def reservar_horario(reservas, sala_actual):
    #sala = seleccionar_sala()
    #if not sala:
    #    return
    
    #mostrar_horarios(sala_actual, reservas)
    
    print("\nSeleccione el día y hora para reservar")
    dia = seleccionar_dia()
    if not dia:
        return
    fecha = dia_a_fecha(dia)
    horas_ocupadas = set(reservas.get(sala_actual, {}).get(fecha, {}).keys())  # Obtiene las horas ocupadas
    
    hora = seleccionar_hora(horas_ocupadas)
    if not hora:
        return
    
    usuario = input("Ingrese su nombre: ").strip()
    if not usuario:
        print(f"{COLOR_ERROR}Debe ingresar un nombre.{COLOR_RESET}")
        return
        
    if hora in horas_ocupadas:  # Validación adicional por seguridad
        print(f"{COLOR_ERROR}¡Este horario ya está reservado!{COLOR_RESET}")
        return

    if reservas[sala_actual].get(fecha, {}).get(hora):
        print(f"{COLOR_ERROR}¡Este horario ya está reservado!{COLOR_RESET}")
        return
    
    reservas[sala_actual].setdefault(fecha, {})[hora] = usuario
    guardar_datos(reservas)
    print(f"{COLOR_EXITO}¡Reserva realizada con éxito!{COLOR_RESET}")

# Módulo de visualización por usuario
def mostrar_por_usuario(reservas):
    usuarios = {}
    for sala in SALAS:
        for fecha in reservas[sala]:
            for hora, usuario in reservas[sala][fecha].items():
                usuarios.setdefault(usuario, []).append((sala, fecha, hora))
    
    if not usuarios:
        print(f"{COLOR_ERROR}No hay reservas registradas.{COLOR_RESET}")
        return
    
    print(f"\n{COLOR_RESALTADO}{' RESERVAS POR USUARIO '.center(30)}{COLOR_RESET}")
    for usuario, reservas_usuario in usuarios.items():
        print(f"\n{COLOR_MENU}Usuario: {usuario}{COLOR_RESET}")
        for sala, fecha, hora in reservas_usuario:
            fecha_formato = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
            dia_semana = DIAS_SEMANA[datetime.strptime(fecha, "%Y-%m-%d").weekday()]
            print(f" - {sala}: {dia_semana} {fecha_formato} a las {hora}")

# Módulo de modificación
def modificar_reserva(reservas):
   # usuario = input("Ingrese su nombre: ").strip()
   # Paso 1: Seleccionar usuario
    usuario = seleccionar_usuario(reservas)  # <- Usa la nueva función
    if not usuario:
        print(f"{COLOR_ERROR}Debe ingresar un nombre.{COLOR_RESET}")
        return
    
    reservas_usuario = []
    for sala in SALAS:
        for fecha in reservas[sala]:
            for hora, usuario_reserva in reservas[sala][fecha].items():
                if usuario_reserva == usuario:
                    reservas_usuario.append((sala, fecha, hora))
    
    if not reservas_usuario:
        print(f"{COLOR_ERROR}No se encontraron reservas para este usuario.{COLOR_RESET}")
        return
    
        print(f"\n{COLOR_RESALTADO}{' RESERVAS DE ' + usuario.upper() + ' '.center(30)}{COLOR_RESET}")
  
    for i, (sala, fecha, hora) in enumerate(reservas_usuario, 1):
        fecha_formato = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
        dia_semana = DIAS_SEMANA[datetime.strptime(fecha, "%Y-%m-%d").weekday()]
        print(f"{i}. {sala}: {dia_semana} {fecha_formato} a las {hora}")
    
    try:
        seleccion = int(input("\nSeleccione la reserva a modificar (0 para cancelar): "))
        if seleccion == 0:
            return
        # Cambio clave aquí - usamos hora_antigua para ser consistentes con el resto
        sala, fecha, hora_antigua = reservas_usuario[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Selección inválida.{COLOR_RESET}")
        return
        # Obtener horas ocupadas en la misma sala y fecha (EXCLUYENDO la hora actual)
    horas_ocupadas = {
        h for h in reservas[sala][fecha].keys() 
        if h != hora_antigua  # Excluimos la hora que se está modificando
    }
    nueva_hora = seleccionar_hora(horas_ocupadas)
    if not nueva_hora:
        return
    
    # Verificar si la nueva hora está disponible
    if nueva_hora in reservas[sala][fecha]:
        print(f"{COLOR_ERROR}La hora {nueva_hora} ya está ocupada.{COLOR_RESET}")
        return
    
    # Realizar la modificación
    try:
        # Eliminar la reserva antigua
        del reservas[sala][fecha][hora_antigua]
        
        # Crear la nueva reserva
        reservas[sala][fecha][nueva_hora] = usuario
        print(f"{COLOR_EXITO}Reserva modificada exitosamente.{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_ERROR}Error al modificar la reserva: {e}{COLOR_RESET}") 

# Módulo de eliminación
def eliminar_reserva(reservas):
    # Paso 1: Seleccionar usuario
    usuario = seleccionar_usuario(reservas)  # <- Usa la nueva función
    if not usuario:
        return
    
    # Paso 2: Mostrar reservas del usuario seleccionado
    reservas_usuario = []
    for sala in SALAS:
        for fecha in reservas[sala]:
            for hora, usuario_reserva in reservas[sala][fecha].items():
                if usuario_reserva == usuario:
                    reservas_usuario.append((sala, fecha, hora))
    
    #print(f"\n{COLOR_RESALTADO}{' RESERVAS DE ' + usuario.upper() + ' '.center(30)}{COLOR_RESET}")
    #for i, (sala, fecha, hora) in enumerate(reservas_usuario, 1):
    #    fecha_formato = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
    #    dia_semana = DIAS_SEMANA[datetime.strptime(fecha, "%Y-%m-%d").weekday()]
    #    print(f"{i}. {sala}: {dia_semana} {fecha_formato} a las {hora}")
    
    if not reservas_usuario:
        print(f"{COLOR_ERROR}No se encontraron reservas para este usuario.{COLOR_RESET}")
        return
    
    print(f"\n{COLOR_RESALTADO}{' RESERVAS DE ' + usuario.upper() + ' '.center(30)}{COLOR_RESET}")
    for i, (sala, fecha, hora) in enumerate(reservas_usuario, 1):
        fecha_formato = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
        dia_semana = DIAS_SEMANA[datetime.strptime(fecha, "%Y-%m-%d").weekday()]
        print(f"{i}. {sala}: {dia_semana} {fecha_formato} a las {hora}")
    
    try:
        seleccion = int(input("\nSeleccione la reserva a eliminar (0 para cancelar): "))
        if seleccion == 0:
            return
        sala, fecha, hora = reservas_usuario[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Selección inválida.{COLOR_RESET}")
        return
    
    # Confirmar eliminación
    confirmacion = input(f"¿Eliminar esta reserva? (S/N): ").lower()
    if confirmacion == 's':
        del reservas[sala][fecha][hora]
        # Eliminar fecha si no hay más reservas
        if not reservas[sala][fecha]:
            del reservas[sala][fecha]
        guardar_datos(reservas)
        print(f"{COLOR_EXITO}¡Reserva eliminada con éxito!{COLOR_RESET}")
    else:
        print("Operación cancelada.")

# Módulo de resumen
def mostrar_resumen(reservas):
    print(f"\n{COLOR_RESALTADO}{' RESUMEN DE RESERVAS '.center(30)}{COLOR_RESET}")
    
    for sala in SALAS:
        print(f"\n{COLOR_MENU}{sala.center(0)}{COLOR_RESET}")
        
        # Cabecera de la tabla
        print(f"{COLOR_TITULO}┌───────┬───┬───┬───┬───┬───┐{COLOR_RESET}")
        print(f"{COLOR_TITULO}│ Hora  │{DIAS_SEMANA[0]} │{DIAS_SEMANA[1]} │{DIAS_SEMANA[2]} │{DIAS_SEMANA[3]} │{DIAS_SEMANA[4]} │{COLOR_RESET}")
        print(f"{COLOR_TITULO}├───────┼───┼───┼───┼───┼───┤{COLOR_RESET}")
        
        for hora in HORAS:
            fila = f"{COLOR_TITULO}│{COLOR_RESET}{hora.ljust(6)}{COLOR_TITULO} │{COLOR_RESET}"
            for dia in DIAS_SEMANA:
                fecha = dia_a_fecha(dia)
                if reservas.get(sala, {}).get(fecha, {}).get(hora):
                    usuario = reservas[sala][fecha][hora]
                    fila += f" {COLOR_ERROR}{usuario[:1]}{COLOR_RESET} {COLOR_TITULO}│{COLOR_RESET}"
                else:
                    fila += f"   {COLOR_TITULO}│{COLOR_RESET}"
            print(fila)
        print(f"{COLOR_TITULO}└───────┴───┴───┴───┴───┴───┘{COLOR_RESET}")

# Funciones auxiliares
def seleccionar_usuario(reservas):
    # Obtener todos los usuarios únicos con reservas
    usuarios = set()
    for sala in SALAS:
        for fecha in reservas[sala]:
            for usuario in reservas[sala][fecha].values():
                usuarios.add(usuario)
    
    if not usuarios:
        print(f"{COLOR_ERROR}No hay reservas registradas.{COLOR_RESET}")
        return None
    
    # Mostrar lista numerada
    print(f"\n{COLOR_RESALTADO}{' USUARIOS CON RESERVAS '.center(30)}{COLOR_RESET}")
    for i, usuario in enumerate(sorted(usuarios), 1):
        print(f"{i}. {usuario}")
    
    # Permitir selección
    try:
        seleccion = input("\nSeleccione un usuario (número) o [X] para cancelar: ").strip().lower()
        if seleccion == 'x':
            return None
        seleccion = int(seleccion)
        return sorted(usuarios)[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Opción no válida.{COLOR_RESET}")
        return None
        
def seleccionar_sala():
      # Obtener todos los usuarios únicos con reservas
    usuarios = set()
    for sala in SALAS:
        for fecha in reservas[sala]:
            for usuario in reservas[sala][fecha].values():
                usuarios.add(usuario)
    
    if not usuarios:
        print(f"{COLOR_ERROR}No hay reservas registradas.{COLOR_RESET}")
        return None
    
    # Mostrar lista numerada
    print(f"\n{COLOR_RESALTADO}{' USUARIOS CON RESERVAS '.center(30)}{COLOR_RESET}")
    for i, usuario in enumerate(sorted(usuarios), 1):
        print(f"{i}. {usuario}")
    
    # Permitir selección
    try:
        seleccion = input("\nSeleccione un usuario (número) o [X] para cancelar: ").strip().lower()
        if seleccion == 'x':
            return None
        seleccion = int(seleccion)
        return sorted(usuarios)[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Opción no válida.{COLOR_RESET}")
        return None
def seleccionar_dia():
    print("\nDías disponibles:")
    for i, dia in enumerate(DIAS_SEMANA, 1):
        print(f"{i}. {dia}")
    try:
        seleccion = int(input("Opción (0 para cancelar): "))
        if seleccion == 0:
            return None
        return DIAS_SEMANA[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Opción inválida.{COLOR_RESET}")
        return None

def seleccionar_hora(horas_ocupadas=None):
    if horas_ocupadas is None:
        horas_ocupadas = set()  # Si no se pasan horas ocupadas, asumimos que ninguna está reservada
    
    horas_disponibles = [hora for hora in HORAS if hora not in horas_ocupadas]
    
    if not horas_disponibles:
        print(f"{COLOR_ERROR}No hay horas disponibles.{COLOR_RESET}")
        return None
        
    print("\nHoras disponibles:")
    for i, hora in enumerate(horas_disponibles, 1):
        print(f"{i}. {hora}")
    try:
        seleccion = int(input("Opción (0 para cancelar): "))
        if seleccion == 0:
            return None
        return horas_disponibles[seleccion-1]
    except (ValueError, IndexError):
        print(f"{COLOR_ERROR}Opción inválida.{COLOR_RESET}")
        return None

# Función principal
def main():
    reservas = cargar_datos()
    if not isinstance(reservas, dict):  # Si no es diccionario, reinicializar
        reservas = {sala: {} for sala in SALAS}
    sala_actual = SALAS[1]
    semana_actual = 0
    
    while True:
        mostrar_menu()
        mostrar_horarios(sala_actual, reservas, semana_actual)
        
        opcion = input("\nOpción (S/R/U/M/E/V/Q): ").lower()
        
        if opcion == 'q':
            print("¡Hasta luego!")
            break
        elif opcion == 's':
        # Cambia a la siguiente sala (alterna entre las disponibles)
            indice_actual = SALAS.index(sala_actual)
            nuevo_indice = (indice_actual + 1) % len(SALAS)  # Circular: si es la última, vuelve a la primera
            sala_actual = SALAS[nuevo_indice]
        elif opcion == 'r':
            reservar_horario(reservas, sala_actual)
        elif opcion == 'u':
            mostrar_por_usuario(reservas)
            input("\nPresione Enter para continuar...")
        elif opcion == 'm':
            modificar_reserva(reservas)
            input("\nPresione Enter para continuar...")
        elif opcion == 'e':
            eliminar_reserva(reservas)
            input("\nPresione Enter para continuar...")
        elif opcion == 'v':
            mostrar_resumen(reservas)
            input("\nPresione Enter para continuar...")
        else:
            print(f"{COLOR_ERROR}Opción no válida.{COLOR_RESET}")
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()

