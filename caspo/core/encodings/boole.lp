clamped(V) :- clamped(V,_).
free(V,D) :- formula(V,D), not clamped(V).

eval(V, S) :- clamped(V,S).
eval(V, 1) :- free(V,D), eval(W,T) : clause(C,W,T), dnf(D,C).
eval(V,-1) :- not eval(V,1), formula(V,_).
