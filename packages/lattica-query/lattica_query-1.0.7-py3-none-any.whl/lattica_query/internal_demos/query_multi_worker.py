import torch
import numpy as np

from lattica_common.dev_utils.dev_mod_utils import RUN_MODE, RunMode
from lattica_query.internal_demos.lattica_query_client_local import LocalQueryClient
from lattica_query.internal_demos.utils import loads_user_data
from lattica_common.internal_demos_common.common_demos_utils import (
    load_e2e_config, print_query_result, load_e2e_results
)


def query_multi_worker():
    print("Starting query client...")

    # Load the configuration and results
    config = load_e2e_config()
    results = load_e2e_results()

    # 'query_tokens' is a dictionary of tokens data for different users
    tokens_data = results["query_tokens"]

    # Example dataset (MNIST). 
    dataset = np.loadtxt('data/mnist_data.csv', delimiter=',', skiprows=1) / 255.0

    for token in tokens_data:
        print(f'Running query for token {token}')
        client = LocalQueryClient(token)
        serialized_context, serialized_secret_key, serialized_homseq = loads_user_data(tokens_data[token])

        # Pick a random index
        idx = np.random.randint(len(dataset))
        data_pt = torch.tensor(dataset[idx])
        
        # For debugging: apply pipeline in the clear
        pt_expected = client.apply_clear(data_pt)
        print(f'Image {idx=}')
        pt_dec = client.run_query(serialized_context, serialized_secret_key, data_pt, serialized_homseq)
        print_query_result(idx, data_pt, pt_expected, pt_dec)

    print("\nAll queries completed successfully.")


if __name__ == "__main__":
    query_multi_worker()
