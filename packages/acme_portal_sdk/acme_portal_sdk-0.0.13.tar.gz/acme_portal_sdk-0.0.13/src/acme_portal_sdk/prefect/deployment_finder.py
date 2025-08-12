import os
import sys
import traceback
from pprint import pp
from typing import List

from prefect.client.orchestration import get_client

from acme_portal_sdk.deployment_finder import (DeploymentDetails,
                                               DeploymentFinder)


class PrefectDeploymentFinder(DeploymentFinder):
    """Finds Prefect deployments in a given context.

    Connects to Prefect's API to discover and retrieve information about existing deployments in the Prefect backend.
    """

    def __init__(self):
        """Initialize the PrefectDeploymentFinder and verify Prefect credentials."""
        self.credentials_verified = False
        try:
            client = get_client(sync_client=True)
            # Make a simple API call to verify authentication
            client.read_deployments(limit=1)
            self.credentials_verified = True
            print("Prefect authentication verified successfully.")
        except ImportError:
            print("Error: Prefect package not installed or not found")
        except Exception as e:
            print(f"Error authenticating with Prefect: {str(e)}")
            traceback.print_exc(file=sys.stderr)

    def _get_deployment_url(self, deployment_id: str) -> str:
        """Construct the URL for a given deployment ID."""
        prefect_api_url = os.environ.get("PREFECT_API_URL")
        if prefect_api_url is None:
            raise ValueError(
                "PREFECT_API_URL environment variable is not set. Please set it to your Prefect API URL."
            )
        prefect_app_url = prefect_api_url.replace(
            "https://api.prefect.cloud/api", "https://app.prefect.cloud"
        )
        prefect_app_url = prefect_app_url.replace("accounts", "account").replace(
            "workspaces", "workspace"
        )
        return f"{prefect_app_url}/deployments/deployment/{deployment_id}"

    def get_deployments(self) -> List[DeploymentDetails]:
        """Connect to Prefect and get deployment information."""
        try:
            client = get_client(sync_client=True)
            deployments = client.read_deployments()

            result = []
            for deployment in deployments:
                print(f"Processing deployment: {deployment.name}")

                # Parse deployment name into components
                parts = deployment.name.split("--")
                if len(parts) < 4:
                    print(
                        f"Skipping deployment with insufficient name parts: {deployment.name}"
                    )
                    continue

                # Create a standardized flow name (replace hyphens with underscores)
                flow_name = parts[-2].replace("-", "_")

                # Construct deployment info
                deploy_info = DeploymentDetails(
                    name=deployment.name,
                    project_name=parts[0],
                    branch=parts[1],
                    flow_name=flow_name,
                    env=parts[-1],
                    commit_hash=next(
                        (
                            tag.split("=")[1]
                            for tag in deployment.tags
                            if "COMMIT_HASH" in tag
                        ),
                        "",
                    ),
                    package_version=next(
                        (
                            tag.split("=")[1]
                            for tag in deployment.tags
                            if "PACKAGE_VERSION" in tag
                        ),
                        "",
                    ),
                    tags=deployment.tags,
                    id=str(deployment.id),
                    created_at=str(deployment.created),
                    updated_at=str(deployment.updated),
                    flow_id=str(deployment.flow_id),
                    url=self._get_deployment_url(str(deployment.id)),
                )

                result.append(deploy_info)
                print(
                    f"Added deployment: {deploy_info.project_name}/{flow_name} ({deploy_info.branch}/{deploy_info.env})"
                )

            return result
        except ImportError:
            print("Error: Prefect package not installed or not found")
            raise
        except Exception as e:
            print(f"Error getting deployments: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            raise


if __name__ == "__main__":
    finder = PrefectDeploymentFinder()
    deployments = finder.get_deployments()
    pp(deployments)
