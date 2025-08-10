#!/usr/bin/env python3
import shutil
from pathlib import Path

import click


@click.command()
def main():
    resources_dir = Path(__file__).parent / "resources"

    target_dir = Path.cwd()

    if not resources_dir.exists():
        click.echo(f"Error: resources directory does not exist: {resources_dir}")
        return

    click.echo(f"Copying {resources_dir} to {target_dir}")

    copied_count = 0
    for item in resources_dir.rglob("*"):
        relative_path = item.relative_to(resources_dir)
        target_path = target_dir / relative_path

        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)


            try:
                shutil.copy2(item, target_path)
                click.echo(f"Copied: {relative_path}")
                copied_count += 1
            except Exception as e:
                click.echo(f"Copy failed {relative_path}: {str(e)}", err=True)

    click.echo(f"\nCopy completed! Copied {copied_count} files")


if __name__ == "__main__":
    main()
