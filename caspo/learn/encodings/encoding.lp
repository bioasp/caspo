formula(V,I)              :- node(V,I), hyper(I,_,_).
{dnf(I,J) : hyper(I,J,N)} :- formula(V,I).
clause(J,V,S)             :- edge(J,V,S), dnf(_,J).

path(U,V) :- formula(V,I), dnf(I,J), edge(J,U,_).
path(U,V) :- path(U,W), path(W,V).

:- path(V,V).

:- formula(V,I), hyper(I,J1,N), hyper(I,J2,M), N < M,
   dnf(I,J1),  dnf(I,J2), edge(J2,U,S) : edge(J1,U,S).
   
:- formula(V,I), dnf(I,J), edge(J,U,S), edge(J,U,-S).

:- dnf(I,J), edge(J,V,_), not stimulus(V), 
   not path(U,V) : stimulus(U).

:- path(_,V), not readout(V), not path(V,U) : readout(U).

exp(E)      :- exp(E,_,_).
free(E,V,I) :- formula(V,I), dnf(I,_), exp(E),
               not stimulus(V), not exp(E,V,0).

active(E,V) :- exp(E,V,1), stimulus(V).
active(E,V) :- exp(E), free(E,V,I), dnf(I,J),
               active(E,W)     : edge(J,W,1), 
               not active(E,W) : edge(J,W,-1). 

rss(D,V,1,#pow(F-D,2)) :- obs(E,V,D), dfactor(F).
rss(D,V,0,#pow(D,2))   :- obs(E,V,D).

#const maxrss=0.
#const maxsize=0.
:- maxrss > 0, maxrss+1 [active(E,V)     : obs(E,V,D) : rss(D,V,1,W) = W,
                         not active(E,V) : obs(E,V,D) : rss(D,V,0,W) = W].

:- maxsize > 0, maxsize+1 [dnf(I,J) : hyper(I,J,L) = L].

#minimize[dnf(I,J) : hyper(I,J,L) = L@1].
#minimize[active(E,V)     : obs(E,V,D) : rss(D,V,1,W) = W@2,
          not active(E,V) : obs(E,V,D) : rss(D,V,0,W) = W@2].