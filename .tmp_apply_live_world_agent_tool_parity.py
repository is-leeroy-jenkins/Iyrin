from pathlib import Path


def replace_once( text: str, old: str, new: str, label: str ) -> str:
	count = text.count( old )
	if count != 1:
		raise RuntimeError( f'{label}: expected one match, found {count}.' )
	return text.replace( old, new, 1 )


def update_tools( ) -> None:
	path = Path( 'tools.py' )
	text = path.read_text( encoding='utf-8' )
	text = replace_once(
		text,
		"import streamlit as st\n",
		"import streamlit as st\n\nfrom history import get_live_world_history_summary, load_live_world_history\n",
		'History imports' )
	text = replace_once(
		text,
		"LIVE_WORLD_ENTITY_TYPES: List[ str ] = [\n    'Aircraft',\n    'Military Aircraft',\n    'Satellite',\n    'Vessel',\n    'Earthquake',\n    'Fire',\n]\n",
		"LIVE_WORLD_ENTITY_TYPES: List[ str ] = [\n    'Aircraft',\n    'Military Aircraft',\n    'Satellite',\n    'Vessel',\n    'Earthquake',\n    'Fire',\n    'Infrastructure',\n    'Camera',\n    'Map Feature',\n]\n",
		'Entity type parity' )
	anchor = "\ndef get_live_world_tracking_status( ) -> Dict[ str, object ]:\n"
	index = text.index( anchor )
	addition = '''\ndef get_live_world_source_status( ) -> List[ Dict[ str, object ] ]:
    \'\'\'

        Purpose:
        --------
        Return provider-level Live World refresh status and failure diagnostics.

        Returns:
        --------
        List[Dict[str, object]]: Provider status records.

    \'\'\'
    statuses = dict( st.session_state.get( 'live_world_source_status', { } ) or { } )
    errors = dict( st.session_state.get( 'live_world_source_errors', { } ) or { } )
    last_attempt = dict( st.session_state.get( 'live_world_source_last_attempt', { } ) or { } )
    last_success = dict( st.session_state.get( 'live_world_source_last_success', { } ) or { } )
    stale = dict( st.session_state.get( 'live_world_source_stale', { } ) or { } )
    keys = sorted( set( statuses ) | set( errors ) | set( last_attempt ) | set( last_success ) )
    return [ {
        'Source': key,
        'Status': str( statuses.get( key, 'Not Refreshed' ) ),
        'Error': str( errors.get( key, '' ) ),
        'LastAttempt': str( last_attempt.get( key, '' ) ),
        'LastSuccess': str( last_success.get( key, '' ) ),
        'Stale': bool( stale.get( key, False ) ),
    } for key in keys ]


def get_live_world_analysis_status( ) -> Dict[ str, object ]:
    \'\'\'

        Purpose:
        --------
        Return the current Cross-Layer Analysis configuration exposed by the Live World UI.

        Returns:
        --------
        Dict[str, object]: Cross-layer analysis configuration.

    \'\'\'
    return {
        'Enabled': bool( st.session_state.get( 'live_world_cross_layer_analysis', False ) ),
        'Origin': str( st.session_state.get( 'live_world_analysis_origin', 'Current Location' ) ),
        'RadiusNM': float( st.session_state.get( 'live_world_analysis_radius_nm', 250 ) ),
        'EntityTypes': list( st.session_state.get( 'live_world_analysis_entity_types', [ ] ) or [ ] ),
        'Limit': int( st.session_state.get( 'live_world_analysis_limit', 100 ) ),
    }


def get_live_world_history_status( ) -> Dict[ str, object ]:
    \'\'\'

        Purpose:
        --------
        Return Historical Replay configuration and persisted-history summary statistics.

        Returns:
        --------
        Dict[str, object]: Historical Replay configuration and persistence summary.

    \'\'\'
    summary = get_live_world_history_summary( )
    return {
        'Enabled': bool( st.session_state.get( 'live_world_historical_replay', False ) ),
        'PersistRefreshes': bool( st.session_state.get( 'live_world_history_persist', False ) ),
        'RetentionDays': int( st.session_state.get( 'live_world_history_retention_days', 30 ) ),
        'Window': str( st.session_state.get( 'live_world_history_window', '24 Hours' ) ),
        'EntityTypes': list( st.session_state.get( 'live_world_history_entity_types', [ ] ) or [ ] ),
        'Limit': int( st.session_state.get( 'live_world_history_limit', 5000 ) ),
        'Snapshot': str( st.session_state.get( 'live_world_history_snapshot', '' ) ),
        'LastSaved': int( st.session_state.get( 'live_world_history_last_saved', 0 ) ),
        'LastError': str( st.session_state.get( 'live_world_history_last_error', '' ) ),
        'Summary': summary,
    }


def list_live_world_history( hours: int, entity_type: str, snapshot: str,
        limit: int ) -> List[ Dict[ str, object ] ]:
    \'\'\'

        Purpose:
        --------
        Return persisted Live World observations through a selected historical snapshot.

        Parameters:
        -----------
        hours (int): Replay lookback in hours; zero loads all retained history.
        entity_type (str): Entity type or All.
        snapshot (str): Maximum replay timestamp to include.
        limit (int): Maximum observations returned.

        Returns:
        --------
        List[Dict[str, object]]: Historical observations in chronological order.

    \'\'\'
    throw_if( 'hours', hours )
    throw_if( 'entity_type', entity_type )
    throw_if( 'snapshot', snapshot )
    throw_if( 'limit', limit )
    if hours < 0:
        raise ValueError( 'Argument "hours" cannot be negative.' )
    if entity_type != 'All' and entity_type not in LIVE_WORLD_ENTITY_TYPES:
        raise ValueError( f'Unsupported entity type: {entity_type}' )
    if limit < 1 or limit > 25000:
        raise ValueError( 'Argument "limit" must be between 1 and 25000.' )
    entity_types = LIVE_WORLD_ENTITY_TYPES if entity_type == 'All' else [ entity_type ]
    df_history = load_live_world_history(
        hours=hours, entity_types=entity_types, snapshot=snapshot, limit=limit )
    if df_history.empty:
        return [ ]
    return [ make_entity_record( row ) for _, row in df_history.iterrows( ) ]


'''
	text = text[ :index ] + addition + text[ index: ]
	text = replace_once(
		text,
		"    'find_live_world_nearest': find_live_world_nearest,\n    'get_live_world_geofence_status': get_live_world_geofence_status,\n    'get_live_world_tracking_status': get_live_world_tracking_status,\n",
		"    'find_live_world_nearest': find_live_world_nearest,\n    'get_live_world_source_status': get_live_world_source_status,\n    'get_live_world_analysis_status': get_live_world_analysis_status,\n    'get_live_world_geofence_status': get_live_world_geofence_status,\n    'get_live_world_tracking_status': get_live_world_tracking_status,\n    'get_live_world_history_status': get_live_world_history_status,\n    'list_live_world_history': list_live_world_history,\n",
		'Agent tool registry parity' )
	path.write_text( text, encoding='utf-8' )


def update_world( ) -> None:
	path = Path( 'world.py' )
	text = path.read_text( encoding='utf-8' )
	text = replace_once(
		text,
		"from sources import (\n\tAdsbLolMilitary, AisStreamLive, CelesTrakLive, OpenSkyLive, OverpassCameras, OverpassInfrastructure,\n\tOverpassMapLayers )\n",
		"from sources import (\n\tAdsbLolMilitary, AisStreamLive, CelesTrakLive, OpenSkyLive, OverpassCameras, OverpassInfrastructure,\n\tOverpassMapLayers )\nfrom tools import LIVE_WORLD_AGENT_TOOLS\n",
		'Agent tools import' )
	text = replace_once(
		text,
		"AI_ADVANCED_TOOLS: Dict[ str, str ] = { 'cross_layer_analysis': '🧭 Cross-Layer Analysis',\n\t\t'geofencing': '🛡️ Geofencing', 'historical_replay': '🕓 Historical Replay', }\n\nAI_ADVANCED_PENDING_TOOLS: Dict[ str, str ] = { 'agent_tools': '🤖 Agent Tools', }\n",
		"AI_ADVANCED_TOOLS: Dict[ str, str ] = { 'cross_layer_analysis': '🧭 Cross-Layer Analysis',\n\t\t'geofencing': '🛡️ Geofencing', 'historical_replay': '🕓 Historical Replay',\n\t\t'agent_tools': '🤖 Agent Tools', }\n",
		'Agent tools availability' )
	text = replace_once(
		text,
		"\t\t'live_world_history_last_error': '',\n\t\t'live_world_refresh_requested': False,\n",
		"\t\t'live_world_history_last_error': '',\n\t\t'live_world_agent_tools': False,\n\t\t'live_world_refresh_requested': False,\n",
		'Agent tools state' )
	text = replace_once(
		text,
		"\t\t\tfor label in AI_ADVANCED_PENDING_TOOLS.values( ):\n\t\t\t\tst.checkbox( label, value=False, disabled=True )\n",
		"\t\t\tst.checkbox( AI_ADVANCED_TOOLS[ 'agent_tools' ], key='live_world_agent_tools' )\n",
		'Agent tools sidebar control' )
	text = replace_once(
		text,
		"entities_tab, aircraft_tab, military_tab, satellites_tab, vessels_tab, earthquakes_tab, fires_tab, infrastructure_tab, cameras_tab, map_layers_tab, tracking_tab, measurements_tab, analysis_tab, geofence_tab, history_tab = st.tabs(\n\t\t[ '🌐 Entities', '✈️ Aircraft', '🛩️ Military', '🛰️ Satellites', '🚢 Vessels',\n\t\t\t'📈 Earthquakes', '🔥 Fires', '📡 Infrastructure', '📷 Cameras', '🗺️ Map Layers', '🎯 Tracking',\n\t\t\t'📏 Measurements', '🧭 Analysis', '🛡️ Geofence', '🕓 Historical Replay' ] )",
		"entities_tab, aircraft_tab, military_tab, satellites_tab, vessels_tab, earthquakes_tab, fires_tab, infrastructure_tab, cameras_tab, map_layers_tab, tracking_tab, measurements_tab, analysis_tab, geofence_tab, history_tab, agent_tools_tab = st.tabs(\n\t\t[ '🌐 Entities', '✈️ Aircraft', '🛩️ Military', '🛰️ Satellites', '🚢 Vessels',\n\t\t\t'📈 Earthquakes', '🔥 Fires', '📡 Infrastructure', '📷 Cameras', '🗺️ Map Layers', '🎯 Tracking',\n\t\t\t'📏 Measurements', '🧭 Analysis', '🛡️ Geofence', '🕓 Historical Replay', '🤖 Agent Tools' ] )",
		'Agent tools tab' )
	history_start = text.index( '\twith history_tab:' )
	next_def = text.find( '\n\ndef ', history_start )
	if next_def < 0:
		raise RuntimeError( 'Could not find the function boundary after Historical Replay tab.' )
	agent_block = '''\n\n\twith agent_tools_tab:
\t\tif not st.session_state[ 'live_world_agent_tools' ]:
\t\t\tst.info( 'Enable Agent Tools in AI & Advanced Tools.' )
\t\telse:
\t\t\tst.markdown( '**Available Callable Tools**' )
\t\t\tdf_agent_tools = pd.DataFrame( [ {
\t\t\t\t'Tool': name,
\t\t\t\t'Callable': callable( tool ),
\t\t\t} for name, tool in LIVE_WORLD_AGENT_TOOLS.items( ) ] )
\t\t\tst.data_editor( df_agent_tools, key='live_world_agent_tools_table',
\t\t\t\twidth='stretch', disabled=True, hide_index=True )
\t\t\tst.caption(
\t\t\t\t'Provider-neutral tools operate on normalized Live World state and return '
\t\t\t\t'JSON-serializable results for external agent frameworks.' )
'''
	text = text[ :next_def ] + agent_block + text[ next_def: ]
	path.write_text( text, encoding='utf-8' )


def update_readme( ) -> None:
	path = Path( 'README.md' )
	text = path.read_text( encoding='utf-8' )
	text = replace_once(
		text,
		"- Cross-layer geospatial context suitable for downstream agent reasoning.\n",
		"- Cross-layer geospatial context suitable for downstream agent reasoning.\n- Provider refresh status and stale/error diagnostics.\n- Cross-Layer Analysis, Geofencing, Tracking, and Historical Replay status.\n- Bounded retrieval of persisted Historical Replay observations.\n- Full normalized entity-type parity, including Infrastructure, Camera, and Map Feature.\n",
		'Agent tool documentation' )
	text = replace_once(
		text,
		"| `OPENSKY_CLIENT_ID`   | OpenSky OAuth client ID          |\n| `OPENSKY_API_CREDENTIALS` | OpenSky OAuth client credentials |\n",
		"| `OPENSKY_CLIENT_ID`          | OpenSky OAuth client ID          |\n| `OPENSKY_API_CLIENT_SECRET` | OpenSky OAuth client secret       |\n",
		'OpenSky configuration documentation' )
	text = replace_once(
		text,
		"Iyrin reads provider credentials from environment variables where required.\n",
		"Iyrin reads provider credentials from environment variables where required. Legacy `OPENSKY_API_CLIENT_ID`, `OPENSKY_API_CREDENTIALS`, and `NASA_FIRMS_MAP_KEY` names remain accepted as compatibility aliases.\n",
		'Compatibility alias documentation' )
	path.write_text( text, encoding='utf-8' )


if __name__ == '__main__':
	update_tools( )
	update_world( )
	update_readme( )
