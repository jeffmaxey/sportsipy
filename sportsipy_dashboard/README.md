# Sportsipy Dashboard

An interactive multipage web dashboard for exploring sports statistics using [sportsipy](https://github.com/roclark/sportsipy).

## Features

- **Data Explorer**: Browse team and player statistics with filtering, sorting, and pagination via AG Grid
- **Dataset Builder**: Step-by-step workflow for building and transforming datasets
- **Saved Queries**: Save, load, and manage frequently used data queries
- **Code Export**: Automatically generates Python scripts and Jupyter notebooks from your exploration
- **Multi-format Export**: Export data as CSV, TSV, JSON, XML, Excel, Parquet, HDF5, or SQLite

## Supported Sports

| Sport | League | Seasons |
|-------|--------|---------|
| MLB | Major League Baseball | 1871–2024 |
| NBA | National Basketball Association | 1947–2024 |
| NFL | National Football League | 1966–2024 |
| NHL | National Hockey League | 1918–2024 |
| NCAAB | NCAA Men's Basketball | 2010–2024 |
| NCAAF | NCAA Football | 2000–2024 |

## Installation

```bash
pip install -e sportsipy_dashboard/
```

## Running the Dashboard

```bash
sportsipy-dashboard
```

Or directly:

```bash
python -m sportsipy_dashboard.app
```

The dashboard will be available at http://localhost:8050.

## Development

```bash
pip install -e "sportsipy_dashboard/[dev]"
python -m pytest sportsipy_dashboard/tests/ -v
```

## Project Structure

```
sportsipy_dashboard/
├── app.py              # Main Dash application
├── wsgi.py             # WSGI entry point for production
├── assets/             # Static assets (CSS)
├── components/         # Reusable UI components (navbar, sidebar)
├── pages/              # Dash pages (home, explorer, builder, queries)
├── utils/              # Utility modules
│   ├── data_loader.py  # sportsipy data loading
│   ├── code_generator.py # Python/notebook code generation
│   ├── exporters.py    # Multi-format data export
│   └── query_manager.py # Saved query persistence
└── tests/              # Unit tests
```

## Dependencies

- [Dash](https://dash.plotly.com/) >= 2.14.0
- [dash-mantine-components](https://www.dash-mantine-components.com/) >= 0.14.0
- [dash-ag-grid](https://dash.plotly.com/dash-ag-grid) >= 31.0.0
- [dash-iconify](https://github.com/snehilvj/dash-iconify) >= 0.1.2
- [pandas](https://pandas.pydata.org/) >= 2.2.0
- [sportsipy](https://github.com/roclark/sportsipy) >= 0.7.0

## License

MIT
