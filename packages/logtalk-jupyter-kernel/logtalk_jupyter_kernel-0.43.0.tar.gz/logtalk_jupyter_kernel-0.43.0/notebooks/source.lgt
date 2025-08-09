
:- set_logtalk_flag(hook, my_macros).

:- object(source).

	:- public(bar/1).
	bar(X) :- foo(X).

	foo(a). foo(b). foo(c).

:- end_object.