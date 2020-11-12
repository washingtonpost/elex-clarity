import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger(__name__)


class ElectionsClient(object):
    """
    Client for retrieving elections data from systems using Clarity.
    """

    # https://results.enr.clarityelections.com//GA/Bacon/105373/269330/reports/detailxml.zip
    # https://results.enr.clarityelections.com//GA//105369/270988/reports/detailxml.zip

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

    # TODO make electionid/statepostal constructor args
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
