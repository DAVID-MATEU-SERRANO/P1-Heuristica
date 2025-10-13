#!/usr/bin/env python3
import sys

if len(sys.argv) == 3:
    input = sys.argv[1]   
    output = sys.argv[2]  

    with open(input, "r") as f:
        try:
            linea_temp = f.readline().split()
            n, m = linea_temp[0], linea_temp[1]
            linea_temp = f.readline().split()
            kd, kp = linea_temp[0], linea_temp[1]
            distancias = f.readline().split()
            pasajeros = f.readline().split()

        except:
            print("Formato incorrecto del archivo de entrada")


