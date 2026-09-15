from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import ast
import re


DUPLICATE_FETCHERS = {
    'CensusData',
    'Socrata',
    'HealthData',
    'GlobalHealthData',
    'UnitedNations',
    'WorldPopulation',
    'Wonder',
}


def remove_duplicate_fetcher_classes( text: str ) -> str:
    module = ast.parse( text )
    definitions: dict[ str, list[ ast.ClassDef ] ] = defaultdict( list )
    for node in module.body:
        if isinstance( node, ast.ClassDef ) and node.name in DUPLICATE_FETCHERS:
            definitions[ node.name ].append( node )

    for name in DUPLICATE_FETCHERS:
        if len( definitions[ name ] ) != 2:
            raise RuntimeError( f'Expected exactly two {name} class definitions before consolidation.' )

    lines = text.splitlines( keepends=True )
    removals: list[ tuple[ int, int, str ] ] = [ ]
    for name, nodes in definitions.items( ):
        second = nodes[ 1 ]
        start = second.lineno - 1
        end = second.end_lineno
        while end < len( lines ) and not lines[ end ].strip( ):
            end += 1
        removals.append( (start, end, name) )

    for start, end, name in sorted( removals, reverse=True ):
        del lines[ start:end ]

    consolidated = ''.join( lines )
    module = ast.parse( consolidated )
    counts: dict[ str, int ] = defaultdict( int )
    for node in module.body:
        if isinstance( node, ast.ClassDef ) and node.name in DUPLICATE_FETCHERS:
            counts[ node.name ] += 1
    for name in DUPLICATE_FETCHERS:
        if counts[ name ] != 1:
            raise RuntimeError( f'Fetcher consolidation failed for {name}.' )
    return consolidated


def find_mode_section( text: str, mode: str ) -> re.Match[ str ]:
    header = re.escape( mode.upper( ) )
    pattern = re.compile(
        rf"^# =+\n# {header} MODE\n# =+\nelif mode == '{re.escape( mode )}':\n.*?"
        rf"(?=^# =+\n# [^\n]+ MODE\n# =+\n(?:elif|if) mode == |\Z)",
        re.M | re.S )
    match = pattern.search( text )
    if match is None:
        raise RuntimeError( f'Unable to locate complete {mode} mode section.' )
    return match


def mode_body( section: str, mode: str ) -> str:
    marker = f"elif mode == '{mode}':\n"
    if marker not in section:
        raise RuntimeError( f'Unable to locate {mode} dispatch marker.' )
    return section.split( marker, 1 )[ 1 ].rstrip( )


def indent_body( body: str, tabs: int ) -> str:
    prefix = '\t' * tabs
    return '\n'.join( prefix + line if line else '' for line in body.splitlines( ) )


def consolidate_geoscience_modes( text: str ) -> str:
    weather_match = find_mode_section( text, 'Weather' )
    environmental_match = find_mode_section( text, 'Environmental' )
    geological_match = find_mode_section( text, 'Geological' )

    weather = mode_body( weather_match.group( 0 ), 'Weather' )
    environmental = mode_body( environmental_match.group( 0 ), 'Environmental' )
    geological = mode_body( geological_match.group( 0 ), 'Geological' )

    geoscience = (
        '# ==============================================================================\n'
        '# GEOSCIENCE DATA MODE\n'
        '# ==============================================================================\n'
        "elif mode == 'Geoscience Data':\n"
        "\twith st.expander( 'Geoscience Data', expanded=True ):\n"
        "\t\twith st.expander( 'Weather', expanded=True ):\n"
        f'{indent_body( weather, 2 )}\n\n'
        "\t\twith st.expander( 'Environmental', expanded=False ):\n"
        f'{indent_body( environmental, 2 )}\n\n'
        "\t\twith st.expander( 'Geological', expanded=False ):\n"
        f'{indent_body( geological, 2 )}\n\n' )

    spans = [
        (weather_match.start( ), weather_match.end( ), geoscience),
        (environmental_match.start( ), environmental_match.end( ), ''),
        (geological_match.start( ), geological_match.end( ), ''),
    ]
    for start, end, replacement in sorted( spans, reverse=True ):
        text = text[ :start ] + replacement + text[ end: ]
    return text


def update_modes( text: str ) -> str:
    old = "'Web Loading', 'Weather', 'Environmental', 'Geological', 'Astronomical'"
    new = "'Web Loading', 'Geoscience Data', 'Astronomical'"
    if old not in text:
        raise RuntimeError( 'Configured Weather/Environmental/Geological mode sequence was not found.' )
    return text.replace( old, new, 1 )


def main( ) -> None:
    fetchers_path = Path( 'fetchers.py' )
    app_path = Path( 'app.py' )
    config_path = Path( 'config.py' )

    fetchers_path.write_text(
        remove_duplicate_fetcher_classes( fetchers_path.read_text( encoding='utf-8' ) ),
        encoding='utf-8' )
    app_path.write_text(
        consolidate_geoscience_modes( app_path.read_text( encoding='utf-8' ) ),
        encoding='utf-8' )
    config_path.write_text(
        update_modes( config_path.read_text( encoding='utf-8' ) ),
        encoding='utf-8' )


if __name__ == '__main__':
    main( )
