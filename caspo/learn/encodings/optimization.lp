residual(D,V,X,N-M) :- rss(D,V,X,N), rss(D,V,1-X,M), M < N.

#minimize[dnf(I,J) : hyper(I,J,L) = L].
#minimize[active(E,V) : obs(E,V,D) : residual(D,V,1,W) = W,
          not active(E,V) : obs(E,V,D) : residual(D,V,0,W) = W].

#hide.