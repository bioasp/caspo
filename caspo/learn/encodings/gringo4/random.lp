%size
:- not minsize #sum{L,I,J : dnf(I,J), hyper(I,J,L)} maxsize.
%and gates
:- not minnand #count{I,J : dnf(I,J), L > 1, hyper(I,J,L)} maxnand.

%reach all readouts
:- readout(V); not path(_,V).

%limit AND gates inputs
:- dnf(I,J); hyper(I,J,L); L > maxin.

%force all possible stimulus to be present
gpath(U,V) :- node(V,I); hyper(I,J,_); edge(J,U,_).
gpath(U,V) :- gpath(U,W); gpath(W,V).
:- stimulus(U), readout(V), gpath(U,V), not clause(_,U,_).