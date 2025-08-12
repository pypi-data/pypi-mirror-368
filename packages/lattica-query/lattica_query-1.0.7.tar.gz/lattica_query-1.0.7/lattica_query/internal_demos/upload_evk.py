import json

from lattica_common.dev_utils.dev_mod_utils import RUN_MODE, RunMode
from lattica_query.internal_demos.lattica_query_client_local import LocalQueryClient
from lattica_query.internal_demos.utils import dumps_user_data
from lattica_common.internal_demos_common.common_demos_utils import (
    load_e2e_config, print_query_result, load_e2e_results, save_to_e2e_results
)


def upload_evk():
    print("Starting query client...")

    # Load the configuration
    config = load_e2e_config()

    # Load results file to get query_tokens
    results = load_e2e_results()

    # Generate new dictionary to store token data
    new_query_tokens = {}
    for token in results["query_tokens"]:
        print(f'Generating keys and uploading EVK for token {token}')
        client = LocalQueryClient(token)

        new_query_tokens[token] = dumps_user_data(*client.generate_key())

    print("\nAll EVKs uploaded successfully.")

    print('Saving secret keys to results file...')
    save_to_e2e_results({'query_tokens': new_query_tokens})
    print('Finished.')


if __name__ == "__main__":
    upload_evk()
