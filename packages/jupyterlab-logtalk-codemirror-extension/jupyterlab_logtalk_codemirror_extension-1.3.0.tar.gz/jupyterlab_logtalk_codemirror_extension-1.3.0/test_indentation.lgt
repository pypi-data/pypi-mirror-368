% Test file for Logtalk indentation
% Try pressing Enter after the following lines to test indentation:

:- object(test_object).
% Press Enter here - should indent

test_predicate(X) :-
% Press Enter here - should indent

:- end_object.
% Press Enter here - should not indent

:- protocol(test_protocol).
% Press Enter here - should indent

:- end_protocol.
% Press Enter here - should not indent
