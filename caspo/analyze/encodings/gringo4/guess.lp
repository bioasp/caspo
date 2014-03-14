{clamped(V, 1)} :- stimulus(V);  clause(_,V,_).
{clamped(V,-1)} :- inhibitor(V); clause(_,V,_).
 clamped(V,-1)  :- stimulus(V), not clamped(V,1).