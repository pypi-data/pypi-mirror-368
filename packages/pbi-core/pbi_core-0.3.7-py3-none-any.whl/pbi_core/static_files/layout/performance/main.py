from pbi_core.ssas.server.tabular_model.tabular_model import LocalTabularModel

from .performance_trace import Performance, PerformanceTrace


def get_performance(model: LocalTabularModel, commands: list[str], *, clear_cache: bool = False) -> list[Performance]:
    """Calculates performance of a DAX query using a Trace.

    Args:
        model (LocalTabularModel): the SSAS instance the DAX should be run against
        commands (list[str]): A list of DAX queries to run against the SSAS model
        clear_cache (bool): Whether to clear the SSAS cache before running the queries.
            Useful to test cold start times for users

    Returns:
        Performance: contains memory and time usage of the DAX query


    """
    perf_trace = PerformanceTrace(model, commands)
    return perf_trace.get_performance(clear_cache=clear_cache)
