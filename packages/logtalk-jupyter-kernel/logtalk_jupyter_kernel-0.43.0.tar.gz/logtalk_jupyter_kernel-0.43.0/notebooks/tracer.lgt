
:- object(tracer,
	% built-in protocol for event handlers
	implements(monitoring)).

	:- initialization(define_events(_, list, _, _, tracer)).

	before(Object, Message, Sender) :-
		write('call: '), writeq(Object), write(' <-- '), writeq(Message),
		write(' from '), writeq(Sender), nl.

	after(Object, Message, Sender) :-
		write('exit: '), writeq(Object), write(' <-- '), writeq(Message),
		write(' from '), writeq(Sender), nl.

:- end_object.