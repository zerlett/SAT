import logging

_LOGGER = logging.getLogger(__name__)


class MinimumSetpoint:
    def __init__(self, adjustment: float, configured_minimum_setpoint: float):
        """Initialize the MinimumSetpoint class."""
        self._setpoint = None
        self._adjustments = 0
        self._adjustment_factor = adjustment

        self.current_minimum_setpoint = None
        self.configured_minimum_setpoint: float = configured_minimum_setpoint

    def warming_up(self, flame_active: bool, boiler_temperature: float) -> None:
        """Adjust the setpoint to trigger the boiler flame during warm-up if needed."""
        if flame_active:
            _LOGGER.debug("Flame is already active. No adjustment needed.")
            return

        self._adjustments = 0
        self.current_minimum_setpoint = boiler_temperature + 10
        _LOGGER.debug("Setpoint adjusted for warm-up: %.1f°C", self.current_minimum_setpoint)

    def calculate(self, requested_setpoint: float, boiler_temperature: float) -> None:
        """Calculate and adjust the minimum setpoint gradually toward the requested setpoint."""
        if self.current_minimum_setpoint is None:
            self.current_minimum_setpoint = boiler_temperature
            _LOGGER.debug("Initialized minimum setpoint to boiler temperature: %.1f°C", boiler_temperature)

        old_setpoint = self.current_minimum_setpoint
        adjustment_factor = 0.0 if self._adjustments < 6 else self._adjustment_factor

        # Gradually adjust the setpoint toward the requested setpoint
        if self.current_minimum_setpoint < requested_setpoint:
            self.current_minimum_setpoint = min(self.current_minimum_setpoint + adjustment_factor, requested_setpoint)
        else:
            self.current_minimum_setpoint = max(self.current_minimum_setpoint - adjustment_factor, requested_setpoint)

        _LOGGER.debug(
            "Changing minimum setpoint: %.1f°C => %.1f°C (requested: %.1f°C, adjustment factor: %.1f)",
             old_setpoint, self.current_minimum_setpoint, requested_setpoint, adjustment_factor
        )

        self._adjustments += 1

    def current(self) -> float:
        """Get the current minimum setpoint."""
        return self.current_minimum_setpoint if self.current_minimum_setpoint is not None else self.configured_minimum_setpoint
