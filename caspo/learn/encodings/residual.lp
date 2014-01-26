rss(D,V,1,#pow(F-D,2)) :- obs(E,V,D), dfactor(F).
rss(D,V,0,#pow(D,2))   :- obs(E,V,D).
