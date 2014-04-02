#include <iclingo>.
#const imax = 20.
#const maxstimuli = -1.
#const maxinhibitors = -1.

model(M) :- formula(M,_,_).

input(V)  :- stimulus(V).
input(V)  :- inhibitor(V).
next(V,W) :- input(V;W); V < W; W <= Z : V < Z, input(Z).
first(V)  :- not next(_,V), input(V).

ubs(maxstimuli)    :- maxstimuli != -1.
ubs(S)             :- maxstimuli == -1; S = #count{V : stimulus(V)}.
ubi(maxinhibitors) :- maxinhibitors != -1.
ubi(I)             :- maxinhibitors == -1; I = #count{V : inhibitor(V)}.

#program cumulative(k).

{clamped(k,V, 1) : clause(_,V,_), stimulus(V) } S :- ubs(S).
{clamped(k,V,-1) : clause(_,V,_), inhibitor(V)} I :- ubi(I).
 clamped(k,V,-1) :- stimulus(V); not clamped(k,V,1).
 
clamped(k,V)  :- clamped(k,V,_).
free(k,M,V,I) :- formula(M,V,I); not clamped(k,V).

eval(k,M,V, S) :- clamped(k,V,S); model(M).
eval(k,M,V, 1) :- free(k,M,V,I); eval(k,M,W,T) : clause(J,W,T); dnf(I,J).
eval(k,M,V,-1) :- not eval(k,M,V,1); model(M); variable(V).

diff(k,M1,M2)   :- diff(k,M1,M2,_).
diff(k,M1,M2,V) :- eval(k,M1,V,S); eval(k,M2,V,-S); 
                   M1 < M2; readout(V); model(M1;M2).

#minimize{1@1,clamped,k,V    : clamped(k,V,-1), inhibitor(V)}.
#minimize{1@2,clamped,k,V    : clamped(k,V,1),  stimulus(V)}.
#maximize{1@3,diff,k,M1,M2,V : diff(k,M1,M2,V)}.

exp(k,V)  :- clamped(k,V, 1); stimulus(V).
exp(k,V)  :- clamped(k,V,-1); inhibitor(V).

le(k-1,k,V) :- first(V); exp(k-1,V); exp(k,V).
le(k-1,k,V) :- first(V); not exp(k-1,V); not exp(k,V).
lt(k-1,k)   :- first(V); exp(k-1,V); not exp(k,V).
lt(k,k-1)   :- first(V); not exp(k-1,V); exp(k,V).

le(k-1,k,V) :- next(W,V); le(k-1,k,W); exp(k-1,V); exp(k,V).
le(k-1,k,V) :- next(W,V); le(k-1,k,W); not exp(k-1,V); not exp(k,V).
lt(k-1,k)   :- next(W,V); le(k-1,k,W); exp(k-1,V); not exp(k,V).
lt(k,k-1)   :- next(W,V); le(k-1,k,W); not exp(k-1,V); exp(k,V).

:- not lt(k-1,k); k > 1.

#program volatile(k). 
#external query(k).

:- not diff(K,M1,M2) : K=1..k; model(M1;M2); M1<M2; query(k).

#show clamped/3.