from lattica_common.app_api import HttpClient, generate_random_token_name


def get_demo_token(model_id: str) -> str:
    http_client = HttpClient(None, module_name='lattica_query')
    token_name = generate_random_token_name(10)
    response = http_client.send_http_request(
        "api/token/generate_token_demo",
        req_params={
            'modelId': model_id,
            'tokenName': token_name
        })
    token = response.get('token')

    if token is None:
        raise ValueError("The response does not contain a 'token' field.")

    return token
