#
# Parte 2.1
#

/* set of buses and slots */
set BUSES; /* {1, ..., m} autobuses */
set SLOTS; /* {1, ..., n} franjas horarias */

/* parameters */
param Distance {BUSES};
param Passengers {BUSES};
param Assigned_cost;
param Unassigned_cost;

/* decision variables */
var x {i in BUSES, j in SLOTS} binary;

/* objective function */
minimize Cost:
    sum {i in BUSES, j in SLOTS} ((Assigned_cost * Distance[i] - Unassigned_cost * Passengers[i]) * x[i,j])
    + sum {i in BUSES} (Unassigned_cost * Passengers[i]);


/* constraints */
s.t. Slot_per_bus {j in SLOTS}: sum {i in BUSES} x[i, j] <= 1;
s.t. Bus_per_slot {i in BUSES}: sum {j in SLOTS} x[i, j] <= 1;

/* Show solution */
solve;

for {i in BUSES, j in SLOTS: x[i,j] = 1} {
    printf "Bus:%d, Franja:%d\n", i, j;
}

end;
