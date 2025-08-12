"""
K6 MCP Server - Python Implementation
Based on FIS MCP Server for k6 load testing
"""

import json
import asyncio
import logging
import os
import subprocess
import tempfile
from typing import Dict, Any, List

# MCP Python SDK imports
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.server.fastmcp import FastMCP
import mcp.types as types


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("k6-mcp-server")

def _run_k6_command(
    cmd: List[str], script_path: str, timeout: int = 300
) -> subprocess.CompletedProcess:
    """Run k6 command either directly or via Docker"""
    # Try direct k6 first
    try:
        result = subprocess.run(["k6", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            # k6 is installed directly
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        pass

    # Fall back to Docker
    try:
        # Check if Docker is available
        subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, check=True
        )

        # Convert k6 command to Docker command
        # Mount the script file and run k6 in container
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{script_dir}:/scripts",
            "grafana/k6:latest",
        ]

        # Replace k6 command parts
        k6_args = cmd[1:]  # Remove 'k6' from the beginning

        # Handle --out json=/dev/stdout for Docker
        for i, arg in enumerate(k6_args):
            if (
                arg == "--out"
                and i + 1 < len(k6_args)
                and k6_args[i + 1] == "json=/dev/stdout"
            ):
                k6_args[i + 1] = "json=-"  # Docker k6 uses - for stdout
            elif arg == script_path:
                k6_args[i] = f"/scripts/{script_name}"

        docker_cmd.extend(k6_args)

        return subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout
        )

    except (FileNotFoundError, subprocess.CalledProcessError):
        raise Exception(
            "Neither k6 nor Docker is available. Please install k6 or Docker."
        )


def _check_k6_installed() -> bool:
    """Check if k6 is installed on the system or Docker is available"""
    # First check if k6 is installed directly
    try:
        result = subprocess.run(["k6", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # If k6 is not installed, check if Docker is available
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


@mcp.tool()
async def run_k6_load_test(
    url: str,
    vus: int = 10,
    duration: str = "30s",
    rps: int = None,
    method: str = "GET",
    headers: Dict[str, str] = None,
    body: str = None,
    thresholds: Dict[str, List[str]] = None,
) -> types.CallToolResult:
    """Run k6 load test against a specific URL and return results as JSON"""

    if not _check_k6_installed():
        raise Exception(
            "Neither k6 nor Docker is installed. Please install k6 (https://k6.io/docs/get-started/installation/) or Docker."
        )

    try:
        # Create k6 script
        k6_script = _generate_k6_script(
            url=url,
            method=method,
            headers=headers or {},
            body=body,
            thresholds=thresholds or {},
        )

        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(k6_script)
            script_path = f.name

        try:
            # Build k6 command
            cmd = ["k6", "run", "--out", "json=/dev/stdout"]

            # Add VUs and duration
            cmd.extend(["--vus", str(vus)])
            cmd.extend(["--duration", duration])

            # Add RPS if specified
            if rps:
                cmd.extend(["--rps", str(rps)])

            cmd.append(script_path)

            # Run k6 using the new function
            logger.info(f"Running k6 command: {' '.join(cmd)}")
            result = _run_k6_command(cmd, script_path, timeout=300)

            if result.returncode != 0:
                raise Exception(f"k6 execution failed: {result.stderr}")

            # Parse k6 output
            test_results = _parse_k6_output(result.stdout)

            result_text = f"K6 Load Test Results:\n{json.dumps(test_results, indent=2)}"

            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )

        finally:
            # Clean up temporary file
            if os.path.exists(script_path):
                os.unlink(script_path)

    except subprocess.TimeoutExpired:
        raise Exception("k6 test timed out after 5 minutes")
    except Exception as error:
        raise Exception(f"Failed to run k6 load test: {str(error)}")


def _generate_k6_script(
    url: str,
    method: str,
    headers: Dict[str, str],
    body: str,
    thresholds: Dict[str, List[str]],
) -> str:
    """Generate k6 JavaScript test script"""

    # Convert headers to JavaScript object
    headers_js = json.dumps(headers) if headers else "{}"

    # Convert thresholds to JavaScript object
    thresholds_js = json.dumps(thresholds) if thresholds else "{}"

    # Handle request body
    body_js = json.dumps(body) if body else "null"

    script = f"""
import http from 'k6/http';
import {{ check }} from 'k6';

export let options = {{
    thresholds: {thresholds_js}
}};

export default function() {{
    let params = {{
        headers: {headers_js}
    }};
    
    let response;
    
    if ('{method.upper()}' === 'GET') {{
        response = http.get('{url}', params);
    }} else if ('{method.upper()}' === 'POST') {{
        response = http.post('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'PUT') {{
        response = http.put('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'DELETE') {{
        response = http.del('{url}', {body_js}, params);
    }} else {{
        response = http.request('{method.upper()}', '{url}', {body_js}, params);
    }}
    
    check(response, {{
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    }});
}}
"""
    return script


def _parse_k6_output(output: str) -> Dict[str, Any]:
    """Parse k6 JSON output and extract key metrics"""
    lines = output.strip().split("\n")
    metrics = {}

    for line in lines:
        if line.strip():
            try:
                data = json.loads(line)
                if data.get("type") == "Point":
                    metric_name = data.get("metric")
                    if metric_name:
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append(
                            {
                                "timestamp": data.get("data", {}).get("time"),
                                "value": data.get("data", {}).get("value"),
                                "tags": data.get("data", {}).get("tags", {}),
                            }
                        )
            except json.JSONDecodeError:
                # Skip non-JSON lines (like k6 summary output)
                continue

    # Calculate summary statistics
    summary = {}
    for metric_name, values in metrics.items():
        if values:
            numeric_values = [
                v["value"] for v in values if isinstance(v["value"], (int, float))
            ]
            if numeric_values:
                summary[metric_name] = {
                    "count": len(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "avg": sum(numeric_values) / len(numeric_values),
                    "values": values[:10],  # Include first 10 data points
                }

    return {
        "summary": summary,
        "total_data_points": sum(len(values) for values in metrics.values()),
    }


@mcp.tool()
async def run_k6_stress_test(
    url: str,
    stages: List[Dict[str, Any]] = None,
    method: str = "GET",
    headers: Dict[str, str] = None,
    body: str = None,
    thresholds: Dict[str, List[str]] = None,
) -> types.CallToolResult:
    """Run k6 stress test with multiple stages"""

    if not _check_k6_installed():
        raise Exception(
            "Neither k6 nor Docker is installed. Please install k6 (https://k6.io/docs/get-started/installation/) or Docker."
        )

    # Default stages if none provided
    if not stages:
        stages = [
            {"duration": "2m", "target": 10},
            {"duration": "5m", "target": 10},
            {"duration": "2m", "target": 20},
            {"duration": "5m", "target": 20},
            {"duration": "2m", "target": 10},
            {"duration": "2m", "target": 0},
        ]

    try:
        # Create k6 script with stages
        k6_script = _generate_k6_stress_script(
            url=url,
            stages=stages,
            method=method,
            headers=headers or {},
            body=body,
            thresholds=thresholds or {},
        )

        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(k6_script)
            script_path = f.name

        try:
            # Build k6 command
            cmd = ["k6", "run", "--out", "json=/dev/stdout", script_path]

            # Run k6 using the new function
            logger.info(f"Running k6 stress test: {' '.join(cmd)}")
            result = _run_k6_command(cmd, script_path, timeout=600)  # 10 minute timeout

            if result.returncode != 0:
                raise Exception(f"k6 execution failed: {result.stderr}")

            # Parse k6 output
            test_results = _parse_k6_output(result.stdout)

            result_text = (
                f"K6 Stress Test Results:\n{json.dumps(test_results, indent=2)}"
            )

            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )

        finally:
            # Clean up temporary file
            if os.path.exists(script_path):
                os.unlink(script_path)

    except subprocess.TimeoutExpired:
        raise Exception("k6 stress test timed out after 10 minutes")
    except Exception as error:
        raise Exception(f"Failed to run k6 stress test: {str(error)}")


def _generate_k6_stress_script(
    url: str,
    stages: List[Dict[str, Any]],
    method: str,
    headers: Dict[str, str],
    body: str,
    thresholds: Dict[str, List[str]],
) -> str:
    """Generate k6 JavaScript stress test script with stages"""

    # Convert headers to JavaScript object
    headers_js = json.dumps(headers) if headers else "{}"

    # Convert thresholds to JavaScript object
    thresholds_js = json.dumps(thresholds) if thresholds else "{}"

    # Convert stages to JavaScript array
    stages_js = json.dumps(stages)

    # Handle request body
    body_js = json.dumps(body) if body else "null"

    script = f"""
import http from 'k6/http';
import {{ check }} from 'k6';

export let options = {{
    stages: {stages_js},
    thresholds: {thresholds_js}
}};

export default function() {{
    let params = {{
        headers: {headers_js}
    }};
    
    let response;
    
    if ('{method.upper()}' === 'GET') {{
        response = http.get('{url}', params);
    }} else if ('{method.upper()}' === 'POST') {{
        response = http.post('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'PUT') {{
        response = http.put('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'DELETE') {{
        response = http.del('{url}', {body_js}, params);
    }} else {{
        response = http.request('{method.upper()}', '{url}', {body_js}, params);
    }}
    
    check(response, {{
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    }});
}}
"""
    return script


def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="run_k6_load_test",
            description="Run k6 load test against a specific URL and return results as JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL for the load test",
                    },
                    "vus": {
                        "type": "integer",
                        "description": "Number of virtual users (default: 10)",
                        "default": 10,
                    },
                    "duration": {
                        "type": "string",
                        "description": "Test duration (e.g., '30s', '5m', '1h') (default: '30s')",
                        "default": "30s",
                    },
                    "rps": {
                        "type": "integer",
                        "description": "Requests per second limit (optional)",
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc.) (default: 'GET')",
                        "default": "GET",
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers to include in requests",
                    },
                    "body": {
                        "type": "string",
                        "description": "Request body for POST/PUT requests",
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "k6 thresholds for pass/fail criteria",
                    },
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="run_k6_stress_test",
            description="Run k6 stress test with multiple stages to gradually increase load",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL for the stress test",
                    },
                    "stages": {
                        "type": "array",
                        "description": "Array of stages with duration and target VUs",
                        "items": {
                            "type": "object",
                            "properties": {
                                "duration": {"type": "string"},
                                "target": {"type": "integer"},
                            },
                        },
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc.) (default: 'GET')",
                        "default": "GET",
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers to include in requests",
                    },
                    "body": {
                        "type": "string",
                        "description": "Request body for POST/PUT requests",
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "k6 thresholds for pass/fail criteria",
                    },
                },
                "required": ["url"],
            },
        ),
    ]

    # 각 도구가 올바른 형식인지 확인
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
