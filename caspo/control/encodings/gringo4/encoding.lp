goal(T,S)        :- goal(_,T,S).
goal(T)          :- goal(T,_).
constrained(Z,E) :- constrained(Z,E,_).
constrained(E)   :- constrained(_,E).
model(M)         :- formula(M,_,_).
formula(W,D)     :- formula(_,W,D).

satisfy(V,W,S) :- formula(W,D); dnf(D,C); clause(C,V,S).
closure(V,T)   :- goal(V,T).
closure(V,S*T) :- closure(W,T); satisfy(V,W,S); not goal(V,-S*T).

{ intervention(V,S) : closure(V,S) , candidate(V) }.
:- intervention(V,1); intervention(V,-1).
intervention(V) :- intervention(V,S).

eval(M,Z,V,S) :- scenario(Z); intervention(V,S); model(M).
eval(M,Z,E,S) :- constrained(Z,E,S); not intervention(E); model(M).
free(M,Z,V,D) :- formula(M,V,D); scenario(Z);
                 not constrained(Z,V); not intervention(V).

eval_clause(M,Z,C,-1) :- clause(C,V,S); eval(M,Z,V,-S); model(M).

eval(M,Z,V, 1) :- free(M,Z,V,D); eval(M,Z,W,T) : clause(C,W,T); dnf(D,C).
eval(M,Z,V,-1) :- free(M,Z,V,D); eval_clause(M,Z,C,-1) :        dnf(D,C).

:- goal(Z,T,S); not eval(M,Z,T,S); model(M).

#const maxsize=0.
:- maxsize>0; maxsize + 1 { intervention(_) }.
