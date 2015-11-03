"""
Get callbacks on changes on the data model.
"""

class APCMiniObserver(object):
    """
    Extend to recieve events from the APC Mini
    """

    def on_press(self, source, btb):
        pass

    def on_hold(self, source, btb):
        pass

    def on_release(self, source, btb):
        pass

    def on_clip_press(self, source, btn):
        pass

    def on_clip_release(self, source, btn):
        pass

    def on_control_press(self, source, btn):
        pass

    def on_control_release(self, source, btn):
        pass

    def on_shift_press(self, source, btn):
        pass

    def on_shift_release(self, source, btn):
        pass

    def on_scene_press(self, source, btn):
        pass

    def on_scene_release(self, source, btn):
        pass

    def on_control_change(self, source, ctl, value):
        pass

    def on_control_msg(self, event, ctl, msg):
        """ update from midi """
        pass

    def on_button_msg(self, event, btn, msg):
        """ update from midi """
        pass


class APCMiniDebugObserver(APCMiniObserver):
    """
    Extend to receive events from the APC Mini
    """
    def on_clip_press(self, source, btn):
        print("clip_press", btn)

    def on_clip_release(self, source, btn):
        print("clip_release", btn)

    def on_control_press(self, source, btn):
        print("control_press", btn)

    def on_control_release(self, source, btn):
        print("control_release", btn)

    def on_shift_press(self, source, btn):
        print("shift_press", btn)

    def on_shift_release(self, source, btn):
        print("shift_release", btn)

    def on_scene_press(self, source, btn):
        print("scene_press", btn)

    def on_scene_release(self, source, btn):
        print("scene_release", btn)

    def on_control_change(self, source, ctl, value):
        print("control_change", ctl, value)

    def on_control_msg(self, ctl, msg):
        print("midi for control ", ctl, msg)

    def on_button_msg(self, btn, msg):
        print("midi for button ", btn, msg)