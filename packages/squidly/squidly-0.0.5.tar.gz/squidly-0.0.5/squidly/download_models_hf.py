from huggingface_hub import snapshot_download
import shutil
import os
from os.path import dirname, join as joinpath

base_dir = dirname(__file__)
squidly_model_dir = base_dir
download_dir = snapshot_download(
    repo_id="WillRieger/Squidly",
    local_dir=base_dir,
    local_dir_use_symlinks=False
)
print(f"Models downloaded to: {squidly_model_dir}")
