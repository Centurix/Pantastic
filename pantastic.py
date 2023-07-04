#!/usr/bin/env python3
import sys
import click
from pantastic import Pantastic
"""
Pantastic
=========

Credit Card PAN finder to satisfy tick boxes on a PCI compliance form
"""

EXIT_OK = 0
EXIT_OTHER_ERROR = 1
EXIT_PARAM_ERROR = 2


@click.command()
@click.option("--config_file", type=str, default="./pantastic.ini")
@click.option("--log_file", type=str, default="./app.log")
@click.option("--log_level", type=str, default="info")
@click.option("--ignore_cards", type=str)
@click.option("--ignore_iins", type=str)
@click.option("--ignore_industries", type=str)
@click.option("--include_deprecated", is_flag=True)
@click.option("--minimum_digits", type=int, default=12)
@click.option("--maximum_digits", type=int, default=19)
@click.option("--cards_per_file", type=int, default=0)
@click.option("--ignore_file_extensions", type=str)
@click.option("--ignore_paths", type=str)
@click.option("--unmask_card_number", is_flag=True, default=False)
@click.option("--max_group_count", type=int, default=0)
@click.option("--max_group_distance", type=int, default=0)
@click.option("--output", type=str)
@click.option("--verbose", is_flag=True, default=True)
@click.option("--dir", type=str)
@click.option("--file", type=str)
def main(
    config_file: str,
    log_file: str,
    log_level: str,
    ignore_cards: str,
    ignore_iins: str,
    ignore_industries: str,
    include_deprecated: bool,
    minimum_digits: int,
    maximum_digits: int,
    cards_per_file: int,
    ignore_file_extensions: str,
    ignore_paths: str, 
    unmask_card_number: bool,
    max_group_count: int,
    max_group_distance: int,
    output: str,
    verbose: bool,
    dir: str,
    file: str
) -> int:
    click.echo("Scanning...")
    ignore_card_list = []
    if ignore_cards:
        with open(ignore_cards, 'r') as ignore_cards_handle:
            ignore_card_list = ignore_cards_handle.read().splitlines()

    ignore_iin_list = []
    if ignore_iins:
        with open(ignore_iins, 'r') as ignore_iins_handle:
            ignore_iin_list = ignore_iins_handle.read().splitlines()

    ignore_industry_list = []
    if ignore_industries:
        with open(ignore_industries, 'r') as ignore_industries_handle:
            ignore_industry_list = ignore_industries_handle.read().splitlines()

    ignore_path_list = []
    if ignore_paths:
        with open(ignore_paths, 'r') as ignore_paths_handle:
            ignore_path_list = ignore_paths_handle.read().splitlines()

    ignore_file_extension_list = []
    if ignore_file_extensions:
        with open(ignore_file_extensions, 'r') as ignore_file_extensions_handle:
            ignore_file_extension_list = ignore_file_extensions_handle.read().splitlines()

    if not verbose and output == '':
        click.echo("No output type specified")
        return EXIT_PARAM_ERROR

    pan_manager = Pantastic(
        ignore_cards=ignore_card_list,
        ignore_iins=ignore_iin_list,
        ignore_industries=ignore_industry_list,
        include_deprecated=include_deprecated,
        minimum_digits=minimum_digits,
        maximum_digits=maximum_digits,
        cards_per_file=cards_per_file,
        ignore_file_extensions=ignore_file_extension_list,
        unmask_card_number=unmask_card_number,
        max_group_count=max_group_count,
        max_group_distance=max_group_distance,
        output=output,
        ignore_paths=ignore_path_list,
        verbose=verbose
    )
    if dir:
        pan_manager.scan_location(dir)
    if file:
        pan_manager.scan_file_with_output(file)

    click.echo("Scan complete")

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
