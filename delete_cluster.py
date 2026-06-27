import sys
import os
import json
from typing import Optional, Dict, Any
import requests


class ClusterManager:
    def __init__(self, workspace_url: str, token: str):
        """Initialize the cluster manager with workspace URL and authentication token."""
        self.workspace_url = workspace_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def cluster_exists(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Check if a cluster exists and return its details."""
        try:
            response = requests.get(
                f"{self.workspace_url}/api/2.0/clusters/get",
                headers=self.headers,
                params={"cluster_id": cluster_id}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking cluster existence: {e}")
            return None

    def get_cluster_status(self, cluster_id: str) -> str:
        """Get the current status of a cluster."""
        try:
            response = requests.get(
                f"{self.workspace_url}/api/2.0/clusters/get",
                headers=self.headers,
                params={"cluster_id": cluster_id}
            )
            response.raise_for_status()
            return response.json().get('state', 'UNKNOWN')
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting cluster status: {e}")
            sys.exit(1)

    def unpin_cluster(self, cluster_id: str) -> bool:
        """Unpin a cluster if it's pinned."""
        try:
            response = requests.post(
                f"{self.workspace_url}/api/2.0/clusters/unpin",
                headers=self.headers,
                json={"cluster_id": cluster_id}
            )
            response.raise_for_status()
            print(f"✓ Cluster unpinned successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠ Warning: Could not unpin cluster: {e}")
            return False

    def stop_cluster(self, cluster_id: str) -> bool:
        """Stop a running cluster."""
        try:
            status = self.get_cluster_status(cluster_id)
            
            if status == "TERMINATED":
                print(f"✓ Cluster is already terminated")
                return True
            elif status == "RUNNING":
                print(f"Stopping cluster (current status: {status})...")
                response = requests.post(
                    f"{self.workspace_url}/api/2.0/clusters/stop",
                    headers=self.headers,
                    json={"cluster_id": cluster_id}
                )
                response.raise_for_status()
                print(f"✓ Cluster stop request sent successfully")
                return True
            else:
                print(f"✓ Cluster is in {status} state, no action needed")
                return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error stopping cluster: {e}")
            return False

    def delete_cluster(self, cluster_id: str) -> bool:
        """Delete a cluster permanently."""
        try:
            response = requests.post(
                f"{self.workspace_url}/api/2.0/clusters/delete",
                headers=self.headers,
                json={"cluster_id": cluster_id}
            )
            response.raise_for_status()
            print(f"✓ Cluster deleted successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error deleting cluster: {e}")
            return False


def main() -> None:
    # Get inputs from command line arguments or environment variables
    if len(sys.argv) < 2:
        print("Usage: python delete_cluster.py <cluster_name> [workspace_id] [cluster_id] [workspace_url] [token]")
        print("\nEnvironment variables:")
        print("  CLUSTER_NAME - Name of the cluster to delete")
        print("  WORKSPACE_ID - Workspace ID")
        print("  CLUSTER_ID - Cluster ID")
        print("  WORKSPACE_URL - Workspace URL")
        print("  DATABRICKS_TOKEN - Authentication token")
        sys.exit(1)

    cluster_name = sys.argv[1]
    workspace_id = sys.argv[2] if len(sys.argv) > 2 else os.getenv('WORKSPACE_ID')
    cluster_id = sys.argv[3] if len(sys.argv) > 3 else os.getenv('CLUSTER_ID')
    workspace_url = sys.argv[4] if len(sys.argv) > 4 else os.getenv('WORKSPACE_URL')
    token = sys.argv[5] if len(sys.argv) > 5 else os.getenv('DATABRICKS_TOKEN')

    if not workspace_url or not token:
        print("❌ Error: workspace_url and token are required")
        print("Provide via command line arguments or environment variables (WORKSPACE_URL, DATABRICKS_TOKEN)")
        sys.exit(1)

    print(f"🔍 Starting cluster deletion process for: {cluster_name}\n")
    print(f"📋 Cluster Details:")
    print(f"  Cluster Name: {cluster_name}")
    print(f"  Workspace ID: {workspace_id if workspace_id else 'N/A'}")
    print(f"  Cluster ID: {cluster_id if cluster_id else 'N/A'}")
    print()

    manager = ClusterManager(workspace_url, token)

    # Step 1: Check if cluster exists
    print("🔍 Checking if cluster exists...")
    cluster_info = manager.cluster_exists(cluster_id)
    if not cluster_info:
        print(f"❌ Cluster '{cluster_name}' not found with ID: {cluster_id}")
        sys.exit(1)
    print(f"✓ Cluster found: {cluster_info.get('cluster_name', cluster_name)}")
    print(f"  Status: {cluster_info.get('state', 'UNKNOWN')}")
    print()

    # Step 2: Unpin if pinned
    print("📌 Checking if cluster is pinned...")
    manager.unpin_cluster(cluster_id)
    print()

    # Step 3: Stop if running
    print("⏹ Checking cluster status and stopping if needed...")
    if not manager.stop_cluster(cluster_id):
        print("⚠ Warning: Could not stop cluster, attempting to delete anyway...")
    print()

    # Step 4: Delete cluster
    print("🗑 Deleting cluster...")
    if manager.delete_cluster(cluster_id):
        print(f"\n✅ Cluster '{cluster_name}' has been successfully deleted!")
    else:
        print(f"\n❌ Failed to delete cluster '{cluster_name}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
