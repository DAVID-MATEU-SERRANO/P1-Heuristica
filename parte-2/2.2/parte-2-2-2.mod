#
# Parte 2.2
#

/* set of buses, slots and workshops */
set BUSES; /* {1, ..., m} autobuses */
set SLOTS; /* {1, ..., n} franjas horarias */
set WORKSHOPS; /* {1, ..., u} talleres */


/* parameters */
param Available_slots {SLOTS, WORKSHOPS} binary;
param Shared_passengers {BUSES, BUSES} integer, >= 0;


/* decision variables */
var x {i in SLOTS, j in WORKSHOPS, k in BUSES} binary;
var y {i in SLOTS, k1 in BUSES, k2 in BUSES} binary;


/* objective function */
minimize Overlap:
    sum {i in SLOTS, k1 in BUSES, k2 in BUSES: k2 > k1} Shared_passengers[k1,k2] * y[i,k1,k2];


/* constraints */
s.t. MAX_ONE_BUS_PER_SLOT {i in SLOTS, j in WORKSHOPS}: sum {k in BUSES} x[i,j,k] <= 1;
s.t. ASSIGN_ALL_BUSSES {k in BUSES}: sum {i in SLOTS, j in WORKSHOPS} x[i,j,k] = 1;
s.t. ALLOWED_SLOT {i in SLOTS, j in WORKSHOPS, k in BUSES}: x[i,j,k] <= Available_slots[i,j];
s.t. AND_1 {i in SLOTS, k1 in BUSES, k2 in BUSES}: y[i,k1,k2] <= sum {j in WORKSHOPS} x[i,j,k1];
s.t. AND_2 {i in SLOTS, k1 in BUSES, k2 in BUSES}: y[i,k1,k2] <= sum {j in WORKSHOPS} x[i,j,k2];
s.t. AND_3 {i in SLOTS, k1 in BUSES, k2 in BUSES}: y[i,k1,k2] >= (sum {j in WORKSHOPS} (x[i,j,k1] + x[i,j,k2])) - 1;

/* Mostrar la solución */
solve;

for {i in SLOTS, j in WORKSHOPS, k in BUSES: x[i,j,k] = 1} {
    printf "Franja:%d, Taller:%d, Bus:%d\n", i, j, k;
}

end;