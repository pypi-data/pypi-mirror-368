# espn-api-orm

ESPN API Object-Relational Mapper (ORM) is a Python package that makes it easy to interact with the ESPN API. It provides an ORM-like interface on top of the API endpoints, making it more intuitive for Python developers. List of endpoints: https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c

## Installation

You can install ESPN API ORM using pip:

```bash
pip install espn-api-orm
```
## Usage

- BaseAPI -> SportAPI -> LeagueAPI -> SeasonAPI
- SeasonAPI -> TeamsAPI
- SeasonAPI -> VenueAPI
- SeasonAPI -> CalendarAPI -> ScoreboardAPI
- ScoreboardAPI -> EventsAPI

## Features
- Easy API interaction: The emphasis is on making ESPN API easy to use for Python developers.
- ORM-like interface: Binding API endpoints to Python classes, giving an ORM-like feel.
- Comprehensive coverage: Covers all ESPN API endpoints.

## Contributing
We appreciate any contributions. Please feel free to fork and create a Pull Request for any changes/updates.

## Publishing

Auto publish available through GitHub Actions and Pypi

Local publishing (include token in rc)

1. ```python -m build```

2. ```twine upload dist/*```