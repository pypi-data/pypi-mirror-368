"""
 Sphinx defaultly generate namespace pages liek azure azure-core
 We have different ways to deal with it compare to Azure SDK scripts
 We pass --implicit-namespaces to mark parent level namespaces, instead they're defaultly packages
 We exclude parent namespaces' __init__.py when running sphinx-apidoc otherwise it throws exception
 Azure SDK scripts don't add the --implicit-namespaces flag
 They removed parent level RSTs
 Check https://github.com/Azure/azure-sdk-for-python/blob/efad456552b8e4aa48db7ee96930223b95144947/eng/tox/run_sphinx_apidoc.py#L37C1-L48C10

 That difference causes our behavior differs from Azure SDK html when package name and its namespace
  structure are inconsistent. For example, azure-core-tracing-opencensus and azure-core-tracing-opentelemetry
  have layer of azure/core/tracing/ext/opencensus_span or azure/core/tracing/ext/opentelemetry_span,
  We generates 2 extra pages of azure.core.tracing.ext because we aren't able to know it is a parent level namespace

 Below map worksaround this issue by excluding know extra parent level __init__.py
"""
extra_exclude_path_by_package = {
    'azure-core-tracing-opencensus': ['azure/core/tracing/ext/__init__.py'],
    'azure-core-tracing-opentelemetry': ['azure/core/tracing/ext/__init__.py'],
    'azure-eventhub-checkpointstoreblob': ['azure/eventhub/extensions/__init__.py'],
    'azure-eventhub-checkpointstoreblob-aio': ['azure/eventhub/extensions/__init__.py'],
}