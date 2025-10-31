#!/usr/bin/env python3
import random

# Parámetros
n = 3    # franjas
m = 10    # autobuses
u = 100    # talleres

# Nombre del fichero de salida
output_file = "entrada.in"

random.seed(42)  # semilla fija para reproducibilidad (puedes quitarla si quieres aleatorio)

with open(output_file, "w") as f:
    # Primera línea: n, m, u
    f.write(f"{n} {m} {u}\n")
    
    # Generar matriz simétrica con diagonal a 0 (Shared_passengers)
    shared = [[0 for _ in range(m)] for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            val = random.randint(0, 10)
            shared[i][j] = val
            shared[j][i] = val  # simetría
    
    # Escribir Shared_passengers
    for i in range(m):
        f.write(" ".join(map(str, shared[i])) + "\n")
    
    # Generar Available_slots: n x u
    # Aseguramos que haya al menos m posiciones disponibles en total
    total_slots = n * u
    available_needed = m
    available_matrix = [[0 for _ in range(u)] for _ in range(n)]

    # Primero, asignamos aleatoriamente m ranuras disponibles
    available_positions = random.sample(range(total_slots), available_needed)
    for pos in available_positions:
        i = pos // u
        j = pos % u
        available_matrix[i][j] = 1

    # Luego, añadimos aleatoriamente más disponibilidad (sin pasarnos)
    for i in range(n):
        for j in range(u):
            if available_matrix[i][j] == 0 and random.random() < 0.3:
                available_matrix[i][j] = 1

    # Aseguramos que cada franja tenga al menos un 1 (por seguridad)
    for i in range(n):
        if sum(available_matrix[i]) == 0:
            available_matrix[i][random.randrange(u)] = 1

    # Escribimos matriz final
    for i in range(n):
        f.write(" ".join(map(str, available_matrix[i])) + "\n")

print(f"✅ Fichero {output_file} generado correctamente.")
