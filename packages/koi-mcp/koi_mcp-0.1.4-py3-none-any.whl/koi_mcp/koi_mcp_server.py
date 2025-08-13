import httpx
from fastmcp import FastMCP
import json
import os
import importlib.resources as pkg_resources

KOI_OPENAPI_SPEC_PATH = pkg_resources.files("koi_mcp").joinpath("openapi.json")

def run_server():
    TOKEN = os.getenv("KOI_API_TOKEN")
    if not TOKEN:
        raise ValueError("KOI_API_TOKEN environment variable is not set")
    
    client = httpx.AsyncClient(base_url="https://api.prod.koi.security", 
                                headers={"Authorization": f"Bearer {TOKEN}"}
    )
    openapi_spec = open(KOI_OPENAPI_SPEC_PATH, "r").read()
    mcp = FastMCP.from_openapi(
        openapi_spec=json.loads(openapi_spec),
        client=client,
        name="KOI API"
    )
    mcp.run(transport='stdio')