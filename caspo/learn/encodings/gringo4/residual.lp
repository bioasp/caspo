rss(D,V, 1,(F-D)**2) :- obs(E,V,D); dfactor(F).
rss(D,V, 0,D**2)     :- obs(E,V,D).
