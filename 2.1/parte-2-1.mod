#
# Parte 2.1
#

/* set of buses and slots */
set BUSES; /* {1, ..., m} autobuses */
set SLOTS; /* {1, ..., n} franjas horarias */

/* parameters */
param Distance {i in BUSES};
param Passengers {i in BUSES};
param Assigned_cost;
param Unassigned_cost;

/* decision variables */
var x {i in BUSES, j in SLOTS} binary;

/* objective function */
minimize Cost: sum {i in BUSES} (
        Assigned_cost * Distance[i] * sum {j in SLOTS} x[i,j]
      + Unassigned_cost * Passengers[i] * (1 - sum {j in SLOTS} x[i,j]));

/* constraints */
s.t. Slot_per_bus {j in SLOTS}: sum {i in BUSES} x[i, j] <= 1;
s.t. Bus_per_slot {i in BUSES}: sum {j in SLOTS} x[i, j] <= 1;

/* Mostrar la solución */
solve;

printf "\nAsignaciones:\n";
for {i in BUSES, j in SLOTS: x[i,j] = 1} {
    printf "x[%d,%d] = 1\n", i, j;
}

end;
