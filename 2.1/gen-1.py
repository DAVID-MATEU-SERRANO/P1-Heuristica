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
        n, m = map(int, lines[0].split())
        kd, kp = map(float, lines[1].split())
        distances = list(map(float, lines[2].split()))
        passengers = list(map(int, lines[3].split()))
        
        # Comprobamos cantidad de datos leídos
        if len(distances) != m or len(passengers) != m:
            raise ValueError("Datos inconsistentes: se esperaban %d autobuses" %m)
        
        # Devolvemos un diccionario con todos los datos
        return {
            "n": n, "m": m, "kd": kd, "kp": kp,
            "distances": distances, "passengers": passengers
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
            f.write("set SLOTS := %s;\n\n" % " ".join(slots_list))
            
            f.write("param Assigned_cost := %s;\n" %data["kd"])
            f.write("param Unassigned_cost := %s;\n\n" %data["kp"])
            
            f.write("param Distance :=\n")
            for i, dist in enumerate(data["distances"], start=1):
                f.write("%d %s\n" %(i, dist))
            f.write(";\n\n")
            
            f.write("param Passengers :=\n")
            for i, pass_count in enumerate(data["passengers"], start=1):
                f.write("%d %d\n" %(i, pass_count))
            f.write(";\n\nend;\n")
    
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
    stats_match = re.search(r"(\d+)\s+rows,\s+(\d+)\s+columns", output)
    if stats_match:
        num_const = int(stats_match.group(1))
        num_vars = int(stats_match.group(2))
    else:
        # Si no se encuentran, calculamos a partir de los datos por defecto
        num_const = data["m"] + data["n"]
        num_vars = data["m"] * data["n"]
    
    # Extraer asignaciones
    assignments = {}
    # Inicializamos a None
    for i in range(1, data["m"] + 1):
        assignments[i] = None
    
    for match in re.finditer(r"x\[(\d+),(\d+)\]\s*=\s*1", output):
        bus = int(match.group(1))
        slot = int(match.group(2))
        assignments[bus] = slot
    
    # Mostramos la solución
    if obj_val is not None:
        print("Valor óptimo: %.2f, Variables: %d, Restricciones: %d" %(obj_val, num_vars, num_const))
    else:
        print("Variables: %d, Restricciones: %d" %(num_vars, num_const))
    
    # Mostramos asignaciones
    assigned = []
    unassigned = []
    
    for bus in sorted(assignments.keys()):
        if assignments[bus] is not None:
            assigned.append((bus, assignments[bus]))
        else:
            unassigned.append(bus)
    
    if assigned:
        print("\nAutobuses asignados:")
        for bus, slot in assigned:
            print("  Autobús a%d -> Franja s%d" %(bus, slot))
    
    if unassigned:
        print("\nAutobuses sin asignar:")
        for bus in unassigned:
            print("  Autobús a%d" %bus)


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
    output = solve_glpk("parte-2-1.mod", os.path.abspath(args.output_file))
    
    # Mostrar solución
    parse_and_display_solution(output, data)


if __name__ == "__main__":
    main()
