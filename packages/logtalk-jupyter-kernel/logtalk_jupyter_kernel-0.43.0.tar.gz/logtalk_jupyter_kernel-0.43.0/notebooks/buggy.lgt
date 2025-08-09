
:- set_logtalk_flag(complements, allow).

:- object(buggy).

	:- public(p/0).
	p :- write(foo).

:- end_object.