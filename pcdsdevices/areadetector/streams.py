from ophyd import (EpicsSignal, EpicsSignalRO, Component as Cpt,
                   FormattedComponent as FCpt)
from .plugins import (ColorConvPlugin, ImagePlugin, OverlayPlugin,
                      ProcessPlugin, ROIPlugin)


class ImageStream(ImagePlugin):
    """
    The set of plugins loaded with a PCDS AreaDetector Stream
    """
    # Plugins
    cc = Cpt(ColorConvPlugin, 'CC:')
    roi = Cpt(ROIPlugin, 'ROI:')
    proc = Cpt(ProccessPlugin, 'Proc:')
    over = Cpt(StreamOverlayPlugin, 'Over:')
    # Desired parameters for automated configuration of stream
    stream_type = Cpt(EpicsSignalRO, 'StreamType', doc="Stream Purpose")
    stream_width = Cpt(EpicsSignal, 'StreamWidth',
                       doc="Desired width of image")
    stream_height = Cpt(EpicsSignal, 'StreamHeight',
                        doc='Desired height of image')
    stream_rate = Cpt(EpicsSignal, 'StreamRate',
                      doc='Desired acquisition rate')


class StreamOverlayPlugin(OverlayPlugin):
    """OverlayPlugin structure for Stream"""
    overlay_1 = FCpt(Overlay, '{self.stream_prefix}Box1:')
    overlay_2 = FCpt(Overlay, '{self.stream_prefix}Box2:')
    overlay_3 = FCpt(Overlay, '{self.stream_prefix}Box3:')
    overlay_4 = FCpt(Overlay, '{self.stream_prefix}Box4:')
    overlay_1 = FCpt(Overlay, '{self.stream_prefix}Cross1:')
    overlay_2 = FCpt(Overlay, '{self.stream_prefix}Cross2:')
    overlay_3 = FCpt(Overlay, '{self.stream_prefix}Cross3:')
    overlay_4 = FCpt(Overlay, '{self.stream_prefix}Cross4:')

    def __init__(self, prefix, *, stream_prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Try and be smart about where we grab the stream_prefix from
        if not stream_prefix:
            # Grab the prefix of the parent if it exists
            if self.parent:
                stream_prefix = self.parent.prefix
            else:
                raise ValueError("If loading StreamOverlayPlugin alone, must "
                                 "enter 'stream_prefix'")
        self.stream_prefix= stream_prefix
