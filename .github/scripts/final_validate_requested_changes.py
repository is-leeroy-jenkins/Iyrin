from __future__ import annotations

import ast
from pathlib import Path

app_source = Path( 'app.py' ).read_text( encoding='utf-8' )
fetcher_source = Path( 'fetchers.py' ).read_text( encoding='utf-8' )
config_source = Path( 'config.py' ).read_text( encoding='utf-8' )
app_tree = ast.parse( app_source )
fetcher_tree = ast.parse( fetcher_source )

if "DEFAULT_DATA = r'UAP Sightings'" not in config_source:
    raise SystemExit( 'DEFAULT_DATA is not UAP Sightings.' )

fetcher_classes = { node.name for node in fetcher_tree.body if isinstance( node, ast.ClassDef ) }
expected_classes = {
    'Weather': [ 'GoogleWeather', 'OpenWeather', 'HistoricalWeather', 'ClimateData', 'TidesAndCurrents' ],
    'Environmental': [ 'AirNow', 'UvIndex', 'OpenAQ', 'PurpleAir', 'EnviroFacts', 'Firms', 'EoNet', 'EarthObservatory' ],
    'Geological': [ 'USGSEarthquakes', 'USGSWaterData', 'USGSTheNationalMap', 'GlobalImagery', 'USGSScienceBase' ],
    'Astronomical': [ 'NavalObservatory', 'SatelliteCenter', 'SpaceWeather', 'AstroCatalog', 'AstroQuery', 'StarMap', 'StarChart', 'NearbyObjects', 'OpenScience' ],
    'Demographic': [ 'CensusData', 'Socrata', 'HealthData', 'GlobalHealthData', 'UnitedNations', 'WorldPopulation', 'Wonder' ],
}
for mode, classes in expected_classes.items( ):
    missing_fetchers = [ name for name in classes if name not in fetcher_classes ]
    if missing_fetchers:
        raise SystemExit( f'{mode} fetchers missing from fetchers.py: {missing_fetchers}' )

mode_order = [ 'Weather', 'Environmental', 'Astronomical', 'Celestial Map', 'Geological', 'Demographic' ]
mode_sections = { }
for index, mode in enumerate( mode_order ):
    marker = f"mode == '{mode}'"
    start = app_source.find( marker )
    if start < 0:
        raise SystemExit( f'Mode marker missing: {mode}' )
    if index + 1 < len( mode_order ):
        next_marker = f"mode == '{mode_order[ index + 1 ]}'"
        end = app_source.find( next_marker, start + len( marker ) )
        if end < 0:
            end = len( app_source )
    else:
        end = len( app_source )
    mode_sections[ mode ] = app_source[ start:end ]

mode_sections[ 'Astronomical' ] = app_source[
    app_source.find( "mode == 'Astronomical'" ):
    app_source.find( "mode == 'Celestial Map'" ) ]
mode_sections[ 'Geological' ] = app_source[
    app_source.find( "mode == 'Geological'" ):
    app_source.find( "mode == 'Demographic'" ) ]

for mode, classes in expected_classes.items( ):
    section = mode_sections[ mode ]
    missing_ui = [ name for name in classes if name not in section ]
    if missing_ui:
        raise SystemExit( f'{mode} fetchers missing from UI section: {missing_ui}' )

geocoding_start = app_source.index( "if mode == 'Geocoding':" )
interactive_start = app_source.index( "elif mode == 'Interactive Map':", geocoding_start )
geocoding_section = app_source[ geocoding_start:interactive_start ]
if 'read_table( cfg.DEFAULT_DATA )' in geocoding_section:
    raise SystemExit( 'Geocoding still reads DEFAULT_DATA directly.' )
for contract in [ 'get_loaded_dataset( )', "st.session_state.get( 'active_dataset_name', cfg.DEFAULT_DATA )" ]:
    if contract not in geocoding_section:
        raise SystemExit( f'Geocoding contract missing: {contract}' )

map_start = app_source.index( 'def create_reports_map(' )
map_end = app_source.index( '# ------------ GIS MAPPING UTILITIES', map_start )
map_source = app_source[ map_start:map_end ]
for table_name in [ 'UAP Sightings', 'Nuclear Sites', 'Airports', 'EPA Sites' ]:
    if table_name not in map_source:
        raise SystemExit( f'Map source profile missing: {table_name}' )
for field in [ 'Capacity', 'Identifier', 'Elevation' ]:
    if field not in map_source:
        raise SystemExit( f'Map field missing: {field}' )
if '<b>ID:</b>' in map_source:
    raise SystemExit( 'UAP tooltip still renders ID.' )
if 'overflow-wrap:anywhere' not in map_source or 'max-width:320px' not in map_source:
    raise SystemExit( 'UAP Summary tooltip wrapping contract is missing.' )
if "st.subheader( active_source )" not in map_source:
    raise SystemExit( 'Map header is not source-aware.' )

redundant_text = 'Select a source, configure the request, and submit it to display results.'
if redundant_text in app_source:
    raise SystemExit( 'Redundant Demographic empty-state information remains.' )
demographic_section = mode_sections[ 'Demographic' ]
if "st.markdown( '##### Results' )" in demographic_section:
    raise SystemExit( 'Redundant Demographic Results heading remains.' )

expected_new_keys = {
    'env_earth_observatory_mode', 'env_earth_observatory_timeout', 'env_earth_observatory_run',
    'astro_nearby_mode', 'astro_nearby_timeout', 'astro_nearby_run',
    'astro_open_science_mode', 'astro_open_science_timeout', 'astro_open_science_run',
    'geo_sciencebase_mode', 'geo_sciencebase_timeout', 'geo_sciencebase_run',
}
static_keys = { }
for node in ast.walk( app_tree ):
    if not isinstance( node, ast.Call ):
        continue
    for keyword in node.keywords:
        if keyword.arg == 'key' and isinstance( keyword.value, ast.Constant ):
            value = keyword.value.value
            if isinstance( value, str ):
                static_keys.setdefault( value, [ ] ).append( node.lineno )
for key in expected_new_keys:
    if key not in static_keys:
        raise SystemExit( f'Expected new Streamlit key missing: {key}' )
    if len( static_keys[ key ] ) != 1:
        raise SystemExit( f'New Streamlit key is duplicated: {key} {static_keys[key]}' )

allowed_existing_duplicates = {
    'pubmed_query', 'pubmed_max_docs', 'pubmed_clear', 'open_city_dataset_id', 'open_city_limit',
    'open_city_clear', 'pubmed_save', 'pubmed_save_disabled', 'open_city_save',
    'open_city_save_disabled',
}
duplicates = { key: lines for key, lines in static_keys.items( ) if len( lines ) > 1 }
unexpected_duplicates = { key: lines for key, lines in duplicates.items( )
    if key not in allowed_existing_duplicates }
if unexpected_duplicates:
    raise SystemExit( f'Unexpected duplicate Streamlit keys: {unexpected_duplicates}' )

print( 'All requested-change contracts validated.' )
