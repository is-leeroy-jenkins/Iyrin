from __future__ import annotations

from pathlib import Path

APP = Path( 'app.py' )
source = APP.read_text( encoding='utf-8' )

old_import = 'StarMap, StarChart, WebFetcher, EarthObservatory, NearbyObjects, USGSScienceBase, CensusData'
new_import = 'StarMap, StarChart, WebFetcher, EarthObservatory, NearbyObjects, OpenScience, USGSScienceBase, CensusData'
if source.count( old_import ) != 1:
    raise RuntimeError( f'OpenScience import anchor count: {source.count( old_import )}' )
source = source.replace( old_import, new_import, 1 )

astro_marker = "\t\twith astro_c2:\n\t\t\trender_mode_document_tabs( 'astro', '📄 Loaded' )"
if source.count( astro_marker ) != 1:
    raise RuntimeError( f'Astronomical insertion anchor count: {source.count( astro_marker )}' )

open_science_ui = '''\n\t\t\t# --------- NASA OPEN SCIENCE DATA REPOSITORY\n\t\t\twith st.expander( '🧬 NASA Open Science Data', expanded=False ):\n\t\t\t\topen_science_mode = st.selectbox( 'Mode',\n\t\t\t\t\toptions=[ 'dataset', 'metadata', 'assays', 'data' ],\n\t\t\t\t\tkey='astro_open_science_mode' )\n\t\t\t\topen_science_timeout = st.slider( 'Timeout', min_value=1, max_value=60, value=20,\n\t\t\t\t\tkey='astro_open_science_timeout' )\n\t\t\t\topen_science_query = ''\n\t\t\t\topen_science_accession = ''\n\t\t\t\topen_science_format = 'json'\n\t\t\t\tif open_science_mode == 'dataset':\n\t\t\t\t\topen_science_accession = st.text_input( 'OSDR Accession', value='OSD-48',\n\t\t\t\t\t\tkey='astro_open_science_accession' )\n\t\t\t\telse:\n\t\t\t\t\topen_science_c1, open_science_c2 = st.columns( 2 )\n\t\t\t\t\twith open_science_c1:\n\t\t\t\t\t\topen_science_query = st.text_input( 'Query',\n\t\t\t\t\t\t\tkey='astro_open_science_query' )\n\t\t\t\t\twith open_science_c2:\n\t\t\t\t\t\topen_science_format = st.selectbox( 'Format',\n\t\t\t\t\t\t\toptions=[ 'json', 'csv', 'tsv', 'browser' ],\n\t\t\t\t\t\t\tkey='astro_open_science_format' )\n\t\t\t\topen_science_btn_c1, open_science_btn_c2 = st.columns( 2 )\n\t\t\t\twith open_science_btn_c1:\n\t\t\t\t\tif st.button( label='Run', icon='🏃', key='astro_open_science_run',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\ttry:\n\t\t\t\t\t\t\tservice = OpenScience( )\n\t\t\t\t\t\t\tresult = service.fetch( mode=open_science_mode, query=open_science_query,\n\t\t\t\t\t\t\t\taccession=open_science_accession, format_value=open_science_format,\n\t\t\t\t\t\t\t\ttime=int( open_science_timeout ) )\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_source' ] = 'NASA Open Science Data'\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_result' ] = normalize( result ) or { }\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_latitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_longitude' ] = None\n\t\t\t\t\t\t\tst.session_state[ 'astro_last_url' ] = ''\n\t\t\t\t\t\t\tst.success( 'NASA Open Science Data request completed.' )\n\t\t\t\t\t\texcept Exception as ex:\n\t\t\t\t\t\t\tst.error( f'NASA Open Science Data request failed: {ex}' )\n\t\t\t\twith open_science_btn_c2:\n\t\t\t\t\tif st.button( label='Clear', icon='🧹', key='astro_open_science_clear',\n\t\t\t\t\t\t\tuse_container_width=True ):\n\t\t\t\t\t\tst.session_state[ 'astro_last_source' ] = ''\n\t\t\t\t\t\tst.session_state[ 'astro_last_result' ] = { }\n\t\t\t\t\t\tst.session_state[ 'astro_last_latitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'astro_last_longitude' ] = None\n\t\t\t\t\t\tst.session_state[ 'astro_last_url' ] = ''\n\t\t\t\tst.divider( )\n\t\t\t\trender_source_processing_controls( 'astro', 'astro_last_result',\n\t\t\t\t\t'astro_last_source', 'NASA Open Science Data', 'astro_open_science' )\n'''
source = source.replace( astro_marker, open_science_ui + astro_marker, 1 )
APP.write_text( source, encoding='utf-8' )
print( 'OpenScience UI integration written to app.py.' )
