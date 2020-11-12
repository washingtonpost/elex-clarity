import os
import json
import click

from elexclarity.client import ElectionsClient

BASE_URL = os.environ.get('CLARITY_API_BASE_URL', 'https://results.enr.clarityelections.com/')


@click.command()
@click.argument('electionID', type=click.INT)
@click.argument('statePostal', type=click.STRING)
@click.option('--filename', type=click.Path(exists=True), help='Specify data file instead of making HTTP request')
@click.option('--level', help='Specify the subunit type/reporting level for results', default='county', type=click.Choice([
    'county',
    'precinct',
    'state'
]))
@click.option('--outputType', 'outputType', default='results', type=click.Choice([
    'results'
]))
@click.option('--resultsBy', 'resultsBy', default='candidate', type=click.Choice([
    'candidate',
    'party',
]))
@click.option('--style', default='default', type=click.Choice([
    'default',
    'raw'
]))
def cli(electionid, statepostal, filename=None, style="default", outputType="results", resultsBy='candidate', **kwargs):
    """
    This tool accepts an election ID (e.g. 105369) and a state postal code (e.g. GA)
    and the options below and outputs formatted elections data. If a filename is provided,
    that file's data will be used as input. If not, Clarity will be queried
    for elections data.

    Right now, a command like `elexclarity 105369 GA` will return a JSON summary.
    """
    if filename:
        # load races from local file
        with click.open_file(filename) as f:
            election_results = json.load(f)
    else:
        api_client = ElectionsClient(BASE_URL)
        election_results = api_client.get_summary(electionid, statepostal)

    '''
    result = convert(
        election_results,
        electionID=electionID,
        style=style,
        outputType=outputType,
        resultsBy=resultsBy,
        **kwargs)
    '''

    print(json.dumps(election_results, indent=2))
