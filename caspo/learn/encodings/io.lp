{clamped(V, 1)} :- stimulus(V);  clause(_,V,_).
{clamped(V,-1)} :- inhibitor(V); clause(_,V,_).
 clamped(V,-1)  :- stimulus(V); not clamped(V,1).
 
model(M) :- formula(M,_,_).

clamped(V)  :- clamped(V,_).
free(M,V,I) :- formula(M,V,I); not clamped(V).

eval(M,V, S) :- clamped(V,S); model(M).
eval(M,V, 1) :- free(M,V,I); eval(M,W,T) : clause(J,W,T); dnf(I,J).
eval(M,V,-1) :- not eval(M,V,1); model(M); variable(V).

diff :- eval(M1,V,S); eval(M2,V,-S); M1 < M2; readout(V); model(M1;M2).
