from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import ast
import re


DUPLICATE_FETCHERS = {
    'CensusData': { 'fetch_variables', 'fetch_data', 'fetch', 'create_schema' },
    'Socrata': { 'fetch_metadata', 'fetch_rows', 'fetch', 'create_schema' },
    'HealthData': { 'fetch_metadata', 'fetch_rows', 'fetch', 'create_schema' },
    'GlobalHealthData': { 'fetch_indicator_registry', 'fetch_athena', 'fetch', 'create_schema' },
    'UnitedNations': { 'fetch_datasets', 'fetch_sdmx_query', 'fetch', 'create_schema' },
    'WorldPopulation': { 'fetch_catalog', 'search_catalog', 'fetch_raster_metadata', 'fetch', 'create_schema' },
    'Wonder': { 'build_template', 'fetch_template', 'submit_query', 'fetch', 'create_schema' },
}

PROVIDER_LABELS = [
    '🌦️ Google Weather',
    '🌤️ OpenWeather / Open-Meteo',
    '🕰️ Historical Weather',
    '🌡️ Climate Data',
    '🌊 Tides & Currents',
    '🌫️ AirNow Air Quality',
    '☀️ UV Index',
    '🧪 OpenAQ',
    '🟣 PurpleAir Sensors',
    '🏭 EPA EnviroFacts Facilities',
    '🔥 NASA FIRMS',
    '🌎 NASA Earth Observatory Natural Events',
    '🌎 USGS Earthquakes',
    '🛰️ Global Imagery',
    '💧 USGS Water Data',
    '🗺️ USGS The National Map',
    '🧭 USGS ScienceBase',
]


def assert_fetchers( ) -> None:
    text = Path( 'fetchers.py' ).read_text( encoding='utf-8' )
    module = ast.parse( text )
    definitions: dict[ str, list[ ast.ClassDef ] ] = defaultdict( list )
    for node in module.body:
        if isinstance( node, ast.ClassDef ) and node.name in DUPLICATE_FETCHERS:
            definitions[ node.name ].append( node )

    for name, required_methods in DUPLICATE_FETCHERS.items( ):
        assert len( definitions[ name ] ) == 1, f'{name} is still duplicated.'
        methods = {
            item.name for item in definitions[ name ][ 0 ].body
            if isinstance( item, (ast.FunctionDef, ast.AsyncFunctionDef) )
        }
        missing = required_methods - methods
        assert not missing, f'{name} lost methods: {sorted( missing )}'


def geoscience_block( text: str ) -> str:
    match = re.search(
        r"^# =+\n# GEOSCIENCE DATA MODE\n# =+\nelif mode == 'Geoscience Data':\n.*?"
        r"(?=^# =+\n# [^\n]+ MODE\n# =+\n(?:elif|if) mode == |\Z)",
        text,
        re.M | re.S )
    assert match is not None, 'Geoscience Data mode section is missing.'
    return match.group( 0 )


def assert_app( ) -> None:
    text = Path( 'app.py' ).read_text( encoding='utf-8' )
    ast.parse( text )
    block = geoscience_block( text )

    assert "elif mode == 'Weather':" not in text
    assert "elif mode == 'Environmental':" not in text
    assert "elif mode == 'Geological':" not in text
    assert text.count( "elif mode == 'Geoscience Data':" ) == 1

    assert "st.expander( 'Geoscience Data', expanded=True )" in block
    assert "st.expander( 'Weather', expanded=True )" in block
    assert "st.expander( 'Environmental', expanded=False )" in block
    assert "st.expander( 'Geological', expanded=False )" in block

    for label in PROVIDER_LABELS:
        assert label in block, f'Missing Geoscience provider expander: {label}'

    for state_key in (
            'weather_last_result', 'weather_last_source',
            'env_last_result', 'env_last_source',
            'geo_last_result', 'geo_last_source' ):
        assert state_key in block, f'Missing preserved state contract: {state_key}'

    assert "render_mode_document_tabs( 'weather', '📄 Loaded' )" in block
    assert "render_mode_document_tabs( 'env', '📄 Loaded' )" in block
    assert "render_mode_document_tabs( 'geo', '📄 Loaded' )" in block


def assert_config( ) -> None:
    text = Path( 'config.py' ).read_text( encoding='utf-8' )
    module = ast.parse( text )
    modes = None
    for node in module.body:
        if isinstance( node, ast.Assign ):
            for target in node.targets:
                if isinstance( target, ast.Name ) and target.id == 'MODES':
                    modes = ast.literal_eval( node.value )
                    break
    assert modes is not None, 'config.MODES was not found.'
    assert 'Geoscience Data' in modes
    assert 'Weather' not in modes
    assert 'Environmental' not in modes
    assert 'Geological' not in modes


def main( ) -> None:
    assert_fetchers( )
    assert_app( )
    assert_config( )
    print( 'Geoscience refactor contract tests passed.' )


if __name__ == '__main__':
    main( )
