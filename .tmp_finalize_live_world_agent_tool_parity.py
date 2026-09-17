from pathlib import Path

for filename in [ 'tools.py', 'world.py', 'README.md' ]:
	path = Path( filename )
	text = path.read_text( encoding='utf-8' )
	path.write_text( text.rstrip( ) + '\n', encoding='utf-8' )
