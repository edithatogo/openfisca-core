from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import os
import warnings

import numpy
import psutil

from openfisca_core import (
    commons,
    data_storage as storage,
    errors,
    indexed_enums as enums,
    periods,
    types,
)

from . import types as t


class Holder:
    """A holder keeps tracks of a variable values after they have been calculated, or set as an input."""

    def __init__(self, variable, population) -> None:
        self.population = population
        self.variable = variable
        self.simulation = population.simulation
        self._eternal = self.variable.definition_period == periods.DateUnit.ETERNITY
        self._memory_storage = storage.InMemoryStorage(is_eternal=self._eternal)

        # By default, do not activate on-disk storage, or variable dropping
        self._disk_storage = None
        self._on_disk_storable = False
        self._do_not_store = False
        if self.simulation and self.simulation.memory_config:
            if (
                self.variable.name
                not in self.simulation.memory_config.priority_variables
            ):
                self._disk_storage = self.create_disk_storage()
                self._on_disk_storable = True
            if self.variable.name in self.simulation.memory_config.variables_to_drop:
                self._do_not_store = True
        # Periods whose values were set via set_input (not formula cache).
        self._user_input_periods: set = set()

    def clone(self, population: t.CorePopulation) -> t.Holder:
        """Copy the holder just enough to be able to run a new simulation without modifying the original simulation."""
        new = commons.empty_clone(self)
        new_dict = new.__dict__

        for key, value in self.__dict__.items():
            if key not in ("population", "formula", "simulation"):
                new_dict[key] = value

        new_dict["_user_input_periods"] = self._user_input_periods.copy()
        new_dict["population"] = population
        new_dict["simulation"] = population.simulation

        return new

    def create_disk_storage(self, directory=None, preserve=False):
        if directory is None:
            directory = self.simulation.data_storage_dir
        storage_dir = os.path.join(directory, self.variable.name)
        if not os.path.isdir(storage_dir):
            os.mkdir(storage_dir)
        return storage.OnDiskStorage(
            storage_dir,
            self._eternal,
            preserve_storage_dir=preserve,
        )

    def delete_arrays(self, period=None) -> None:
        """If ``period`` is ``None``, remove all known values of the variable.

        If ``period`` is not ``None``, only remove all values for any period included in period (e.g. if period is "2017", values for "2017-01", "2017-07", etc. would be removed)
        """
        self._memory_storage.delete(period)
        if self._disk_storage:
            self._disk_storage.delete(period)
        if period is None:
            self._user_input_periods.clear()
        else:
            period = periods.period(period)
            self._user_input_periods = {
                known
                for known in self._user_input_periods
                if not period.contains(known)
            }

    def get_array(self, period):
        """Get the value of the variable for the given period.

        If the value is not known, return ``None``.
        """
        if self.variable.is_neutralized:
            return self.default_array()
        value = self._memory_storage.get(period)
        if value is not None:
            return value
        if self._disk_storage:
            return self._disk_storage.get(period)
        return None

    def get_memory_usage(self) -> t.MemoryUsage:
        """Get data about the virtual memory usage of the Holder.

        Returns:
            Memory usage data.

        Examples:
            >>> from pprint import pprint

            >>> from openfisca_core import (
            ...     entities,
            ...     populations,
            ...     simulations,
            ...     taxbenefitsystems,
            ...     variables,
            ... )

            >>> entity = entities.Entity("", "", "", "")

            >>> class MyVariable(variables.Variable):
            ...     definition_period = periods.DateUnit.YEAR
            ...     entity = entity
            ...     value_type = int

            >>> population = populations.Population(entity)
            >>> variable = MyVariable()
            >>> holder = Holder(variable, population)

            >>> tbs = taxbenefitsystems.TaxBenefitSystem([entity])
            >>> entities = {entity.key: population}
            >>> simulation = simulations.Simulation(tbs, entities)
            >>> holder.simulation = simulation

            >>> pprint(holder.get_memory_usage(), indent=3)
            {  'cell_size': nan,
               'dtype': <class 'numpy.int32'>,
               'nb_arrays': 0,
               'nb_cells_by_array': 0,
               'total_nb_bytes': 0...

        """
        usage = t.MemoryUsage(
            nb_cells_by_array=self.population.count,
            dtype=self.variable.dtype,
        )

        usage.update(self._memory_storage.get_memory_usage())

        if self.simulation.trace:
            nb_requests = self.simulation.tracer.get_nb_requests(self.variable.name)
            usage.update(
                {
                    "nb_requests": nb_requests,
                    "nb_requests_by_array": (
                        nb_requests / float(usage["nb_arrays"])
                        if usage["nb_arrays"] > 0
                        else numpy.nan
                    ),
                },
            )

        return usage

    def get_known_periods(self):
        """Get the list of periods the variable value is known for."""
        return list(self._memory_storage.get_known_periods()) + list(
            self._disk_storage.get_known_periods() if self._disk_storage else [],
        )

    def set_input(
        self,
        period: types.Period,
        array: numpy.ndarray | Sequence[Any],
    ) -> numpy.ndarray | None:
        """Set a Variable's array of values of a given Period.

        Args:
            period: The period at which the value is set.
            array: The input value for the variable.

        Returns:
            The set input array.

        Note:
            If a ``set_input`` property has been set for the variable, this
            method may accept inputs for periods not matching the
            ``definition_period`` of the Variable. To read
            more about this, check the `documentation`_.

        Examples:
            >>> from openfisca_core import entities, populations, variables

            >>> entity = entities.Entity("", "", "", "")

            >>> class MyVariable(variables.Variable):
            ...     definition_period = periods.DateUnit.YEAR
            ...     entity = entity
            ...     value_type = float

            >>> variable = MyVariable()

            >>> population = populations.Population(entity)
            >>> population.count = 2

            >>> holder = Holder(variable, population)
            >>> holder.set_input("2018", numpy.array([12.5, 14]))
            >>> holder.get_array("2018")
            array([12.5, 14. ], dtype=float32)

            >>> holder.set_input("2018", [12.5, 14])
            >>> holder.get_array("2018")
            array([12.5, 14. ], dtype=float32)

        .. _documentation:
            https://openfisca.org/doc/coding-the-legislation/35_periods.html#set-input-automatically-process-variable-inputs-defined-for-periods-not-matching-the-definition-period

        """
        period = periods.period(period)

        if period.unit == periods.DateUnit.ETERNITY and not self._eternal:
            error_message = os.linesep.join(
                [
                    "Unable to set a value for variable {1} for {0}.",
                    "{1} is only defined for {2}s. Please adapt your input.",
                ],
            ).format(
                periods.DateUnit.ETERNITY.upper(),
                self.variable.name,
                self.variable.definition_period,
            )
            raise errors.PeriodMismatchError(
                self.variable.name,
                period,
                self.variable.definition_period,
                error_message,
            )
        if self.variable.is_neutralized:
            warning_message = f"You cannot set a value for the variable {self.variable.name}, as it has been neutralized. The value you provided ({array}) will be ignored."
            return warnings.warn(warning_message, Warning, stacklevel=2)
        if self.variable.value_type in (float, int) and isinstance(array, str):
            array = commons.eval_expression(array)
        # Mark every ``_set`` performed while handling this call as user input
        # (including period-casting helpers and custom ``variable.set_input``).
        previous_recording = getattr(self, "_recording_user_input", False)
        self._recording_user_input = True
        try:
            if self.variable.set_input:
                return self.variable.set_input(self, period, array)
            return self._set(period, array, as_input=True)
        finally:
            self._recording_user_input = previous_recording

    def _to_array(self, value):
        if not isinstance(value, numpy.ndarray):
            value = numpy.asarray(value)
        if value.ndim == 0:
            # 0-dim arrays are casted to scalar when they interact with float. We don't want that.
            value = value.reshape(1)
        if len(value) != self.population.count:
            msg = f'Unable to set value "{value}" for variable "{self.variable.name}", as its length is {len(value)} while there are {self.population.count} {self.population.entity.plural} in the simulation.'
            raise ValueError(
                msg,
            )
        if self.variable.value_type == enums.Enum:
            value = self.variable.possible_values.encode(value)
        if value.dtype != self.variable.dtype:
            try:
                value = value.astype(self.variable.dtype)
            except ValueError:
                msg = f'Unable to set value "{value}" for variable "{self.variable.name}", as the variable dtype "{self.variable.dtype}" does not match the value dtype "{value.dtype}".'
                raise ValueError(
                    msg,
                )
        return value

    def _set(self, period, value, *, as_input: bool = False) -> None:
        value = self._to_array(value)
        if not self._eternal:
            if period is None:
                msg = (
                    f"A period must be specified to set values, except for variables with "
                    f"{periods.DateUnit.ETERNITY.upper()} as as period_definition."
                )
                raise ValueError(
                    msg,
                )
            if self.variable.definition_period != period.unit or period.size > 1:
                name = self.variable.name
                period_size_adj = (
                    f"{period.unit}"
                    if (period.size == 1)
                    else f"{period.size}-{period.unit}s"
                )
                error_message = os.linesep.join(
                    [
                        f'Unable to set a value for variable "{name}" for {period_size_adj}-long period "{period}".',
                        f'"{name}" can only be set for one {self.variable.definition_period} at a time. Please adapt your input.',
                        f'If you are the maintainer of "{name}", you can consider adding it a set_input attribute to enable automatic period casting.',
                    ],
                )

                raise errors.PeriodMismatchError(
                    self.variable.name,
                    period,
                    self.variable.definition_period,
                    error_message,
                )

        should_store_on_disk = (
            self._on_disk_storable
            and self._memory_storage.get(period) is None
            and psutil.virtual_memory().percent  # If there is already a value in memory, replace it and don't put a new value in the disk storage
            >= self.simulation.memory_config.max_memory_occupation_pc
        )

        if should_store_on_disk:
            self._disk_storage.put(value, period)
        else:
            self._memory_storage.put(value, period)
        if as_input or getattr(self, "_recording_user_input", False):
            self._user_input_periods.add(period)

    def is_input(self, period) -> bool:
        """Return whether a value for ``period`` was set via :meth:`set_input`.

        Distinguishes explicit user input (including explicit zeros) from values
        that come from variable defaults or formula cache. Values stored only by
        :meth:`put_in_cache` are not considered inputs.

        Args:
            period: Period to inspect (string or :class:`~openfisca_core.periods.Period`).

        Returns:
            True if at least one matching period was set through :meth:`set_input`.

        """
        period = periods.period(period)
        if period in self._user_input_periods:
            return True
        # Accept a wider query period when the stored inputs are elementary periods.
        if period.unit != self.variable.definition_period or period.size > 1:
            try:
                subperiods = period.get_subperiods(self.variable.definition_period)
            except ValueError:
                return False
            return any(
                sub_period in self._user_input_periods for sub_period in subperiods
            )
        return False

    def get_value_state(self, period) -> str:
        """Return ``"explicit"`` if the value was set as input, else ``"default"``.

        ``"default"`` means the value was not supplied via :meth:`set_input` for
        this period: the engine may still return the variable default or a
        calculated value, but that is not tagged as user-provided input.

        This is a narrow API for partial-input / screener workflows (see
        https://github.com/openfisca/openfisca-core/issues/1380). It does not
        change calculation semantics.

        """
        return "explicit" if self.is_input(period) else "default"

    def put_in_cache(self, value, period) -> None:
        if self._do_not_store:
            return

        if (
            self.simulation.opt_out_cache
            and self.simulation.tax_benefit_system.cache_blacklist
            and self.variable.name in self.simulation.tax_benefit_system.cache_blacklist
        ):
            return

        self._set(period, value)

    def default_array(self):
        """Return a new array of the appropriate length for the entity, filled with the variable default values."""
        return self.variable.default_array(self.population.count)
