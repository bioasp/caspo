#minimize{W, rss,E,V : active(E,V)    , obs(E,V,D), rss(D,V,1,W);
          W, rss,E,V : not active(E,V), obs(E,V,D), rss(D,V,0,W)}.
