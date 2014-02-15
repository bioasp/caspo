clamped(E,V) :- clamped(E,V,_).
free(E,V,I)  :- formula(V,I); dnf(I,_); exp(E); not clamped(E,V).

eval(E,V, S) :- clamped(E,V,S).
eval(E,V, 1) :- free(E,V,I); eval(E,W,T) : edge(J,W,T); dnf(I,J).
eval(E,V,-1) :- not eval(E,V,1); exp(E); formula(V,_).

active(E,V) :- eval(E,V,1).
