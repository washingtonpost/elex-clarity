def convert(data, *, outputType="results", level=None, style="default", resultsBy=None, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if style == "raw":
        return data
    raise Exception("No Clarity formatters implemented yet")
