from huggingface_hub import snapshot_download
from appdirs import user_cache_dir
import os
import glob
import lhcb_rex.tools.display as display
from pathlib import Path
# from importlib.metadata import version as get_version


class HuggingFacePath:
    def __init__(self, path):
        self.path = path

def get_model_paths():

    with (
        display.status_execution(
            status_message="[bold green]Downloading/checking for network weights...",
            complete_message="[bold green]Complete.:white_check_mark:",
        )
    ):  
        # rex_version = get_version("lhcb_rex")

        if "CI_PROJECT_DIR" in os.environ:
            base_cache = Path(os.environ["CI_PROJECT_DIR"]) / ".cache" / "lhcb_rex"
        elif "REX_WEIGHT_DIR" in os.environ:
            base_cache = Path(os.environ["REX_WEIGHT_DIR"]) / ".cache" / "lhcb_rex"
        else:
            base_cache = user_cache_dir("lhcb_rex")
        cache_dir = os.path.join(base_cache, "weights")
        model_path = snapshot_download(
            # repo_id=f"alexmarshallbristol/Rex/{rex_version}", # not allowed this syntax
            repo_id="alexmarshallbristol/Rex",
            cache_dir=cache_dir,
            local_dir_use_symlinks=True,
        )
        weight_files = glob.glob(f'{model_path}/*.pkl')

        paths = {}
        for weight_file in weight_files:
            paths[weight_file.split('/')[-1].replace('.pkl','')] = HuggingFacePath(weight_file)

    display.info_print(f'Weights stored at: {Path(model_path).parent.parent}')

    return paths
