from pathlib import Path


processing_path = Path( 'processing.py' )
pipelines_path = Path( 'pipelines.py' )
app_path = Path( 'app.py' )
readme_path = Path( 'README.md' )

if not processing_path.exists( ):
	raise RuntimeError( 'processing.py was not found.' )
if pipelines_path.exists( ):
	raise RuntimeError( 'pipelines.py already exists.' )

pipelines = processing_path.read_text( encoding='utf-8' )
pipelines = pipelines.replace( 'Filename:                processing.py',
	'Filename:                pipelines.py', 1 )
pipelines = pipelines.replace( '<copyright file="processing.py"',
	'<copyright file="pipelines.py"', 1 )
pipelines = pipelines.replace( '\t     processing.py\n', '\t     pipelines.py\n', 1 )
pipelines = pipelines.replace(
	'    processing.py — multi-provider generative AI clients and orchestration helpers.',
	'    pipelines.py — application processing pipelines and orchestration helpers.', 1 )
pipelines = pipelines.replace(
	'        Provides Iyrin\'s documnet processing functionality',
	'        Provides Iyrin\'s document processing pipelines and orchestration functionality', 1 )

processor_import = 'from processors import PdfParser\n'
anchor = 'from langchain_text_splitters import RecursiveCharacterTextSplitter\n'
if processor_import not in pipelines:
	if anchor not in pipelines:
		raise RuntimeError( 'Could not locate pipelines import anchor.' )
	pipelines = pipelines.replace( anchor, anchor + processor_import, 1 )

pipelines_path.write_text( pipelines, encoding='utf-8' )
processing_path.unlink( )

app = app_path.read_text( encoding='utf-8' )
if 'from processing import (' not in app:
	raise RuntimeError( 'app.py processing import was not found.' )
app = app.replace( 'from processing import (', 'from pipelines import (PdfParser, ', 1 )
app = app.replace( 'from processors import PdfParser\n', '', 1 )
app_path.write_text( app, encoding='utf-8' )

readme = readme_path.read_text( encoding='utf-8' )
if 'processing.py' in readme:
	readme = readme.replace( 'processing.py', 'pipelines.py' )
readme_path.write_text( readme, encoding='utf-8' )
