
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_scraper.app import ScraperApp

env_store = EnvironmentStore()
app_instance = ScraperApp()



mcp = SingleMCPServer(
    app_instance=app_instance,
    host="0.0.0.0",
)

if __name__ == "__main__":
    # print(app_instance.integration.client.base_url)
    # creds = app_instance.integration.get_credentials()
    # print(creds)
    # resp = app_instance.linkedin_retrieve_profile(
    #     identifier="manojbajaj95"
    # )
    mcp.run(transport="streamable-http")


