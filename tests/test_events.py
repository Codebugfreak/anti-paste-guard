from core.hooks.events import KeyEvent, MouseEvent, KeyAction, MouseAction, EventType

def test_keyevent_auto_etype_and_serialization():
    ev = KeyEvent(key="a", action=KeyAction.DOWN, mods={"ctrl"})
    assert ev.etype == EventType.KEY
    rec = ev.to_record()
    assert rec["etype"] == "KEY"
    assert rec["key"] == "a"
    assert rec["action"] == "down"
    assert rec["mods"] == ["ctrl"]
    assert "t_utc" in rec and isinstance(rec["t_utc"], str)
    assert "t_mono" in rec and isinstance(rec["t_mono"], float)

def test_mouseevent_auto_etype_and_serialization():
    ev = MouseEvent(button="left", action=MouseAction.UP, x=10, y=20)
    assert ev.etype == EventType.MOUSE
    rec = ev.to_record()
    assert rec["etype"] == "MOUSE"
    assert rec["button"] == "left"
    assert rec["action"] == "up"
    assert rec["x"] == 10 and rec["y"] == 20
