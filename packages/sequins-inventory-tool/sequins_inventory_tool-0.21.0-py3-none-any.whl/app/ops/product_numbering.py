"""CLI tool for interacting with product numbering in the inventory system."""

import logging
from typing import Optional

import pandas
import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local

logger = logging.getLogger(__name__)

product_naming_app = typer.Typer()


@product_naming_app.command(name='display')
@require_api_endpoint_and_key()
def display_product_numbering(
    ctx: typer.Context,
    description: Annotated[
        Optional[str], typer.Option(help='Filter by description')
    ] = None,
    category: Annotated[
        Optional[str], typer.Option(help='Filter by category')
    ] = None,
    status: Annotated[
        Optional[str], typer.Option(help='Filter by status')
    ] = None,
    sort_by: Annotated[
        Optional[str], typer.Option(help='Field to sort by')
    ] = None,
    sort_order: Annotated[
        Optional[str], typer.Option(help='Sort order (asc or desc)')
    ] = None,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display all product numbers from the database.

    Optionally
    - sort by a field and order (asc or desc).
    - filter by description, category, or status.

    If no product numbers are found, a message is displayed and the command
    exits.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    console = get_console()
    product_naming_url = f'{api_endpoint}{ApiPaths.PART_DEFINITIONS}'
    headers = {API_KEY_NAME: api_key}

    sort_params = {}
    if sort_by:
        if not sort_order:
            sort_order = 'asc'
        elif sort_order not in ['asc', 'desc']:
            console.print(
                f'Invalid sort order: {sort_order}. Using default "asc" order.'
            )
            sort_order = 'asc'
        sort_params = {'sortBy': sort_by, 'sortOrder': sort_order}

    filters = {
        'description': description,
        'category': category,
        'status': status,
    }

    filters_query = {k: v for k, v in filters.items() if v is not None}

    page = 1
    size = 50
    items = []
    while True:
        result = requests.get(
            product_naming_url,
            headers=headers,
            params={'page': page, 'size': size} | sort_params | filters_query,
        )
        result.raise_for_status()
        data = result.json()
        current_items = data.get('items', [])
        items.extend(current_items)
        pages = data.get('pages', 1)
        if page >= pages:
            break
        page += 1

    if not items:
        console.print('No product numbers found.')
        raise typer.Exit()

    table = Table(title='Product Numbers')
    table.add_column('Part Number', justify='left')
    table.add_column('Name')
    table.add_column('Description')
    table.add_column('Content')
    table.add_column('Category')
    table.add_column('Status')
    if verbose:
        table.add_column('Created By', justify='left')
        table.add_column('Created At', justify='left')
        table.add_column('Updated By', justify='left')
        table.add_column('Updated At', justify='left')

    for item in items:
        row_data = [
            item['part_number'],
            item['name'],
            item['description'],
            item['content'],
            item['category'],
            item['status'],
        ]
        if verbose:
            row_data.extend(
                [
                    item.get('created_by', ''),
                    format_utc_to_local(item['created_at_utc']),
                    item.get('updated_by', ''),
                    format_utc_to_local(item['updated_at_utc']),
                ]
            )

        table.add_row(*row_data)

    console.print(table)


@product_naming_app.command(name='upload')
@require_api_endpoint_and_key()
def upload_product_numbering_database(
    product_numbering_file: Annotated[
        str, typer.Argument(help='Path to the product numbering file (csv)')
    ],
    ctx: typer.Context,
):
    """Upload a product numbering file to the database.

    This uploads a CSV file containing product numbers, names, descriptions,
    content, categories, statuses, and suppliers.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    product_naming_url = f'{api_endpoint}{ApiPaths.PART_DEFINITIONS}'

    console = get_console()

    console.log(
        f'Uploading product numbering file: url={product_naming_url}, '
        f'file={product_numbering_file}',
    )

    # Load the file
    data = pandas.read_csv(product_numbering_file).fillna(
        {
            'Content': 'N/A',
            'Category': 'N/A',
            'Part Status': 'pending',
            'Supplier': 'N/A',
            'Cat #': '',
        }
    )

    data.rename(
        columns={'Cat #': 'Cat_Number', 'Part Status': 'status'},
        inplace=True,
    )
    data.columns = data.columns.str.replace(' ', '_').str.lower()

    headers = {API_KEY_NAME: api_key}

    with console.status('Uploading product numbering file...'):
        for _, row in data.iterrows():
            console.log(f'Checking part number {row["part_number"]}')

            result = requests.get(
                f'{product_naming_url}{row["part_number"]}',
                headers=headers,
            )

            if result.status_code == 404:
                # If the part does not have a category, we cannot create it.
                if row['category'] == 'N/A':
                    console.log(
                        f'Part number {row["part_number"]} has no category, '
                        f'skipping.'
                    )
                    continue

                console.log(
                    f'Part number {row["part_number"]} not found, '
                    f'creating new entry.'
                )
                response = requests.post(
                    product_naming_url,
                    headers=headers,
                    json={
                        'part_number': row['part_number'],
                        'name': row['name'],
                        'description': row['description'],
                        'content': row['content'],
                        'category': row['category'],
                        'status': str(row['status']).lower().strip(),
                        'supplier': {
                            'name': row['supplier'],
                            'catalogue': str(row['cat_number']),
                        },
                    },
                )
                response.raise_for_status()
                console.log(f'Created new part number {row["part_number"]}')
            elif result.status_code == 200:
                console.log(
                    f'Part number {row["part_number"]} already exists, '
                    'skipping.'
                )
                # TODO(slangley): Check if the part needs to be updated.
            else:
                logger.error(
                    'Error checking product number %s: %s',
                    row['part_number'],
                    result.text,
                )
                result.raise_for_status()


@product_naming_app.command(name='update')
@require_api_endpoint_and_key()
def update_product_numbering(
    product_number: Annotated[
        str, typer.Argument(help='Part number to update')
    ],
    ctx: typer.Context,
    name: Annotated[
        Optional[str], typer.Option(help='New name for the product number')
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(help='New description for the product number'),
    ] = None,
    content: Annotated[
        Optional[str], typer.Option(help='New content for the product number')
    ] = None,
    category: Annotated[
        Optional[str], typer.Option(help='New category for the product number')
    ] = None,
    status: Annotated[
        Optional[str], typer.Option(help='New status for the product number')
    ] = None,
):
    """Update a product number in the database."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    product_naming_url = (
        f'{api_endpoint}{ApiPaths.PART_DEFINITIONS}{product_number}'
    )
    headers = {API_KEY_NAME: api_key}

    console = get_console()

    console.log(
        f'Updating product number: url={product_naming_url}, '
        f'product_number={product_number}',
    )

    update = {
        k: (v.lower().strip() if k == 'status' else v)
        for k, v in {
            'name': name,
            'description': description,
            'content': content,
            'category': category,
            'status': status,
        }.items()
        if v is not None
    }

    if not update:
        console.log('No updates provided, nothing to do.')
        raise typer.Exit()

    response = requests.patch(
        product_naming_url,
        headers=headers,
        json=update,
    )

    if response.status_code == 200:
        console.log(f'Updated product number {product_number}')
    else:
        logger.error(
            'Error updating product number %s: %s',
            product_number,
            response.text,
        )
        response.raise_for_status()


@product_naming_app.command(name='create')
@require_api_endpoint_and_key()
def create_product_numbering(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help='Name for the product number')],
    description: Annotated[
        str, typer.Option(help='Description for the product number')
    ],
    content: Annotated[
        str, typer.Option(help='Content for the product number')
    ],
    category: Annotated[
        str, typer.Option(help='Category for the product number')
    ],
    product_number: Annotated[
        Optional[str],
        typer.Option(
            help='Part number to create, if not provided will be auto-generated'
        ),
    ] = None,
    status: Annotated[
        str, typer.Option(help='Status for the product number')
    ] = 'pending',
    supplier_name: Annotated[
        str, typer.Option(help='Supplier for the product number')
    ] = 'Internal',
    supplier_catalogue: Annotated[
        Optional[str], typer.Option(help='Supplied catalogue number')
    ] = None,
):
    """Create a new product number in the database."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    product_naming_url = f'{api_endpoint}{ApiPaths.PART_DEFINITIONS}'
    headers = {API_KEY_NAME: api_key}

    response = requests.post(
        product_naming_url,
        headers=headers,
        json={
            'part_number': product_number,
            'name': name,
            'description': description,
            'content': content,
            'category': category,
            'status': status.lower().strip(),
            'supplier': {
                'name': supplier_name,
                'catalogue': supplier_catalogue,
            },
        },
    )

    console = get_console()

    if response.status_code == 201:
        console.log(f'Created new product number {product_number}')
    else:
        logger.error(
            'Error creating product number %s: %s',
            product_number,
            response.text,
        )
        response.raise_for_status()
