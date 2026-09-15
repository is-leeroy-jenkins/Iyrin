from pathlib import Path
import ast

app_text = Path('app.py').read_text(encoding='utf-8')

assert 'Washington, DC' not in app_text, 'Washington, DC fallback still exists.'
assert '38.907200' not in app_text, 'Washington latitude fallback still exists.'
assert '-77.036900' not in app_text, 'Washington longitude fallback still exists.'

module = ast.parse(app_text)
wanted = {'bootstrap_browser_geolocation', 'ensure_active_location_state'}
nodes = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
assert len(nodes) == 2, 'Expected both location-state functions.'
code = compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), '<location-state-functions>', 'exec')


class Session(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class FakeStreamlit:
    def __init__(self, state):
        self.session_state = state
        self.rerun_called = False

    def rerun(self):
        self.rerun_called = True


def has_valid_coordinates(latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and not (lat == 0.0 and lon == 0.0)


def make_namespace(state, geolocation_payload=None):
    fake_st = FakeStreamlit(state)

    def set_coordinates(latitude, longitude):
        state['latitude'] = float(latitude)
        state['longitude'] = float(longitude)
        state['coordinates'] = (float(latitude), float(longitude))

    def set_location_state(location=None, city=None, state_value=None, country=None, zipcode=None,
                           description=None, latitude=None, longitude=None, **kwargs):
        region = kwargs.get('state', state_value)
        if location is not None:
            state['location'] = str(location).strip()
        if city is not None:
            state['city'] = str(city).strip()
        if region is not None:
            state['state'] = str(region).strip()
        if country is not None:
            state['country'] = str(country).strip()
        if zipcode is not None:
            state['zipcode'] = str(zipcode).strip()
        if description is not None:
            state['description'] = str(description).strip()
        if latitude is not None and longitude is not None:
            set_coordinates(latitude, longitude)

    def update_location_state_from_browser_geolocation(geo):
        coords = geo.get('coords', {})
        if not has_valid_coordinates(coords.get('latitude'), coords.get('longitude')):
            return False
        set_location_state(description='Browser geolocation.',
                           latitude=coords['latitude'], longitude=coords['longitude'])
        state['browser_geolocation'] = geo
        state['browser_geolocation_loaded'] = True
        state['browser_geolocation_permission_denied'] = False
        return True

    namespace = {
        'st': fake_st,
        'Geocoder': object,
        'has_valid_coordinates': has_valid_coordinates,
        'set_coordinates': set_coordinates,
        'set_location_state': set_location_state,
        'update_location_state_from_browser_geolocation': update_location_state_from_browser_geolocation,
        'get_geolocation': lambda: geolocation_payload,
    }
    exec(code, namespace)
    return fake_st, namespace


class ArlingtonGeocoder:
    def __init__(self):
        self.calls = 0

    def reverse(self, latitude, longitude):
        self.calls += 1
        assert round(latitude, 4) == 38.8615
        assert round(longitude, 4) == -77.0634
        return {
            'formatted_address': 'Arlington, VA, USA',
            'locality': 'Arlington',
            'admin_level_1': 'VA',
            'country_code': 'US',
            'postal_code': '22202',
        }


state = Session({
    'browser_geolocation_enabled': True,
    'browser_geolocation_loaded': True,
    'browser_geolocation_permission_denied': False,
    'browser_geolocation_reverse_geocoded': True,
    'browser_geolocation': {'coords': {'latitude': 38.861534, 'longitude': -77.063378}},
    'browser_location_signature': '',
    'location': 'Washington, DC',
    'latitude': 38.861534,
    'longitude': -77.063378,
    'coordinates': (38.861534, -77.063378),
    'active_location_source': 'browser',
})

fake_st, namespace = make_namespace(state)
geocoder = ArlingtonGeocoder()
namespace['bootstrap_browser_geolocation'](geocoder)
assert state['location'] == 'Arlington, VA', state
assert state['active_location_source'] == 'browser', state
assert geocoder.calls == 1
assert fake_st.rerun_called

fake_st.rerun_called = False
namespace['bootstrap_browser_geolocation'](geocoder)
assert state['location'] == 'Arlington, VA'
assert geocoder.calls == 1
assert not fake_st.rerun_called

state['geocoded_location'] = 'Dallas, TX, USA'
state['geocoded_latitude'] = 32.7766642
state['geocoded_longitude'] = -96.7969879
namespace['ensure_active_location_state']()
assert state['location'] == 'Arlington, VA', state
assert round(state['latitude'], 4) == 38.8615
assert round(state['longitude'], 4) == -77.0634
assert state['active_location_source'] == 'browser'

state['browser_geolocation_enabled'] = False
namespace['ensure_active_location_state']()
assert state['location'] == 'Dallas, TX, USA', state
assert round(state['latitude'], 4) == 32.7767
assert round(state['longitude'], 4) == -96.7970
assert state['active_location_source'] == 'geocoding'

state['geocoded_location'] = ''
state['geocoded_latitude'] = 0.0
state['geocoded_longitude'] = 0.0
namespace['ensure_active_location_state']()
assert state['location'] == '', state
assert state['coordinates'] == ()
assert state['latitude'] == 0.0
assert state['longitude'] == 0.0
assert state['active_location_source'] == ''

print('Location-state authority tests passed.')
