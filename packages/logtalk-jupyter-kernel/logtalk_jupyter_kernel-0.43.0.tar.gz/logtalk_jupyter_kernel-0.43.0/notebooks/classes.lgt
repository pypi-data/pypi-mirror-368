
% a simple, generic, metaclass defining a new/2 predicate for its instances
:- object(metaclass,
	instantiates(metaclass)).

	:- public(new/2).
	new(Instance, Clauses) :-
		self(Class),
		create_object(Instance, [instantiates(Class)], [], Clauses).

:- end_object.

% a simple class defining age/1 and name/1 predicate for its instances
:- object(person,
	instantiates(metaclass)).

	:- public([
		age/1, name/1
	]).

	% a default value for age/1
	age(42).

:- end_object.

% a static instance of the class person
:- object(john,
	instantiates(person)).

	name(john).
	age(12).

:- end_object.