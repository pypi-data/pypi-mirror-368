#!/usr/bin/env python3
import requests
import webbrowser
import subprocess
import json
import urllib.parse
from fastmcp import FastMCP

# Configuration options for URL rendering
USE_LOCAL_API = False
USE_MARIONETTE = False  # Set to True to use marionette.navigate

mcp = FastMCP("IBM Cloud Browser")

def render_url(url: str) -> str:
    """Renders a URL using local API, marionette, or system browser based on configuration"""
    if USE_LOCAL_API:
        try:
            response = requests.post(
                "http://localhost:3001/render",
                headers={"Content-Type": "application/json"},
                json={"url": url},
                timeout=10
            )
            if response.status_code == 200:
                return f"Successfully rendered {url} via local API"
            else:
                return f"Failed to render {url} via local API: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return f"Failed to connect to local API at http://localhost:3001/render. Make sure the service is running."
        except requests.exceptions.Timeout:
            return f"Timeout while trying to render {url} via local API"
        except Exception as e:
            return f"Error rendering {url} via local API: {str(e)}"
    elif USE_MARIONETTE:
        try:
            from marionette_driver import marionette
            # Connect to marionette (assumes Firefox is running with marionette enabled)
            # Start Firefox with: firefox --marionette --headless (or without --headless for visible)
            client = marionette.Marionette(host='localhost', port=2828)
            client.start_session()
            client.navigate(url)
            client.delete_session()
            return f"Successfully navigated to {url} via marionette"
        except ImportError:
            return f"marionette_driver not installed. Install with: pip install marionette_driver"
        except Exception as e:
            return f"Error navigating to {url} via marionette: {str(e)}. Make sure Firefox is running with --marionette flag"
    else:
        webbrowser.open(url)
        return f"Opened {url} in system browser"

@mcp.tool()
def open_ibm_cloud_console() -> str:
    """Opens IBM Cloud console in the browser"""
    result = render_url("https://cloud.ibm.com")
    return f"Opened IBM Cloud console at https://cloud.ibm.com - {result}"

@mcp.tool()
def open_ibm_cloud_resources(product: str = "") -> str:
    """Shows IBM Cloud resources in the browser, optionally filtered by product. This is best way to display clusters, databases, etc. to the user"""
    url = "https://cloud.ibm.com/resources"
    if product:
        url += f"?product={product}"
    result = render_url(url)
    return f"Opened IBM Cloud resources at {url} - {result}"

@mcp.tool()
def show_cluster(cluster_id: str) -> str:
    """Opens a specific cluster overview page in the browser"""
    url = f"https://cloud.ibm.com/containers/cluster-management/clusters/{cluster_id}/overview"
    result = render_url(url)
    return f"Opened cluster overview for {cluster_id} at {url} - {result}"

@mcp.tool()
def provision(search: str = "") -> str:
    """Opens IBM Cloud catalog to provision services with optional search"""
    url = "https://cloud.ibm.com/catalog"
    if search:
        encoded_search = urllib.parse.quote_plus(search)
        url += f"?search={encoded_search}#search_results"
    result = render_url(url)
    return f"Opened IBM Cloud catalog at {url} - {result}"

@mcp.tool()
def open_cloud_logs(instance_id: str, region: str, view_id: str = "") -> str:
    """Opens the IBM Cloud Logs dashboard with required instance ID and region, and optional view ID"""
    url = f"https://dashboard.{region}.logs.cloud.ibm.com/{instance_id}"
    if view_id:
        url += f"#/query-new/logs?viewId={view_id}&permalink=true"
    result = render_url(url)
    return f"Opened IBM Cloud Logs dashboard at {url} - {result}"

@mcp.tool()
def open_sysdig_monitoring(dashboard_id: str, region: str) -> str:
    """Opens the IBM Cloud Sysdig monitoring dashboard with required dashboard ID and region"""
    url = f"https://{region}.monitoring.cloud.ibm.com/#/dashboards/{dashboard_id}"
    result = render_url(url)
    return f"Opened Sysdig monitoring dashboard at {url} - {result}"

@mcp.tool()
def open_redis_monitoring(region: str, service_instance_id: str) -> str:
    """Opens IBM Cloud Redis monitoring dashboard with region and service instance ID"""
    # URL encode the scope parameters
    scope = urllib.parse.quote(f'ibm_location = "{region}" and ibm_service_instance = "{service_instance_id}"')
    url = f"https://{region}.monitoring.cloud.ibm.com/#/dashboard-template/ibm_databases_for_redis?skip-welcome=true&scope={scope}&last=3600"
    result = render_url(url)
    return f"Opened Redis monitoring dashboard at {url} - {result}"

@mcp.tool()
def list_clusters() -> str:
    """internal helper: Lists IBM Cloud Kubernetes cluster names and IDs"""
    try:
        result = subprocess.run(
            ["ibmcloud", "ks", "clusters", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            clusters_data = json.loads(result.stdout)
            filtered_clusters = [{"name": cluster["name"], "id": cluster["id"]} for cluster in clusters_data]
            return json.dumps(filtered_clusters, indent=2)
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except json.JSONDecodeError:
        return "Error parsing JSON output from CLI"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_monitoring_dashboards(instance_id: str, region: str) -> str:
    """internal helper: Lists IBM Cloud monitoring dashboards for specified instance and region"""
    try:
        # First set the target region
        target_result = subprocess.run(
            ["ibmcloud", "target", "-r", region],
            capture_output=True,
            text=True,
            timeout=30
        )
        if target_result.returncode != 0:
            return f"Error setting target region: {target_result.stderr}"
        
        # Then list the dashboards
        result = subprocess.run(
            ["ibmcloud", "monitoring", "dashboard", "list", "--instance-id", instance_id, "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            dashboards_data = json.loads(result.stdout)
            filtered_dashboards = [{"name": dashboard["name"], "id": dashboard["id"]} for dashboard in dashboards_data]
            return json.dumps(filtered_dashboards, indent=2)
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except json.JSONDecodeError:
        return "Error parsing JSON output from CLI"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_logs_dashboards(instance_id: str, region: str) -> str:
    """Internal helper: Lists IBM Cloud Logs views/dashboards for specified instance and region"""
    try:
        service_url = f"https://{instance_id}.api.{region}.logs.cloud.ibm.com"
        result = subprocess.run(
            ["ibmcloud", "logs", "views", "--service-url", service_url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_redis_database_metadata() -> str:
    """Internal helper: Gets Redis database id, name, and region."""
    try:
        result = subprocess.run(
            ["ibmcloud", "resource", "service-instances", "--service-name", "databases-for-redis", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            redis_data = json.loads(result.stdout)
            filtered_redis = [{"id": instance["guid"], "name": instance["name"], "region": instance["region_id"]} for instance in redis_data]
            return json.dumps(filtered_redis, indent=2)
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except json.JSONDecodeError:
        return "Error parsing JSON output from CLI"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_sysdig_metadata() -> str:
    """Internal helper: Gets Sysdig monitoring instance metadata including id, name, and region"""
    try:
        result = subprocess.run(
            ["ibmcloud", "resource", "service-instances", "--service-name", "sysdig-monitor", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            sysdig_data = json.loads(result.stdout)
            filtered_sysdig = [{"id": instance["guid"], "name": instance["name"], "region": instance["region_id"]} for instance in sysdig_data]
            return json.dumps(filtered_sysdig, indent=2)
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except json.JSONDecodeError:
        return "Error parsing JSON output from CLI"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_cloud_logs_metadata() -> str:
    """Internal helper: Gets Cloud Logs instance metadata including id, name, and region"""
    try:
        result = subprocess.run(
            ["ibmcloud", "resource", "service-instances", "--service-name", "logs", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            logs_data = json.loads(result.stdout)
            filtered_logs = [{"id": instance["guid"], "name": instance["name"], "region": instance["region_id"]} for instance in logs_data]
            return json.dumps(filtered_logs, indent=2)
        else:
            return f"Error running command: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except FileNotFoundError:
        return "IBM Cloud CLI not found. Please install it first."
    except json.JSONDecodeError:
        return "Error parsing JSON output from CLI"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
