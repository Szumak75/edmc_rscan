# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: dialogs helper classes.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class DialogKeys(object, metaclass=ReadOnlyClass):
    """Keys container class for dialogs."""

    BODIES = "_bodies_"
    BUTTON = "_button_"
    CLIP = "_clip_"
    CLOSED = "_closed_"
    EUCLID = "_euclid_"
    FDATA = "_fdata_"
    FONTS = "_fonts_"
    ID = "_id_"
    MATH = "_math_"
    PARENT = "_parent_"
    QTH = "_rscan_qth_"
    RADIUS = "_radius_"
    RDATA = "_rscan_data_"
    RTH = "_rscan_th_"
    SBUTTON = "_sbutton_"
    SCROLLBAR = "_scrollbar_"
    SPANEL = "_spanel_"
    STARS = "_stars_"
    START = "_start_"
    STATUS = "_status_"
    SYSTEM = "_system_"
    TEXT = "text"
    TOOLS = "_tools_"
    TT_TEXT = "_tool_tip_text_"
    TW = "_tw_"
    WAITTIME = "_waittime_"
    WIDGET = "_widget_"
    WIDGETS = "_widgets_"
    WINDOWS = "_windows_"
    WRAPLENGTH = "_wraplength_"


# #[EOF]#######################################################################
