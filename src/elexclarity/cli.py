import os
import json
import click

from elexclarity.client import ElectionsClient
from elexclarity.convert import ClarityXMLConverter

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
    'summary',
    'settings',
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

    Sample commands:
    > elexclarity 105369 GA --outputType=summary
    > elexclarity 105369 GA --outputType=settings
    > elexclarity 105369 GA --level=precinct
    > elexclarity 105369 GA --level=state
    """
    if filename:
        # load races from local file
        with click.open_file(filename) as f:
            if ".json" in filename:
                result = json.load(f)
            if ".xml" in filename:
                with open(filename) as f:
                    result = f.read()
    else:
        api_client = ElectionsClient(BASE_URL)
        if outputType == "summary":
            result = api_client.get_summary(electionid, statepostal, **kwargs)
        elif outputType == "settings":
            result = api_client.get_settings(electionid, statepostal, **kwargs)
        else:
            result = api_client.get_results(electionid, statepostal, **kwargs)

    result = ClarityXMLConverter().convert(result, statepostal=statepostal)

    # if outputType in ["summary", "settings"]:
    #     result = json.dumps(result, indent=2)
    
    print(json.dumps(result, indent=2))