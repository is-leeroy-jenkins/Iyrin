from __future__ import annotations

from pathlib import Path

APP = Path( 'app.py' )
source = APP.read_text( encoding='utf-8' )


def replace_once( text: str, old: str, new: str, label: str ) -> str:
    count = text.count( old )
    if count != 1:
        raise RuntimeError( f'{label}: expected exactly one match, found {count}.' )
    return text.replace( old, new, 1 )


source = replace_once(
    source,
    "StarMap, StarChart, WebFetcher, CensusData, Socrata, HealthData, GlobalHealthData, UnitedNations, WorldPopulation, Wonder)",
    "StarMap, StarChart, WebFetcher, EarthObservatory, NearbyObjects, USGSScienceBase, CensusData, Socrata, HealthData, GlobalHealthData, UnitedNations, WorldPopulation, Wonder)",
    'fetcher imports' )

source = replace_once(
    source,
    "if 'df_dataset' not in st.session_state:\n\tst.session_state[ 'df_dataset' ] = pd.DataFrame( )\n",
    "if 'df_dataset' not in st.session_state:\n\tst.session_state[ 'df_dataset' ] = pd.DataFrame( )\n\nif 'active_dataset_name' not in st.session_state:\n\tst.session_state[ 'active_dataset_name' ] = cfg.DEFAULT_DATA\n",
    'active dataset state' )

source = replace_once(
    source,
    "\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\tlog_step( f'Loaded Database Table: {cfg.DEFAULT_DATA}' )",
    "\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\tst.session_state[ 'active_dataset_name' ] = cfg.DEFAULT_DATA\n\t\t\t\tlog_step( f'Loaded Database Table: {cfg.DEFAULT_DATA}' )",
    'default dataset name' )

source = replace_once(
    source,
    "\t\t\t\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\t\t\t\tst.session_state[ 'map_mode_table' ] = selected_table",
    "\t\t\t\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\t\t\t\tst.session_state[ 'active_dataset_name' ] = selected_table\n\t\t\t\t\t\t\tst.session_state[ 'map_mode_table' ] = selected_table",
    'database dataset name' )

source = replace_once(
    source,
    "\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\tlog_step( f'Loaded uploaded file: {uploaded.name}' )",
    "\t\t\t\tdf_original = df_default.copy( )\n\t\t\t\tst.session_state[ 'active_dataset_name' ] = uploaded.name\n\t\t\t\tlog_step( f'Loaded uploaded file: {uploaded.name}' )",
    'custom dataset name' )

map_start = source.index( 'def create_reports_map(' )
map_end = source.index( '# ------------ GIS MAPPING UTILITIES', map_start )
new_map_function = '''def create_reports_map( df: pd.DataFrame, df_overlay: Optional[ pd.DataFrame ]=None,
		use_user_location: bool=True, key_prefix: str='reports_map', source_name: str='' ) -> None:
	"""
	
		Purpose:
		--------
		Render an interactive PyDeck map for records containing Latitude and Longitude fields.
		The map title, filters, tooltip fields, and mapped-record table adapt to known source schemas.

		Parameters:
		-----------
		df (pd.DataFrame): Source DataFrame containing geospatial records.
		df_overlay (Optional[pd.DataFrame]): Optional geocoded records rendered above the base layer.
		use_user_location (bool): Use the global/user location as a fallback map point.
		key_prefix (str): Unique Streamlit widget key prefix for this map instance.
		source_name (str): Active database table or custom dataset name displayed as the map header.

		Returns:
		--------
		None
		
	"""
	try:
		active_source = str( source_name or st.session_state.get( 'active_dataset_name', '' )
			or cfg.DEFAULT_DATA ).strip( )
		st.subheader( active_source )
		
		profiles: Dict[ str, Dict[ str, List[ str ] ] ] = {
			'UAP Sightings': {
				'filters': [ 'Year', 'Country', 'State', 'Shape' ],
				'tooltip': [ 'CalendarDate', 'City', 'State', 'Country', 'Latitude', 'Longitude',
				             'Shape', 'Summary' ],
				'display': [ 'Year', 'Month', 'Day', 'CalendarDate', 'City', 'State', 'Country',
				             'Latitude', 'Longitude', 'Shape', 'Summary' ],
			},
			'Nuclear Sites': {
				'filters': [ 'Name', 'Capacity', 'City', 'State' ],
				'tooltip': [ 'Name', 'Capacity', 'City', 'State', 'Latitude', 'Longitude' ],
				'display': [ 'Name', 'Capacity', 'City', 'State', 'Latitude', 'Longitude' ],
			},
			'Airports': {
				'filters': [ 'Name', 'Identifier', 'Elevation', 'City', 'State' ],
				'tooltip': [ 'Name', 'Identifier', 'Elevation', 'City', 'State', 'Latitude', 'Longitude' ],
				'display': [ 'Name', 'Identifier', 'Elevation', 'City', 'State', 'Latitude', 'Longitude' ],
			},
			'EPA Sites': {
				'filters': [ 'Name', 'City', 'State' ],
				'tooltip': [ 'Name', 'City', 'State', 'Latitude', 'Longitude' ],
				'display': [ 'Name', 'City', 'State', 'Latitude', 'Longitude' ],
			},
		}
		profile = profiles.get( active_source, { } )
		df_source = pd.DataFrame( ) if df is None else df.copy( )
		df_overlay_source = pd.DataFrame( ) if df_overlay is None else df_overlay.copy( )
		required_cols = [ 'Latitude', 'Longitude' ]
		
		if not df_source.empty:
			missing_cols = [ col for col in required_cols if col not in df_source.columns ]
			if missing_cols:
				st.warning( f'Map requires missing column(s): {", ".join( missing_cols )}' )
				return
		
		if not df_overlay_source.empty:
			overlay_missing_cols = [ col for col in required_cols
				if col not in df_overlay_source.columns ]
			if overlay_missing_cols:
				df_overlay_source = pd.DataFrame( )
		
		total_count = len( df_source )
		df_base_map = pd.DataFrame( )
		if not df_source.empty:
			df_source[ 'Latitude' ] = pd.to_numeric( df_source[ 'Latitude' ], errors='coerce' )
			df_source[ 'Longitude' ] = pd.to_numeric( df_source[ 'Longitude' ], errors='coerce' )
			base_mask = (df_source[ 'Latitude' ].notna( )
			             & df_source[ 'Longitude' ].notna( )
			             & df_source[ 'Latitude' ].between( -90.0, 90.0 )
			             & df_source[ 'Longitude' ].between( -180.0, 180.0 )
			             & ~((df_source[ 'Latitude' ] == 0.0)
			                 & (df_source[ 'Longitude' ] == 0.0)))
			df_base_map = df_source.loc[ base_mask ].copy( )
		
		mapped_count = len( df_base_map )
		missing_count = total_count - mapped_count
		df_overlay_map = pd.DataFrame( )
		if not df_overlay_source.empty:
			df_overlay_source[ 'Latitude' ] = pd.to_numeric(
				df_overlay_source[ 'Latitude' ], errors='coerce' )
			df_overlay_source[ 'Longitude' ] = pd.to_numeric(
				df_overlay_source[ 'Longitude' ], errors='coerce' )
			overlay_mask = (df_overlay_source[ 'Latitude' ].notna( )
			                & df_overlay_source[ 'Longitude' ].notna( )
			                & df_overlay_source[ 'Latitude' ].between( -90.0, 90.0 )
			                & df_overlay_source[ 'Longitude' ].between( -180.0, 180.0 )
			                & ~((df_overlay_source[ 'Latitude' ] == 0.0)
			                    & (df_overlay_source[ 'Longitude' ] == 0.0)))
			df_overlay_map = df_overlay_source.loc[ overlay_mask ].copy( )
		
		df_user_map = pd.DataFrame( )
		if use_user_location and df_base_map.empty and df_overlay_map.empty:
			user_latitude = st.session_state.get( 'latitude', None )
			user_longitude = st.session_state.get( 'longitude', None )
			if has_valid_coordinates( user_latitude, user_longitude ):
				user_location = compose_location_from_state( )
				user_description = st.session_state.get( 'description', '' )
				if not user_location:
					user_location = (f'{float( user_latitude ):.4f},'
					                 f'{float( user_longitude ):.4f}')
				df_user_map = pd.DataFrame( [ {
					'CalendarDate': dt.datetime.now( ).strftime( '%Y-%m-%d %H:%M:%S' ),
					'City': user_location,
					'State': '',
					'Country': '',
					'Latitude': float( user_latitude ),
					'Longitude': float( user_longitude ),
					'Shape': 'User Location',
					'Summary': user_description or 'Current user location fallback.',
				} ] )
		
		metric_c1, metric_c2, metric_c3, metric_c4 = st.columns( 4, border=True )
		metric_c1.metric( 'Total Records', f'{total_count:,}' )
		metric_c2.metric( 'Mapped Records', f'{mapped_count:,}' )
		metric_c3.metric( 'Missing / Invalid Coordinates', f'{missing_count:,}' )
		metric_c4.metric( 'Overlay / User Records',
			f'{len( df_overlay_map ) + len( df_user_map ):,}' )
		
		if df_base_map.empty and df_overlay_map.empty and df_user_map.empty:
			st.info( 'No usable base, overlay, or user-location coordinates are available.' )
			return
		
		filter_fields = [ col for col in profile.get( 'filters',
			[ 'Year', 'Country', 'State', 'Shape' ] ) if col in df_base_map.columns ]
		if not df_base_map.empty and filter_fields:
			for row_start in range( 0, len( filter_fields ), 2 ):
				filter_columns = st.columns( 2, border=True )
				for offset, field in enumerate( filter_fields[ row_start: row_start + 2 ] ):
					with filter_columns[ offset ]:
						options = sorted( [ str( value ) for value in
							df_base_map[ field ].dropna( ).unique( ) ] )
						field_key = re.sub( r'[^0-9a-zA-Z_]+', '_', field.lower( ) )
						selected_values = st.multiselect( field, options,
							key=f'{key_prefix}_{field_key}' )
						if selected_values:
							df_base_map = df_base_map[
								df_base_map[ field ].astype( str ).isin( selected_values ) ]
		
		if df_base_map.empty and df_overlay_map.empty and df_user_map.empty:
			st.info( 'No mapped records match the selected filters.' )
			return
		
		map_style_options = {
			'Carto Positron': 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
			'Carto Dark Matter': 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
			'Carto Voyager': 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
			'Dark': 'dark', 'Light': 'light', 'Road': 'road', 'Satellite': 'satellite',
			'Dark - No Labels': 'dark_no_labels', 'Light - No Labels': 'light_no_labels',
			'Streamlit Theme': None,
		}
		control_c1, control_c2, control_c3, control_c4 = st.columns(
			[ 0.20, 0.20, 0.30, 0.30 ], border=True )
		with control_c1:
			zoom_level = st.slider( 'Initial Zoom', min_value=0, max_value=50, step=1,
				value=5, key=f'{key_prefix}_zoom' )
		with control_c2:
			point_radius = st.slider( 'Point Radius', min_value=1, max_value=50, value=1,
				step=5, key=f'{key_prefix}_radius' )
		with control_c3:
			selected_map_style = st.selectbox( 'Map Style', list( map_style_options.keys( ) ),
				index=1, key=f'{key_prefix}_style' )
			map_style = map_style_options[ selected_map_style ]
		with control_c4:
			if len( df_base_map ) > 100:
				max_records = st.slider( 'Maximum Records', min_value=100,
					max_value=len( df_base_map ), value=min( 2500, len( df_base_map ) ),
					step=500, key=f'{key_prefix}_limit' )
				df_base_map = df_base_map.head( max_records )
			elif not df_base_map.empty:
				st.caption( f'Displaying all {len( df_base_map ):,} mapped base records.' )
			elif not df_overlay_map.empty:
				st.caption( f'Displaying {len( df_overlay_map ):,} overlay record(s).' )
			else:
				st.caption( 'Displaying current user/global location fallback.' )
		
		tooltip_fields = profile.get( 'tooltip', [ 'City', 'State', 'Country',
			'Latitude', 'Longitude', 'Shape', 'Summary' ] )
		for df_target in [ df_base_map, df_overlay_map, df_user_map ]:
			if df_target.empty:
				continue
			for col in tooltip_fields:
				if col not in df_target.columns:
					df_target[ col ] = ''
			df_target[ 'Position' ] = df_target.apply(
				lambda row: [ float( row[ 'Longitude' ] ), float( row[ 'Latitude' ] ) ], axis=1 )
		
		if not df_base_map.empty:
			df_view = df_base_map
		elif not df_overlay_map.empty:
			df_view = df_overlay_map
		else:
			df_view = df_user_map
		
		view_state = pdk.ViewState( latitude=float( df_view[ 'Latitude' ].median( ) ),
			longitude=float( df_view[ 'Longitude' ].median( ) ), zoom=zoom_level, pitch=0 )
		layers = [ ]
		if not df_base_map.empty:
			layers.append( pdk.Layer( 'ScatterplotLayer', data=df_base_map,
				get_position='Position', get_radius=point_radius,
				get_fill_color=[ 0, 120, 252, 160 ], get_line_color=[ 255, 255, 255, 180 ],
				line_width_min_pixels=1, radius_min_pixels=4, radius_max_pixels=24,
				filled=True, stroked=True, pickable=True ) )
		if not df_overlay_map.empty:
			layers.append( pdk.Layer( 'ScatterplotLayer', data=df_overlay_map,
				get_position='Position', get_radius=max( point_radius * 2, 20000 ),
				get_fill_color=[ 255, 80, 0, 220 ], get_line_color=[ 255, 255, 255, 255 ],
				line_width_min_pixels=2, radius_min_pixels=8, radius_max_pixels=40,
				filled=True, stroked=True, pickable=True ) )
		if not df_user_map.empty:
			layers.append( pdk.Layer( 'ScatterplotLayer', data=df_user_map,
				get_position='Position', get_radius=max( point_radius * 2, 20000 ),
				get_fill_color=[ 0, 180, 80, 230 ], get_line_color=[ 255, 255, 255, 255 ],
				line_width_min_pixels=2, radius_min_pixels=10, radius_max_pixels=42,
				filled=True, stroked=True, pickable=True ) )
		
		labels = { 'CalendarDate': 'Date' }
		tooltip_lines = [ ]
		for field in tooltip_fields:
			label = labels.get( field, field )
			if field == 'Summary':
				tooltip_lines.append(
					'<b>Summary:</b><div style="max-width:320px;white-space:normal;overflow-wrap:anywhere;">{Summary}</div>' )
			else:
				tooltip_lines.append( f'<b>{label}:</b> {{{field}}}<br/>' )
		tooltip = {
			'html': ''.join( tooltip_lines ),
			'style': { 'backgroundColor': 'rgba(0, 0, 0, 0.85)', 'color': 'white',
				'fontSize': '12px' },
		}
		set_blue_divider( )
		deck = pdk.Deck( layers=layers, initial_view_state=view_state,
			map_style=map_style, tooltip=tooltip )
		st.pydeck_chart( deck, use_container_width=True )
		
		show_table = st.checkbox( 'Show mapped records table', value=False,
			key=f'{key_prefix}_show_table' )
		if show_table:
			if df_base_map.empty:
				if not df_user_map.empty:
					st.info( 'No base mapped records are available.' )
					st.data_editor( df_user_map, key=f'{key_prefix}_user_location_table',
						use_container_width=True, disabled=True )
				else:
					st.info( 'No base mapped records are available to display.' )
			else:
				display_cols = [ col for col in profile.get( 'display', list( df_base_map.columns ) )
					if col in df_base_map.columns and col != 'Position' ]
				st.data_editor( df_base_map[ display_cols ], key=f'{key_prefix}_table',
					use_container_width=True, disabled=True )
	
	except Exception as e:
		st.error( f'Interactive map failed: {e}' )

'''
source = source[ :map_start ] + new_map_function + source[ map_end: ]

old_geocoding_map = '''\t\ttry:
\t\t\ttables = list_tables( )
\t\t\tif cfg.DEFAULT_DATA not in tables:
\t\t\t\tst.warning( f'Default table "{cfg.DEFAULT_DATA}" was not found in {cfg.DB_PATH}.' )
\t\t\telse:
\t\t\t\tdf_reports = read_table( cfg.DEFAULT_DATA )
\t\t\t\tdf_overlay = st.session_state.get( 'df_geocoding_map_results', pd.DataFrame( ) )
\t\t\t\tcreate_reports_map( df_reports, df_overlay=df_overlay )
\t\t\t\tif df_overlay is not None and not df_overlay.empty:
\t\t\t\t\twith st.expander( 'Geocoded Map Results', expanded=False ):
\t\t\t\t\t\tst.data_editor( df_overlay, key='geocoding_map_results_table',
\t\t\t\t\t\t\tuse_container_width=True, disabled=True )
\t\t
\t\texcept Exception as e:
\t\t\tst.error( f'Reports map failed: {e}' )
'''
new_geocoding_map = '''\t\ttry:
\t\t\tdf_reports = get_loaded_dataset( )
\t\t\tif df_reports is None:
\t\t\t\tst.warning( 'No dataset is currently loaded for mapping.' )
\t\t\telse:
\t\t\t\tdf_overlay = st.session_state.get( 'df_geocoding_map_results', pd.DataFrame( ) )
\t\t\t\tdataset_name = st.session_state.get( 'active_dataset_name', cfg.DEFAULT_DATA )
\t\t\t\tcreate_reports_map( df_reports, df_overlay=df_overlay,
\t\t\t\t\tsource_name=dataset_name )
\t\t\t\tif df_overlay is not None and not df_overlay.empty:
\t\t\t\t\twith st.expander( 'Geocoded Map Results', expanded=False ):
\t\t\t\t\t\tst.data_editor( df_overlay, key='geocoding_map_results_table',
\t\t\t\t\t\t\tuse_container_width=True, disabled=True )
\t\t
\t\texcept Exception as e:
\t\t\tst.error( f'Geocoding map failed: {e}' )
'''
source = replace_once( source, old_geocoding_map, new_geocoding_map, 'geocoding map source' )

source = replace_once(
    source,
    "\t\t\tcreate_reports_map( df_map_source, df_overlay=df_overlay )",
    "\t\t\tcreate_reports_map( df_map_source, df_overlay=df_overlay, source_name=table )",
    'interactive map source name' )

environmental_insert = '''\n\t\t\t# --------- NASA EARTH OBSERVATORY\n\t\t\twith st.expander( '🌍 NASA Earth Observatory', expanded=False ):\n\t\t\t\tearth_mode = st.selectbox( 'Mode',\n\t\t\t\t\toptions=[ 'events', 'categories', 'sources', 'layers' ],\n\t\t\t\t\tkey='env_earth_observatory_mode' )\n\t\t\t\tearth_timeout = st.slider( 'Timeout', min_value=1, max_value=60, value=20,\n\t\t\t\t\tkey='env_earth_observatory_timeout' )\n\t\t\t\tearth_status = 'open'\n\t\t\t\tearth_category = ''\n\t\t\t\tearth_source = ''\n\t\t\t\tearth_limit = 20\n\t\t\t\tearth_days = 30\n\t\t\t\tearth_start_date = ''\n\t\t\t\tearth_end_date = ''\n\t\t\t\tif earth_mode == 'events':\n\t\t\t\t\tearth_c1, earth_c2 = st.columns( 2 )\n\t\t\t\t\twith earth_c1:\n\t\t\t\t\t\tearth_status = st.selectbox( 'Status', [ 'open', 'closed', 'all' ],\n\t\t\t\t\t\t\tkey='env_earth_observatory_status' )\n\t\t\t\t\t\tearth_category = st.text_input( 'Category',\n\t\t\t\t\t\t\tkey='env_earth_observatory_category' )\n\t\t\t\t\t\tearth_limit = st.slider( 'Maximum Events', min_value=1, max_value=500,\n\t\t\t\t\t\t\tvalue=20, key='env_earth_observatory_limit' )\n\t\t\t\t\twith earth_c2:\n\t\t\t\t\t\tearth_source = st.text_input( 'Source',\n\t\t\t\t\t\t\tkey='env_earth_observatory_source' )\n\t\t\t\t\t\tearth_days = st.slider( 'Prior Days', min_value=1, max_value=3650,\n\t\t\t\t\t\t\tvalue=30, key='env_earth_observatory_days' )\n\t\t\t\t\t\tearth_start_date = st.text_input( 'Start Date', placeholder='YYYY-MM-DD',\n\t\t\t\t\t\t\tkey='env_earth_observatory_start_date' )\n\t\t\t\t\t\tearth_end_date = st.text_input( 'End Date', placeholder='YYYY-MM-DD',\n\t\t\t\t\t\t\tkey='env_earth_observatory_end_date' )\n\t\t\t\telif earth_mode == 'layers':\n\t\t\t\t\tearth_category = st.text_input( 'Category',\n\t\t\t\t\t\tkey='env_earth_observatory_layer_category' )\n\t\t\t\tearth_btn_c1, earth_btn_c2 = st.columns( 2 )\n\t\t\t\twith earth_btn_c1:\n\t\t\t\t\tif st.button( label='Run', icon='🏃', key='env_earth_observatory_run',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\ttry:\n\t\t\t\t\t\t\tservice = EarthObservatory( )\n\t\t\t\t\t\t\tresult = service.fetch( mode=earth_mode, status=earth_status,\n\t\t\t\t\t\t\t\tcategory=earth_category, source=earth_source, limit=int( earth_limit ),\n\t\t\t\t\t\t\t\tdays=int( earth_days ), start_date=earth_start_date,\n\t\t\t\t\t\t\t\tend_date=earth_end_date, time=int( earth_timeout ) )\n\t\t\t\t\t\t\tst.session_state[ 'env_last_source' ] = 'NASA Earth Observatory'\n\t\t\t\t\t\t\tst.session_state[ 'env_last_result' ] = result or { }\n\t\t\t\t\t\t\tst.session_state[ 'env_last_latitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'env_last_longitude' ] = None\n\t\t\t\t\t\t\tst.success( 'NASA Earth Observatory request completed.' )\n\t\t\t\t\t\texcept Exception as ex:\n\t\t\t\t\t\t\tst.error( f'NASA Earth Observatory request failed: {ex}' )\n\t\t\t\twith earth_btn_c2:\n\t\t\t\t\tif st.button( label='Clear', icon='🧹', key='env_earth_observatory_clear',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\tst.session_state[ 'env_last_source' ] = ''\n\t\t\t\t\t\tst.session_state[ 'env_last_result' ] = { }\n\t\t\t\t\t\tst.session_state[ 'env_last_latitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'env_last_longitude' ] = None\n\t\t\t\tst.divider( )\n\t\t\t\trender_source_processing_controls( 'env', 'env_last_result', 'env_last_source',\n\t\t\t\t\t'NASA Earth Observatory', 'env_earth_observatory' )\n'''
env_marker = "\t\twith enviro_c2:\n\t\t\trender_mode_document_tabs( 'env', '📄 Loaded' )"
env_pos = source.index( env_marker )
source = source[ :env_pos ] + environmental_insert + source[ env_pos: ]

astronomical_insert = '''\n\t\t\t# --------- JPL NEARBY OBJECTS\n\t\t\twith st.expander( '☄️ JPL Nearby Objects', expanded=False ):\n\t\t\t\tnearby_mode = st.selectbox( 'Mode',\n\t\t\t\t\toptions=[ 'close_approaches', 'object_lookup', 'nhats_summary', 'nhats_object',\n\t\t\t\t\t          'fireballs' ], key='astro_nearby_mode' )\n\t\t\t\tnearby_timeout = st.slider( 'Timeout', min_value=1, max_value=60, value=20,\n\t\t\t\t\tkey='astro_nearby_timeout' )\n\t\t\t\tnearby_start_date = ''\n\t\t\t\tnearby_end_date = ''\n\t\t\t\tnearby_query = ''\n\t\t\t\tnearby_query_type = 'sstr'\n\t\t\t\tnearby_dist_max = '10LD'\n\t\t\t\tnearby_body = 'Earth'\n\t\t\t\tnearby_sort = 'date'\n\t\t\t\tnearby_limit = 20\n\t\t\t\tnearby_dv = 6.0\n\t\t\t\tnearby_dur = 360\n\t\t\t\tnearby_stay = 8\n\t\t\t\tnearby_launch = '2020-2045'\n\t\t\t\tnearby_h = 26.0\n\t\t\t\tnearby_occ = 7\n\t\t\t\tnearby_include_physical = True\n\t\t\t\tnearby_include_close = True\n\t\t\t\tnearby_include_discovery = True\n\t\t\t\tnearby_ca_body = 'Earth'\n\t\t\t\tif nearby_mode == 'close_approaches':\n\t\t\t\t\tnearby_c1, nearby_c2 = st.columns( 2 )\n\t\t\t\t\twith nearby_c1:\n\t\t\t\t\t\tnearby_start_date = st.text_input( 'Start Date', placeholder='YYYY-MM-DD',\n\t\t\t\t\t\t\tkey='astro_nearby_start_date' )\n\t\t\t\t\t\tnearby_dist_max = st.text_input( 'Maximum Distance', value='10LD',\n\t\t\t\t\t\t\tkey='astro_nearby_dist_max' )\n\t\t\t\t\t\tnearby_sort = st.selectbox( 'Sort', [ 'date', 'dist' ],\n\t\t\t\t\t\t\tkey='astro_nearby_sort' )\n\t\t\t\t\twith nearby_c2:\n\t\t\t\t\t\tnearby_end_date = st.text_input( 'End Date', placeholder='YYYY-MM-DD',\n\t\t\t\t\t\t\tkey='astro_nearby_end_date' )\n\t\t\t\t\t\tnearby_body = st.selectbox( 'Body', [ 'Earth', 'Moon', 'Mars', 'Juptr' ],\n\t\t\t\t\t\t\tkey='astro_nearby_body' )\n\t\t\t\t\t\tnearby_limit = st.slider( 'Maximum Records', min_value=1, max_value=500,\n\t\t\t\t\t\t\tvalue=20, key='astro_nearby_limit' )\n\t\t\t\telif nearby_mode == 'object_lookup':\n\t\t\t\t\tnearby_query = st.text_input( 'Object', value='Apophis',\n\t\t\t\t\t\tkey='astro_nearby_query' )\n\t\t\t\t\tnearby_query_type = st.selectbox( 'Query Type', [ 'sstr', 'spk', 'des' ],\n\t\t\t\t\t\tkey='astro_nearby_query_type' )\n\t\t\t\t\tnearby_opt_c1, nearby_opt_c2 = st.columns( 2 )\n\t\t\t\t\twith nearby_opt_c1:\n\t\t\t\t\t\tnearby_include_physical = st.checkbox( 'Physical Parameters', value=True,\n\t\t\t\t\t\t\tkey='astro_nearby_physical' )\n\t\t\t\t\t\tnearby_include_close = st.checkbox( 'Close Approaches', value=True,\n\t\t\t\t\t\t\tkey='astro_nearby_close' )\n\t\t\t\t\twith nearby_opt_c2:\n\t\t\t\t\t\tnearby_include_discovery = st.checkbox( 'Discovery Data', value=True,\n\t\t\t\t\t\t\tkey='astro_nearby_discovery' )\n\t\t\t\t\t\tnearby_ca_body = st.selectbox( 'Approach Body', [ 'Earth', 'Moon', 'Mars' ],\n\t\t\t\t\t\t\tkey='astro_nearby_ca_body' )\n\t\t\t\telif nearby_mode in [ 'nhats_summary', 'nhats_object' ]:\n\t\t\t\t\tif nearby_mode == 'nhats_object':\n\t\t\t\t\t\tnearby_query = st.text_input( 'Designation', key='astro_nearby_designation' )\n\t\t\t\t\tnhats_c1, nhats_c2 = st.columns( 2 )\n\t\t\t\t\twith nhats_c1:\n\t\t\t\t\t\tnearby_dv = st.number_input( 'Maximum ΔV', min_value=0.0, value=6.0,\n\t\t\t\t\t\t\tstep=0.1, key='astro_nearby_dv' )\n\t\t\t\t\t\tnearby_stay = st.number_input( 'Minimum Stay', min_value=0, value=8,\n\t\t\t\t\t\t\tstep=1, key='astro_nearby_stay' )\n\t\t\t\t\t\tnearby_h = st.number_input( 'Maximum H', min_value=0.0, value=26.0,\n\t\t\t\t\t\t\tstep=0.1, key='astro_nearby_h' )\n\t\t\t\t\twith nhats_c2:\n\t\t\t\t\t\tnearby_dur = st.number_input( 'Maximum Duration', min_value=1, value=360,\n\t\t\t\t\t\t\tstep=1, key='astro_nearby_dur' )\n\t\t\t\t\t\tnearby_launch = st.text_input( 'Launch Window', value='2020-2045',\n\t\t\t\t\t\t\tkey='astro_nearby_launch' )\n\t\t\t\t\t\tnearby_occ = st.number_input( 'Minimum Opportunities', min_value=1, value=7,\n\t\t\t\t\t\t\tstep=1, key='astro_nearby_occ' )\n\t\t\t\telse:\n\t\t\t\t\tnearby_start_date = st.text_input( 'Minimum Date', placeholder='YYYY-MM-DD',\n\t\t\t\t\t\tkey='astro_nearby_fireball_date' )\n\t\t\t\t\tnearby_limit = st.slider( 'Maximum Records', min_value=1, max_value=500,\n\t\t\t\t\t\tvalue=20, key='astro_nearby_fireball_limit' )\n\t\t\t\tnearby_btn_c1, nearby_btn_c2 = st.columns( 2 )\n\t\t\t\twith nearby_btn_c1:\n\t\t\t\t\tif st.button( label='Run', icon='🏃', key='astro_nearby_run',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\ttry:\n\t\t\t\t\t\t\tservice = NearbyObjects( )\n\t\t\t\t\t\t\tresult = service.fetch( mode=nearby_mode, start_date=nearby_start_date,\n\t\t\t\t\t\t\t\tend_date=nearby_end_date, query=nearby_query,\n\t\t\t\t\t\t\t\tquery_type=nearby_query_type, dist_max=nearby_dist_max,\n\t\t\t\t\t\t\t\tbody=nearby_body, sort=nearby_sort, limit=int( nearby_limit ),\n\t\t\t\t\t\t\t\tdv=float( nearby_dv ), dur=int( nearby_dur ), stay=int( nearby_stay ),\n\t\t\t\t\t\t\t\tlaunch=nearby_launch, h=float( nearby_h ), occ=int( nearby_occ ),\n\t\t\t\t\t\t\t\tinclude_physical=bool( nearby_include_physical ),\n\t\t\t\t\t\t\t\tinclude_close_approaches=bool( nearby_include_close ),\n\t\t\t\t\t\t\t\tca_body=nearby_ca_body, include_discovery=bool( nearby_include_discovery ),\n\t\t\t\t\t\t\t\ttime=int( nearby_timeout ) )\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_source' ] = 'JPL Nearby Objects'\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_result' ] = normalize( result ) or { }\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_latitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_longitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_url' ] = ''\n\t\t\t\t\t\t\tst.success( 'JPL Nearby Objects request completed.' )\n\t\t\t\t\t\texcept Exception as ex:\n\t\t\t\t\t\t\tst.error( f'JPL Nearby Objects request failed: {ex}' )\n\t\t\t\twith nearby_btn_c2:\n\t\t\t\t\tif st.button( label='Clear', icon='🧹', key='astro_nearby_clear',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\tst.session_state[ 'astro_last_source' ] = ''\n\t\t\t\t\t\tst.session_state[ 'astro_last_result' ] = { }\n\t\t\t\t\t\tst.session_state[ 'astro_last_latitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'astro_last_longitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'astro_last_url' ] = ''\n\t\t\t\tst.divider( )\n\t\t\t\trender_source_processing_controls( 'astro', 'astro_last_result',\n\t\t\t\t\t'astro_last_source', 'JPL Nearby Objects', 'astro_nearby_objects' )\n'''
astro_marker = "\t\twith astro_c2:\n\t\t\trender_mode_document_tabs( 'astro', '📄 Loaded' )"
astro_pos = source.index( astro_marker )
source = source[ :astro_pos ] + astronomical_insert + source[ astro_pos: ]

geological_insert = '''\n\t\t\t# --------- USGS SCIENCEBASE\n\t\t\twith st.expander( '🧭 USGS ScienceBase', expanded=False ):\n\t\t\t\tsciencebase_mode = st.selectbox( 'Mode', options=[ 'items', 'item' ],\n\t\t\t\t\tkey='geo_sciencebase_mode' )\n\t\t\t\tsciencebase_timeout = st.slider( 'Timeout', min_value=1, max_value=60, value=20,\n\t\t\t\t\tkey='geo_sciencebase_timeout' )\n\t\t\t\tsciencebase_query = ''\n\t\t\t\tsciencebase_item_id = ''\n\t\t\t\tsciencebase_max_items = 25\n\t\t\t\tsciencebase_offset = 0\n\t\t\t\tsciencebase_fields = ''\n\t\t\t\tif sciencebase_mode == 'items':\n\t\t\t\t\tsciencebase_c1, sciencebase_c2 = st.columns( 2 )\n\t\t\t\t\twith sciencebase_c1:\n\t\t\t\t\t\tsciencebase_query = st.text_input( 'Query', key='geo_sciencebase_query' )\n\t\t\t\t\t\tsciencebase_max_items = st.slider( 'Maximum Items', min_value=1,\n\t\t\t\t\t\t\tmax_value=500, value=25, key='geo_sciencebase_max_items' )\n\t\t\t\t\twith sciencebase_c2:\n\t\t\t\t\t\tsciencebase_fields = st.text_input( 'Fields',\n\t\t\t\t\t\t\tplaceholder='Optional comma-separated fields', key='geo_sciencebase_fields' )\n\t\t\t\t\t\tsciencebase_offset = st.number_input( 'Offset', min_value=0, value=0, step=1,\n\t\t\t\t\t\t\tkey='geo_sciencebase_offset' )\n\t\t\t\telse:\n\t\t\t\t\tsciencebase_item_id = st.text_input( 'Item ID', key='geo_sciencebase_item_id' )\n\t\t\t\tsciencebase_btn_c1, sciencebase_btn_c2 = st.columns( 2 )\n\t\t\t\twith sciencebase_btn_c1:\n\t\t\t\t\tif st.button( label='Run', icon='🏃', key='geo_sciencebase_run',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\ttry:\n\t\t\t\t\t\t\tservice = USGSScienceBase( )\n\t\t\t\t\t\t\tresult = service.fetch( mode=sciencebase_mode, q=sciencebase_query,\n\t\t\t\t\t\t\t\titem_id=sciencebase_item_id, max_items=int( sciencebase_max_items ),\n\t\t\t\t\t\t\t\toffset=int( sciencebase_offset ), fields=sciencebase_fields,\n\t\t\t\t\t\t\t\ttime=int( sciencebase_timeout ) )\n\t\t\t\t\t\t\tst.session_state[ 'geo_last_source' ] = 'USGS ScienceBase'\n\t\t\t\t\t\t\tst.session_state[ 'geo_last_result' ] = result or { }\n\t\t\t\t\t\t\tst.session_state[ 'geo_last_latitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'geo_last_longitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'geo_last_image_path' ] = ''\n\t\t\t\t\t\t\tst.success( 'USGS ScienceBase request completed.' )\n\t\t\t\t\t\texcept Exception as ex:\n\t\t\t\t\t\t\tst.error( f'USGS ScienceBase request failed: {ex}' )\n\t\t\t\twith sciencebase_btn_c2:\n\t\t\t\t\tif st.button( label='Clear', icon='🧹', key='geo_sciencebase_clear',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\tst.session_state[ 'geo_last_source' ] = ''\n\t\t\t\t\t\tst.session_state[ 'geo_last_result' ] = { }\n\t\t\t\t\t\tst.session_state[ 'geo_last_latitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'geo_last_longitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'geo_last_image_path' ] = ''\n\t\t\t\tst.divider( )\n\t\t\t\trender_source_processing_controls( 'geo', 'geo_last_result', 'geo_last_source',\n\t\t\t\t\t'USGS ScienceBase', 'geo_usgs_sciencebase' )\n'''
geo_marker = "\t\twith geo_c2:\n\t\t\trender_mode_document_tabs( 'geo', '📄 Loaded' )"
geo_pos = source.index( geo_marker )
source = source[ :geo_pos ] + geological_insert + source[ geo_pos: ]

old_demographic_results = '''\twith right:\n\t\tst.markdown( '##### Results' )\n\t\tactive_source = st.session_state.get( 'demographic_active_source', '' )\n\t\tdisplay_names: Dict[ str, str ] = { 'u_s_census_bureau': 'U.S. Census Bureau',\n\t\t                                    'cdc_socrata': 'CDC Socrata',\n\t\t                                    'u_s_health': 'U.S. Health', 'who_global': 'WHO Global',\n\t\t                                    'united_nations': 'United Nations',\n\t\t                                    'world_population': 'World Population',\n\t\t                                    'cdc_wonder': 'CDC Wonder',\n\t\t                                    'pub_med_search': 'Pub Med Search',\n\t\t                                    'open_city_data': 'Open City Data', }\n\t\tif not active_source:\n\t\t\tst.info( 'Select a source, configure the request, and submit it to display results.' )\n\t\telse:\n\t\t\tst.caption( f"Active Source: {display_names.get( active_source, active_source )}" )\n'''
new_demographic_results = '''\twith right:\n\t\tactive_source = st.session_state.get( 'demographic_active_source', '' )\n\t\tdisplay_names: Dict[ str, str ] = { 'u_s_census_bureau': 'U.S. Census Bureau',\n\t\t                                    'cdc_socrata': 'CDC Socrata',\n\t\t                                    'u_s_health': 'U.S. Health', 'who_global': 'WHO Global',\n\t\t                                    'united_nations': 'United Nations',\n\t\t                                    'world_population': 'World Population',\n\t\t                                    'cdc_wonder': 'CDC Wonder',\n\t\t                                    'pub_med_search': 'Pub Med Search',\n\t\t                                    'open_city_data': 'Open City Data', }\n\t\tif active_source:\n\t\t\tst.caption( f"Active Source: {display_names.get( active_source, active_source )}" )\n'''
source = replace_once( source, old_demographic_results, new_demographic_results,
    'demographic redundant result panel' )

APP.write_text( source, encoding='utf-8' )
print( 'Requested application changes written to app.py.' )
