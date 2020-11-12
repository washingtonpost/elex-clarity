import logging
import requests
from collections import namedtuple
import zipfile
from io import BytesIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger(__name__)


CountyIdentifier = namedtuple('CountyIdentifier', ['id', 'name', 'version', 'last_updated'])

class ElectionsClient(object):
    """
    Client for retrieving elections data from systems using Clarity.
    """

    # TODO make electionid/statepostal constructor args and/or add caching of retrieved version and so on

    def __init__(
            self,
            base_url,
            timeout=5,
            session=None,
            retry_params={},
            **kwargs):

        if session is None:
            session = requests.Session()
            session.headers.update({'Accept-Encoding': 'gzip'})

        retry_params = {"total": 3, "status_forcelist": (502, 504, 429, 499), "backoff_factor": 0.2, **retry_params}
        adapter = HTTPAdapter(max_retries=Retry(**retry_params))
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        self.base_url = base_url
        self.session = session
        self.timeout = timeout

    def make_request(self, route, **kwargs):
        """
        Makes a request relative to ``self.base_url``.

        :param route: the route to request (relative to the base ``api_url``)
        :type route: str
        :param kwargs: keyword args passed to underlying requests call
        :return: the response xml
        :rtype: str

        """
        url = f'{self.base_url}/{route}'
        LOG.debug("Making request at %s", url)

        response = self.session.get(url, params=kwargs, timeout=self.timeout)
        response.raise_for_status()
        return response

    def get_current_version(self, electionid, statepostal, **kwargs):
        current_ver_url = f"{statepostal}/{electionid}/current_ver.txt"
        current_ver_response = self.make_request(current_ver_url)
        return current_ver_response.text

    def get_summary(self, electionid, statepostal, **kwargs):
        current_ver = self.get_current_version(electionid, statepostal, **kwargs)
        resp = self.make_request(f"{statepostal}/{electionid}/{current_ver}/json/en/summary.json", **kwargs)
        return resp.json()

    def get_detail_xml(self, route):
        resp = self.make_request(f"{route}/reports/detailxml.zip")
        filebytes = BytesIO(resp.content)
        _zipfile = zipfile.ZipFile(filebytes)
        for name in _zipfile.namelist():
            with _zipfile.open(name) as myfile:
                return myfile.read()

    def get_settings(self, electionid, statepostal, **kwargs):
        """
        :param electionid: the election ID
        :type electionid: str
        :keyword statepostal: the state(s) to query
        :type statepostal: str or tuple(str)

        :param kwargs: other keyword args passed to underlying requests call
        :return: the response json
        :rtype: str

        """
        current_ver = self.get_current_version(electionid, statepostal, **kwargs)
        resp = self.make_request(f"{statepostal}/{electionid}/{current_ver}/json/en/electionsettings.json", **kwargs)
        return resp.json()

    def get_counties(self, electionid, statepostal, **kwargs):
        """
        :param electionid: the election ID
        :type electionid: str
        :keyword statepostal: the state(s) to query
        :type statepostal: str or tuple(str)

        :param kwargs: other keyword args passed to underlying requests call
        :return: the response json
        :rtype: str

        """
        summary = self.get_settings(electionid, statepostal)
        raw_counties = summary.get("settings", {}).get("electiondetails", {}).get("participatingcounties")
        counties = []
        for raw_county in raw_counties:
            name, _id, version, last_updated = raw_county.split("|")[0:4]
            counties.append(CountyIdentifier(_id, name, version, last_updated))
        return counties

    # https://results.enr.clarityelections.com//GA//105369/270988/reports/detailxml.zip
    def get_county_results(self, statepostal, county, **kwargs):
        return self.get_detail_xml(f"{statepostal}/{county.name}/{county.id}/{county.version}")

    def get_state_results(self, electionid, statepostal, version, **kwargs):
        return self.get_detail_xml(f"{statepostal}/{electionid}/{version}")

    def get_results(self, electionid, statepostal, level, **kwargs):
        if level == "precinct":
            results = []
            # Bad bad bad; do not use in production! This will request _many_ files
            for county in self.get_counties(electionid, statepostal):
                results.append(self.get_county_results(statepostal, county, **kwargs))
            return results
        elif level == "state":
            current_ver = self.get_current_version(electionid, statepostal, **kwargs)
            return self.get_state_results(electionid, statepostal, current_ver, **kwargs)
        return None
