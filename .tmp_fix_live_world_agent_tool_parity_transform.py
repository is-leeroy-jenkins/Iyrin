from pathlib import Path

path = Path( '.tmp_apply_live_world_agent_tool_parity.py' )
text = path.read_text( encoding='utf-8' )
old = "\tnext_def = text.find( '\\n\\ndef ', history_start )\n\tif next_def < 0:\n\t\traise RuntimeError( 'Could not find the function boundary after Historical Replay tab.' )\n"
new = "\tnext_def = text.find( '\\n\\ndef ', history_start )\n\tif next_def < 0:\n\t\tnext_def = len( text.rstrip( ) )\n"
if text.count( old ) != 1:
	raise RuntimeError( 'Agent tab boundary transformation anchor was not found exactly once.' )
path.write_text( text.replace( old, new, 1 ), encoding='utf-8' )
