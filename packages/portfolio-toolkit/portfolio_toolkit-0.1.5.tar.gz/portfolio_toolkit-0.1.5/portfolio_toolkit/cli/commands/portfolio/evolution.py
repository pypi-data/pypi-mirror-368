import click

from portfolio_toolkit.data_provider.yf_data_provider import YFDataProvider
from portfolio_toolkit.plot.engine import PlotEngine
from portfolio_toolkit.portfolio.load_portfolio_json import load_portfolio_json
from portfolio_toolkit.portfolio.plot_evolution import plot_portfolio_evolution
from portfolio_toolkit.portfolio.time_series_portfolio import (
    create_time_series_portfolio_from_portfolio,
)

from ..utils import load_json_file


@click.command()
@click.argument("file", type=click.Path(exists=True))
def evolution(file):
    """Plot portfolio value evolution"""
    data = load_json_file(file)
    data_provider = YFDataProvider()
    basic_portfolio = load_portfolio_json(data, data_provider=data_provider)
    portfolio = create_time_series_portfolio_from_portfolio(basic_portfolio)

    line_data = plot_portfolio_evolution(portfolio)
    PlotEngine.plot(line_data)
