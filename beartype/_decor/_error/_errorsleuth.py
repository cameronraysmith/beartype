#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking error cause sleuth** (i.e., object recursively
fabricating the human-readable string describing the failure of the pith
associated with this object to satisfy this PEP-compliant type hint also
associated with this object) classes.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype.typing import (
    Any,
    Callable,
    Optional,
    Tuple,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED_DEEP,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign,
)
from beartype._util.hint.pep.utilpeptest import (
    is_hint_pep,
    is_hint_pep_args,
)
from beartype._util.hint.convert.utilconvsanify import sanify_hint_child
from beartype._util.hint.utilhinttest import is_hint_ignorable

# ....................{ CLASSES                            }....................
class CauseSleuth(object):
    '''
    **Type-checking error cause sleuth** (i.e., object recursively fabricating
    the human-readable string describing the failure of the pith associated
    with this object to satisfy this PEP-compliant type hint also associated
    with this object).

    Attributes
    ----------
    cause_indent : str
        **Indentation** (i.e., string of zero or more spaces) preceding each
        line of the string returned by this getter if this string spans
        multiple lines *or* ignored otherwise (i.e., if this string is instead
        embedded in the current line).
    exception_prefix : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    func : Callable
        Decorated callable generating this type-checking error.
    hint_sign : Any
        Unsubscripted :mod:`typing` attribute identifying this hint if this hint
        is PEP-compliant *or* ``None`` otherwise.
    hint_childs : Optional[Tuple]
        Either:

        * If this hint is PEP-compliant, the possibly empty tuple of all
          arguments subscripting (indexing) this hint.

        * Else, ``None``.
    pith : Any
        Arbitrary object to be validated.
    random_int: Optional[int]
        **Pseudo-random integer** (i.e., unsigned 32-bit integer
        pseudo-randomly generated by the parent :func:`beartype.beartype`
        wrapper function in type-checking randomly indexed container items by
        the current call to that function) if that function generated such an
        integer *or* ``None`` otherwise (i.e., if that function generated *no*
        such integer). See the same parameter accepted by the higher-level
        :func:`beartype._decor._error.errormain.get_beartype_violation`
        function for further details.

    Attributes (Private)
    ----------
    _hint : Any
        Type hint to validate this object against.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot *ALL* instance variables defined on this object to both:
    # * Prevent accidental declaration of erroneous instance variables.
    # * Minimize space and time complexity.
    __slots__ = (
        'cause_indent',
        'exception_prefix',
        'func',
        'hint_sign',
        'hint_childs',
        'pith',
        'random_int',
        '_hint',
    )


    _INIT_PARAM_NAMES = frozenset((
        'cause_indent',
        'exception_prefix',
        'func',
        'hint',
        'pith',
        'random_int',
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as a set to enable efficient membership testing.
    '''

    # ..................{ INITIALIZERS                       }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Whenever adding, deleting, or renaming any parameter accepted by
    # this method, make similar changes to the "_INIT_PARAM_NAMES" set above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def __init__(
        self,
        func: Callable,
        pith: Any,
        hint: Any,
        cause_indent: str,
        exception_prefix: str,
        random_int: Optional[int],
    ) -> None:
        '''
        Initialize this object.
        '''
        assert callable(func), f'{repr(func)} not callable.'
        assert isinstance(cause_indent, str), (
            f'{repr(cause_indent)} not string.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(random_int, NoneTypeOr[int]), (
            f'{repr(random_int)} not integer or "None".')

        # Classify all passed parameters.
        self.func = func
        self.pith = pith
        self.cause_indent = cause_indent
        self.exception_prefix = exception_prefix
        self.random_int = random_int

        # Nullify all remaining parameters for safety.
        self.hint_sign: Any = None
        self.hint_childs: Tuple = None  # type: ignore[assignment]

        # Classify this hint *AFTER* initializing all parameters above.
        self.hint = hint

    # ..................{ PROPERTIES                         }..................
    @property
    def hint(self) -> Any:
        '''
        Type hint to validate this object against.
        '''

        return self._hint


    @hint.setter
    def hint(self, hint: Any) -> None:
        '''
        Set the type hint to validate this object against.
        '''

        # Sanitize this hint if unsupported by @beartype in its current form
        # (e.g., "numpy.typing.NDArray[...]") to another form supported by
        # @beartype (e.g., "typing.Annotated[numpy.ndarray, beartype.vale.*]").
        hint = sanify_hint_child(
            hint=hint,
            exception_prefix=self.exception_prefix,
        )

        # If this hint is PEP-compliant...
        if is_hint_pep(hint):
            # Arbitrary object uniquely identifying this hint.
            self.hint_sign = get_hint_pep_sign(hint)

            # Tuple of the zero or more arguments subscripting this hint.
            self.hint_childs = get_hint_pep_args(hint)

        # Classify this hint *AFTER* all other assignments above.
        self._hint = hint

    # ..................{ GETTERS                            }..................
    def get_cause_or_none(self) -> Optional[str]:
        '''
        Human-readable string describing the failure of this pith to satisfy
        this PEP-compliant type hint if this pith fails to satisfy this pith
        *or* ``None`` otherwise (i.e., if this pith satisfies this hint).

        Design
        ----------
        This getter is intentionally generalized to support objects both
        satisfying and *not* satisfying hints as equally valid use cases. While
        the parent :func:`.errormain.get_beartype_violation` function
        calling this getter is *always* passed an object *not* satisfying the
        passed hint, this getter is under no such constraints. Why? Because
        this getter is also called to find which of an arbitrary number of
        objects transitively nested in the object passed to
        :func:`.errormain.get_beartype_violation` fails to satisfy the
        corresponding hint transitively nested in the hint passed to that
        function.

        For example, consider the PEP-compliant type hint ``List[Union[int,
        str]]`` describing a list whose items are either integers or strings
        and the list ``list(range(256)) + [False,]`` consisting of the integers
        0 through 255 followed by boolean ``False``. Since this list is a
        standard sequence, the
        :func:`._peperrorsequence.get_cause_or_none_sequence_args_1`
        function must decide the cause of this list's failure to comply with
        this hint by finding the list item that is neither an integer nor a
        string, implemented by by iteratively passing each list item to the
        :func:`._peperrorunion.get_cause_or_none_union` function. Since
        the first 256 items of this list are integers satisfying this hint,
        :func:`._peperrorunion.get_cause_or_none_union` returns
        ``None`` to
        :func:`._peperrorsequence.get_cause_or_none_sequence_args_1`
        before finally finding the non-compliant boolean item and returning the
        human-readable cause.

        Returns
        ----------
        Optional[str]
            Either:

            * If this object fails to satisfy this hint, human-readable string
            describing the failure of this object to do so.
            * Else, ``None``.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If this type hint is either:

            * PEP-noncompliant (e.g., tuple union).
            * PEP-compliant but no getter function has been implemented to
              handle this category of PEP-compliant type hint yet.
        '''

        # Getter function returning the desired string.
        get_cause_or_none: Callable[[CauseSleuth], Optional[str]] = None  # type: ignore[assignment]

        # If this hint is ignorable, all possible objects satisfy this hint,
        # implying this hint *CANNOT* by definition be the cause of this
        # failure. In this case, immediately report None.
        if is_hint_ignorable(self.hint):
            return None
        # Else, this hint is unignorable.
        #
        # If *NO* sign uniquely identifies this hint, this hint is either
        # PEP-noncompliant *OR* only contextually PEP-compliant in certain
        # specific use cases. In either case...
        elif self.hint_sign is None:
            # If this hint is a tuple union...
            if isinstance(self.hint, tuple):
                # Avoid circular import dependencies.
                from beartype._decor._error._errortype import (
                    get_cause_or_none_instance_types_tuple)

                # Defer to the getter function specific to tuple unions.
                get_cause_or_none = get_cause_or_none_instance_types_tuple
            # Else, this hint *NOT* is a tuple union. In this case, assume this
            # hint to be an isinstanceable class. If this is *NOT* the case,
            # the getter deferred to below raises a human-readable exception.
            else:
                # Avoid circular import dependencies.
                from beartype._decor._error._errortype import (
                    get_cause_or_none_instance_type)

                # Defer to the getter function specific to classes.
                get_cause_or_none = get_cause_or_none_instance_type
        # Else, this hint is PEP-compliant.
        #
        # If this hint is neither...
        elif (
            # Originates from an origin type and may thus be shallowly
            # type-checked against that type *AND is either...
            self.hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE and (
                # Unsubscripted *OR*...
                not is_hint_pep_args(self.hint) or
                #FIXME: Remove this branch *AFTER* deeply supporting all
                #hints.
                # Currently unsupported with deep type-checking...
                self.hint_sign not in HINT_SIGNS_SUPPORTED_DEEP
            )
        # Then this hint is both unsubscripted and originating from a standard
        # type origin. In this case, this hint was type-checked shallowly.
        ):
            # Avoid circular import dependencies.
            from beartype._decor._error._errortype import (
                get_cause_or_none_type_instance_origin)

            # Defer to the getter function supporting hints originating
            # from origin types.
            get_cause_or_none = get_cause_or_none_type_instance_origin
        # Else, this hint is either subscripted *OR* unsubscripted but not
        # originating from a standard type origin. In either case, this hint
        # was type-checked deeply.
        else:
            # Avoid circular import dependencies.
            from beartype._decor._error.errormain import (
                PEP_HINT_SIGN_TO_GET_CAUSE_FUNC)

            # Getter function returning the desired string for this attribute
            # if any *OR* "None" otherwise.
            get_cause_or_none = PEP_HINT_SIGN_TO_GET_CAUSE_FUNC.get(
                self.hint_sign, None)  # type: ignore[arg-type]

            # If no such function has been implemented to handle this attribute
            # yet, raise an exception.
            if get_cause_or_none is None:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.exception_prefix} type hint '
                    f'{repr(self.hint)} unsupported (i.e., no '
                    f'"get_cause_or_none_"-prefixed getter function defined '
                    f'for this category of hint).'
                )
            # Else, a getter function has been implemented to handle this
            # attribute.

        # Call this getter function with ourselves and return the string
        # returned by this getter.
        return get_cause_or_none(self)

    # ..................{ PERMUTERS                          }..................
    def permute(self, **kwargs) -> 'CauseSleuth':
        '''
        Shallow copy of this object such that each the passed keyword argument
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword arguments of the same name and type as instance variables of
        this object (e.g., ``hint``, ``pith``).

        Returns
        ----------
        CauseSleuth
            Shallow copy of this object such that each keyword argument
            overwrites the instance variable of the same name in this copy.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If the name of any passed keyword argument is *not* the name of an
            existing instance variable of this object.

        Examples
        ----------
            >>> sleuth = CauseSleuth(
            ...     pith=[42,]
            ...     hint=typing.List[int],
            ...     cause_indent='',
            ...     exception_prefix='List of integers',
            ... )
            >>> sleuth_copy = sleuth.permute(pith=[24,])
            >>> sleuth_copy.pith
            [24,]
            >>> sleuth_copy.hint
            typing.List[int]
        '''

        # For the name of each passed keyword argument...
        for arg_name in kwargs.keys():
            # If this name is *NOT* that of a parameter accepted by the
            # __init__() method, raise an exception.
            if arg_name not in self._INIT_PARAM_NAMES:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.__class__}.__init__() parameter '
                    f'{arg_name} unrecognized.'
                )

        # For the name of each parameter accepted by the __init__() method...
        for arg_name in self._INIT_PARAM_NAMES:
            # If this parameter was *NOT* explicitly passed by the caller,
            # default this parameter to its current value from this object.
            if arg_name not in kwargs:
                kwargs[arg_name] = getattr(self, arg_name)

        # Return a new instance of this class initialized with these arguments.
        return CauseSleuth(**kwargs)
