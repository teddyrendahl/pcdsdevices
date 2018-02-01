import logging

from ophyd.utils import LimitError
from ophyd import EpicsMotor, Component, EpicsSignal, Signal

from .mv_interface import FltMvInterface


logger = logging.getLogger(__name__)


class EpicsMotor(EpicsMotor, FltMvInterface):
    """
    EpicsMotor for PCDS

    This incapsulates all motor record implementations standard for PCDS,
    including but not exclusive to Pico, Piezo, IMS and Newport motors. While
    these types of motors may have additional records and configuration
    requirements, this class is meant to handle the shared records between
    them.

    Notes
    -----
    The purpose of this class is to account for the differences between the
    community Motor Record and the PCDS Motor Record. The points that matter
    for this class are:

        1. The ``TDIR`` field does not exist on the PCDS implementation. This
        indicates what direction the motor has travelled last. To account for
        this difference, we use the `_pos_changed` callback to keep track of
        which direction we believe the motor to be travelling and store this in
        a simple ``ophyd.Signal``
        2. Instead of using the limit fields on the setpoint PV, the EPICS
        motor class has the ``LLM`` and ``HLM`` soft limit fields for
        convenient usage. Unfortunately, pyepics does not update its internal
        cache of the limits after the first get attempt. We therefore disregard
        the internal limits of the PV and use the soft limit records
        exclusively.
    """
    # Reimplemented because pyepics does not recognize when the limits have
    # been changed without a re-connection of the PV. Instead we trust the soft
    # limits records
    user_setpoint = Component(EpicsSignal, ".VAL", limits=False)
    # Additional soft limit configurations
    low_soft_limit = Component(EpicsSignal, ".LLM")
    high_soft_limit = Component(EpicsSignal, ".HLM")
    # These limit switch fields are monitored to avoid any `caget` calls in
    # subscriptions. In particular, ophyd.EpicsMotor._move_changed makes calls
    # to either limit switch depending on direction of motion
    low_limit_switch = Component(EpicsSignalRO, ".LLS", auto_monitor=True)
    high_limit_switch = Component(EpicsSignalRO, ".HLS", auto_monitor=True)
    # Disable missing field that our EPICS motor record lacks
    # This attribute is tracked by the _pos_changed callback
    direction_of_travel = Component(Signal)

    @property
    def low_limit(self):
        """
        Returns the lower soft limit for the motor.

        Returns
        -------
        low_limit : float
            The lower soft limit of the motor.
        """
        return self.low_soft_limit.value

    @low_limit.setter
    def low_limit(self, value):
        """
        Sets the low limit for the motor.

        Returns
        -------
        status : StatusObject
            Status object of the set.
        """
        return self.low_soft_limit.put(value)

    @property
    def high_limit(self):
        """
        Returns the higher soft limit for the motor.

        Returns
        -------
        high_limit : float
            The higher soft limit of the motor.
        """
        return self.high_soft_limit.value

    @high_limit.setter
    def high_limit(self, value):
        """
        Sets the high limit for the motor.

        Returns
        -------
        status : StatusObject
            Status object of the set.
        """
        return self.high_soft_limit.put(value)

    @property
    def limits(self):
        """
        Returns the soft limits of the motor.

        Returns
        -------
        limits : tuple
            Soft limits of the motor.
        """
        return (self.low_limit, self.high_limit)

    @limits.setter
    def limits(self, limits):
        """
        Sets the limits for the motor.

        Parameters
        ----------
        limits : tuple
            Desired low and high limits.
        """
        self.low_limit = limits[0]
        self.high_limit = limits[1]

    def check_value(self, value):
        """
        Check if the value is within the soft limits of the motor.

        Raises
        ------
        ValueError
        """
        # First check that the user has returned a valid EPICS value. It will
        # not consult the limits of the PV itself because limits=False
        super().check_value(value)
        # Find the soft limit values from EPICS records and check that this
        # command will be accepted by the motor
        low_limit, high_limit = self.limits

        if not (low_limit <= value <= high_limit):
            raise LimitError("Value {} outside of range: [{}, {}]"
                             .format(value, low_limit, high_limit))

    def _pos_changed(self, timestamp=None, old_value=None,
                     value=None, **kwargs):
        # Store the internal travelling direction of the motor to account for
        # the fact that our EPICS motor does not have DIR field
        if None not in (value, old_value):
            self.direction_of_travel.put(int(value > old_value))
        # Pass information to PositionerBase
        super()._pos_changed(timestamp=timestamp, old_value=old_value,
                             value=value, **kwargs)
