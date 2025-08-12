import os
import json
import torch
import matplotlib.pyplot as plt
from lattica_common.dev_utils.dev_mod_utils import RUN_MODE, RunMode


def print_query_result(idx, data_pt, pt_expected, pt_dec):
    print(f'{pt_expected.shape=} {pt_dec.shape=}')
    print(f'{pt_dec=}')
    print(f'{pt_expected=}')

    # Visualize
    plt.figure()
    plt.imshow(data_pt.reshape(28, 28), cmap="gray")
    plt.title(f"idx={idx}\nhom prediction: {pt_dec.argmax()}")
    plt.axis("off")
    plt.show()

    # Verify similarity
    torch.testing.assert_close(
            pt_expected, pt_dec,
            rtol=1 / 2**9, atol=1 / 2**9
        )
    print("Homomorphic and clear outputs are close.\n")

def load_e2e_config() -> tuple:
    """
    Locate the e2e.json file relative to the calling script, load its content, 
    and return both the file path and the configuration dictionary.
    :return: A tuple containing the config file path and the configuration dictionary.
    """
    # Get the directory of the calling script
    current_script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct the path to e2e.json relative to the calling script's directory
    config_path = os.path.join(current_script_dir, '../../../e2e.json')
    
    print(f'Searching for config file at: {config_path}')
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"e2e.json file not found at: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON from the config file at: {config_path}")


def get_results_file_path():
    """
    Return the path to e2e_results.json in the repository's temp directory
    """
    # Get the directory of this script
    current_script_dir = os.path.dirname(os.path.realpath(__file__))
    # Go up 3 levels to reach the repository root
    repo_root = os.path.abspath(os.path.join(current_script_dir, '../../../'))
    # Return the path to e2e_results.json in the temp directory
    return os.path.join(repo_root, 'temp', 'e2e_results.json')


def load_e2e_results():
    """
    Load the e2e_results.json file if it exists; otherwise, raise an error.
    """
    results_path = get_results_file_path()
    try:
        with open(results_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"E2E results file not found at: {results_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to parse JSON from e2e results file at {results_path}: {str(e)}", e.doc, e.pos)
    except IOError as e:
        raise IOError(f"IO error while reading e2e results file at {results_path}: {str(e)}")


def save_to_e2e_results(data_to_save):
    """
    Save specified data to e2e_results.json
    """
    results_path = get_results_file_path()

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    
    # Load existing data if any
    try:
        with open(results_path, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to parse existing JSON from e2e results file at {results_path}: {str(e)}", e.doc, e.pos)
    except IOError as e:
        raise IOError(f"IO error while reading e2e results file at {results_path}: {str(e)}")
    
    # Update with new data
    existing_data.update(data_to_save)
    
    # Write back to file
    with open(results_path, 'w') as file:
        json.dump(existing_data, file, indent=4)
    
    print(f'Saved results to {results_path}')
    return results_path
