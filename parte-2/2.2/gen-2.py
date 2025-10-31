#!env python3
import argparse
import os
import subprocess
import sys
import re


def parse_input(input_path):
    """Lee el fichero de entrada y devuelve un diccionario con los datos"""
    try:
        # Abrimos el fichero de entrada
        with open(input_path, "r") as f:
            lines = []
            for line in f.readlines():
                # Guardamos linea si no está vacia
                if line.strip():
                    lines.append(line.strip())
        
        # Leemos los datos de las líneas
        n, m, u = map(int, lines[0].split())
        shared_passengers = []
        for i in range(1, m+1):
            row = list(map(int, lines[i].split()))
            if len(row) != m:
                raise ValueError("Datos inconsistentes: debe especificarse los pasajeros compartidos de los %d autobuses" %m)
            shared_passengers.append(row)
        available_slots = []
        for i in range(m+1, m+1+n):
            row = list(map(int, lines[i].split()))
            if len(row) != u:
                raise ValueError("Datos inconsistentes: debe especificarse la disponibilidad de las %d franjas para los %d talleres" %(n,u))
            available_slots.append(row)
        
        # Comprobamos cantidad de datos leídos
        if len(shared_passengers) != m:
            raise ValueError("Datos inconsistentes: debe especificarse los pasajeros compartidos de los %d autobuses" %m)
        if len(available_slots) != n:
                raise ValueError("Datos inconsistentes: debe especificarse la disponibilidad de las %d franjas para los %d talleres" %(n,u))
        
        # Devolvemos un diccionario con todos los datos
        return {
            "n": n, "m": m, "u": u,
            "shared_passengers": shared_passengers, "available_slots": available_slots
        }
    except (FileNotFoundError, ValueError, IndexError) as e:
        print("Error al leer %s: %s" %(input_path, e), file=sys.stderr)
        sys.exit(1)


def generate_dat(data, output_path):
    """Genera el fichero .dat para GLPK"""
    try:
        output_dir = os.path.dirname(output_path)
        # si el directorio no existe, lo creamos
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_path, "w") as f:
            # Escribimos los buses
            buses_list = []
            for i in range(1, data["m"] + 1):
                buses_list.append(str(i))
            f.write("set BUSES := %s;\n" % " ".join(buses_list))
            
            # Escribimos los slots
            slots_list = []
            for i in range(1, data["n"] + 1):
                slots_list.append(str(i))
            f.write("set SLOTS := %s;\n" % " ".join(slots_list))
            
            # Escribimos los talleres
            workshops_list = []
            for i in range(1, data["u"] + 1):
                workshops_list.append(str(i))
            f.write("set WORKSHOPS := %s;\n\n" % " ".join(workshops_list))
            
            # Escribimos la matriz de Shared_passengers
            f.write("param Shared_passengers :=\n")
            for i, row in enumerate(data["shared_passengers"], start=1):
                for j, shared in enumerate(row, start=1):
                    f.write("[%d, %d] %s\n" %(i, j, shared))
            f.write(";\n\n")
            
            # Escribimos la matriz de Available_slots
            f.write("param Available_slots :=\n")
            for i, row in enumerate(data["available_slots"], start=1):
                for j, available in enumerate(row, start=1):
                    f.write("[%d, %d] %s\n" %(i, j, available))
            f.write(";\n\n")
    
    except IOError as e:
        print("Error al escribir %s: %s" %(output_path, e), file=sys.stderr)
        sys.exit(1)


def solve_glpk(mod_file, data_file):
    """Usamos GLPK para resolver el problema"""
    # Si el fichero .mod no existe lanzamos error
    if not os.path.exists(mod_file):
        print("Error: No se encontró %s" %mod_file, file=sys.stderr)
        sys.exit(1)
    
    try:
        # subprocess.run para ejecutar glpsol
        result = subprocess.run(
            ["glpsol", "--model", mod_file, "--data", data_file],
            capture_output=True, text=True # captura stdout y stderr
        )
        if result.returncode != 0:
            print("Error al ejecutar GLPK:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
        
        return result.stdout
    
    except FileNotFoundError:
        print("Error: glpsol no encontrado.", file=sys.stderr)
        sys.exit(1)


def parse_and_display_solution(output, data):
    """Parsea la salida de GLPK y muestra la solución."""
    # Extraer funcion objetivo de la solucion dada por glpsol
    obj_match = re.search(r"mip\s*=\s*([\d.]+e[+-]?\d+|[\d.]+)", output) 
    if obj_match:
        obj_val = float(obj_match.group(1))
    else:
        obj_val = None
    
    # Extraer variables y restricciones
    stats_match = re.search(r"GLPK Simplex Optimizer 5.0\n(\d+)\s+rows,\s+(\d+)\s+columns", output)
    if stats_match:
        num_const = int(stats_match.group(1))
        num_vars = int(stats_match.group(2))
    else:
        # Si no se encuentran, calculamos a partir de los datos por defecto
        num_const = data["m"] + data["n"]
        num_vars = data["m"] * data["n"]
    
    # Extraer asignaciones
    assignments = {}
    
    for match in re.finditer(r"Franja:(\d+),\sTaller:(\d+), Bus:(\d+)\n", output):
        slot = int(match.group(1))
        workshop = int(match.group(2))
        bus = int(match.group(3))
        assignments[bus] = (slot, workshop)
    
    # Mostramos la solución
    if obj_val is not None:
        print("Valor óptimo: %.2f, Variables: %d, Restricciones: %d" %(obj_val, num_vars, num_const))
    else:
        print("Variables: %d, Restricciones: %d" %(num_vars, num_const))
    
    # Mostramos asignaciones
    print("Asignaciones:\n")
    # Si se han introducido datos q no permiten q se resuelva el problema
    if not assignments:
        print("No hay franjas suficientes para todos los autobuses, no se puede resolver el problema\n")
    for bus in sorted(assignments.keys()):
        print("Autobús a%d -> Franja s%d, Taller t%d" %(bus, assignments[bus][0], assignments[bus][1]))


def main():
    parser = argparse.ArgumentParser(
        description="Genera .dat y resuelve el problema de asignación"
    )
    parser.add_argument("input_file", help="Fichero de entrada")
    parser.add_argument("output_file", help="Fichero de salida .dat")
    args = parser.parse_args()
    
    # Leer datos
    data = parse_input(os.path.abspath(args.input_file))
    
    # Generar .dat
    generate_dat(data, os.path.abspath(args.output_file))
    
    # Resolver con GLPK
    output = solve_glpk("parte-2-2.mod", os.path.abspath(args.output_file))

    # Mostrar solución
    parse_and_display_solution(output, data)


if __name__ == "__main__":
    main()
