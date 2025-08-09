
:- object(foo).

    :- public(bar/0).
    bar :-
        write('Hello world!\n').

:- end_object.