# Deployment

## Requirements

- `git`
- `docker` and `docker-compose`
- [`mise`](https://mise.jdx.dev/) (for convenience)

## Setup

```bash
git clone git@gitlab.tu-clausthal.de:ifi-data/api.git
cd api
cp .env.example .env
# change credentials in .env
mise trust
mise install
just start
```

# Installation

https://pypi.org/project/ifi_data/

```bash
pip install ifi_data
```

See `demo.ipynb` for usage example.

# TODOs

- [ ] support insertion via REST api
- [ ] visualization (using `grafana`)
- [ ] config file management (at least for `cli`)
- [ ] docs site
- [ ] support read/append only
- [X] Implement a method/dataclass or the like to handle the frontend authentication with minimal required information
    - using default values if not provided
- [X] Backup and restore the database with periodic snapshots
  - try out the `pg_dump` while-loop in `compose.yml`
- [X] Start pushing data to the arcade server using the API
- [X] Implement REST API for inserting a single row for now
  - Make sure to separate the code that need to be executed on the backend from the frontend code in `src/ifi_data`
  - FUTURE: add the appropriate docker container configuration to run the API using docker-compose instead of relying on local server environment setup
  - Consider the appropriate approach for user authentication and authorization using the REST API
- [X] Ensure that we can import and save HDF (`.h5`) into the system

## Ideas

- [ ] duckdb and [duckdbui](https://github.com/duckdb/duckdb-ui)
- [ ] hyperfunctions for efficient time-related queries (https://docs.timescale.com/api/latest/hyperfunctions/time-weighted-calculations/time_weight/)

# Adminer Setup

for direct access to the database. Use `just open adminer` or the login info, which should be matched as follows:

- System: `PostgreSQL`
- Server: `postgres` (the service name for the PostgreSQL database in `compose.yml`)
- Username: `${POSTGRES_USER}` from `.env`
- Password: `${POSTGRES_PASSWORD}` from `.env`
- Database: `${POSTGRES_DB}` from `.env`
