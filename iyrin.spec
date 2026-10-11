# -*- mode: python ; coding: utf-8 -*-
"""Package Iyrin and its dynamically loaded application dependencies."""
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata

root = Path( SPECPATH )
datas = [(str( root / 'app.py' ), '.'),
         (str( root / '.streamlit' / 'config.toml' ), '.streamlit')]
datas += [(str( asset ), str( asset.parent.relative_to( root ) ))
          for asset in (root / 'resources').rglob( '*' )
          if asset.suffix.lower( ) in ('.png', '.ico', '.jpg')]
datas += [(str( root / 'static' ), 'static'),
          (str( root / 'browser-binaries' ), 'browser-binaries')]
# Runtime databases are created in user storage; development data and secrets are excluded.
hiddenimports = ['boogr', 'fetchers', 'history', 'distances', 'caches', 'sources', 'embedders', 'pipelines', 'generators', 'loaders', 'exceptions', 'processors', 'timezones', 'tools', 'maps', 'excel', 'world', 'geocode', 'places', 'staticmaps', 'core', 'rates', 'config', 'stores.vector']
binaries = []
for package in ('streamlit', 'webview', 'plotly', 'pydeck', 'matplotlib', 'streamlit_js_eval', 'streamlit_extras', 'cartopy', 'pyproj', 'astropy', 'astroquery', 'sgp4', 'sscws', 'owslib', 'google.genai', 'grokipedia_api', 'langchain_core', 'langchain_community', 'langchain_googledrive', 'langchain_text_splitters', 'langchain_openai', 'langchain_google_genai', 'langchain_mistralai', 'langchain_huggingface', 'langchain_chroma', 'langchain_pinecone', 'langchain_google_community', 'sentence_transformers', 'chromadb', 'pinecone', 'llama_cpp', 'unstructured', 'playwright', 'openai', 'anthropic', 'xai_sdk', 'mistralai', 'nltk', 'gensim', 'spacy', 'textblob', 'tiktoken'):
    package_datas, package_bins, package_hidden = collect_all( package )
    datas += package_datas
    binaries += package_bins
    hiddenimports += package_hidden
for distribution in ('streamlit', 'sentence-transformers', 'transformers'):
    datas += copy_metadata( distribution, recursive=True )

a = Analysis( [str( root / 'desktop.py' )], pathex=[str( root )],
    binaries=binaries, datas=datas, hiddenimports=hiddenimports,
    hookspath=[], runtime_hooks=[], excludes=[], noarchive=False )
pyz = PYZ( a.pure )
exe = EXE( pyz, a.scripts, [], exclude_binaries=True, name='Iyrin',
    console=False, disable_windowed_traceback=False )
coll = COLLECT( exe, a.binaries, a.datas, strip=False, upx=False, name='Iyrin' )
