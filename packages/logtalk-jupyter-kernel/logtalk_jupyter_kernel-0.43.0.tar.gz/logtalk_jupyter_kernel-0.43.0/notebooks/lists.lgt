
:- protocol(lists_protocol).

	:- public(member/2).

:- end_protocol.

:- object(lists,
	implements(lists_protocol)).

	member(Head, [Head| _]).
	member(Head, [_| Tail]) :-
		member(Head, Tail).

:- end_object.