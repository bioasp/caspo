#const maxsize = -1.
#const maxrss = -1.
         
:- maxsize + 1 #sum {L, hyper,I,J : dnf(I,J) , hyper(I,J,L)}, maxsize >= 0.

:- maxrss + 1 #sum {W, rss,E,V : active(E,V)     , obs(E,V,D) , rss(D,V,1,W);
                    W, rss,E,V : not active(E,V) , obs(E,V,D) , rss(D,V,0,W)}, maxrss >= 0.
