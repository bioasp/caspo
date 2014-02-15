residual(D,V,X,N-M) :- rss(D,V,X,N); rss(D,V,1-X,M); M < N.

#minimize{L@1, hyper,I,J: dnf(I,J), hyper(I,J,L)}.
#minimize{W@2, residual,E,V : active(E,V)    , obs(E,V,D), residual(D,V,1,W);
          W@2, residual,E,V : not active(E,V), obs(E,V,D), residual(D,V,0,W)}.
