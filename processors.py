'''
******************************************************************************************
 Assembly:                iyr
 Filename:                processors.py
 Author:                  Terry D. Eppler
******************************************************************************************

Purpose:
    Geometry-aware document processing used by Iyrin loading workflows.
******************************************************************************************
'''
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
