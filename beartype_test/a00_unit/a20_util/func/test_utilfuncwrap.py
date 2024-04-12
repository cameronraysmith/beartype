#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable wrapper utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncwrap` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ all                        }....................
def test_unwrap_func_all() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_all` function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.utilfuncwrap import unwrap_func_all
    from functools import wraps

    # ....................{ CALLABLES                      }....................
    def in_a_station_of_the_metro_line_two():
        '''
        Arbitrary wrappee callable.
        '''

        return 'Petals on a wet, black bough.'


    @wraps(in_a_station_of_the_metro_line_two)
    def in_a_station_of_the_metro():
        '''
        Arbitrary wrapper callable.
        '''

        return (
            'THE apparition of these faces in the crowd;\n' +
            in_a_station_of_the_metro_line_two()
        )

    # ....................{ ASSERTS                        }....................
    # Assert this function returns unwrapped callables unmodified.
    assert unwrap_func_all(in_a_station_of_the_metro_line_two) is (
        in_a_station_of_the_metro_line_two)
    assert unwrap_func_all(iter) is iter

    # Assert this function returns wrapper callables unwrapped.
    assert unwrap_func_all(in_a_station_of_the_metro) is (
        in_a_station_of_the_metro_line_two)

# ....................{ TESTS ~ descriptor                 }....................
def test_unwrap_func_classmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_classmethod`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
    from beartype._util.func.utilfuncwrap import unwrap_func_classmethod
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

    # ....................{ LOCALS                         }....................
    def never_to_be_reclaimed() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'


    class TheLimitsOfTheDeadAndLivingWorld(object):
        '''
        Arbitrary pure-Python class defining a class method wrapping the
        pure-Python function defined above.
        '''

        of_insects_beasts_and_birds = classmethod(never_to_be_reclaimed)

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected wrappee when passed a class method
    # descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    class_method = TheLimitsOfTheDeadAndLivingWorld.__dict__[
        'of_insects_beasts_and_birds']
    class_method_wrappee = unwrap_func_classmethod(class_method)
    assert class_method_wrappee is never_to_be_reclaimed

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a class method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableWrapperException):
            unwrap_func_classmethod(some_callable)


def test_unwrap_func_staticmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_staticmethod`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
    from beartype._util.func.utilfuncwrap import unwrap_func_staticmethod
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

    # ....................{ LOCALS                         }....................
    def becomes_its_spoil() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'

    class TheirFoodAndTheirRetreatForEverGone(object):
        '''
        Arbitrary pure-Python static defining a static method wrapping the
        pure-Python function defined above.
        '''

        so_much_of_life_and_joy_is_lost = staticmethod(becomes_its_spoil)

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected wrappee when passed a static method
    # descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as static or instance
    # attributes, static methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    static_method = TheirFoodAndTheirRetreatForEverGone.__dict__[
        'so_much_of_life_and_joy_is_lost']
    static_method_wrappee = unwrap_func_staticmethod(static_method)
    assert static_method_wrappee is becomes_its_spoil

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a static method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableWrapperException):
            unwrap_func_staticmethod(some_callable)
