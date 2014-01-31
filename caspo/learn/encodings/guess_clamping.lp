1 {clamped(V,1;-1)} 1 :- stimulus(V),  clause(_,V,_).
{clamped(V,-1)}       :- inhibitor(V), clause(_,V,_).
