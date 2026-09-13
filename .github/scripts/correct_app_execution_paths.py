from pathlib import Path
import re

app_path = Path( 'app.py' )
app = app_path.read_text( encoding='utf-8' )

app = app.replace(
    "from pipelines import (PdfParser, clear_if_active, initialize_loading_state,",
    "from pipelines import (PdfParser, clear_if_active, clear_loader_documents, "
    "promote_loader_documents, initialize_loading_state, sync_mode_document," )

app = app.replace(
    "StarMap, StarChart, WebFetcher)",
    "StarMap, StarChart, WebFetcher, CensusData, Socrata, HealthData, GlobalHealthData, "
    "UnitedNations, WorldPopulation, Wonder)" )

helper_replacements = {
    '_render_result_metadata': 'render_result_metadata',
    '_render_summary_kv': 'render_summary_kv',
    '_render_rows_table': 'render_rows_table',
    '_render_fallback_raw': 'render_fallback_raw',
    '_render_html_preview': 'render_html_preview',
    '_render_xml_preview': 'render_xml_preview',
    '_clear_loader_documents': 'clear_loader_documents',
    '_promote_loader_documents': 'promote_loader_documents',
}
for old_name, new_name in helper_replacements.items( ):
    app = app.replace( old_name, new_name )

source_result_keys = {
    'u_s_census_bureau': 'census_results',
    'cdc_socrata': 'socrata_results',
    'u_s_health': 'healthdata_results',
    'who_global': 'who_results',
    'united_nations': 'un_results',
    'world_population': 'worldpop_results',
    'cdc_wonder': 'wonder_results',
    'pub_med_search': 'pubmed_results',
    'open_city_data': 'open_city_results',
}
pattern = re.compile(
    r"render_source_processing_controls\(\s*'(?P<source>" +
    '|'.join( re.escape( source ) for source in source_result_keys ) +
    r")',\s*'(?P<key>[^']+)'\s*\)" )

def replace_processing_call( match: re.Match[ str ] ) -> str:
    source = match.group( 'source' )
    key_prefix = match.group( 'key' )
    result_key = source_result_keys[ source ]
    return (
        "render_source_processing_controls( 'demographic', "
        f"'{result_key}', 'demographic_active_source', '{source}', '{key_prefix}' )" )

app = pattern.sub( replace_processing_call, app )

old_footer = """\t\tdemographic_result_keys: Dict[ str, str ] = { 'u_s_census_bureau': 'census_results',
\t\t\t\t'cdc_socrata': 'socrata_results', 'u_s_health': 'healthdata_results',
\t\t\t\t'who_global': 'who_results', 'united_nations': 'un_results',
\t\t\t\t'world_population': 'worldpop_results', 'cdc_wonder': 'wonder_results',
\t\t\t\t'pub_med_search': 'pubmed_results', 'open_city_data': 'open_city_results', }
\t\tif active_source in demographic_result_keys:
\t\t\tpromote_source_result( mode_name='Demographic', source_name=active_source,
\t\t\t\tresult=st.session_state.get( demographic_result_keys[ active_source ] ) )
\t\trender_document_processing_tabs( key_prefix='demographic' )
"""
new_footer = """\t\tdemographic_result_keys: Dict[ str, str ] = { 'u_s_census_bureau': 'census_results',
\t\t\t\t'cdc_socrata': 'socrata_results', 'u_s_health': 'healthdata_results',
\t\t\t\t'who_global': 'who_results', 'united_nations': 'un_results',
\t\t\t\t'world_population': 'worldpop_results', 'cdc_wonder': 'wonder_results',
\t\t\t\t'pub_med_search': 'pubmed_results', 'open_city_data': 'open_city_results', }
\t\tif active_source in demographic_result_keys:
\t\t\tsync_mode_document( 'demographic', demographic_result_keys[ active_source ],
\t\t\t\t'demographic_active_source' )
\t\trender_mode_document_tabs( 'demographic', '📄 Loaded' )
"""
if old_footer not in app:
    raise RuntimeError( 'Demographic processing footer was not found.' )
app = app.replace( old_footer, new_footer )

ui_helpers = r'''
def render_result_metadata( result: Dict[ str, Any ] ) -> None:
	"""
		Purpose:
		--------
		Render common metadata returned by an API fetcher.

		Parameters:
		-----------
		result (Dict[str, Any]): Structured fetcher result.

		Returns:
		--------
		None
	"""
	throw_if( 'result', result )
	metadata = { key: result.get( key ) for key in [ 'source', 'mode', 'status', 'url' ]
		if result.get( key ) not in [ None, '' ] }
	if metadata:
		st.caption( ' | '.join( f'{key.title( )}: {value}' for key, value in metadata.items( ) ) )


def render_summary_kv( title: str, values: Dict[ str, Any ] ) -> None:
	"""
		Purpose:
		--------
		Render a two-column key/value summary table.

		Parameters:
		-----------
		title (str): Markdown heading displayed above the summary.
		values (Dict[str, Any]): Summary values to display.

		Returns:
		--------
		None
	"""
	throw_if( 'title', title )
	throw_if( 'values', values )
	st.markdown( title )
	rows = [ { 'Field': key, 'Value': value } for key, value in values.items( ) ]
	st.data_editor( pd.DataFrame( rows ), use_container_width=True, hide_index=True, disabled=True )


def render_rows_table( title: str, rows: List[ Dict[ str, Any ] ] ) -> None:
	"""
		Purpose:
		--------
		Render structured API rows in a read-only data editor.

		Parameters:
		-----------
		title (str): Markdown heading displayed above the rows.
		rows (List[Dict[str, Any]]): Records to display.

		Returns:
		--------
		None
	"""
	throw_if( 'title', title )
	st.markdown( title )
	if rows:
		st.data_editor( pd.DataFrame( rows ), use_container_width=True, hide_index=True,
			disabled=True )
	else:
		st.info( 'No rows returned.' )


def render_fallback_raw( result: Dict[ str, Any ] ) -> None:
	"""
		Purpose:
		--------
		Expose the complete structured API response for inspection.

		Parameters:
		-----------
		result (Dict[str, Any]): Structured fetcher result.

		Returns:
		--------
		None
	"""
	throw_if( 'result', result )
	with st.expander( 'Raw Response', expanded=False ):
		st.json( result )


def render_html_preview( title: str, html_text: str ) -> None:
	"""
		Purpose:
		--------
		Render returned HTML content in an isolated Streamlit component.

		Parameters:
		-----------
		title (str): Markdown heading displayed above the preview.
		html_text (str): HTML payload to render.

		Returns:
		--------
		None
	"""
	throw_if( 'title', title )
	throw_if( 'html_text', html_text )
	st.markdown( title )
	components.html( html_text, height=500, scrolling=True )


def render_xml_preview( title: str, xml_text: str ) -> None:
	"""
		Purpose:
		--------
		Pretty-print returned XML content.

		Parameters:
		-----------
		title (str): Markdown heading displayed above the preview.
		xml_text (str): XML payload to display.

		Returns:
		--------
		None
	"""
	throw_if( 'title', title )
	throw_if( 'xml_text', xml_text )
	st.markdown( title )
	try:
		root = etree.fromstring( xml_text.encode( 'utf-8' ) )
		formatted = etree.tostring( root, pretty_print=True, encoding='unicode' )
	except Exception:
		formatted = xml_text
	st.code( formatted, language='xml' )
'''
if 'def render_result_metadata( result: Dict[ str, Any ] ) -> None:' not in app:
    anchor = 'def style_subheaders( ) -> None:'
    if anchor not in app:
        raise RuntimeError( 'Application utility insertion anchor was not found.' )
    app = app.replace( anchor, ui_helpers.strip( ) + '\n\n' + anchor, 1 )
app_path.write_text( app, encoding='utf-8' )

pipelines_path = Path( 'pipelines.py' )
pipelines = pipelines_path.read_text( encoding='utf-8' )
loader_helpers = r'''
def clear_loader_documents( loader_name: str ) -> int:
	"""
		Purpose:
		--------
		Remove documents owned by one loader and return the remaining document count.

		Parameters:
		-----------
		loader_name (str): Loader metadata name to clear.

		Returns:
		--------
		int: Number of documents remaining in shared loading state.
	"""
	throw_if( 'loader_name', loader_name )
	clear_if_active( loader_name )
	return len( st.session_state.get( 'documents', [ ] ) or [ ] )


def promote_loader_documents( documents: List[ Document ], loader_name: str ) -> int:
	"""
		Purpose:
		--------
		Promote loader output into shared document-processing state.

		Parameters:
		-----------
		documents (List[Document]): Documents returned by the loader.
		loader_name (str): Loader metadata name assigned to promoted documents.

		Returns:
		--------
		int: Number of documents promoted.
	"""
	throw_if( 'documents', documents )
	throw_if( 'loader_name', loader_name )
	initialize_loading_state( )
	clear_if_active( loader_name )
	promoted: List[ Document ] = [ ]
	for document in documents:
		metadata = dict( document.metadata or { } )
		metadata[ 'loader' ] = loader_name
		document.metadata = metadata
		promoted.append( document )
	remaining = st.session_state.get( 'documents', [ ] ) or [ ]
	st.session_state[ 'documents' ] = list( remaining ) + promoted
	st.session_state[ 'raw_documents' ] = list( st.session_state[ 'documents' ] )
	st.session_state[ 'raw_text' ] = rebuild_raw_text_from_documents( )
	st.session_state[ 'active_loader' ] = loader_name
	st.session_state[ 'processed_text' ] = None
	st.session_state[ 'lines' ] = None
	st.session_state[ 'chunked_documents' ] = [ ]
	st.session_state[ 'df_chunks' ] = pd.DataFrame( )
	st.session_state[ 'embeddings' ] = [ ]
	st.session_state[ 'embedder' ] = None
	st.session_state[ 'vector_store' ] = None
	return len( promoted )
'''
if 'def clear_loader_documents( loader_name: str ) -> int:' not in pipelines:
    pipelines = pipelines.rstrip( ) + '\n\n' + loader_helpers.strip( ) + '\n'
pipelines_path.write_text( pipelines, encoding='utf-8' )

fetchers_path = Path( 'fetchers.py' )
fetchers = fetchers_path.read_text( encoding='utf-8' )
if 'crawl4ai = None' not in fetchers:
    import_anchor = 'import xml.etree.ElementTree as ET\n'
    optional_import = """import xml.etree.ElementTree as ET

try:
	import crawl4ai
except ImportError:
	crawl4ai = None
"""
    if import_anchor not in fetchers:
        raise RuntimeError( 'Fetcher import insertion anchor was not found.' )
    fetchers = fetchers.replace( import_anchor, optional_import, 1 )

old_crawl = """\t\t\tconfiguration = { 'url': url }
\t\t\tpayload = crawl4ai.fetch_and_render( configuration )
\t\t\tif payload and isinstance( payload, dict ) and 'content' in payload:
\t\t\t\tself.raw_html = payload.get( 'content', '' )
\t\t\t\ttext = self.html_to_text( self.raw_html )
\t\t\t\tself.result = Result( url = url, status=200, text=text,
\t\t\t\t\thtml=self.raw_html, headers=self.headers )
\t\t\t\treturn self.result
"""
new_crawl = """\t\t\tif crawl4ai is not None and hasattr( crawl4ai, 'fetch_and_render' ):
\t\t\t\tconfiguration = { 'url': url }
\t\t\t\tpayload = crawl4ai.fetch_and_render( configuration )
\t\t\t\tif payload and isinstance( payload, dict ) and 'content' in payload:
\t\t\t\t\tself.raw_html = payload.get( 'content', '' )
\t\t\t\t\ttext = self.html_to_text( self.raw_html )
\t\t\t\t\tself.result = Result( url=url, status=200, text=text,
\t\t\t\t\t\thtml=self.raw_html, headers=self.headers )
\t\t\t\t\treturn self.result
\t\t\tresponse = requests.get( url, headers=self.headers, timeout=int( time ) )
\t\t\tresponse.raise_for_status( )
\t\t\tself.raw_html = response.text
\t\t\ttext = self.html_to_text( self.raw_html )
\t\t\tself.result = Result( url=url, status=response.status_code, text=text,
\t\t\t\thtml=self.raw_html, headers=dict( response.headers ) )
\t\t\treturn self.result
"""
if old_crawl in fetchers:
    fetchers = fetchers.replace( old_crawl, new_crawl, 1 )

fetcher_classes = r'''
def build_fetch_result( source: str, mode: str, url: str, status: int,
	data: Any ) -> Dict[ str, Any ]:
	"""Build the common structured result returned by demographic API fetchers."""
	throw_if( 'source', source )
	throw_if( 'mode', mode )
	throw_if( 'url', url )
	return { 'source': source, 'mode': mode, 'url': url, 'status': status, 'data': data }


class CensusData( ):
	"""U.S. Census Bureau API fetcher."""
	def fetch( self, mode: str, year: str, dataset: str, fields: str='',
		geography_for: str='', geography_in: str='', predicates: str='',
		time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		throw_if( 'year', year )
		throw_if( 'dataset', dataset )
		self.mode = mode
		self.year = year
		self.dataset = dataset.strip( '/' )
		self.fields = fields
		self.geography_for = geography_for
		self.geography_in = geography_in
		self.predicates = predicates
		self.time = time
		self.api_key = getattr( cfg, 'CENSUS_API_KEY', '' ) or ''
		base_url = f'https://api.census.gov/data/{self.year}/{self.dataset}'
		params: Dict[ str, str ] = { }
		if self.api_key:
			params[ 'key' ] = self.api_key
		if self.mode == 'variables':
			url = f'{base_url}/variables.json'
		elif self.mode == 'data':
			throw_if( 'fields', self.fields )
			throw_if( 'geography_for', self.geography_for )
			url = base_url
			params[ 'get' ] = self.fields
			params[ 'for' ] = self.geography_for
			if self.geography_in.strip( ):
				params[ 'in' ] = self.geography_in
			for key, value in urllib.parse.parse_qsl( self.predicates, keep_blank_values=True ):
				params[ key ] = value
		else:
			raise ValueError( f'Unsupported Census mode: {self.mode}' )
		response = requests.get( url, params=params, timeout=int( self.time ) )
		response.raise_for_status( )
		payload = response.json( )
		if self.mode == 'data' and isinstance( payload, list ) and payload:
			headers = payload[ 0 ]
			rows = [ dict( zip( headers, row ) ) for row in payload[ 1: ] ]
			payload = { 'rows': rows }
		return build_fetch_result( 'U.S. Census Bureau', self.mode, response.url,
			response.status_code, payload )


class Socrata( ):
	"""Socrata Open Data API fetcher."""
	def fetch( self, mode: str, domain: str, dataset_id: str, select: str='',
		where: str='', order: str='', group: str='', limit: int=100, offset: int=0,
		time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		throw_if( 'domain', domain )
		throw_if( 'dataset_id', dataset_id )
		self.mode = mode
		self.domain = domain.replace( 'https://', '' ).replace( 'http://', '' ).strip( '/' )
		self.dataset_id = dataset_id
		self.select = select
		self.where = where
		self.order = order
		self.group = group
		self.limit = limit
		self.offset = offset
		self.time = time
		self.api_key = getattr( cfg, 'SOCRATA_API_KEY', '' ) or ''
		headers = { 'X-App-Token': self.api_key } if self.api_key else { }
		if self.mode == 'metadata':
			url = f'https://{self.domain}/api/views/{self.dataset_id}'
			params = { }
		elif self.mode == 'rows':
			url = f'https://{self.domain}/resource/{self.dataset_id}.json'
			params: Dict[ str, Any ] = { '$limit': int( self.limit ), '$offset': int( self.offset ) }
			for key, value in [ ( '$select', self.select ), ( '$where', self.where ),
				( '$order', self.order ), ( '$group', self.group ) ]:
				if value.strip( ):
					params[ key ] = value
		else:
			raise ValueError( f'Unsupported Socrata mode: {self.mode}' )
		response = requests.get( url, params=params, headers=headers, timeout=int( self.time ) )
		response.raise_for_status( )
		return build_fetch_result( 'CDC Socrata', self.mode, response.url,
			response.status_code, response.json( ) )


class HealthData( Socrata ):
	"""U.S. HealthData.gov Socrata fetcher."""
	def fetch( self, mode: str, domain: str, dataset_id: str, select: str='',
		where: str='', order: str='', group: str='', limit: int=100, offset: int=0,
		time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		throw_if( 'domain', domain )
		throw_if( 'dataset_id', dataset_id )
		self.mode = mode
		self.domain = domain.replace( 'https://', '' ).replace( 'http://', '' ).strip( '/' )
		self.dataset_id = dataset_id
		self.select = select
		self.where = where
		self.order = order
		self.group = group
		self.limit = limit
		self.offset = offset
		self.time = time
		self.api_key = getattr( cfg, 'HEALTHDATA_API_KEY', '' ) or ''
		headers = { 'X-App-Token': self.api_key } if self.api_key else { }
		if self.mode == 'metadata':
			url = f'https://{self.domain}/api/views/{self.dataset_id}'
			params = { }
		elif self.mode == 'rows':
			url = f'https://{self.domain}/resource/{self.dataset_id}.json'
			params: Dict[ str, Any ] = { '$limit': int( self.limit ), '$offset': int( self.offset ) }
			for key, value in [ ( '$select', self.select ), ( '$where', self.where ),
				( '$order', self.order ), ( '$group', self.group ) ]:
				if value.strip( ):
					params[ key ] = value
		else:
			raise ValueError( f'Unsupported HealthData mode: {self.mode}' )
		response = requests.get( url, params=params, headers=headers, timeout=int( self.time ) )
		response.raise_for_status( )
		return build_fetch_result( 'U.S. Health', self.mode, response.url,
			response.status_code, response.json( ) )


class GlobalHealthData( ):
	"""WHO Global Health Observatory fetcher."""
	def fetch( self, mode: str, query_path: str='', fmt: str='json',
		time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		self.mode = mode
		self.query_path = query_path.strip( '/' )
		self.fmt = fmt
		self.time = time
		if self.mode == 'indicator_registry':
			url = 'https://www.who.int/data/gho/indicator-metadata-registry'
			response = requests.get( url, timeout=int( self.time ) )
			response.raise_for_status( )
			data: Any = { 'html': response.text }
		elif self.mode == 'athena':
			throw_if( 'query_path', self.query_path )
			url = f'https://ghoapi.azureedge.net/api/{self.query_path}'
			headers = { 'Accept': 'application/json' if self.fmt == 'json' else 'text/plain' }
			response = requests.get( url, headers=headers, timeout=int( self.time ) )
			response.raise_for_status( )
			if self.fmt == 'json':
				data = response.json( )
			else:
				data = { 'text': response.text }
		else:
			raise ValueError( f'Unsupported WHO mode: {self.mode}' )
		return build_fetch_result( 'WHO Global', self.mode, response.url,
			response.status_code, data )


class UnitedNations( ):
	"""United Nations UNdata REST/SDMX fetcher."""
	def fetch( self, mode: str, query_path: str='', time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		self.mode = mode
		self.query_path = query_path.strip( '/' )
		self.time = time
		if self.mode == 'datasets':
			url = 'https://data.un.org/'
			response = requests.get( url, timeout=int( self.time ) )
			response.raise_for_status( )
			data: Any = { 'html': response.text }
		elif self.mode == 'sdmx_query':
			throw_if( 'query_path', self.query_path )
			url = f'https://data.un.org/ws/rest/{self.query_path}'
			response = requests.get( url, timeout=int( self.time ) )
			response.raise_for_status( )
			content_type = response.headers.get( 'Content-Type', '' ).lower( )
			if 'json' in content_type:
				data = response.json( )
			elif 'html' in content_type:
				data = { 'html': response.text }
			else:
				data = { 'text': response.text }
		else:
			raise ValueError( f'Unsupported United Nations mode: {self.mode}' )
		return build_fetch_result( 'United Nations', self.mode, response.url,
			response.status_code, data )


class WorldPopulation( ):
	"""WorldPop REST data catalog fetcher."""
	def fetch( self, mode: str, query: str='', asset_path: str='', page: int=1,
		page_size: int=25, time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		self.mode = mode
		self.query = query
		self.asset_path = asset_path.lstrip( '/' )
		self.page = page
		self.page_size = page_size
		self.time = time
		base_url = 'https://www.worldpop.org/rest/data'
		if self.mode == 'catalog':
			response = requests.get( base_url, timeout=int( self.time ) )
			response.raise_for_status( )
			data: Any = response.json( )
		elif self.mode == 'raster_metadata':
			throw_if( 'asset_path', self.asset_path )
			url = f'https://www.worldpop.org/rest/{self.asset_path}'
			response = requests.get( url, timeout=int( self.time ) )
			response.raise_for_status( )
			try:
				data = response.json( )
			except ValueError:
				data = { 'text': response.text }
		elif self.mode == 'search':
			throw_if( 'query', self.query )
			response = requests.get( base_url, timeout=int( self.time ) )
			response.raise_for_status( )
			catalog = response.json( )
			records = catalog.get( 'data', [ ] ) if isinstance( catalog, dict ) else [ ]
			terms = [ term.lower( ) for term in self.query.split( ) if term.strip( ) ]
			matches = [ record for record in records if all(
				term in str( record ).lower( ) for term in terms ) ]
			start = max( 0, (int( self.page ) - 1) * int( self.page_size ) )
			data = { 'results': matches[ start:start + int( self.page_size ) ],
				'total': len( matches ) }
		else:
			raise ValueError( f'Unsupported WorldPop mode: {self.mode}' )
		return build_fetch_result( 'World Population', self.mode, response.url,
			response.status_code, data )


class Wonder( ):
	"""CDC WONDER XML API fetcher."""
	def fetch( self, mode: str, dataset_id: str, request_xml: str='',
		time: int=20 ) -> Dict[ str, Any ]:
		throw_if( 'mode', mode )
		throw_if( 'dataset_id', dataset_id )
		self.mode = mode
		self.dataset_id = dataset_id
		self.request_xml = request_xml
		self.time = time
		url = f'https://wonder.cdc.gov/controller/datarequest/{self.dataset_id}'
		if self.mode == 'metadata_template':
			template = (
				'<request-parameters>\n'
				'  <parameter>\n'
				'    <name>accept_datause_restrictions</name>\n'
				'    <value>true</value>\n'
				'  </parameter>\n'
				'</request-parameters>' )
			data: Any = { 'dataset_id': self.dataset_id, 'request_xml': template,
				'notes': 'Add dataset-specific grouping, filter, and measure parameters before submission.' }
			return build_fetch_result( 'CDC WONDER', self.mode, url, 200, data )
		if self.mode != 'query_xml':
			raise ValueError( f'Unsupported CDC WONDER mode: {self.mode}' )
		throw_if( 'request_xml', self.request_xml )
		response = requests.post( url, data={ 'request_xml': self.request_xml,
			'accept_datause_restrictions': 'true' }, timeout=int( self.time ) )
		response.raise_for_status( )
		data = { 'xml': response.text }
		return build_fetch_result( 'CDC WONDER', self.mode, response.url,
			response.status_code, data )
'''
if 'class CensusData( ):' not in fetchers:
    fetchers = fetchers.rstrip( ) + '\n\n' + fetcher_classes.strip( ) + '\n'
fetchers_path.write_text( fetchers, encoding='utf-8' )

requirements_path = Path( 'requirements.txt' )
requirements = requirements_path.read_text( encoding='utf-8' ).splitlines( )
for package in [ 'gensim', 'scikit-learn', 'spacy', 'textblob', 'tiktoken', 'lxml' ]:
    if package not in requirements:
        requirements.append( package )
requirements_path.write_text( '\n'.join( requirements ).rstrip( ) + '\n', encoding='utf-8' )
