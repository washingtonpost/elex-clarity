import logging
from io import BytesIO
import zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger(__name__)


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
            # faking a user-agent because Clarity is giving us forbidden errors otherwise
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            **kwargs):

        if session is None:
            session = requests.Session()
            session.headers.update({'Accept-Encoding': 'gzip'})
            session.headers.update({"User-Agent": user_agent})

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

    def _get_url_subdirectories(self, electionid, statepostal, county_name):
        url_subdirectory = f"{statepostal}/"
        if county_name:
            url_subdirectory += f"{county_name}/{electionid}"
        else:
            url_subdirectory += str(electionid)
        return url_subdirectory

    def get_current_version(self, electionid, statepostal, county_name, **kwargs):
        url_subdirectory = self._get_url_subdirectories(electionid, statepostal, county_name)
        current_ver_url = f"{url_subdirectory}/current_ver.txt"
        current_ver_response = self.make_request(current_ver_url)
        return current_ver_response.text

    def get_summary(self, electionid, statepostal, county_name, **kwargs):
        current_ver = self.get_current_version(electionid, statepostal, county_name)
        url_subdirectory = self._get_url_subdirectories(electionid, statepostal, county_name)
        summary_url = f"{url_subdirectory}/{current_ver}/json/en/summary.json"
        resp = self.make_request(summary_url, **kwargs)
        return resp.json()

    def get_detail_xml(self, route):
        resp = self.make_request(f"{route}/reports/detailxml.zip")
        filebytes = BytesIO(resp.content)
        _zipfile = zipfile.ZipFile(filebytes)
        for name in _zipfile.namelist():
            with _zipfile.open(name) as myfile:
                return myfile.read()

    def get_settings(self, electionid, statepostal, county_name, **kwargs):
        """
        :param electionid: the election ID
        :type electionid: str
        :keyword statepostal: the state(s) to query
        :type statepostal: str or tuple(str)

        :param kwargs: other keyword args passed to underlying requests call
        :return: the response json
        :rtype: str

        """
        current_ver = self.get_current_version(electionid, statepostal, county_name)
        url_subdirectory = self._get_url_subdirectories(electionid, statepostal, county_name)
        settings_url = f"{url_subdirectory}/{current_ver}/json/en/electionsettings.json"
        resp = self.make_request(settings_url, **kwargs)
        return resp.json()

    # https://results.enr.clarityelections.com//GA//105369/270988/reports/detailxml.zip
    def get_county_results(self, statepostal, county_name, county_id, county_version, **kwargs):
        return self.get_detail_xml(f"{statepostal}/{county_name}/{county_id}/{county_version}")

    def get_state_results(self, electionid, statepostal, county_name, version, **kwargs):
        url_subdirectory = self._get_url_subdirectories(electionid, statepostal, county_name)
        results_url = f"{url_subdirectory}/{version}"
        return self.get_detail_xml(results_url)

    def get_results(self, electionid, statepostal, county_name, level, **kwargs):
        if level == "precinct" and not county_name:
            results = []
            # Bad bad bad; do not use in production! This will request _many_ files
            election_settings = self.get_settings(electionid, statepostal, county_name)
            raw_counties = election_settings.get("settings", {}).get("electiondetails", {}).get("participatingcounties")
            success = 0
            failure = 0
            for raw_county in raw_counties:
                name, clarity_id, _, _ = raw_county.split("|")[0:4]
                try:
                    current_ver = self.get_current_version(clarity_id, statepostal, name)
                    results.append(self.get_county_results(statepostal, name, clarity_id, current_ver, **kwargs))
                    success += 1
                except requests.exceptions.HTTPError:
                    try:
                        name, clarity_id, version, _ = raw_county.split("|")[0:4]
                        results.append(self.get_county_results(statepostal, name, clarity_id, version, **kwargs))
                        success += 1
                    except requests.exceptions.HTTPError:
                        failure += 1
                        LOG.info(f"Failed to get results for {name}")
                except:
                    failure += 1
                    LOG.info(f"Failed to get results for {name}")
            LOG.info("Number of successes: ", success)
            LOG.info("Number of failures: ", failure)
            return results
        elif (level == "state" or level == "county") and not county_name:
            current_ver = self.get_current_version(electionid, statepostal, county_name)
            return self.get_state_results(electionid, statepostal, county_name, current_ver, **kwargs)
        elif level == "precinct" and county_name:
            current_ver = self.get_current_version(electionid, statepostal, county_name)
            return self.get_state_results(electionid, statepostal, county_name, current_ver, **kwargs)
        return None
