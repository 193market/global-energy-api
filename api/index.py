from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Energy API",
    description="Global energy data including consumption, production, renewable energy share, fossil fuel use, and CO2 emissions for 190+ countries. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "energy_use":        {"id": "EG.USE.PCAP.KG.OE",  "name": "Energy Use Per Capita",             "unit": "kg of oil equivalent"},
    "renewable_share":   {"id": "EG.FEC.RNEW.ZS",     "name": "Renewable Energy Share",            "unit": "% of Total"},
    "electricity_access":{"id": "EG.ELC.ACCS.ZS",     "name": "Access to Electricity",             "unit": "% of Population"},
    "fossil_fuel":       {"id": "EG.USE.COMM.FO.ZS",  "name": "Fossil Fuel Energy Consumption",    "unit": "% of Total"},
    "electric_power":    {"id": "EG.USE.ELEC.KH.PC",  "name": "Electric Power Consumption",        "unit": "kWh per Capita"},
    "co2_emissions":     {"id": "EN.ATM.CO2E.PC",     "name": "CO2 Emissions Per Capita",          "unit": "Metric Tons"},
    "co2_intensity":     {"id": "EN.ATM.CO2E.EG.ZS",  "name": "CO2 Intensity of Energy",           "unit": "kg per kg of oil equiv"},
    "alt_nuclear":       {"id": "EG.ELC.NUCL.ZS",     "name": "Nuclear Energy Share",              "unit": "% of Total Electricity"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "RUS": "Russia",
    "JPN": "Japan",
    "DEU": "Germany",
    "KOR": "South Korea",
    "CAN": "Canada",
    "BRA": "Brazil",
    "SAU": "Saudi Arabia",
    "IRN": "Iran",
    "GBR": "United Kingdom",
    "FRA": "France",
    "IDN": "Indonesia",
    "AUS": "Australia",
    "MEX": "Mexico",
    "ZAF": "South Africa",
    "TUR": "Turkey",
    "POL": "Poland",
    "NGA": "Nigeria",
    "EGY": "Egypt",
    "ARE": "UAE",
    "NOR": "Norway",
    "SWE": "Sweden",
    "NLD": "Netherlands",
    "ESP": "Spain",
    "ITA": "Italy",
    "VNM": "Vietnam",
    "THA": "Thailand",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str):
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": 1, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    results = []
    for r in records:
        if r.get("value") is not None and r.get("countryiso3code"):
            results.append({
                "country_code": r["countryiso3code"],
                "country": r["country"]["value"],
                "year": str(r["date"]),
                "value": r["value"],
            })
    return results


@app.get("/")
def root():
    return {
        "api": "Global Energy API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/energy-use", "/renewable", "/electricity-access",
            "/fossil-fuel", "/electric-power", "/co2", "/nuclear",
            "/top-consumers", "/top-renewable"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All energy indicators for a country"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {
            "name": INDICATORS[key]["name"],
            "unit": INDICATORS[key]["unit"],
            "data": results[key],
        }
        for key in INDICATORS
    }
    return {
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank Open Data",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/energy-use")
async def energy_use(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Energy use per capita (kg of oil equivalent)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.USE.PCAP.KG.OE", limit)
    return {"indicator": "Energy Use Per Capita", "series_id": "EG.USE.PCAP.KG.OE", "unit": "kg of oil equivalent", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/renewable")
async def renewable(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Renewable energy share of total final energy consumption (%)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.FEC.RNEW.ZS", limit)
    return {"indicator": "Renewable Energy Share", "series_id": "EG.FEC.RNEW.ZS", "unit": "% of Total Energy", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/electricity-access")
async def electricity_access(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Access to electricity (% of population)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.ELC.ACCS.ZS", limit)
    return {"indicator": "Access to Electricity", "series_id": "EG.ELC.ACCS.ZS", "unit": "% of Population", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/fossil-fuel")
async def fossil_fuel(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Fossil fuel energy consumption (% of total)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.USE.COMM.FO.ZS", limit)
    return {"indicator": "Fossil Fuel Energy Consumption", "series_id": "EG.USE.COMM.FO.ZS", "unit": "% of Total", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/electric-power")
async def electric_power(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Electric power consumption per capita (kWh)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.USE.ELEC.KH.PC", limit)
    return {"indicator": "Electric Power Consumption", "series_id": "EG.USE.ELEC.KH.PC", "unit": "kWh per Capita", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/co2")
async def co2(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """CO2 emissions per capita (metric tons)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EN.ATM.CO2E.PC", limit)
    return {"indicator": "CO2 Emissions Per Capita", "series_id": "EN.ATM.CO2E.PC", "unit": "Metric Tons per Capita", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/nuclear")
async def nuclear(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Nuclear energy share of electricity production (%)"""
    country = country.upper()
    data = await fetch_wb_country(country, "EG.ELC.NUCL.ZS", limit)
    return {"indicator": "Nuclear Energy Share", "series_id": "EG.ELC.NUCL.ZS", "unit": "% of Total Electricity", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/top-consumers")
async def top_consumers(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by energy use per capita"""
    data = await fetch_wb_all_countries("EG.USE.PCAP.KG.OE")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Energy Use Per Capita", "unit": "kg of oil equivalent", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "top_consumers": ranked}


@app.get("/top-renewable")
async def top_renewable(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by renewable energy share"""
    data = await fetch_wb_all_countries("EG.FEC.RNEW.ZS")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Renewable Energy Share", "unit": "% of Total Energy", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "top_renewable": ranked}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)
    key = request.headers.get("X-RapidAPI-Key", "")
    if not key:
        return JSONResponse(status_code=401, content={"detail": "Missing X-RapidAPI-Key header"})
    return await call_next(request)
