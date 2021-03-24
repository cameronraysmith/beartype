#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 563`_ **unit tests.**

This submodule unit tests `PEP 563`_ support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
# from pytest import raises

# ....................{ TESTS                             }....................
@skip_if_python_version_less_than('3.7.0')
def test_pep563_module() -> None:
    '''
    Test module-scoped `PEP 563`_ support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype_test.a00_unit.data.data_pep563 import (
        get_minecraft_end_txt,
        get_minecraft_end_txt_stanza,
    )

    # Dictionary of these callables' annotations, localized to enable debugging
    # in the likely event of unit test failure. *sigh*
    GET_MINECRAFT_END_TXT_ANNOTATIONS = get_minecraft_end_txt.__annotations__
    GET_MINECRAFT_END_TXT_STANZA_ANNOTATIONS = (
        get_minecraft_end_txt_stanza.__annotations__)

    # Assert that all annotations of a callable *NOT* decorated by @beartype
    # are postponed under PEP 563 as expected.
    assert all(
        isinstance(param_hint, str)
        for param_name, param_hint in (
            GET_MINECRAFT_END_TXT_ANNOTATIONS.items())
    )

    # Assert that *NO* annotations of a @beartype-decorated callable are
    # postponed, as @beartype implicitly resolves all annotations.
    assert all(
        not isinstance(param_hint, str)
        for param_name, param_hint in (
            GET_MINECRAFT_END_TXT_STANZA_ANNOTATIONS.items())
    )

    # Assert that a @beartype-decorated callable works under PEP 563.
    assert get_minecraft_end_txt_stanza(
        player_name='Notch', stanza_index=33) == 'Notch. Player of games.'

    # Test that @beartype silently accepts callables with one or more
    # non-postponed annotations under PEP 563, a technically non-erroneous edge
    # case that needlessly complicates code life.
    #
    # Manually resolve all postponed annotations on a callable.
    get_minecraft_end_txt.__annotations__ = {
        param_name: eval(param_hint, get_minecraft_end_txt.__globals__)
        for param_name, param_hint in (
            get_minecraft_end_txt.__annotations__.items())
    }

    # Manually decorate this callable with @beartype.
    get_minecraft_end_txt_typed = beartype(get_minecraft_end_txt)

    # Assert that this callable works under PEP 563.
    assert isinstance(get_minecraft_end_txt_typed(player_name='Notch'), str)


@skip_if_python_version_less_than('3.7.0')
def test_pep563_closure() -> None:
    '''
    Test closure-scoped `PEP 563`_ support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    # Defer heavyweight imports.
    from beartype_test.a00_unit.data.data_pep563 import (
        get_minecraft_end_txt_closure,
        get_minecraft_end_txt_closure_factory,
    )

    # Assert that declaring a @beartype-decorated closure works under PEP 563.
    get_minecraft_end_txt_substr = get_minecraft_end_txt_closure(
        player_name='Julian Gough')
    assert callable(get_minecraft_end_txt_substr)

    # Assert that this closure works under PEP 563.
    minecraft_end_txt_substr = get_minecraft_end_txt_substr('player')
    assert isinstance(minecraft_end_txt_substr, list)
    assert 'You are the player.' in minecraft_end_txt_substr

    # Assert that declaring a @beartype-decorated closure factory works under
    # PEP 563.
    get_minecraft_end_txt_closure_outer = (
        get_minecraft_end_txt_closure_factory(player_name='Markus Persson'))
    assert callable(get_minecraft_end_txt_closure_outer)

    # Assert that declaring a @beartype-decorated closure declared by a
    # @beartype-decorated closure factory works under PEP 563.
    get_minecraft_end_txt_closure_inner = get_minecraft_end_txt_closure_outer(
        stanza_len_min=65)
    assert callable(get_minecraft_end_txt_closure_inner)

    # Assert that this closure works under PEP 563.
    minecraft_end_txt_inner = get_minecraft_end_txt_closure_inner('thought')
    assert isinstance(minecraft_end_txt_inner, list)
    assert (
        'It is reading our thoughts as though they were words on a screen.' in
        minecraft_end_txt_inner
    )
    assert 'It cannot read that thought.' not in minecraft_end_txt_inner
    assert 'It reads our thoughts.'       not in minecraft_end_txt_inner


@skip_if_python_version_less_than('3.7.0')
def test_pep563_class() -> None:
    '''
    Test class-scoped `PEP 563`_ support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    # Defer heavyweight imports.
    # from beartype_test.a00_unit.data.data_pep563 import (
    #     get_minecraft_end_txt_class,
    # )

# ....................{ TESTS ~ limit                     }....................
#FIXME: Hilariously, we can't even unit test whether the
#beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit() function
#behaves as expected. See commentary in the
#"beartype_test.a00_unit.data.data_pep563" submodule for all the appalling details.

# @skip_if_python_version_less_than('3.7.0')
# def test_die_if_hint_repr_exceeds_child_limit() -> None:
#     '''
#     Test the private
#     :func:`beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit`
#     function if the active Python interpreter targets at least Python 3.7.0
#     (i.e., the first major Python version to support PEP 563) *or* skip
#     otherwise.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype import beartype
#     from beartype.roar import BeartypeDecorHintPepException
#     from beartype_test.a00_unit.data.data_pep563 import player_was_love
#
#     # Assert @beartype raises the expected exception when decorating a
#     # callable violating this limit.
#     with raises(BeartypeDecorHintPepException):
#         beartype(player_was_love)
