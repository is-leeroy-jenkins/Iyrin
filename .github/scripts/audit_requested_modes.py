from __future__ import annotations

import ast
from pathlib import Path

FETCHERS = Path( 'fetchers.py' )
APP = Path( 'app.py' )

fetcher_source = FETCHERS.read_text( encoding='utf-8' )
app_source = APP.read_text( encoding='utf-8' )
fetcher_tree = ast.parse( fetcher_source )
app_tree = ast.parse( app_source )

classes = [ ]
class_nodes = { }
for node in fetcher_tree.body:
    if isinstance( node, ast.ClassDef ):
        doc = ast.get_docstring( node ) or ''
        summary = ' '.join( doc.strip( ).split( ) )[ :220 ]
        classes.append( (node.name, node.lineno, summary) )
        class_nodes[ node.name ] = node

imports = set( )
for node in ast.walk( app_tree ):
    if isinstance( node, ast.ImportFrom ) and node.module == 'fetchers':
        imports.update( alias.asname or alias.name for alias in node.names )

print( 'FETCHER CLASS INVENTORY' )
for name, line, summary in classes:
    referenced = name in app_source
    imported = name in imports
    print( f'{line:5d} | {name:28s} | imported={imported!s:5s} | referenced={referenced!s:5s} | {summary}' )

print( '\nMODE SECTION FETCHER REFERENCES' )
modes = [ 'Weather', 'Environmental', 'Geological', 'Astronomical', 'Demographic' ]
for mode in modes:
    marker = f"mode == '{mode}'"
    start = app_source.find( marker )
    if start < 0:
        print( f'{mode}: MODE MARKER NOT FOUND' )
        continue
    next_positions = [ p for p in [ app_source.find( "elif mode == '", start + len( marker ) ), app_source.find( "if mode == '", start + len( marker ) ) ] if p >= 0 ]
    end = min( next_positions ) if next_positions else len( app_source )
    section = app_source[ start:end ]
    refs = [ name for name, _, _ in classes if name in section ]
    print( f'{mode}: {refs}' )

print( '\nRELEVANT KEYWORD CANDIDATES' )
keywords = {
    'Weather': [ 'weather', 'climate', 'tide', 'forecast', 'meteorolog' ],
    'Environmental': [ 'air', 'environment', 'pollution', 'fire', 'event', 'uv', 'water quality' ],
    'Geological': [ 'earthquake', 'geolog', 'water', 'terrain', 'imagery', 'map', 'sciencebase' ],
    'Astronomical': [ 'astro', 'space', 'satellite', 'star', 'naval observatory', 'celestial', 'near-earth', 'jpl', 'cneos' ],
    'Demographic': [ 'census', 'demograph', 'population', 'health', 'united nations', 'who', 'wonder', 'socrata' ],
}
for mode, terms in keywords.items( ):
    candidates = [ ]
    for name, line, summary in classes:
        haystack = f'{name} {summary}'.lower( )
        if any( term in haystack for term in terms ):
            candidates.append( name )
    print( f'{mode}: {candidates}' )

print( '\nMISSING DOMAIN CANDIDATE METHOD SIGNATURES' )
for class_name in [ 'EarthObservatory', 'NearbyObjects', 'OpenScience', 'USGSScienceBase' ]:
    node = class_nodes.get( class_name )
    if node is None:
        continue
    print( f'[{class_name}]' )
    for child in node.body:
        if isinstance( child, (ast.FunctionDef, ast.AsyncFunctionDef) ):
            args = [ arg.arg for arg in child.args.args ]
            defaults = [ None ] * (len( args ) - len( child.args.defaults )) + child.args.defaults
            rendered = [ ]
            for arg, default in zip( args, defaults ):
                if default is None:
                    rendered.append( arg )
                else:
                    try:
                        rendered.append( f'{arg}={ast.unparse( default )}' )
                    except Exception:
                        rendered.append( f'{arg}=...' )
            print( f'  {child.name}( {", ".join( rendered )} )' )

print( '\nDEMOGRAPHIC REDUNDANT RESULT TEXT OCCURRENCES' )
for phrase in [ 'Results', 'Select a source, configure the request, and submit it to display results.' ]:
    index = app_source.find( phrase )
    print( f'{phrase!r}: {index}' )
