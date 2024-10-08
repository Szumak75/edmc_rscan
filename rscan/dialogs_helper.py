# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: dialogs helper classes.
"""

from rscan.jsktoolbox.attribtool import ReadOnlyClass


class DialogKeys(object, metaclass=ReadOnlyClass):
    """Keys container class for dialogs."""

    BODIES: str = "_bodies_"
    BUTTON: str = "_button_"
    CLIP: str = "_clip_"
    CLOSED: str = "_closed_"
    EUCLID: str = "_euclid_"
    FONTS: str = "_fonts_"
    F_DATA: str = "_f_data_"
    ID: str = "_id_"
    MATH: str = "_math_"
    PARENT: str = "_parent_"
    QTH: str = "_rscan_qth_"
    RADIUS: str = "_radius_"
    RTH: str = "_rscan_th_"
    R_DATA: str = "_rscan_data_"
    SCROLLBAR: str = "_scrollbar_"
    STARS: str = "_stars_"
    START: str = "_start_"
    STATUS: str = "_status_"
    SYSTEM: str = "_system_"
    S_BUTTON: str = "_s_button_"
    S_PANEL: str = "_s_panel_"
    TEXT: str = "text"
    TOOLS: str = "_tools_"
    TT_TEXT: str = "_tool_tip_text_"
    TW: str = "_tw_"
    WAIT_TIME: str = "_wait_time_"
    WIDGET: str = "_widget_"
    WIDGETS: str = "_widgets_"
    WINDOWS: str = "_windows_"
    WRAPLENGTH: str = "_wraplength_"


# #[EOF]#######################################################################
