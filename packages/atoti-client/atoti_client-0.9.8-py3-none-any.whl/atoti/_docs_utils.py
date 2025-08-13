QUANTILE_DOC = """Return a measure equal to the requested quantile {what}.

    Here is how to obtain the same behavior as `these standard quantile calculation methods <https://en.wikipedia.org/wiki/Quantile#Estimating_quantiles_from_a_sample>`__:

    * R-1: ``mode="centered"`` and ``interpolation="lower"``
    * R-2: ``mode="centered"`` and ``interpolation="midpoint"``
    * R-3: ``mode="simple"`` and ``interpolation="nearest"``
    * R-4: ``mode="simple"`` and ``interpolation="linear"``
    * R-5: ``mode="centered"`` and ``interpolation="linear"``
    * R-6 (similar to Excel's ``PERCENTILE.EXC``): ``mode="exc"`` and ``interpolation="linear"``
    * R-7 (similar to Excel's ``PERCENTILE.INC``): ``mode="inc"`` and ``interpolation="linear"``
    * R-8 and R-9 are not supported

    The formulae given for the calculation of the quantile index assume a 1-based indexing system.

    Args:
        {measure_or_operand}: The {measure_or_operand} to get the quantile of.
        q: The quantile to take.
            For instance, ``0.95`` is the 95th percentile and ``0.5`` is the median.
        mode: The method used to calculate the index of the quantile.
            Available options are, when searching for the *q* quantile of a vector ``X``:

            * ``simple``: ``len(X) * q``
            * ``centered``: ``len(X) * q + 0.5``
            * ``exc``: ``(len(X) + 1) * q``
            * ``inc``: ``(len(X) - 1) * q + 1``

        interpolation: If the quantile index is not an integer, the interpolation decides what value is returned.
            The different options are, considering a quantile index ``k`` with ``i < k < j`` for a sorted vector ``X``:

            * ``linear``: ``v = X[i] + (X[j] - X[i]) * (k - i)``
            * ``lower``: ``v = X[i]``
            * ``higher``: ``v = X[j]``
            * ``nearest``: ``v = X[i]`` or ``v = X[j]`` depending on which of ``i`` or ``j`` is closest to ``k``
            * ``midpoint``: ``v = (X[i] + X[j]) / 2``
"""

QUANTILE_INDEX_DOC = """Return a measure equal to the index of requested quantile {what}.

    Args:
        measure: The measure to get the quantile of.
        q: The quantile to take.
            For instance, ``0.95`` is the 95th percentile and ``0.5`` is the median.
        mode: The method used to calculate the index of the quantile.
            Available options are, when searching for the *q* quantile of a vector ``X``:

            * ``simple``: ``len(X) * q``
            * ``centered``: ``len(X) * q + 0.5``
            * ``exc``: ``(len(X) + 1) * q``
            * ``inc``: ``(len(X) - 1) * q + 1``

        interpolation: If the quantile index is not an integer, the interpolation decides what value is returned.
            The different options are, considering a quantile index ``k`` with ``i < k < j`` for the original vector ``X``
            and the sorted vector ``Y``:

            * ``lowest``: the index in ``X`` of ``Y[i]``
            * ``highest``: the index in ``X`` of ``Y[j]``
            * ``nearest``: the index in ``X`` of ``Y[i]`` or ``Y[j]`` depending on which of ``i`` or ``j`` is closest to ``k``
"""

QUERY_KWARGS = {
    "widget_conversion": "In JupyterLab with :mod:`atoti-jupyterlab <atoti_jupyterlab>` installed, query results can be converted to interactive widgets with the :guilabel:`Convert to Widget Below` action available in the command palette or by right clicking on the representation of the returned Dataframe.",
    "context": """context: Context values to use when executing the query.""",
    "explain": """explain: When ``True``, execute the query but, instead of returning its result, return an explanation of how it was executed containing a summary, global timings, and the query plan and all its retrievals.""",
    "mode": """mode: The query mode.""",
    "pretty": """* ``"pretty"`` is best for queries returning small results.""",
    "raw": """* ``"raw"`` is best for benchmarks or large exports:

                * A faster and more efficient endpoint reducing the data transfer from Java to Python will be used.
                * The :guilabel:`Convert to Widget Below` action provided by :mod:`atoti-jupyterlab <atoti_jupyterlab>` will not be available.""",
    "timeout": """timeout: The duration the query execution can take before being aborted.""",
    "totals": """Totals can be useful but they make the DataFrame harder to work with since its index will have some empty values.""",
}


STD_DOC_KWARGS = {
    "op": "standard deviation",
    "population_excel": "STDEV.P",
    "population_formula": "\\sqrt{\\frac{\\sum_{i=1}^{n}(X_i - m)^{2}}{n}}",
    "sample_excel": "STDEV.S",
    "sample_formula": "\\sqrt{\\frac{\\sum_{i=1}^{n} (X_i - m)^{2}}{n - 1}}",
}
VAR_DOC_KWARGS = {
    "op": "variance",
    "population_excel": "VAR.P",
    "population_formula": "\\frac{\\sum_{i=1}^{n}(X_i - m)^{2}}{n}",
    "sample_excel": "VAR.S",
    "sample_formula": "\\frac{\\sum_{i=1}^{n} (X_i - m)^{2}}{n - 1}",
}

STD_AND_VAR_DOC = """Return a measure equal to the {op} {what}.

    Args:
        {measure_or_operand}: The {measure_or_operand} to get the {op} of.
        mode: One of the supported modes:

            * The ``sample`` {op}, similar to Excel's ``{sample_excel}``, is :math:`{sample_formula}` where ``m`` is the sample mean and ``n`` the size of the sample.
              Use this mode if the data represents a sample of the population.
            * The ``population`` {op}, similar to Excel's ``{population_excel}`` is :math:`{population_formula}` where ``m`` is the mean of the ``Xi`` elements and ``n`` the size of the population.
              Use this mode if the data represents the entire population.
"""
