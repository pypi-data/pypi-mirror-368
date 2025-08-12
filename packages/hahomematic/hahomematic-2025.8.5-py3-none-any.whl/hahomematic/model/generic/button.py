"""Module for data points implemented using the button category."""

from __future__ import annotations

from hahomematic.const import DataPointCategory
from hahomematic.decorators import inspector
from hahomematic.model.generic.data_point import GenericDataPoint


class DpButton(GenericDataPoint[None, bool]):
    """
    Implementation of a button.

    This is a default data point that gets automatically generated.
    """

    __slots__ = ()

    _category = DataPointCategory.BUTTON
    _validate_state_change = False

    @inspector()
    async def press(self) -> None:
        """Handle the button press."""
        await self.send_value(value=True)
