import xmltodict
from slugify import slugify
from collections import defaultdict
from elexstatic import STATES


class ClarityXMLConverter:
    """
    A class to convert Clarity XML into our expected data format.
    """
    def __init__(self, XML_data, **kwargs):
        self.data = xmltodict.parse(data, attr_prefix="")["ElectionResult"]
        self.county_name = 





# def convert(data, *, outputType="results", level=None, style="default", resultsBy=None, **kwargs):
#     """
#     The entry point for formatting Clarity results data.
#     """
#     if style == "raw":
#         return data
#     raise Exception("No Clarity formatters implemented yet")
