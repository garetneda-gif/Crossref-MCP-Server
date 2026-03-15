from typing import Any, List, Dict, Optional, Union
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from crossref_search import CrossrefSearch

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server
mcp = FastMCP("crossref")
default_crossref = CrossrefSearch()  # 使用默认设置初始化

@mcp.tool()
async def search_works_by_query(query: str, limit: int = 20, mailto: str = None) -> Dict[str, Any]:
    logging.info(f"Searching for works with query: {query}")
    try:
        crossref = CrossrefSearch(mailto=mailto) if mailto else default_crossref
        result = await asyncio.to_thread(crossref.search_works, query, limit)
        return result
    except Exception as e:
        return {"error": f"An error occurred while searching works: {str(e)}"}

@mcp.tool()
async def get_work_metadata(doi: str, mailto: str = None) -> Dict[str, Any]:
    logging.info(f"Getting metadata for work with DOI: {doi}")
    try:
        crossref = CrossrefSearch(mailto=mailto) if mailto else default_crossref
        result = await asyncio.to_thread(crossref.get_work_by_doi, doi)
        return result
    except Exception as e:
        return {"error": f"An error occurred while getting work metadata: {str(e)}"}

@mcp.tool()
async def search_journals(query: str = None, limit: int = 20, mailto: str = None) -> Dict[str, Any]:
    logging.info(f"Searching for journals with query: {query}")
    try:
        crossref = CrossrefSearch(mailto=mailto) if mailto else default_crossref
        result = await asyncio.to_thread(crossref.get_journals, query, limit)
        return result
    except Exception as e:
        return {"error": f"An error occurred while searching journals: {str(e)}"}

@mcp.tool()
async def search_funders(query: str = None, limit: int = 20, mailto: str = None) -> Dict[str, Any]:
    logging.info(f"Searching for funders with query: {query}")
    try:
        crossref = CrossrefSearch(mailto=mailto) if mailto else default_crossref
        result = await asyncio.to_thread(crossref.search_funders, query, limit)
        return result
    except Exception as e:
        return {"error": f"An error occurred while searching funders: {str(e)}"}

def _kill_stale_instances():
    """杀掉已有的同名进程，防止多实例堆积吃内存。"""
    import os, signal, subprocess
    my_pid = os.getpid()
    script_name = os.path.basename(__file__)
    try:
        result = subprocess.run(
            ["pgrep", "-f", script_name],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            pid = int(line.strip())
            if pid != my_pid:
                os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


if __name__ == "__main__":
    _kill_stale_instances()
    logging.info("Starting Crossref MCP Server")
    mcp.run(transport='stdio')
