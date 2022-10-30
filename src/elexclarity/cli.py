import os
import json
import click
import logging

from elexclarity.client import ElectionsClient
from elexclarity.convert import convert

LOG = logging.getLogger(__name__)

class StringListParamType(click.ParamType):
    name = "stringlist"

    def convert(self, value, param, ctx):
        return value.split(",")


BASE_URL = os.environ.get('CLARITY_API_BASE_URL', 'https://results.enr.clarityelections.com')
STRING_LIST = StringListParamType()


@click.command()
@click.argument('electionID', type=click.INT)
@click.argument('statePostal', type=click.STRING)
@click.option('--countyName', 'county_name', type=click.STRING, help="If county specific clarity page")
@click.option('--filename', type=click.Path(exists=True), help='Specify data file instead of making HTTP request')
@click.option('--countyMapping', 'countyMapping', default={}, help='Specify county mapping')
@click.option('--officeID', 'officeID', help='The office ID(s) to process', type=STRING_LIST)
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
@click.option('--voteCompletionMode', 'voteCompletionMode', default='percentReporting', type=click.Choice([
    'percentReporting',
    'voteTypes'
]))
@click.option('--style', default='default', type=click.Choice([
    'default',
    'raw'
]))
def cli(electionid, statepostal, filename=None, countyMapping={}, outputType="results", **kwargs):
    """
    This tool accepts an election ID (e.g. 105369) and a state postal code (e.g. GA)
    and the options below and outputs formatted elections data. If a filename is provided,
    that file's data will be used as input. If not, Clarity will be queried
    for elections data.

    Sample commands:
    > elexclarity 105369 GA --outputType=summary
    > elexclarity 105369 GA --outputType=settings
    > elexclarity 105369 GA --level=precinct
    > elexclarity 105369 GA --level=county
    """
    if filename:
        # load races from local file
        with click.open_file(filename) as results_file:
            # load these into a list as that's what convert expects
            if ".json" in filename:
                result = [json.load(results_file)]
            if ".xml" in filename:
                result = [results_file.read()]
    else:
        api_client = ElectionsClient(BASE_URL)
        if outputType == "summary":
            result = api_client.get_summary(electionid, statepostal, **kwargs)
        elif outputType == "settings":
            result = api_client.get_settings(electionid, statepostal, **kwargs)
        else:
            result = api_client.get_results(electionid, statepostal, **kwargs)

    if isinstance(countyMapping, str):
        countyMapping = json.loads(countyMapping)

    result = convert(result, statepostal, outputType=outputType, countyMapping=countyMapping, **kwargs)
    LOG.debug("Total length: ", len(result))

    print(json.dumps(result, indent=2))
