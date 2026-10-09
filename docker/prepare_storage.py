"""Attach persistent data to baked code without replacing existing user files."""
import argparse
from pathlib import Path
import shutil

DIRECTORIES = ('models', 'input', 'output', 'user', 'template_apis', '.model-downloads')
FILES = ('comfyui.log', 'template-download.log', '.template-download.lock')


def attach_storage(comfy_dir, data_dir):
    comfy_dir, data_dir = Path(comfy_dir).resolve(), Path(data_dir).resolve()
    if comfy_dir == data_dir or comfy_dir in data_dir.parents or data_dir in comfy_dir.parents:
        raise ValueError('Code and persistent data paths must be separate directories')
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in DIRECTORIES:
        source, target = comfy_dir / name, data_dir / name
        target.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            if source.resolve() != target.resolve():
                raise ValueError(f'Unexpected symlink: {source}')
            continue
        if source.exists():
            # Preserve model subfolders shipped with ComfyUI; never overwrite data.
            for child in source.iterdir():
                destination = target / child.name
                if not destination.exists() and not destination.is_symlink():
                    if child.is_dir():
                        shutil.copytree(child, destination)
                    else:
                        shutil.copy2(child, destination)
            shutil.rmtree(source)
        source.symlink_to(target, target_is_directory=True)
    for name in FILES:
        source, target = comfy_dir / name, data_dir / name
        if source.is_symlink():
            if source.resolve() != target.resolve():
                raise ValueError(f'Unexpected symlink: {source}')
            continue
        if not target.exists():
            if source.is_file():
                shutil.copy2(source, target)
            else:
                target.touch()
        source.unlink(missing_ok=True)
        source.symlink_to(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comfy-dir', required=True)
    parser.add_argument('--data-dir', required=True)
    args = parser.parse_args()
    attach_storage(args.comfy_dir, args.data_dir)
