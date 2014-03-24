#include <iclingo>.

%#const istop  = "SAT".
%#const imin   = 1.
#const imax = 20.
%#const iquery = 1.
#const maxstimuli = -1.
#const maxinhibitors = -1.

#program base.

model(M) :- formula(M,_,_).

#program cumulative(k).

clamping(k).

{clamped(k,V, 1)} :- stimulus(V); clause(_,V,_).
{clamped(k,V,-1)} :- inhibitor(V); clause(_,V,_).
 clamped(k,V,-1)  :- stimulus(V); not clamped(k,V,1); clamping(k).
 
:- maxstimuli + 1 { clamped(k,V,1) : stimulus(V) }; clamping(k); maxstimuli >= 0.
:- maxinhibitors + 1 { clamped(k,V,-1) : inhibitor(V) }; clamping(k); maxinhibitors >= 0.

clamped(k,V)  :- clamped(k,V,_).
free(k,M,V,I) :- formula(M,V,I); clamping(k); not clamped(k,V).

eval(k,M,V, S) :- clamped(k,V,S); model(M).
eval(k,M,V, 1) :- free(k,M,V,I); eval(k,M,W,T) : clause(J,W,T); dnf(I,J).
eval(k,M,V,-1) :- not eval(k,M,V,1); model(M); variable(V); clamping(k).

diff(k,M1,M2,V) :- eval(k,M1,V,S); eval(k,M2,V,-S); M1 < M2; readout(V); model(M1;M2).
diff(k,M1,M2)   :- diff(k,M1,M2,_).

#program volatile(k).

#external query(k).
:- model(M1;M2); M1<M2; not diff(K,M1,M2) : K <= k, clamping(K); query(k).

#minimize{1@1,clamped,K,V : clamped(K,V,-1), inhibitor(V), K <= k, query(k)}.
#minimize{1@2,clamped,K,V : clamped(K,V,1), stimulus(V), K <= k, query(k)}.
#maximize{1@3,diff,K,M1,M2,V : diff(K,M1,M2,V), K <= k, query(k)}.

#show clamped/3.