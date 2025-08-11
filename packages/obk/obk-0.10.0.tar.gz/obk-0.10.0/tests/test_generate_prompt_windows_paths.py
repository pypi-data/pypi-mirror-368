from pathlib import PureWindowsPath

from obk.trace_id import is_valid_trace_id


def test_windows_paths_format(tmp_path):
    # Simulate a known trace id and derived paths
    tid = "20250809T130102+0000"
    assert is_valid_trace_id(tid)
    win_prompt = PureWindowsPath(rf"prompts\\2025\\08\\09\\{tid}.md")
    win_task = PureWindowsPath(rf"tasks\\2025\\08\\09\\{tid}")
    # Pure path checks separator semantics without needing Windows
    assert "\\" in str(win_prompt)
    assert str(win_prompt).endswith(f"{tid}.md")
    assert "\\" in str(win_task)
    assert str(win_task).endswith(tid)
