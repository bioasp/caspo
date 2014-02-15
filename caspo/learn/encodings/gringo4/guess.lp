formula(V,I)              :- node(V,I); hyper(I,_,_).
{dnf(I,J) : hyper(I,J,N)} :- formula(V,I).
clause(J,V,S)             :- edge(J,V,S); dnf(_,J).

path(U,V) :- formula(V,I); dnf(I,J); edge(J,U,_).
path(U,V) :- path(U,W); path(W,V).

:- path(V,V).

:- formula(V,I); hyper(I,J1,N); hyper(I,J2,M); N < M,
   dnf(I,J1);  dnf(I,J2); edge(J2,U,S) : edge(J1,U,S).
   
:- formula(V,I); dnf(I,J); edge(J,U,S); edge(J,U,-S).

:- dnf(I,J); edge(J,V,_); not stimulus(V);
   not path(U,V) : stimulus(U).

:- path(_,V); not readout(V); not path(V,U) : readout(U).
