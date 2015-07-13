#const nexp = 10.
#const maxstimuli = -1.
#const maxinhibitors = -1.

model(M) :- formula(M,_,_).

input(V)  :- stimulus(V).
input(V)  :- inhibitor(V).
next(V,W) :- input(V); input(W); V < W; W <= Z : V < Z, input(Z).
first(V)  :- not next(_,V), input(V).

ubs(maxstimuli)    :- maxstimuli != -1.
ubs(S)             :- maxstimuli == -1; S = #count{V : stimulus(V)}.
ubi(maxinhibitors) :- maxinhibitors != -1.
ubi(I)             :- maxinhibitors == -1; I = #count{V : inhibitor(V)}.

listed(C) :- listed(C,_,_).

nexp(K) :- K=1..nexp.

{clamped(K,V, 1) : clause(_,V,_), stimulus(V)} S :- ubs(S); mode(1); nexp(K).
{clamped(K,V,-1) : clause(_,V,_), inhibitor(V)} I :- ubi(I); mode(1); nexp(K).
 clamped(K,V,-1) :- stimulus(V); not clamped(K,V,1); nexp(K).

1 {selected(K,C) : listed(C)} 1 :- mode(2); nexp(K).
clamped(K,V,S)  :- selected(K,C); listed(C,V,S); mode(2).

clamped(K,V)  :- clamped(K,V,_).
free(K,M,V,I) :- formula(M,V,I); not clamped(K,V); nexp(K).

eval(K,M,V, S) :- clamped(K,V,S); model(M).
eval(K,M,V, 1) :- free(K,M,V,I); eval(K,M,W,T) : clause(J,W,T); dnf(I,J).
eval(K,M,V,-1) :- not eval(K,M,V,1); model(M); variable(V); nexp(K).

diff(K,M1,M2)   :- diff(K,M1,M2,_).
diff(K,M1,M2,V) :- eval(K,M1,V,S); eval(K,M2,V,-S); 
                   M1 < M2; readout(V); model(M1;M2).

#minimize{1@1,clamped,K,V    : clamped(K,V,-1), inhibitor(V)}.
#minimize{1@2,clamped,K,V    : clamped(K,V,1),  stimulus(V)}.
#maximize{1@3,diff,K,M1,M2,V : diff(K,M1,M2,V)}.

exp(K,V)  :- clamped(K,V, 1); stimulus(V).
exp(K,V)  :- clamped(K,V,-1); inhibitor(V).

le(K-1,K,V) :- first(V); exp(K-1,V); exp(K,V).
le(K-1,K,V) :- first(V); not exp(K-1,V); not exp(K,V); nexp(K).
lt(K-1,K)   :- first(V); exp(K-1,V); not exp(K,V); nexp(K).
lt(K,K-1)   :- first(V); not exp(K-1,V); exp(K,V); nexp(K).

le(K-1,K,V) :- next(W,V); le(K-1,K,W); exp(K-1,V); exp(K,V).
le(K-1,K,V) :- next(W,V); le(K-1,K,W); not exp(K-1,V); not exp(K,V); nexp(K).
lt(K-1,K)   :- next(W,V); le(K-1,K,W); exp(K-1,V); not exp(K,V).
lt(K,K-1)   :- next(W,V); le(K-1,K,W); not exp(K-1,V); exp(K,V).

:- not lt(K-1,K); nexp(K), K>1.

:- #count{K,M1,M2,V : diff(K,M1,M2,V), nexp(K)} 0.
