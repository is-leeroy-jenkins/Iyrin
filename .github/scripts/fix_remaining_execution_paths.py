from pathlib import Path


app_path = Path( 'app.py' )
loaders_path = Path( 'loaders.py' )

app = app_path.read_text( encoding='utf-8' )
loaders = loaders_path.read_text( encoding='utf-8' )

replacements = {
    "render_source_processing_controls( 'JupyterNotebookLoader',\n\t\t\t\t\t'loader_jupyter_notebook_loader' )":
        "render_document_processing_controls( 'JupyterNotebookLoader',\n\t\t\t\t\t'loader_jupyter_notebook_loader' )",
    "render_source_processing_controls( 'GoogleCloudFileLoader',\n\t\t\t\t\t'loader_google_cloud_file_loader' )":
        "render_document_processing_controls( 'GoogleCloudFileLoader',\n\t\t\t\t\t'loader_google_cloud_file_loader' )",
    "render_source_processing_controls( 'GoogleBucketLoader',\n\t\t\t\t\t'loader_google_bucket_loader' )":
        "render_document_processing_controls( 'GoogleBucketLoader',\n\t\t\t\t\t'loader_google_bucket_loader' )",
}

for old_value, new_value in replacements.items( ):
    if old_value not in app:
        raise RuntimeError( f'Missing remaining loader-processing anchor: {old_value}' )
    app = app.replace( old_value, new_value, 1 )

stale_import = 'from langchain_community.chat_models import ChatOpenAI\n'
if stale_import in loaders:
    loaders = loaders.replace( stale_import, '', 1 )

app_path.write_text( app, encoding='utf-8' )
loaders_path.write_text( loaders, encoding='utf-8' )
