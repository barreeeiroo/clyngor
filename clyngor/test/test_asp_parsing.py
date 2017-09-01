

from clyngor.asp_parsing import parse_asp_program, CodeAsTuple


def test_comments():
    ASP_CODE = r"""
    %a.
    %.
    %{}
    %a:- test
    %    *%
    % *
    ok.
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 1
    assert rules[0] == ('term', 'ok', ())


def test_non_working_multiline_comments():
    ASP_CODE = r"""
    %    *%
    %*
    ai.
    b: %bug
    :c- *%
    % *
    ok.
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 1
    assert rules[0] == ('term', 'ai', ()), ("Multiline comments are now handled !"
                                            " You can now change this test")



def test_disjunction():
    ASP_CODE = r"""
    rel(a,(c;d)).
    rel(b,(d;e)).
    rel(c,(e(1),f;g,h(2))).
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 3
    first, second, third = rules

    print('FIRST:', first)
    expected = ('term', 'rel', (('term', 'a', ()),
                                ('disjunction',
                                 (('term', 'c', ()),),
                                 (('term', 'd', ()),)
                                )))
    print('EXPEC:', expected)
    assert first == expected

    print('SECOD:', second)
    expected = ('term', 'rel', (('term', 'b', ()),
                                ('disjunction',
                                 (('term', 'd', ()),),
                                 (('term', 'e', ()),)
                                )))
    print('EXPEC:', expected)
    assert second == expected
 
    print('THIRD:', third)
    expected = ('term', 'rel', (('term', 'c', ()),
                                ('disjunction',
                                 (('term', 'e', (1,)), ('term', 'f', ())),
                                 (('term', 'g', ()), ('term', 'h', (2,)))
                                )))
    print('EXPEC:', expected)
    assert third == expected


def test_constraint():
    ASP_CODE = r"""
    :- a.
    :- not obj(X):obj(X).
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 2
    first, second = rules

    print('FIRST:', first)
    expected = ('constraint', (('term', 'a', ()),) )
    print('EXPEC:', expected)
    assert first == expected

    print('SECOD:', second)
    expected = ('constraint', (('¬forall', 'obj', ('X',), (('term', 'obj', ('X',)),) ),) )
    print('EXPEC:', expected)
    assert second == expected


def test_forall():
    ASP_CODE = r"""
    a:- rel(X,Y): obj(X), att(Y).
    b:- not rel(X,Y): obj(X), att(Y).
    c:- not rel(X,Y): obj(X), att(Y) ; rel(c,_).
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 3
    first, second, third = rules

    print('FIRST:', first)
    expected = ('rule', ('term', 'a', ()), (('forall', 'rel', ('X', 'Y'), (('term', 'obj', ('X',)), ('term', 'att', ('Y',))) ),) )
    print('EXPEC:', expected)
    assert first == expected

    print('SECOD:', second)
    expected = ('rule', ('term', 'b', ()), (('¬forall', 'rel', ('X', 'Y'), (('term', 'obj', ('X',)), ('term', 'att', ('Y',))) ),) )
    print('EXPEC:', expected)
    assert second == expected

    print('THIRD:', third)
    expected = ('rule', ('term', 'c', ()), (('¬forall', 'rel', ('X', 'Y'), (('term', 'obj', ('X',)), ('term', 'att', ('Y',))) ), ('term', 'rel', (('term', 'c', ()), '_'))) )
    print('EXPEC:', expected)
    assert third == expected


def test_term():
    ASP_CODE = r"""
    a.
    b(1).
    c(2):- not b(2).
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 3
    first, second, third = rules

    print('FIRST:', first)
    expected = ('term', 'a', ())
    print('EXPEC:', expected)
    assert first == expected

    print('SECOD:', second)
    expected = ('term', 'b', (1,))
    print('EXPEC:', expected)
    assert second == expected

    print('THIRD:', third)
    expected = ('rule', ('term', 'c', (2,)), (('¬term', 'b', (2,)),) )
    print('EXPEC:', expected)
    assert third == expected


def test_selection():
    ASP_CODE = r"""
    1 { sel(X): obj(X) } 1.
    { con(X,Y): obj(X), att(Y, 2) }.
    2 { sel(X): obj(X) } 4:- anatom.
    """
    rules = tuple(parse_asp_program(ASP_CODE, do=CodeAsTuple()))
    assert len(rules) == 3

    first, second, third = rules

    print('FIRST:', first)
    expected = ('selection', 1, 1, (('forall', 'sel', ('X',), (('term', 'obj', ('X',)),)),),)
    print('EXPEC:', expected)
    assert first == expected

    print('SECOD:', second)
    expected = ('selection', 0, None, (('forall', 'con', ('X', 'Y'),
                                        (('term', 'obj', ('X',)),
                                         ('term', 'att', ('Y', 2)),),
                                        ),),)
    print('EXPEC:', expected)
    assert second == expected

    print('THIRD:', third)
    expected = ('rule',
                ('selection', 2, 4, (('forall', 'sel', ('X',),
                                     (('term', 'obj', ('X',)),),),)),
                (('term', 'anatom', ()),))
    print('EXPEC:', expected)
    assert third == expected


def test_multiple_rules():
    ASP_CODE = r"""
    a.
    b("les amis, \"coucou\".").
    obj(X):- rel(X,_) ; rel(X,Y): att(Y).
    att(Y):- rel(_,Y) ; rel(X,Y): obj(X).
    """

    rules = tuple(parse_asp_program(ASP_CODE))
    assert len(rules) == 4

    first, second, third, fourth = rules
    assert first == ('term', 'a', ())

    print('SECOND:', second)
    assert second == ('term', 'b', (('text', r'les amis, \"coucou\".'),))

    print('THIRD:', third)
    expected = ('rule', ('term', 'obj', ('X',)), (
        ('term', 'rel', ('X', '_')),
        ('forall', 'rel', ('X', 'Y'), (('term', 'att', ('Y',)),)),
    ))
    print('EXPEC:', expected)
    assert third == expected

    print('FOURTH:', fourth)
    expected = ('rule', ('term', 'att', ('Y',)), (
        ('term', 'rel', ('_', 'Y')),
        ('forall', 'rel', ('X', 'Y'), (('term', 'obj', ('X',)),)),
    ))
    print('EXPECT:', expected)
    assert fourth == expected