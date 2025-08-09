import os

import weaviate

weaviate_client = weaviate.connect_to_local(
    host=os.getenv('WEAVIATE_HOST'),
    port=int(os.getenv('WEAVIATE_PORT')),
    grpc_port=int(os.getenv('WEAVIATE_GRPC_PORT')),
    headers=None,
    additional_config=None,
    skip_init_checks=False,
    auth_credentials=weaviate.auth.AuthApiKey(
        api_key=os.getenv('WEAVIATE_API_KEY')
    )
)
