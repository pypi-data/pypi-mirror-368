
:- object(my_macros,
	% built-in protocol for expanding predicates
	implements(expanding)).

	term_expansion(foo(Char), baz(Code)) :-
		% standard built-in predicate
		char_code(Char, Code).

	goal_expansion(foo(X), baz(X)).

:- end_object.