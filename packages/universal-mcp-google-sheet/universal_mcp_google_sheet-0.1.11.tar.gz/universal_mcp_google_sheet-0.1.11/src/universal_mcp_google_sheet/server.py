
from universal_mcp.servers.server import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores.store import EnvironmentStore
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp_google_sheet.app import GoogleSheetApp

env_store = EnvironmentStore()
integration_instance = AgentRIntegration(name="google-sheet", client=AgentrClient(api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev"))
app_instance = GoogleSheetApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run(transport="sse")


