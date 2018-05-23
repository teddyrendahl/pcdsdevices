"""
EVR objects
"""
from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO


class Trigger(Device):
    """
    Class for an individual Trigger
    """
    eventcode = Cpt(EpicsSignal, ':TEC')
    label = Cpt(EpicsSignal, ':TCTL.DESC')
    ns_delay = Cpt(EpicsSignal, ':TDES')
    polarity = Cpt(EpicsSignal, ':TPOL')
    width = Cpt(EpicsSignal, ':TWID')
    enable_cmd = Cpt(EpicsSignal, ':TCTL')

    _default_configuration_attrs = ['ns_delay', 'width', 'label',
                                    'polarity', 'eventcode']

    def enable(self):
        """Enable the trigger"""
        self.enable_cmd.put(1)

    def disable(self):
        """Disable the trigger"""
        self.enable_cmd.put(0)
