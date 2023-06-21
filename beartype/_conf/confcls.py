#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration class hierarchy** (i.e., public dataclasses enabling
users to configure :mod:`beartype` with optional runtime behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.__init__` submodule.
This private submodule is *not* intended for direct importation by downstream
callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeConfException
from beartype.typing import (
    TYPE_CHECKING,
    Optional,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcache import (
    beartype_conf_args_to_conf,
    beartype_conf_id_to_conf,
    beartype_conf_lock,
)
from beartype._conf.confenum import BeartypeStrategy

# ....................{ CLASSES                            }....................
#FIXME: Document "claw_is_pep526" in our reST-formatted docos, please.
#FIXME: Refactor to use @dataclass.dataclass once we drop Python 3.7 support.
#Note that doing so will require usage of "frozen=True" to prevent unwanted
#modification of read-only properties.
class BeartypeConf(object):
    '''
    **Beartype configuration** (i.e., self-caching dataclass encapsulating all
    flags, options, settings, and other metadata configuring each type-checking
    operation performed by :mod:`beartype` -- including each decoration of a
    callable or class by the :func:`beartype.beartype` decorator).

    Attributes
    ----------
    _claw_is_pep526 : bool, optional
        :data:`True` only if type-checking **annotated variable assignments**
        (i.e., :pep:`526`-compliant assignments to local, global, class, and
        instance variables annotated by type hints) when importing modules
        under import hooks published by the :mod:`beartype.claw` subpackage. See
        also the :meth:`__new__` method docstring.
    _is_color : Optional[bool]
        Tri-state boolean governing how and whether beartype colours
        **type-checking violations** (i.e.,
        :class:`beartype.roar.BeartypeCallHintViolation` exceptions) with
        POSIX-compliant ANSI escape sequences for readability. Specifically, if
        this boolean is:

        * :data:`False`, beartype *never* colours type-checking violations
          raised by callables configured with this configuration.
        * :data:`True`, beartype *always* colours type-checking violations
          raised by callables configured with this configuration.
        * :data:`None`, beartype conditionally colours type-checking violations
          raised by callables configured with this configuration only when
          standard output is attached to an interactive terminal.
    _is_debug : bool, optional
        :data:`True` only if debugging :mod:`beartype`. See also the
        :meth:`__new__` method docstring.
    _is_pep484_tower : bool, optional
        :data:`True` only if enabling support for the :pep:`484`-compliant
        implicit numeric tower. See also the :meth:`__new__` method docstring.
    _strategy : BeartypeStrategy, optional
        **Type-checking strategy** (i.e., :class:`BeartypeStrategy` enumeration
        member) with which to implement all type-checks in the wrapper function
        dynamically generated by the :func:`beartype.beartype` decorator for
        the decorated callable.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize this slots list with the implementations of:
    # * The __new__() dunder method.
    # * The __eq__() dunder method.
    # * The __hash__() dunder method.
    # * The __repr__() dunder method.
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_claw_is_pep526',
        '_is_color',
        '_is_debug',
        '_is_pep484_tower',
        '_strategy',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _claw_is_pep526: bool
        _is_color: Optional[bool]
        _is_debug: bool
        _is_pep484_tower: bool
        _strategy: BeartypeStrategy

    # ..................{ INSTANTIATORS                      }..................
    # Note that this __new__() dunder method implements the superset of the
    # functionality typically implemented by the __init__() dunder method. Due
    # to Python instantiation semantics, the __init__() dunder method is
    # intentionally left undefined. Why? Because Python unconditionally invokes
    # __init__() if defined, even when the initialization performed by that
    # __init__() has already been performed for the cached instance returned by
    # __new__(). In short, __init__() and __new__() are largely mutually
    # exclusive; one typically defines one or the other but *NOT* both.

    def __new__(
        cls,

        # Optional keyword-only parameters.
        *,

        #FIXME: Uncomment us when implementing O(n) type-checking, please.
        # check_time_max_multiplier: Union[int, None] = 1000,

        claw_is_pep526: bool = True,
        is_color: Optional[bool] = None,
        is_debug: bool = False,
        is_pep484_tower: bool = False,
        strategy: BeartypeStrategy = BeartypeStrategy.O1,
    ) -> 'BeartypeConf':
        '''
        Instantiate this configuration if needed (i.e., if *no* prior
        configuration with these same parameters was previously instantiated)
        *or* reuse that previously instantiated configuration otherwise.

        This dunder methods guarantees beartype configurations to be memoized:

        .. code-block:: python

           >>> from beartype import BeartypeConf
           >>> BeartypeConf() is BeartypeConf()
           True

        This memoization is *not* merely an optimization. The
        :func:`beartype.beartype` decorator internally memoizes the private
        closure it creates and returns on the basis of this configuration,
        which *must* thus also be memoized.

        Parameters
        ----------
        check_time_max_multiplier : Union[int, None] = 1000
            **Deadline multiplier** (i.e., positive integer instructing
            :mod:`beartype` to prematurely halt the current type-check when the
            total running time of the active Python interpreter exceeds this
            integer multiplied by the running time consumed by both the current
            type-check and all prior type-checks *and* the caller also passed a
            non-default ``strategy``) *or* ``None`` if :mod:`beartype` should
            never prematurely halt runtime type-checks.

            Increase this quantity to type-check more container items at a cost
            of decreasing application responsiveness. Likewise, decrease this
            quantity to increase application responsiveness at a cost of
            type-checking fewer container items.

            Ignored when ``strategy`` is :attr:`BeartypeStrategy.O1`, as that
            strategy is already effectively instantaneous; imposing deadlines
            and thus bureaucratic bookkeeping on that strategy would only
            reduce its efficiency for no good reason, which is a bad reason.

            Defaults to 1000, in which case a maximum of %0.1 of the total
            runtime of the active Python process will be devoted to performing
            non-constant :mod:`beartype` type-checks over container items. This
            default has been carefully tuned to strike a reasonable balance
            between runtime type-check coverage and application responsiveness,
            typically enabling smaller containers to be fully type-checked
            without noticeably impacting codebase performance.

            *Theory time.* Let:

            * ``T`` be the total time this interpreter has been running.
            * ``b`` be the total time :mod:`beartype` has spent type-checking in
              this interpreter.

            Clearly, ``b <= T``. Generally, ``b <<<<<<< T`` (i.e., type-checks
            consume much less time than the total time consumed by the process).
            However, it's all too easy to exhibit worst-case behaviour of
            ``b ~= T`` (i.e., type-checks consume most of the total time). How?
            By passing the :func:`beartype.door.is_bearable` tester an absurdly
            large nested container subject to the non-default ``strategy`` of
            :attr:`BeartypeStrategy.On`.

            This deadline multiplier mitigates that worst-case behaviour.
            Specifically, :mod:`beartype` will prematurely halt any iterative
            type-check across a container when this constraint is triggered:

            .. code-block:: python

               b * check_time_max_multiplier >= T
        claw_is_pep526 : bool, optional
            :data:`True` only if implicitly type-checking **annotated variable
            assignments** (i.e., :pep:`526`-compliant assignments to local,
            global, class, and instance variables annotated by type hints) by
            injecting calls to the :func:`beartype.door.die_if_unbearable`
            function immediately *after* those assignments when importing
            modules under import hooks published by the :mod:`beartype.claw`
            subpackage. Enabling this boolean:

            * Effectively augments :mod:`beartype` into a full-blown **hybrid
              runtime-static type-checker** (i.e., performing both standard
              runtime type-checking *and* non-standard static type-checking at
              runtime).
            * Adds negligible runtime overhead to all annotated variable
              assignments in all modules imported under those import hooks.
              Although the *individual* cost of this overhead for any given
              assignment is negligible, the *aggregate* cost across all such
              assignments could be non-negligible in worst-case use cases.

            Ideally, this boolean should only be disabled for a small subset of
            performance-sensitive modules *after* profiling those modules to
            suffer performance regressions under import hooks published by the
            :mod:`beartype.claw` subpackage. Defaults to :data:`True`.
        is_color : Optional[bool]
            Tri-state boolean governing how and whether beartype colours
            **type-checking violations** (i.e.,
            :class:`beartype.roar.BeartypeCallHintViolation` exceptions) with
            POSIX-compliant ANSI escape sequences for readability. Specifically,
            if this boolean is:

            * :data:`False`, beartype *never* colours type-checking violations
              raised by callables configured with this configuration.
            * :data:``True`, beartype *always* colours type-checking violations
              raised by callables configured with this configuration.
            * :data:`None`, beartype conditionally colours type-checking
              violations raised by callables configured with this configuration
              only when standard output is attached to an interactive terminal.

            Defaults to :data:`None`.
        is_debug : bool, optional
            :data:`True` only if debugging :mod:`beartype`. Enabling this
            boolean:

            * Prints the definition (including both the signature and body) of
              each type-checking wrapper function dynamically generated by
              :mod:`beartype` to standard output.
            * Caches the body of each type-checking wrapper function dynamically
              generated by :mod:`beartype` with the standard :mod:`linecache`
              module, enabling these function bodies to be introspected at
              runtime *and* improving the readability of tracebacks whose call
              stacks contain one or more calls to these
              :func:`beartype.beartype`-decorated functions.
            * Appends to the declaration of each **hidden parameter** (i.e.,
              whose name is prefixed by ``"__beartype_"`` and whose value is
              that of an external attribute internally referenced in the body of
              that function) the machine-readable representation of the initial
              value of that parameter, stripped of newlines and truncated to a
              hopefully sensible length. Since the
              :func:`beartype._util.text.utiltextrepr.represent_object` function
              called to do so is shockingly slow, these substrings are
              conditionally embedded in the returned signature *only* when
              enabling this boolean.

            Defaults to :data:`False`.
        is_pep484_tower : bool, optional
            :data:`True` only if enabling support for the :pep:`484`-compliant
            **implicit numeric tower** (i.e., lossy conversion of integers to
            floating-point numbers as well as both integers and floating-point
            numbers to complex numbers). Specifically, enabling this instructs
            :mod:`beartype` to automatically expand:

            * All :class:`float` type hints to ``float | int``, thus implicitly
              accepting both integers and floating-point numbers for objects
              annotated as only accepting floating-point numbers.
            * All :class:`complex` type hints to ``complex | float | int``, thus
              implicitly accepting integers, floating-point, and complex numbers
              for objects annotated as only accepting complex numbers.

            Defaults to :data:`False` to minimize precision error introduced by
            lossy conversions from integers to floating-point numbers to complex
            numbers. Since most integers do *not* have exact representations
            as floating-point numbers, each conversion of an integer into a
            floating-point number typically introduces a small precision error
            that accumulates over multiple conversions and operations into a
            larger precision error. Enabling this improves the usability of
            public APIs at a cost of introducing precision errors.
        strategy : BeartypeStrategy, optional
            **Type-checking strategy** (i.e., :class:`BeartypeStrategy`
            enumeration member) with which to implement all type-checks in the
            wrapper function dynamically generated by the
            :func:`beartype.beartype` decorator for the decorated callable.
            Defaults to :attr: `BeartypeStrategy.O1`, the ``O(1)`` constant-time
            strategy.

        Returns
        ----------
        BeartypeConf
            Beartype configuration memoized with these parameters.

        Raises
        ----------
        BeartypeConfException
            If either:

            * ``is_color`` is *not* a tri-state boolean.
            * ``is_debug`` is *not* a boolean.
            * ``is_pep484_tower`` is *not* a boolean.
            * ``strategy`` is *not* a :class:`BeartypeStrategy` enumeration
              member.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize this logic with BeartypeConf.__hash__().
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Efficiently hashable tuple of these parameters (in arbitrary order).
        beartype_conf_args = (
            claw_is_pep526,
            is_color,
            is_debug,
            is_pep484_tower,
            strategy,
        )

        # In a non-reentrant thread lock specific to beartype configurations...
        #
        # Note that this lock is potentially overkill and thus unnecessary.
        # Nonetheless, since the number of beartype configurations instantiated
        # over the lifetime of the average Python interpreter is small, since
        # non-reentrant thread locks are reasonably fast to enter, and since the
        # cost of race conditions is high, this lock does no real-world harm and
        # may actually do a great deal of real-world good. Safety first, all!
        with beartype_conf_lock:
            # If this method has already instantiated a configuration with these
            # parameters, return that configuration for consistency and
            # efficiency.
            if beartype_conf_args in beartype_conf_args_to_conf:
                return beartype_conf_args_to_conf[beartype_conf_args]
            # Else, this method has yet to instantiate a configuration with
            # these parameters. In this case, do so below (and cache that
            # configuration).
            #
            # If "claw_is_pep526" is *NOT* a boolean, raise an exception.
            elif not isinstance(claw_is_pep526, bool):
                raise BeartypeConfException(
                    f'Beartype configuration parameter "claw_is_pep526" '
                    f'value {repr(claw_is_pep526)} not boolean.'
                )
            # Else, "claw_is_pep526" is a boolean.
            #
            # If "is_color" is *NOT* a tri-state boolean, raise an exception.
            elif not isinstance(is_color, NoneTypeOr[bool]):
                raise BeartypeConfException(
                    f'Beartype configuration parameter "is_color" '
                    f'value {repr(is_color)} not tri-state boolean '
                    f'(i.e., "True", "False", or "None").'
                )
            # Else, "is_color" is a tri-state boolean, raise an exception.
            #
            # If "is_debug" is *NOT* a boolean, raise an exception.
            elif not isinstance(is_debug, bool):
                raise BeartypeConfException(
                    f'Beartype configuration parameter "is_debug" '
                    f'value {repr(is_debug)} not boolean.'
                )
            # Else, "is_debug" is a boolean.
            #
            # If "is_pep484_tower" is *NOT* a boolean, raise an exception.
            elif not isinstance(is_pep484_tower, bool):
                raise BeartypeConfException(
                    f'Beartype configuration parameter "is_pep484_tower" '
                    f'value {repr(is_debug)} not boolean.'
                )
            # Else, "is_pep484_tower" is a boolean.
            #
            # If "strategy" is *NOT* an enumeration member, raise an exception.
            elif not isinstance(strategy, BeartypeStrategy):
                raise BeartypeConfException(
                    f'Beartype configuration parameter "strategy" '
                    f'value {repr(strategy)} not '
                    f'"beartype.BeartypeStrategy" enumeration member.'
                )
            # Else, "strategy" is an enumeration member.

            # Instantiate a new configuration of this type.
            self = super().__new__(cls)

            # Classify all passed parameters with this configuration.
            self._claw_is_pep526 = claw_is_pep526
            self._is_color = is_color
            self._is_debug = is_debug
            self._is_pep484_tower = is_pep484_tower
            self._strategy = strategy

            # Cache this configuration with all relevant dictionary singletons.
            beartype_conf_args_to_conf[beartype_conf_args] = self
            beartype_conf_id_to_conf[id(self)] = self
            # print(f'Caching beartype configuration {repr(self)} as {id(self)}...')

        # Return this configuration.
        return self

    # ..................{ PROPERTIES                         }..................
    # Read-only public properties effectively prohibiting mutation of their
    # underlying private attributes.

    @property
    def claw_is_pep526(self) -> bool:
        '''
        :data:`True` only if type-checking **annotated variable assignments**
        (i.e., :pep:`526`-compliant assignments to local, global, class, and
        instance variables annotated by type hints) when importing modules
        under import hooks published by the :mod:`beartype.claw` subpackage.

        See Also
        ----------
        :meth:`__new__`
            Further details.
        '''

        return self._claw_is_pep526


    @property
    def is_color(self) -> Optional[bool]:
        '''
        Tri-state boolean governing how and whether beartype colours
        **type-checking violations** (i.e.,
        :class:`beartype.roar.BeartypeCallHintViolation` exceptions) with
        POSIX-compliant ANSI escape sequences for readability. Specifically, if
        this boolean is:

        * :data:`False`, beartype *never* colours type-checking violations
          raised by callables configured with this configuration.
        * :data:`True`, beartype *always* colours type-checking violations
          raised by callables configured with this configuration.
        * :data:`None`, beartype conditionally colours type-checking violations
          raised by callables configured with this configuration only when
          standard output is attached to an interactive terminal.
        '''

        return self._is_color


    @property
    def is_debug(self) -> bool:
        '''
        :data:`True` only if debugging :mod:`beartype`.

        See Also
        ----------
        :meth:`__new__`
            Further details.
        '''

        return self._is_debug


    @property
    def is_pep484_tower(self) -> bool:
        '''
        :data:`True` only if enabling support for the :pep:`484`-compliant
        implicit numeric tower.

        See Also
        ----------
        :meth:`__new__`
            Further details.
        '''

        return self._is_pep484_tower


    @property
    def strategy(self) -> BeartypeStrategy:
        '''
        **Type-checking strategy** (i.e., :class:`BeartypeStrategy`
        enumeration member) with which to implement all type-checks in the
        wrapper function dynamically generated by the
        :func:`beartype.beartype` decorator for the decorated callable.
        '''

        return self._strategy

    # ..................{ DUNDERS                            }..................
    def __eq__(self, other: object) -> bool:
        '''
        **Beartype configuration equality comparator.**

        Parameters
        ----------
        other : object
            Arbitrary object to be compared for equality against this
            configuration.

        Returns
        ----------
        Union[bool, type(NotImplemented)]
            Either:

            * If this other object is also a beartype configuration, either:

              * If these configurations share the same settings, ``True``.
              * Else, ``False``.

            * Else, ``NotImplemented``.

        See Also
        ----------
        :func:`_hash_beartype_conf`
            Further details.
        '''

        # If this other object is also a beartype configuration...
        if isinstance(other, BeartypeConf):
            # Return true only if these configurations share the same settings.
            return (
                self._claw_is_pep526 == other._claw_is_pep526 and
                self._is_color == other._is_color and
                self._is_debug == other._is_debug and
                self._is_pep484_tower == other._is_pep484_tower and
                self._strategy == other._strategy
            )
        # Else, this other object is *NOT* also a beartype configuration.

        # In this case, return the standard singleton informing Python that
        # this equality comparator fails to support this comparison.
        return NotImplemented


    def __hash__(self) -> int:
        '''
        **Hash** (i.e., non-negative integer quasi-uniquely identifying this
        beartype configuration with respect to hashable container membership).

        Returns
        ----------
        int
            Hash of this configuration.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize this logic with BeartypeConf.__new__().
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Return the hash of a tuple containing these parameters in an
        # arbitrary (albeit well-defined) order.
        #
        # Note this has been profiled to be the optimal means of hashing object
        # attributes in Python, where "optimal" means:
        # * Optimally fast. CPython in particular optimizes the creation and
        #   garbage collection of "small" tuples, where "small" is ill-defined
        #   but almost certainly applies here.
        # * Optimally uniformly distributed, thus minimizing the likelihood of
        #   expensive hash collisions.
        return hash((
            self._claw_is_pep526,
            self._is_color,
            self._is_debug,
            self._is_pep484_tower,
            self._strategy,
        ))


    def __repr__(self) -> str:
        '''
        **Beartype configuration representation** (i.e., machine-readable
        string which, when dynamically evaluated as code, restores access to
        this exact configuration object).

        Returns
        ----------
        str
            Representation of this configuration.
        '''

        return (
            f'{self.__class__.__name__}('
            f'claw_is_pep526={repr(self._claw_is_pep526)}, '
            f'is_color={repr(self._is_color)}, '
            f'is_debug={repr(self._is_debug)}, '
            f'is_pep484_tower={repr(self._is_pep484_tower)}, '
            f'strategy={repr(self._strategy)}'
            f')'
        )

# ....................{ GLOBALS                            }....................
# This global is intentionally defined *AFTER* all other attributes above, which
# this global implicitly assumes to be defined.
BEARTYPE_CONF_DEFAULT = BeartypeConf()
'''
**Default beartype configuration** (i.e., :class:`BeartypeConf` class
instantiated with *no* parameters and thus default parameters), globalized to
trivially optimize external access to this configuration throughout this
codebase.

Note that this global is *not* publicized to end users, who can simply
instantiate ``BeartypeConf()`` to obtain the same singleton.
'''
