#const maxsize = -1.
#const maxrss = -1.
         
:- maxsize + 1 [dnf(I,J) : hyper(I,J,L) = L], maxsize >= 0.

:- maxrss + 1 [active(E,V)     : obs(E,V,D) : rss(D,V,1,W) = W,
               not active(E,V) : obs(E,V,D) : rss(D,V,0,W) = W], maxrss >= 0.

#hide.