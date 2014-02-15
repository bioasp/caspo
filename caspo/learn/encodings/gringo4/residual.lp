rss(D,V,1,(F-D)*(F-D)) :- obs(E,V,D); dfactor(F).
rss(D,V,0,D*D)   :- obs(E,V,D).
