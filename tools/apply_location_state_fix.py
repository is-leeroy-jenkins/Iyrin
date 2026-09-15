from pathlib import Path
import re

path = Path('app.py')
app = path.read_text(encoding='utf-8')

init_anchor = "if 'active_location_source' not in st.session_state:\n\tst.session_state[ 'active_location_source' ] = ''\n"
init_replacement = init_anchor + "\nif 'browser_location_signature' not in st.session_state:\n\tst.session_state[ 'browser_location_signature' ] = ''\n"
if init_anchor not in app:
    raise SystemExit('Active location state initialization anchor not found.')
app = app.replace(init_anchor, init_replacement, 1)

app = app.replace("def get_global_location_default( fallback: str = 'Washington, DC' ) -> str:",
                  "def get_global_location_default( fallback: str = '' ) -> str:", 1)
app = app.replace("def get_global_latitude_default( fallback: float = 38.907200 ) -> float:",
                  "def get_global_latitude_default( fallback: float = 0.0 ) -> float:", 1)
app = app.replace("def get_global_longitude_default( fallback: float = -77.036900 ) -> float:",
                  "def get_global_longitude_default( fallback: float = 0.0 ) -> float:", 1)


def replace_function(text: str, name: str, replacement: str) -> str:
    pattern = rf'^def {name}\(.*?(?=^def |^# ------------- VISUALIZATION UTILITIES|\Z)'
    match = re.search(pattern, text, re.M | re.S)
    if not match:
        raise SystemExit(f'Function {name} not found.')
    return text[:match.start()] + replacement.rstrip() + '\n\n' + text[match.end():]


bootstrap = '''def bootstrap_browser_geolocation( geocoder: Geocoder ) -> None:
\t"""
\t
\t\tPurpose:
\t\t--------
\t\tRequest browser geolocation and keep the canonical global Location State synchronized
\t\twith the browser coordinates before location-dependent modes render.

\t\tParameters:
\t\t-----------
\t\tgeocoder (Geocoder): Existing geocoder instance used to reverse geocode browser coordinates.

\t\tReturns:
\t\t--------
\t\tNone
\t\t
\t"""
\ttry:
\t\tif not st.session_state.get( 'browser_geolocation_enabled', True ):
\t\t\treturn
\t\t
\t\tif st.session_state.get( 'browser_geolocation_permission_denied', False ):
\t\t\treturn
\t\t
\t\tbrowser_loaded = bool( st.session_state.get( 'browser_geolocation_loaded', False ) )
\t\tgeo_payload = st.session_state.get( 'browser_geolocation', None ) if browser_loaded else get_geolocation( )
\t\t
\t\tif not geo_payload:
\t\t\treturn
\t\t
\t\tstate_changed = False
\t\tif not browser_loaded:
\t\t\tif not update_location_state_from_browser_geolocation( geo_payload ):
\t\t\t\treturn
\t\t\tstate_changed = True
\t\t
\t\tcoords = geo_payload.get( 'coords', { } ) if isinstance( geo_payload, dict ) else { }
\t\tlatitude = coords.get( 'latitude', None )
\t\tlongitude = coords.get( 'longitude', None )
\t\tif not has_valid_coordinates( latitude, longitude ):
\t\t\treturn
\t\t
\t\tlatitude = float( latitude )
\t\tlongitude = float( longitude )
\t\tsignature = f'{latitude:.6f},{longitude:.6f}'
\t\tresolved_signature = str( st.session_state.get( 'browser_location_signature', '' ) or '' )
\t\tlocation_text = str( st.session_state.get( 'location', '' ) or '' ).strip( )
\t\tactive_source = str( st.session_state.get( 'active_location_source', '' ) or '' ).strip( )
\t\tneeds_resolution = (resolved_signature != signature or not location_text or active_source != 'browser')
\t\t
\t\tif needs_resolution:
\t\t\ttry:
\t\t\t\tresult = geocoder.reverse( latitude, longitude ) if geocoder is not None else { }
\t\t\t\tresult = result or { }
\t\t\t\tlocality = str( result.get( 'locality', '' ) or '' ).strip( )
\t\t\t\tregion = str( result.get( 'admin_level_1', '' ) or '' ).strip( )
\t\t\t\tlocation_parts = [ part for part in [ locality, region ] if part ]
\t\t\t\tlocation_text = ', '.join( location_parts )
\t\t\t\tif not location_text:
\t\t\t\t\tlocation_text = str( result.get( 'formatted_address', '' ) or '' ).strip( )
\t\t\t\tif not location_text:
\t\t\t\t\tlocation_text = f'{latitude:.6f}, {longitude:.6f}'
\t\t\t\tset_location_state(
\t\t\t\t\tlocation=location_text,
\t\t\t\t\tcity=locality,
\t\t\t\t\tstate=region,
\t\t\t\t\tcountry=str( result.get( 'country_code', '' ) or '' ).strip( ),
\t\t\t\t\tzipcode=str( result.get( 'postal_code', '' ) or '' ).strip( ),
\t\t\t\t\tdescription='Browser geolocation resolved by reverse geocoding.',
\t\t\t\t\tlatitude=latitude,
\t\t\t\t\tlongitude=longitude )
\t\t\texcept Exception:
\t\t\t\tset_location_state(
\t\t\t\t\tlocation=f'{latitude:.6f}, {longitude:.6f}',
\t\t\t\t\tcity='', state='', country='', zipcode='',
\t\t\t\t\tdescription='Browser geolocation coordinates.',
\t\t\t\t\tlatitude=latitude,
\t\t\t\t\tlongitude=longitude )
\t\t\t
\t\t\tst.session_state[ 'browser_location_signature' ] = signature
\t\t\tst.session_state[ 'browser_geolocation_reverse_geocoded' ] = True
\t\t\tstate_changed = True
\t\telse:
\t\t\tset_coordinates( latitude, longitude )
\t\t
\t\tst.session_state[ 'browser_geolocation' ] = geo_payload
\t\tst.session_state[ 'browser_geolocation_loaded' ] = True
\t\tst.session_state[ 'browser_geolocation_permission_denied' ] = False
\t\tst.session_state[ 'browser_geolocation_error' ] = ''
\t\tst.session_state[ 'active_location_source' ] = 'browser'
\t\t
\t\tif state_changed:
\t\t\tst.rerun( )
\t
\texcept Exception as ex:
\t\tst.session_state[ 'browser_geolocation_error' ] = str( ex )
'''
app = replace_function(app, 'bootstrap_browser_geolocation', bootstrap)

ensure = '''def ensure_active_location_state( ) -> None:
\t"""
\t
\t\tPurpose:
\t\t--------
\t\tApply the active-location priority: browser location first and the most recent
\t\tGeocoding result second. Leave location state empty when neither source is available.
\t
\t\tReturns:
\t\t--------
\t\tNone
\t\t
\t"""
\tbrowser_enabled = bool( st.session_state.get( 'browser_geolocation_enabled', True ) )
\tbrowser_loaded = bool( st.session_state.get( 'browser_geolocation_loaded', False ) )
\tbrowser_geo = st.session_state.get( 'browser_geolocation', None )
\tif browser_enabled and browser_loaded and isinstance( browser_geo, dict ):
\t\tcoords = browser_geo.get( 'coords', { } ) or { }
\t\tbrowser_latitude = coords.get( 'latitude', None )
\t\tbrowser_longitude = coords.get( 'longitude', None )
\t\tif has_valid_coordinates( browser_latitude, browser_longitude ):
\t\t\tbrowser_latitude = float( browser_latitude )
\t\t\tbrowser_longitude = float( browser_longitude )
\t\t\tlocation_text = str( st.session_state.get( 'location', '' ) or '' ).strip( )
\t\t\tif not location_text or st.session_state.get( 'active_location_source', '' ) != 'browser':
\t\t\t\tlocation_text = f'{browser_latitude:.6f}, {browser_longitude:.6f}'
\t\t\t\tset_location_state(
\t\t\t\t\tlocation=location_text, city='', state='', country='', zipcode='',
\t\t\t\t\tdescription='Browser geolocation coordinates.',
\t\t\t\t\tlatitude=browser_latitude, longitude=browser_longitude )
\t\t\telse:
\t\t\t\tset_coordinates( browser_latitude, browser_longitude )
\t\t\tst.session_state[ 'active_location_source' ] = 'browser'
\t\t\treturn
\t
\tgeocoded_latitude = st.session_state.get( 'geocoded_latitude', 0.0 )
\tgeocoded_longitude = st.session_state.get( 'geocoded_longitude', 0.0 )
\tif has_valid_coordinates( geocoded_latitude, geocoded_longitude ):
\t\tlocation_text = str( st.session_state.get( 'geocoded_location', '' ) or '' ).strip( )
\t\tif not location_text:
\t\t\tlocation_text = f'{float( geocoded_latitude ):.6f}, {float( geocoded_longitude ):.6f}'
\t\tset_location_state(
\t\t\tlocation=location_text, city='', state='', country='', zipcode='',
\t\t\tdescription='Geocoding mode location fallback.',
\t\t\tlatitude=float( geocoded_latitude ),
\t\t\tlongitude=float( geocoded_longitude ) )
\t\tst.session_state[ 'active_location_source' ] = 'geocoding'
\t\treturn
\t
\tset_location_state(
\t\tlocation='', city='', state='', country='', zipcode='', description='' )
\tst.session_state[ 'coordinates' ] = ( )
\tst.session_state[ 'latitude' ] = 0.0
\tst.session_state[ 'longitude' ] = 0.0
\tst.session_state[ 'active_location_source' ] = ''
'''
app = replace_function(app, 'ensure_active_location_state', ensure)

path.write_text(app, encoding='utf-8')
print('Applied location-state correction.')
