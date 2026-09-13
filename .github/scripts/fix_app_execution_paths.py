from pathlib import Path
import re


app_path = Path( 'app.py' )
processing_path = Path( 'processing.py' )
requirements_path = Path( 'requirements.txt' )

app = app_path.read_text( encoding='utf-8' )
processing = processing_path.read_text( encoding='utf-8' )
requirements = requirements_path.read_text( encoding='utf-8' )

# -----------------------------------------------------------------------------
# Imports and shared state
# -----------------------------------------------------------------------------
app = app.replace( 'import html as html_lib\nimport json\nimport os\n',
    'import html as html_lib\nimport inspect\nimport json\nimport os\nimport tempfile\n', 1 )

old_processing_import = "from processing import (render_web_document_processing, render_source_processing_controls,\n                        render_mode_document_tabs)"
new_processing_import = "from processing import (clear_if_active, initialize_loading_state,\n                        rebuild_raw_text_from_documents, render_document_processing_actions,\n                        render_document_processing_controls, render_document_processing_inputs,\n                        render_loading_tabs, render_mode_document_tabs,\n                        render_source_processing_controls, reset_document_processing_controls,\n                        render_web_document_processing)"
if old_processing_import not in app:
    raise RuntimeError( 'Missing processing import anchor.' )
app = app.replace( old_processing_import, new_processing_import, 1 )

loader_import_end = "\tGoogleBucketLoader, AwsBucketLoader, EmailLoader, SpfxLoader, WebCrawler as LoaderWebCrawler)\n"
if loader_import_end not in app:
    raise RuntimeError( 'Missing loader import anchor.' )
app = app.replace( loader_import_end,
    loader_import_end + "from generators import Chat, Gemini, Grok, Mistral\nfrom processors import PdfParser\n", 1 )

utility_anchor = '# ---------------------------------------------------------------------\n# UTILITIES\n# ---------------------------------------------------------------------\n'
if utility_anchor not in app:
    raise RuntimeError( 'Missing utilities anchor.' )
app = app.replace( utility_anchor, 'initialize_loading_state( )\n\n' + utility_anchor, 1 )

# -----------------------------------------------------------------------------
# Provider dispatcher
# -----------------------------------------------------------------------------
selector_end = "\treturn selected\n\n# ------------- DATASET UTILITIES"
provider_helper = """\treturn selected\n\ndef invoke_provider( provider: object, prompt: str, parameters: Dict[ str, object ] ) -> object:\n\t\"\"\"\n\t\tPurpose:\n\t\t--------\n\t\tInvoke a provider's text-generation method using only parameters declared by the\n\t\tprovider method signature.\n\n\t\tParameters:\n\t\t-----------\n\t\tprovider (object): Provider wrapper instance.\n\t\tprompt (str): Prompt submitted to the provider.\n\t\tparameters (Dict[str, object]): Candidate provider parameters.\n\n\t\tReturns:\n\t\t--------\n\t\tobject: Provider response.\n\t\"\"\"\n\tthrow_if( 'provider', provider )\n\tthrow_if( 'prompt', prompt )\n\tthrow_if( 'parameters', parameters )\n\tmethod = getattr( provider, 'generate_text', None )\n\tif not callable( method ):\n\t\traise TypeError( 'Provider does not expose generate_text( ).' )\n\n\tsignature = inspect.signature( method )\n\taccepted = {\n\t\tname for name, parameter in signature.parameters.items( )\n\t\tif parameter.kind in ( inspect.Parameter.POSITIONAL_OR_KEYWORD,\n\t\t\tinspect.Parameter.KEYWORD_ONLY ) }\n\tfirst_parameter = next( iter( signature.parameters ), '' )\n\taccepted.discard( first_parameter )\n\tfiltered = { key: value for key, value in parameters.items( ) if key in accepted }\n\treturn method( prompt, **filtered )\n\n# ------------- DATASET UTILITIES"""
if selector_end not in app:
    raise RuntimeError( 'Missing model selector anchor.' )
app = app.replace( selector_end, provider_helper, 1 )
app = app.replace( '_invoke_provider(', 'invoke_provider(' )

# -----------------------------------------------------------------------------
# Sidebar execution paths
# -----------------------------------------------------------------------------
app = app.replace( "st.sessionn_state[ 'mode' ] = 'Geocoding'",
    "st.session_state[ 'mode' ] = 'Geocoding'" )

source_anchor = "\t\tuploaded = st.file_uploader( label='Upload Spreadsheet', type=[ 'xlsx', 'xls', 'csv' ],\n\t\t\tkey='source_uploader' )\n\t\t\n\t\tif source == 'Default Data':"
source_replacement = "\t\tuploaded = st.file_uploader( label='Upload Spreadsheet', type=[ 'xlsx', 'xls', 'csv' ],\n\t\t\tkey='source_uploader' )\n\t\tdf_default = pd.DataFrame( )\n\t\tdf_original: pd.DataFrame | None = None\n\t\t\n\t\tif source == 'Default Data':"
if source_anchor not in app:
    raise RuntimeError( 'Missing source initialization anchor.' )
app = app.replace( source_anchor, source_replacement, 1 )
app = app.replace( "table_options = df_tables[ 'name' ].tolist( )[ :3 ]",
    "table_options = df_tables[ 'name' ].tolist( )", 1 )
app = app.replace( 'loaded_original = df_default.copy( )', 'df_original = df_default.copy( )' )
app = app.replace( "\t\t\t\t\t\t\tlog_step( f'Loaded Database Table: {selected_table}' )",
    "\t\t\t\t\t\t\tst.session_state[ 'map_mode_table' ] = selected_table\n\t\t\t\t\t\t\tlog_step( f'Loaded Database Table: {selected_table}' )", 1 )
app = app.replace( "\t\t\tdf_original = df_default.copy( )\n\t\t\tlog_step( f'Loaded Database Table: {cfg.DEFAULT_DATA}' )",
    "\t\t\tdf_original = df_default.copy( )\n\t\t\tst.session_state[ 'map_mode_table' ] = cfg.DEFAULT_DATA\n\t\t\tlog_step( f'Loaded Database Table: {cfg.DEFAULT_DATA}' )", 1 )

# Credentials use the matching session/config/environment keys.
app = app.replace( "os.environ[ 'AIRNOW_API_KEY' ] = openaq_key",
    "os.environ[ 'OPENAQ_API_KEY' ] = openaq_key", 1 )
app = app.replace( "value=st.session_state.opensky_api_client_id or '',\n\t\t\thelp='Overrides FIRMS_MAP_KEY",
    "value=st.session_state.firms_map_key or '',\n\t\t\thelp='Overrides FIRMS_MAP_KEY", 1 )
app = app.replace( "\t\tif opensky_client:\n\t\t\tst.session_state.opensky_api_credentials = opensky_credentials",
    "\t\tif opensky_credentials:\n\t\t\tst.session_state.opensky_api_credentials = opensky_credentials", 1 )
app = app.replace( "st.session_state.purpleair_key = purpleair_key",
    "st.session_state.purpleair_api_key = purpleair_key", 1 )

# Keep config constants synchronized with session overrides used by provider wrappers.
credential_assignments = {
    "os.environ[ 'OPENAI_API_KEY' ] = openai_key": "os.environ[ 'OPENAI_API_KEY' ] = openai_key\n\t\t\tcfg.OPENAI_API_KEY = openai_key",
    "os.environ[ 'GEMINI_API_KEY' ] = gemini_key": "os.environ[ 'GEMINI_API_KEY' ] = gemini_key\n\t\t\tcfg.GEMINI_API_KEY = gemini_key",
    "os.environ[ 'XAI_API_KEY' ] = xai_key": "os.environ[ 'XAI_API_KEY' ] = xai_key\n\t\t\tcfg.XAI_API_KEY = xai_key",
    "os.environ[ 'CLAUDE_API_KEY' ] = claude_key": "os.environ[ 'CLAUDE_API_KEY' ] = claude_key\n\t\t\tcfg.CLAUDE_API_KEY = claude_key",
    "os.environ[ 'MISTRAL_API_KEY' ] = mistral_key": "os.environ[ 'MISTRAL_API_KEY' ] = mistral_key\n\t\t\tcfg.MISTRAL_API_KEY = mistral_key",
    "os.environ[ 'GOOGLE_API_KEY' ] = google_key": "os.environ[ 'GOOGLE_API_KEY' ] = google_key\n\t\t\tcfg.GOOGLE_API_KEY = google_key",
    "os.environ[ 'GOOGLEMAPS_API_KEY' ] = googlemaps_key": "os.environ[ 'GOOGLEMAPS_API_KEY' ] = googlemaps_key\n\t\t\tcfg.GOOGLEMAPS_API_KEY = googlemaps_key",
}
for old_value, new_value in credential_assignments.items( ):
    if old_value in app:
        app = app.replace( old_value, new_value, 1 )

# -----------------------------------------------------------------------------
# Loading-mode processing contracts
# -----------------------------------------------------------------------------
pattern = re.compile(
    r"(?P<indent>\t+)render_source_processing_controls\( '(?P<loader>[A-Za-z0-9_]+)', '(?P<key>loader_[A-Za-z0-9_]+)' \)" )
app, replaced_count = pattern.subn(
    lambda match: (f"{match.group( 'indent' )}render_document_processing_controls( "
                   f"'{match.group( 'loader' )}', '{match.group( 'key' )}' )"), app )
if replaced_count != 18:
    raise RuntimeError( f'Expected 18 invalid loader processing calls; replaced {replaced_count}.' )

# Remove the non-formatting f-prefix flagged by static analysis.
app = app.replace( 'st.markdown( f"""\n    <div class="foo-status-bar">',
    'st.markdown( """\n    <div class="foo-status-bar">', 1 )

# -----------------------------------------------------------------------------
# Generic Loading-mode processing helpers
# -----------------------------------------------------------------------------
processing_anchor = 'def initialize_web_state( ) -> None:\n'
if processing_anchor not in processing:
    raise RuntimeError( 'Missing processing helper insertion anchor.' )

loader_helpers = r'''def initialize_loading_state( ) -> None:
	"""
		Purpose:
		--------
		Initialize the shared document-loading state used by every Loading-mode execution path.

		Returns:
		--------
		None
	"""
	defaults = {
		'documents': [ ], 'raw_documents': [ ], 'raw_text': '', 'processed_text': None,
		'lines': None, 'tokens': [ ], 'chunked_documents': [ ], 'df_chunks': pd.DataFrame( ),
		'embeddings': [ ], 'embedder': None, 'vector_store': None, 'active_loader': None,
		'pdf_pages': None,
	}
	for key, value in defaults.items( ):
		if key not in st.session_state:
			st.session_state[ key ] = value

def rebuild_raw_text_from_documents( ) -> str:
	"""
		Purpose:
		--------
		Rebuild the shared raw-text representation from the currently loaded documents.

		Returns:
		--------
		str: Concatenated document text.
	"""
	initialize_loading_state( )
	return '\n\n'.join(
		document.page_content for document in st.session_state[ 'documents' ]
		if isinstance( getattr( document, 'page_content', None ), str )
		and document.page_content.strip( ) )

def reset_document_processing_controls( key_prefix: str ) -> None:
	"""
		Purpose:
		--------
		Clear derived chunk, embedding, and vector-store state for one loader workflow.

		Parameters:
		-----------
		key_prefix (str): Stable loader-control key prefix.

		Returns:
		--------
		None
	"""
	throw_if( 'key_prefix', key_prefix )
	initialize_loading_state( )
	st.session_state[ 'chunked_documents' ] = [ ]
	st.session_state[ 'df_chunks' ] = pd.DataFrame( )
	st.session_state[ 'embeddings' ] = [ ]
	st.session_state[ 'embedder' ] = None
	st.session_state[ 'vector_store' ] = None
	st.session_state.pop( f'{key_prefix}_processing_settings', None )

def clear_if_active( loader_name: str ) -> None:
	"""
		Purpose:
		--------
		Remove documents owned by the selected loader while preserving documents from other loaders.

		Parameters:
		-----------
		loader_name (str): Loader metadata name to clear.

		Returns:
		--------
		None
	"""
	throw_if( 'loader_name', loader_name )
	initialize_loading_state( )
	documents = st.session_state.get( 'documents', [ ] ) or [ ]
	remaining = [
		document for document in documents
		if ( getattr( document, 'metadata', { } ) or { } ).get( 'loader' ) != loader_name ]
	st.session_state[ 'documents' ] = remaining
	st.session_state[ 'raw_documents' ] = list( remaining )
	st.session_state[ 'raw_text' ] = rebuild_raw_text_from_documents( )
	if st.session_state.get( 'active_loader' ) == loader_name:
		st.session_state[ 'active_loader' ] = (
			( getattr( remaining[ -1 ], 'metadata', { } ) or { } ).get( 'loader' )
			if remaining else None )
	st.session_state[ 'processed_text' ] = None
	st.session_state[ 'lines' ] = None
	st.session_state[ 'chunked_documents' ] = [ ]
	st.session_state[ 'df_chunks' ] = pd.DataFrame( )
	st.session_state[ 'embeddings' ] = [ ]
	st.session_state[ 'embedder' ] = None
	st.session_state[ 'vector_store' ] = None

def render_document_processing_inputs( loader_name: str, key_prefix: str ) -> None:
	"""
		Purpose:
		--------
		Render chunking, embedding, and vector-storage controls for a document loader.

		Parameters:
		-----------
		loader_name (str): Loader metadata name.
		key_prefix (str): Stable Streamlit widget key prefix.

		Returns:
		--------
		None
	"""
	throw_if( 'loader_name', loader_name )
	throw_if( 'key_prefix', key_prefix )
	initialize_loading_state( )
	st.session_state[ f'{key_prefix}_processing_settings' ] = render_processing_inputs(
		key_prefix, f'iyr-{key_prefix}-documents' )

def get_loader_documents( loader_name: str ) -> List[ Document ]:
	"""Return documents owned by one loader from shared Loading-mode state."""
	throw_if( 'loader_name', loader_name )
	initialize_loading_state( )
	documents = st.session_state.get( 'documents', [ ] ) or [ ]
	matched = [
		document for document in documents
		if ( getattr( document, 'metadata', { } ) or { } ).get( 'loader' ) == loader_name ]
	if matched:
		return matched
	if st.session_state.get( 'active_loader' ) == loader_name:
		return list( documents )
	return [ ]

def render_document_processing_actions( loader_name: str, key_prefix: str ) -> None:
	"""
		Purpose:
		--------
		Execute chunking, embedding, and vector-storage actions for one document loader.

		Parameters:
		-----------
		loader_name (str): Loader metadata name.
		key_prefix (str): Stable Streamlit widget key prefix.

		Returns:
		--------
		None
	"""
	throw_if( 'loader_name', loader_name )
	throw_if( 'key_prefix', key_prefix )
	initialize_loading_state( )
	settings = st.session_state.get( f'{key_prefix}_processing_settings', None )
	if not isinstance( settings, dict ):
		st.warning( 'Processing controls are not initialized.' )
		return

	chunk_col, embed_col, store_col = st.columns( 3 )
	chunk_run = chunk_col.button( 'Chunk', icon='✂️', key=f'{key_prefix}_loader_chunk',
		use_container_width=True )
	embed_run = embed_col.button( 'Embed', icon='🧬', key=f'{key_prefix}_loader_embed',
		use_container_width=True )
	store_run = store_col.button( 'Store', icon='🗄️', key=f'{key_prefix}_loader_store',
		use_container_width=True )

	if chunk_run:
		try:
			documents = get_loader_documents( loader_name )
			throw_if( 'documents', documents )
			chunks = chunk_documents( documents, settings[ 'chunk_size' ], settings[ 'chunk_overlap' ] )
			st.session_state[ 'chunked_documents' ] = chunks
			st.session_state[ 'df_chunks' ] = pd.DataFrame( [ {
				'Chunk': index,
				'Chunk ID': ( document.metadata or { } ).get( 'chunk_id', '' ),
				'Source': ( document.metadata or { } ).get( 'source', '' ),
				'Characters': len( document.page_content ),
				'Text': document.page_content,
			} for index, document in enumerate( chunks, start=1 ) ] )
			st.session_state[ 'embeddings' ] = [ ]
			st.session_state[ 'embedder' ] = None
			st.session_state[ 'vector_store' ] = None
			st.success( f'Created {len( chunks ):,} chunk(s).' )
		except Exception as exc:
			st.error( str( exc ) )

	if embed_run:
		try:
			chunks = st.session_state.get( 'chunked_documents', [ ] ) or [ ]
			throw_if( 'chunks', chunks )
			embedder, vectors = create_embeddings( chunks, settings[ 'provider' ],
				settings[ 'model' ], settings[ 'model_path' ] )
			st.session_state[ 'embedder' ] = embedder
			st.session_state[ 'embeddings' ] = vectors
			st.session_state[ 'vector_store' ] = None
			st.success( f'Created {len( vectors ):,} embedding vector(s).' )
		except Exception as exc:
			st.error( str( exc ) )

	if store_run:
		try:
			chunks = st.session_state.get( 'chunked_documents', [ ] ) or [ ]
			embedder = st.session_state.get( 'embedder', None )
			throw_if( 'chunks', chunks )
			throw_if( 'embedder', embedder )
			st.session_state[ 'vector_store' ] = store_documents(
				chunks, embedder, settings[ 'vector_backend' ], settings[ 'vector_target' ],
				settings[ 'persist_directory' ], settings[ 'namespace' ] )
			st.success( f"Stored {len( chunks ):,} chunk(s) in {settings[ 'vector_backend' ]}." )
		except Exception as exc:
			st.error( str( exc ) )

def render_document_processing_controls( loader_name: str, key_prefix: str ) -> None:
	"""Render document-processing inputs and actions for one loader."""
	render_document_processing_inputs( loader_name, key_prefix )
	render_document_processing_actions( loader_name, key_prefix )

def render_loading_tabs( ) -> None:
	"""Render shared Loaded, Chunks, and Embeddings tabs for Loading mode."""
	initialize_loading_state( )
	loaded_tab, chunks_tab, embeddings_tab = st.tabs(
		[ '📄 Loaded', '✂️ Chunks', '🔢 Embeddings' ] )
	with loaded_tab:
		documents = st.session_state.get( 'documents', [ ] ) or [ ]
		if not documents:
			st.info( 'Load a document to display its content.' )
		else:
			rows = [ {
				'Document': index,
				'Loader': ( document.metadata or { } ).get( 'loader', '' ),
				'Source': ( document.metadata or { } ).get( 'source', '' ),
				'Characters': len( document.page_content ),
				'Text': document.page_content,
			} for index, document in enumerate( documents, start=1 ) ]
			st.data_editor( pd.DataFrame( rows ), use_container_width=True, hide_index=True,
				disabled=True )
	with chunks_tab:
		df_chunks = st.session_state.get( 'df_chunks', pd.DataFrame( ) )
		if not isinstance( df_chunks, pd.DataFrame ) or df_chunks.empty:
			st.info( 'Run Chunk to display document chunks.' )
		else:
			st.data_editor( df_chunks, use_container_width=True, hide_index=True, disabled=True )
	with embeddings_tab:
		vectors = st.session_state.get( 'embeddings', [ ] ) or [ ]
		chunks = st.session_state.get( 'chunked_documents', [ ] ) or [ ]
		if not vectors:
			st.info( 'Run Embed to display embedding vectors.' )
		else:
			rows = [ {
				'Chunk': index + 1,
				'Dimensions': len( vector ),
				'Source': ( chunks[ index ].metadata or { } ).get( 'source', '' )
					if index < len( chunks ) else '',
				'Vector': vector,
			} for index, vector in enumerate( vectors ) ]
			st.data_editor( pd.DataFrame( rows ), use_container_width=True, hide_index=True,
				disabled=True )

'''
processing = processing.replace( processing_anchor, loader_helpers + processing_anchor, 1 )

# -----------------------------------------------------------------------------
# Geometry-aware PDF parser
# -----------------------------------------------------------------------------
processors_path = Path( 'processors.py' )
processors = r'''\'\'\'
******************************************************************************************
 Assembly:                iyr
 Filename:                processors.py
 Author:                  Terry D. Eppler
******************************************************************************************

Purpose:
    Geometry-aware document processing used by Iyrin loading workflows.
******************************************************************************************
\'\'\'
from __future__ import annotations

from typing import List


def throw_if( name: str, value: object ) -> None:
	if value is None:
		raise ValueError( f'Argument "{name}" cannot be empty!' )
	if isinstance( value, str ) and not value.strip( ):
		raise ValueError( f'Argument "{name}" cannot be empty!' )


class PdfParser( ):
	"""Geometry-aware PDF extraction component."""

	def extract_pages( self, path: str, count: int=0, header_ratio: float=0.08,
		footer_ratio: float=0.08 ) -> List[ dict ]:
		"""
		Purpose:
		    Extract text blocks by page and classify them as header, body, or footer content.

		Parameters:
		    path (str): PDF file path.
		    count (int): Maximum pages to read; zero reads all pages.
		    header_ratio (float): Fraction of page height reserved for the header band.
		    footer_ratio (float): Fraction of page height reserved for the footer band.

		Returns:
		    List[dict]: Page records containing classified text blocks.
		"""
		throw_if( 'path', path )
		if header_ratio < 0.0 or header_ratio > 0.5:
			raise ValueError( 'Header ratio must be between 0.0 and 0.5.' )
		if footer_ratio < 0.0 or footer_ratio > 0.5:
			raise ValueError( 'Footer ratio must be between 0.0 and 0.5.' )
		import fitz

		pages: List[ dict ] = [ ]
		with fitz.open( path ) as document:
			page_count = len( document ) if count <= 0 else min( count, len( document ) )
			for page_index in range( page_count ):
				page = document[ page_index ]
				height = float( page.rect.height )
				header_limit = height * float( header_ratio )
				footer_limit = height * ( 1.0 - float( footer_ratio ) )
				record = { 'page': page_index + 1, 'header': [ ], 'body': [ ], 'footer': [ ] }
				for block in page.get_text( 'blocks' ):
					x0, y0, x1, y1, text = block[ :5 ]
					value = str( text or '' ).strip( )
					if not value:
						continue
					item = { 'text': value, 'x0': float( x0 ), 'y0': float( y0 ),
						'x1': float( x1 ), 'y1': float( y1 ) }
					if float( y1 ) <= header_limit:
						record[ 'header' ].append( item )
					elif float( y0 ) >= footer_limit:
						record[ 'footer' ].append( item )
					else:
						record[ 'body' ].append( item )
				pages.append( record )
		return pages

	def rebuild_pages( self, pages: List[ dict ], preserve_page_breaks: bool=False ) -> str:
		"""Rebuild body text from geometry-aware page records."""
		throw_if( 'pages', pages )
		page_text: List[ str ] = [ ]
		for page in pages:
			body = page.get( 'body', [ ] ) if isinstance( page, dict ) else [ ]
			text = '\n'.join( str( block.get( 'text', '' ) ).strip( ) for block in body
				if isinstance( block, dict ) and str( block.get( 'text', '' ) ).strip( ) )
			if text:
				page_text.append( text )
		separator = '\n\n--- PAGE BREAK ---\n\n' if preserve_page_breaks else '\n\n'
		return separator.join( page_text )
'''
processors_path.write_text( processors, encoding='utf-8' )

# -----------------------------------------------------------------------------
# Runtime dependencies used directly by app execution paths
# -----------------------------------------------------------------------------
required_packages = [ 'PyMuPDF', 'openai', 'anthropic', 'xai-sdk', 'mistralai', 'nltk' ]
lines = requirements.splitlines( )
for package in required_packages:
    if package not in lines:
        lines.append( package )
requirements = '\n'.join( lines ) + '\n'

app_path.write_text( app, encoding='utf-8' )
processing_path.write_text( processing, encoding='utf-8' )
requirements_path.write_text( requirements, encoding='utf-8' )
