try:
    import wx

    EVT_DEBUG_ID = 1010
    
    def debug_display(window, position, message):
        if window is None:
            print(message)
        else:
            wx.PostEvent(window, DebugEvent([position, message]))
       
    class DebugEvent(wx.PyEvent):
        def __init__(self, data):
            wx.PyEvent.__init__(self)
            self.SetEventType(EVT_DEBUG_ID)
            self.data = data
except ImportError as e:
    def debug_display(window, position, message):
        print(message)