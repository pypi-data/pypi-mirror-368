
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_scraper.app import ScraperApp

env_store = EnvironmentStore()
integration_instance = AgentRIntegration(name="unipile", store=env_store)
app_instance = ScraperApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
    host="0.0.0.0",
)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")


