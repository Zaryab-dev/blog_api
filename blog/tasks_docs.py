from celery import shared_task
from django.conf import settings
import os
import json


@shared_task
def generate_openapi_schema():
    """
    Generate static OpenAPI schema JSON file
    
    Runs nightly to keep docs in sync
    """
    from django.core.management import call_command
    from io import StringIO
    
    # Generate schema
    out = StringIO()
    call_command('spectacular', '--file', '-', stdout=out)
    schema_json = out.getvalue()
    
    # Save to docs directory
    docs_dir = os.path.join(settings.BASE_DIR, 'docs', 'openapi')
    os.makedirs(docs_dir, exist_ok=True)
    
    output_path = os.path.join(docs_dir, 'openapi.json')
    with open(output_path, 'w') as f:
        f.write(schema_json)
    
    # Also save formatted version
    schema_dict = json.loads(schema_json)
    formatted_path = os.path.join(docs_dir, 'openapi-formatted.json')
    with open(formatted_path, 'w') as f:
        json.dump(schema_dict, f, indent=2)
    
    return f"OpenAPI schema generated: {output_path}"
