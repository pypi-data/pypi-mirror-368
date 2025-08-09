
:- object(circle(_Radius, _Color)).

	:- public([
		area/1, perimeter/1
	]).

	area(Area) :-
		parameter(1, Radius),
		Area is pi*Radius*Radius.

	perimeter(Perimeter) :-
		parameter(1, Radius),
		Perimeter is 2*pi*Radius.

:- end_object.