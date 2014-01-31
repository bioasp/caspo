model(M) :- formula(M,_,_).

clamped(V)  :- clamped(V,_).
free(M,V,I) :- formula(M,V,I), not clamped(V).

eval(M,V, S) :- clamped(V,S), model(M).
eval(M,V, 1) :- free(M,V,I), eval(M,W,T) : clause(J,W,T), dnf(I,J).
eval(M,V,-1) :- not eval(M,V,1), model(M), variable(V).
