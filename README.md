# Global Energy API

Global energy data including energy consumption, renewable energy share, fossil fuel use, electricity access, CO2 emissions, and nuclear energy for 190+ countries. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All energy indicators for a country |
| `GET /energy-use` | Energy use per capita (kg oil equivalent) |
| `GET /renewable` | Renewable energy share (% of total) |
| `GET /electricity-access` | Access to electricity (% of population) |
| `GET /fossil-fuel` | Fossil fuel consumption (% of total) |
| `GET /electric-power` | Electric power consumption per capita |
| `GET /co2` | CO2 emissions per capita |
| `GET /nuclear` | Nuclear energy share of electricity |
| `GET /top-consumers` | Countries ranked by energy use |
| `GET /top-renewable` | Countries ranked by renewable share |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, CHN, NOR) | `WLD` |
| `limit` | Number of years or countries | `10` |

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator/EG.USE.PCAP.KG.OE

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
