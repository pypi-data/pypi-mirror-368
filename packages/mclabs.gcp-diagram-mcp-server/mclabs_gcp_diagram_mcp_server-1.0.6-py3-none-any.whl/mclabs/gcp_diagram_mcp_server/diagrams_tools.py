# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Diagram generation and example functions for the diagrams-mcp-server."""

import diagrams
import importlib
import inspect
import json
import logging
import os
import re
import signal
import uuid
from mclabs.gcp_diagram_mcp_server.models import (
    DiagramExampleResponse,
    DiagramGenerateResponse,
    DiagramIconsResponse,
    DiagramType,
)
from mclabs.gcp_diagram_mcp_server.scanner import scan_python_code
from typing import Optional


logger = logging.getLogger(__name__)


def _load_enhanced_gcp_icons():
    """Load enhanced GCP icons from the curated collection."""
    try:
        # Get the current module's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the extra_symbols directory (it's in mclabs/extra_symbols)
        extra_symbols_dir = os.path.join(current_dir, "..", "extra_symbols")
        curated_icons_path = os.path.join(extra_symbols_dir, "curated-icons-index.json")

        if not os.path.exists(curated_icons_path):
            logger.warning(f"Curated icons index not found at {curated_icons_path}")
            return {}

        with open(curated_icons_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Organize icons by category, mapping to GCP services
        category_service_mapping = {
            "ai-ml": "ml",
            "data-integration-databases": "database",
            "devops-ci-cd": "devtools",
            "network-edge-cdn": "network",
            "security-identity": "security",
            "management-operations": "operations",
            "maps-geospatial": "api"
        }

        enhanced_icons = {}

        for item in data.get("items", []):
            if not item.get("present", False):
                continue

            category = item["category"]
            name = item["name"]
            file_path = item["file"]

            # Map category to GCP service
            service = category_service_mapping.get(category, "misc")

            if service not in enhanced_icons:
                enhanced_icons[service] = []

            # Create a clean class name from the service name
            class_name = name.replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace(".", "")
            enhanced_icons[service].append({
                "class_name": class_name,
                "display_name": name,
                "file_path": file_path,
                "category": category
            })

        logger.debug(f"Loaded {sum(len(icons) for icons in enhanced_icons.values())} enhanced GCP icons")
        return enhanced_icons

    except Exception as e:
        logger.error(f"Error loading enhanced GCP icons: {str(e)}")
        return {}


def _generate_enhanced_gcp_custom_classes():
    """Generate Custom class definitions for enhanced GCP icons."""
    try:
        enhanced_icons = _load_enhanced_gcp_icons()
        if not enhanced_icons:
            return ""

        # Get the current module's directory and path to extra_symbols
        current_dir = os.path.dirname(os.path.abspath(__file__))
        extra_symbols_dir = os.path.join(current_dir, "..", "extra_symbols")

        custom_classes = []
        custom_classes.append("# Enhanced GCP Icons as Custom classes")
        custom_classes.append("# These provide additional GCP services not available in the standard diagrams package")

        for service, icons in enhanced_icons.items():
            for icon_info in icons:
                class_name = icon_info["class_name"]
                display_name = icon_info["display_name"]
                file_path = icon_info["file_path"]

                # Create absolute path to the icon file
                icon_file_path = os.path.join(extra_symbols_dir, file_path)

                # Generate the Custom class definition
                custom_class_def = f'{class_name} = lambda label: Custom(label, "{icon_file_path}")  # {display_name}'
                custom_classes.append(custom_class_def)

        custom_classes.append("")  # Add empty line at the end
        return "\n".join(custom_classes)

    except Exception as e:
        logger.error(f"Error generating enhanced GCP custom classes: {str(e)}")
        return ""


async def generate_diagram(
    code: str,
    filename: Optional[str] = None,
    timeout: int = 90,
    workspace_dir: Optional[str] = None,
) -> DiagramGenerateResponse:
    """Generate a diagram from Python code using the `diagrams` package.

    You should use the `get_diagram_examples` tool first to get examples of how to use the `diagrams` package.

    This function accepts Python code as a string that uses the diagrams package DSL
    and generates a PNG diagram without displaying it. The code is executed with
    show=False to prevent automatic display.

    Supported diagram types:
    - GCP architecture diagrams
    - Sequence diagrams
    - Flow diagrams
    - Class diagrams
    - Kubernetes diagrams
    - On-premises diagrams
    - Custom diagrams with custom nodes

    Args:
        code: Python code string using the diagrams package DSL
        filename: Output filename (without extension). If not provided, a random name will be generated.
        timeout: Timeout in seconds for diagram generation
        workspace_dir: The user's current workspace directory. If provided, diagrams will be saved to a "generated-diagrams" subdirectory.

    Returns:
        DiagramGenerateResponse: Response with the path to the generated diagram and status
    """
    # Scan the code for security issues
    scan_result = await scan_python_code(code)
    if scan_result.has_errors:
        return DiagramGenerateResponse(
            status="error",
            message=f"Security issues found in the code: {scan_result.error_message}",
        )

    if filename is None:
        filename = f"diagram_{uuid.uuid4().hex[:8]}"

    # Determine the output path
    if os.path.isabs(filename):
        # If it's an absolute path, use it directly
        output_path = filename
    else:
        # For non-absolute paths, use the "generated-diagrams" subdirectory

        # Strip any path components to ensure it's just a filename
        # (for relative paths with directories like "path/to/diagram.png")
        simple_filename = os.path.basename(filename)

        if (
            workspace_dir
            and os.path.isdir(workspace_dir)
            and os.access(workspace_dir, os.W_OK)
        ):
            # Create a "generated-diagrams" subdirectory in the workspace
            output_dir = os.path.join(workspace_dir, "generated-diagrams")
        else:
            # Fall back to a secure temporary directory if workspace_dir isn't provided or isn't writable
            import tempfile

            temp_base = tempfile.gettempdir()
            output_dir = os.path.join(temp_base, "generated-diagrams")

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Combine directory and filename
        output_path = os.path.join(output_dir, simple_filename)

    try:
        # Create a namespace for execution
        namespace = {}

        # Import necessary modules directly in the namespace
        # nosec B102 - These exec calls are necessary to import modules in the namespace
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            # nosem: python.lang.security.audit.exec-detected.exec-detected
            "import os",
            namespace,
        )
        # nosec B102 - These exec calls are necessary to import modules in the namespace
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            "import diagrams", namespace
        )
        # nosec B102 - These exec calls are necessary to import modules in the namespace
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            "from diagrams import Diagram, Cluster, Edge", namespace
        )  # nosem: python.lang.security.audit.exec-detected.exec-detected
        # nosec B102 - Import Custom class for enhanced GCP icons
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            "from diagrams.custom import Custom", namespace
        )  # nosem: python.lang.security.audit.exec-detected.exec-detected
        # nosec B102 - These exec calls are necessary to import modules in the namespace
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            """# Essential imports for common issues
from diagrams.gcp.api import APIGateway, Endpoints, Apigee
from diagrams.gcp.iot import IotCore
from diagrams.onprem.client import User, Users, Client
from diagrams.saas.crm import *
from diagrams.saas.identity import *
from diagrams.saas.chat import *
from diagrams.saas.recommendation import *
from diagrams.saas.cdn import *
from diagrams.saas.communication import *
from diagrams.saas.media import *
from diagrams.saas.logging import *
from diagrams.saas.security import *
from diagrams.saas.social import *
from diagrams.saas.alerting import *
from diagrams.saas.analytics import *
from diagrams.saas.automation import *
from diagrams.saas.filesharing import *
from diagrams.onprem.vcs import *
from diagrams.onprem.database import *
from diagrams.onprem.gitops import *
from diagrams.onprem.workflow import *
from diagrams.onprem.etl import *
from diagrams.onprem.inmemory import *
from diagrams.onprem.identity import *
from diagrams.onprem.network import *
from diagrams.onprem.proxmox import *
from diagrams.onprem.cd import *
from diagrams.onprem.container import *
from diagrams.onprem.certificates import *
from diagrams.onprem.mlops import *
from diagrams.onprem.dns import *
from diagrams.onprem.compute import *
from diagrams.onprem.logging import *
from diagrams.onprem.registry import *
from diagrams.onprem.security import *
from diagrams.onprem.client import *
from diagrams.onprem.groupware import *
from diagrams.onprem.iac import *
from diagrams.onprem.analytics import *
from diagrams.onprem.messaging import *
from diagrams.onprem.tracing import *
from diagrams.onprem.ci import *
from diagrams.onprem.search import *
from diagrams.onprem.storage import *
from diagrams.onprem.auth import *
from diagrams.onprem.monitoring import *
from diagrams.onprem.aggregator import *
from diagrams.onprem.queue import *
from diagrams.gis.database import *
from diagrams.gis.cli import *
from diagrams.gis.server import *
from diagrams.gis.python import *
from diagrams.gis.organization import *
from diagrams.gis.cplusplus import *
from diagrams.gis.mobile import *
from diagrams.gis.javascript import *
from diagrams.gis.desktop import *
from diagrams.gis.ogc import *
from diagrams.gis.java import *
from diagrams.gis.routing import *
from diagrams.gis.data import *
from diagrams.gis.geocoding import *
from diagrams.gis.format import *
from diagrams.elastic.saas import *
from diagrams.elastic.observability import *
from diagrams.elastic.elasticsearch import *
from diagrams.elastic.orchestration import *
from diagrams.elastic.security import *
from diagrams.elastic.beats import *
from diagrams.elastic.enterprisesearch import *
from diagrams.elastic.agent import *
from diagrams.programming.runtime import *
from diagrams.programming.framework import *
from diagrams.programming.flowchart import *
from diagrams.programming.language import *
from diagrams.gcp.storage import *
from diagrams.gcp.compute import *
from diagrams.gcp.database import *
from diagrams.gcp.analytics import *
from diagrams.gcp.network import *
from diagrams.gcp.security import *
from diagrams.gcp.devtools import *
from diagrams.gcp.ml import *
from diagrams.gcp.operations import *
from diagrams.gcp.migration import *
from diagrams.gcp.api import *
from diagrams.gcp.iot import *
from diagrams.generic.database import *
from diagrams.generic.blank import *
from diagrams.generic.network import *
from diagrams.generic.virtualization import *
from diagrams.generic.place import *
from diagrams.generic.device import *
from diagrams.generic.compute import *
from diagrams.generic.os import *
from diagrams.generic.storage import *
from diagrams.k8s.others import *
from diagrams.k8s.rbac import *
from diagrams.k8s.network import *
from diagrams.k8s.ecosystem import *
from diagrams.k8s.compute import *
from diagrams.k8s.chaos import *
from diagrams.k8s.infra import *
from diagrams.k8s.podconfig import *
from diagrams.k8s.controlplane import *
from diagrams.k8s.clusterconfig import *
from diagrams.k8s.storage import *
from diagrams.k8s.group import *
""",
            namespace,
        )
        # nosec B102 - These exec calls are necessary to import modules in the namespace
        exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
            "from urllib.request import urlretrieve", namespace
        )  # nosem: python.lang.security.audit.exec-detected.exec-detected

        # Add enhanced GCP icons as Custom classes
        enhanced_gcp_code = _generate_enhanced_gcp_custom_classes()
        if enhanced_gcp_code:
            # nosec B102 - Execute enhanced GCP icon definitions
            exec(  # nosem: python.lang.security.audit.exec-detected.exec-detected
                enhanced_gcp_code, namespace
            )  # nosem: python.lang.security.audit.exec-detected.exec-detected

        # No need to add essential imports since they're already available via wildcard imports above

        # Process the code to ensure show=False and set the output path
        if "with Diagram(" in code:
            # Find all instances of Diagram constructor
            diagram_pattern = r"with\s+Diagram\s*\((.*?)\)"
            matches = re.findall(diagram_pattern, code)

            for match in matches:
                # Get the original arguments
                original_args = match.strip()

                # Check if show parameter is already set
                has_show = "show=" in original_args
                has_filename = "filename=" in original_args

                # Prepare new arguments
                new_args = original_args

                # Add or replace parameters as needed
                # If filename is already set, we need to replace it with our output_path
                if has_filename:
                    # Replace the existing filename parameter
                    filename_pattern = r'filename\s*=\s*[\'"]([^\'"]*)[\'"]'
                    new_args = re.sub(
                        filename_pattern, f"filename='{output_path}'", new_args
                    )
                else:
                    # Add the filename parameter
                    if new_args and not new_args.endswith(","):
                        new_args += ", "
                    new_args += f"filename='{output_path}'"

                # Add show=False if not already set
                if not has_show:
                    if new_args and not new_args.endswith(","):
                        new_args += ", "
                    new_args += "show=False"

                # Replace in the code
                code = code.replace(
                    f"with Diagram({original_args})", f"with Diagram({new_args})"
                )

        # Set up a timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Diagram generation timed out after {timeout} seconds")

        # Register the timeout handler
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        # Execute the code
        # nosec B102 - This exec is necessary to run user-provided diagram code in a controlled environment
        exec(
            code, namespace
        )  # nosem: python.lang.security.audit.exec-detected.exec-detected

        # Cancel the alarm
        signal.alarm(0)

        # Check if the file was created
        png_path = f"{output_path}.png"
        if os.path.exists(png_path):
            response = DiagramGenerateResponse(
                status="success",
                path=png_path,
                message=f"Diagram generated successfully at {png_path}",
            )

            return response
        else:
            return DiagramGenerateResponse(
                status="error",
                message="Diagram file was not created. Check your code for errors.",
            )
    except TimeoutError as e:
        return DiagramGenerateResponse(status="error", message=str(e))
    except Exception as e:
        # More detailed error logging
        error_type = type(e).__name__
        error_message = str(e)
        return DiagramGenerateResponse(
            status="error",
            message=f"Error generating diagram: {error_type}: {error_message}",
        )


def get_diagram_examples(
    diagram_type: DiagramType = DiagramType.ALL,
) -> DiagramExampleResponse:
    """Get example code for different types of diagrams.

    Args:
        diagram_type: Type of diagram example to return.

    Returns:
        DiagramExampleResponse: Dictionary with example code for the requested diagram type(s)
    """
    examples = {}

    # Basic examples
    if diagram_type in [DiagramType.GCP, DiagramType.ALL]:
        examples[
            "gcp_basic"
        ] = """with Diagram("Web Service Architecture", show=False):
    LoadBalancing("lb") >> ComputeEngine("web") >> SQL("userdb")
"""

    if diagram_type in [DiagramType.SEQUENCE, DiagramType.ALL]:
        examples[
            "sequence"
        ] = """with Diagram("User Authentication Flow", show=False):
    user = User("User")
    login = InputOutput("Login Form")
    auth = Decision("Authenticated?")
    success = Action("Access Granted")
    failure = Action("Access Denied")

    user >> login >> auth
    auth >> success
    auth >> failure
"""

    if diagram_type in [DiagramType.FLOW, DiagramType.ALL]:
        examples[
            "flow"
        ] = """with Diagram("Order Processing Flow", show=False):
    start = Predefined("Start")
    order = InputOutput("Order Received")
    check = Decision("In Stock?")
    process = Action("Process Order")
    wait = Delay("Backorder")
    ship = Action("Ship Order")
    end = Predefined("End")

    start >> order >> check
    check >> process >> ship >> end
    check >> wait >> process
"""

    if diagram_type in [DiagramType.CLASS, DiagramType.ALL]:
        examples[
            "class"
        ] = """with Diagram("Simple Class Diagram", show=False):
    base = Python("BaseClass")
    child1 = Python("ChildClass1")
    child2 = Python("ChildClass2")

    base >> child1
    base >> child2
"""

    # Advanced examples from the documentation
    if diagram_type in [DiagramType.GCP, DiagramType.ALL]:
        examples[
            "gcp_grouped_workers"
        ] = """with Diagram("Grouped Workers", show=False, direction="TB"):
    LoadBalancing("lb") >> [ComputeEngine("worker1"),
                           ComputeEngine("worker2"),
                           ComputeEngine("worker3"),
                           ComputeEngine("worker4"),
                           ComputeEngine("worker5")] >> SQL("events")
"""

        examples[
            "gcp_clustered_web_services"
        ] = """with Diagram("Clustered Web Services", show=False):
    dns = DNS("dns")
    lb = LoadBalancing("lb")

    with Cluster("Services"):
        svc_group = [GKE("web1"),
                     GKE("web2"),
                     GKE("web3")]

    with Cluster("DB Cluster"):
        db_primary = SQL("userdb")
        db_primary - [SQL("userdb ro")]

    memcached = Memorystore("memcached")

    dns >> lb >> svc_group
    svc_group >> db_primary
    svc_group >> memcached
"""

        examples[
            "gcp_event_processing"
        ] = """with Diagram("Event Processing", show=False):
    source = GKE("k8s source")

    with Cluster("Event Flows"):
        with Cluster("Event Workers"):
            workers = [Run("worker1"),
                       Run("worker2"),
                       Run("worker3")]

        queue = PubSub("event queue")

        with Cluster("Processing"):
            handlers = [Functions("proc1"),
                        Functions("proc2"),
                        Functions("proc3")]

    store = Storage("events store")
    dw = BigQuery("analytics")

    source >> workers >> queue >> handlers
    handlers >> store
    handlers >> dw
"""

        examples[
            "gcp_ai_image_processing"
        ] = """with Diagram("GCS Image Processing with AI Platform", show=False, direction="LR"):
    user = User("User")

    with Cluster("Google Cloud Storage"):
        input_folder = Storage("Input Folder")
        output_folder = Storage("Output Folder")

    function = Functions("Image Processor Function")
    ai_platform = AIPlatform("Vertex AI")

    user >> Edge(label="Upload Image") >> input_folder
    input_folder >> Edge(label="Trigger") >> function
    function >> Edge(label="Process Image") >> ai_platform
    ai_platform >> Edge(label="Return Analysis") >> function
    function >> Edge(label="Upload Processed Image") >> output_folder
    output_folder >> Edge(label="Download Result") >> user
"""

        examples[
            "gcp_api_gateway"
        ] = """with Diagram("API Gateway Architecture", show=False, direction="LR"):
    client = User("Client")

    with Cluster("API Layer"):
        gateway = APIGateway("API Gateway")
        endpoints = Endpoints("Cloud Endpoints")

    with Cluster("Backend Services"):
        service1 = Run("Service 1")
        service2 = Run("Service 2")
        service3 = Run("Service 3")

    database = SQL("Cloud SQL")

    client >> gateway >> endpoints
    endpoints >> service1 >> database
    endpoints >> service2 >> database
    endpoints >> service3 >> database
"""

        examples[
            "gcp_iot_pipeline"
        ] = """with Diagram("IoT Data Pipeline", show=False, direction="TB"):
    devices = IotCore("IoT Devices")

    with Cluster("Message Processing"):
        pubsub = Pubsub("Pub/Sub")
        dataflow = Dataflow("Dataflow")

    with Cluster("Storage & Analytics"):
        bigquery = Bigquery("BigQuery")
        storage = Storage("Cloud Storage")

    devices >> pubsub >> dataflow
    dataflow >> bigquery
    dataflow >> storage
"""

        examples[
            "gcp_connection_patterns"
        ] = """with Diagram("GCP Connection Patterns", show=False, direction="LR"):
    # Pattern 1: Simple connection
    user = User("User")
    gateway = APIGateway("API Gateway")
    service = Run("Cloud Run")

    user >> gateway >> service

    # Pattern 2: One-to-many (correct way to connect to multiple services)
    lb = LoadBalancing("Load Balancer")
    workers = [
        ComputeEngine("Worker 1"),
        ComputeEngine("Worker 2"),
        ComputeEngine("Worker 3")
    ]
    database = SQL("Database")

    # Correct syntax: lb connects to list, then list connects to database
    lb >> workers >> database

    # Pattern 3: Many-to-one using individual connections
    storage1 = Storage("Storage 1")
    storage2 = Storage("Storage 2")
    processor = Functions("Processor")

    storage1 >> processor
    storage2 >> processor

    # Pattern 4: Using loops for complex connections
    apis = [Endpoints("API 1"), Endpoints("API 2")]
    services = [Run("Service A"), Run("Service B")]

    for api in apis:
        for svc in services:
            api >> svc
"""

    if diagram_type in [DiagramType.K8S, DiagramType.ALL]:
        examples[
            "k8s_exposed_pod"
        ] = """with Diagram("Exposed Pod with 3 Replicas", show=False):
    net = Ingress("domain.com") >> Service("svc")
    net >> [Pod("pod1"),
            Pod("pod2"),
            Pod("pod3")] << ReplicaSet("rs") << Deployment("dp") << HPA("hpa")
"""

        examples[
            "k8s_stateful"
        ] = """with Diagram("Stateful Architecture", show=False):
    with Cluster("Apps"):
        svc = Service("svc")
        sts = StatefulSet("sts")

        apps = []
        for _ in range(3):
            pod = Pod("pod")
            pvc = PVC("pvc")
            pod - sts - pvc
            apps.append(svc >> pod >> pvc)

    apps << PV("pv") << StorageClass("sc")
"""

    if diagram_type in [DiagramType.ONPREM, DiagramType.ALL]:
        examples[
            "onprem_web_service"
        ] = """with Diagram("Advanced Web Service with On-Premises", show=False):
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Grafana("monitoring")

    with Cluster("Service Cluster"):
        grpcsvc = [
            Server("grpc1"),
            Server("grpc2"),
            Server("grpc3")]

    with Cluster("Sessions HA"):
        primary = Redis("session")
        primary - Redis("replica") << metrics
        grpcsvc >> primary

    with Cluster("Database HA"):
        primary = PostgreSQL("users")
        primary - PostgreSQL("replica") << metrics
        grpcsvc >> primary

    aggregator = Fluentd("logging")
    aggregator >> Kafka("stream") >> Spark("analytics")

    ingress >> grpcsvc >> aggregator
"""

        examples[
            "onprem_web_service_colored"
        ] = """with Diagram(name="Advanced Web Service with On-Premise (colored)", show=False):
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Edge(color="firebrick", style="dashed") << Grafana("monitoring")

    with Cluster("Service Cluster"):
        grpcsvc = [
            Server("grpc1"),
            Server("grpc2"),
            Server("grpc3")]

    with Cluster("Sessions HA"):
        primary = Redis("session")
        primary - Edge(color="brown", style="dashed") - Redis("replica") << Edge(label="collect") << metrics
        grpcsvc >> Edge(color="brown") >> primary

    with Cluster("Database HA"):
        primary = PostgreSQL("users")
        primary - Edge(color="brown", style="dotted") - PostgreSQL("replica") << Edge(label="collect") << metrics
        grpcsvc >> Edge(color="black") >> primary

    aggregator = Fluentd("logging")
    aggregator >> Edge(label="parse") >> Kafka("stream") >> Edge(color="black", style="bold") >> Spark("analytics")

    ingress >> Edge(color="darkgreen") << grpcsvc >> Edge(color="darkorange") >> aggregator
"""

    if diagram_type in [DiagramType.CUSTOM, DiagramType.ALL]:
        examples[
            "custom_rabbitmq"
        ] = """# Download an image to be used into a Custom Node class
rabbitmq_url = "https://jpadilla.github.io/rabbitmqapp/assets/img/icon.png"
rabbitmq_icon = "rabbitmq.png"
urlretrieve(rabbitmq_url, rabbitmq_icon)

with Diagram("Broker Consumers", show=False):
    with Cluster("Consumers"):
        consumers = [
            Pod("worker"),
            Pod("worker"),
            Pod("worker")]

    queue = Custom("Message queue", rabbitmq_icon)

    queue >> consumers >> Aurora("Database")
"""

    return DiagramExampleResponse(examples=examples)


def list_diagram_icons(
    provider_filter: Optional[str] = None, service_filter: Optional[str] = None
) -> DiagramIconsResponse:
    """List available icons from the diagrams package, with optional filtering.

    This function now includes enhanced GCP icons from the curated collection.
    These additional icons are available as Custom nodes in diagram generation.

    Args:
        provider_filter: Optional filter by provider name (e.g., "gcp")
        service_filter: Optional filter by service name (e.g., "compute", "database")

    Returns:
        DiagramIconsResponse: Dictionary with available providers, services, and icons
    """
    logger.debug("Starting list_diagram_icons function")
    logger.debug(f"Filters - provider: {provider_filter}, service: {service_filter}")

    try:
        # If no filters provided, just return the list of available providers
        if not provider_filter and not service_filter:
            # Get the base path of the diagrams package
            diagrams_path = os.path.dirname(diagrams.__file__)
            providers = {}

            # List of provider directories to exclude
            exclude_dirs = ["__pycache__", "_template"]

            # Just list the available providers without their services/icons
            for provider_name in os.listdir(os.path.join(diagrams_path)):
                provider_path = os.path.join(diagrams_path, provider_name)

                # Skip non-directories and excluded directories
                if (
                    not os.path.isdir(provider_path)
                    or provider_name.startswith("_")
                    or provider_name in exclude_dirs
                ):
                    continue

                # Add provider to the dictionary with empty services
                providers[provider_name] = {}

            return DiagramIconsResponse(
                providers=providers, filtered=False, filter_info=None
            )

        # Dictionary to store filtered providers and their services/icons
        providers = {}

        # Get the base path of the diagrams package
        diagrams_path = os.path.dirname(diagrams.__file__)

        # List of provider directories to exclude
        exclude_dirs = ["__pycache__", "_template"]

        # If only provider filter is specified
        if provider_filter and not service_filter:
            provider_path = os.path.join(diagrams_path, provider_filter)

            # Check if the provider exists
            if not os.path.isdir(provider_path) or provider_filter in exclude_dirs:
                return DiagramIconsResponse(
                    providers={},
                    filtered=True,
                    filter_info={
                        "provider": provider_filter,
                        "error": "Provider not found",
                    },
                )

            # Add provider to the dictionary
            providers[provider_filter] = {}

            # Iterate through all service modules in the provider
            for service_file in os.listdir(provider_path):
                # Skip non-Python files and special files
                if not service_file.endswith(".py") or service_file.startswith("_"):
                    continue

                service_name = service_file[:-3]  # Remove .py extension

                # Import the service module
                module_path = f"diagrams.{provider_filter}.{service_name}"
                try:
                    service_module = importlib.import_module(  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                        module_path  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                    )  # nosem: python.lang.security.audit.non-literal-import.non-literal-import

                    # Find all classes in the module that are Node subclasses
                    icons = []
                    for name, obj in inspect.getmembers(service_module):
                        # Skip private members and imported modules
                        if name.startswith("_") or inspect.ismodule(obj):
                            continue

                        # Check if it's a class and likely a Node subclass
                        if inspect.isclass(obj) and hasattr(obj, "_icon"):
                            icons.append(name)

                    # Add service and its icons to the provider
                    if icons:
                        providers[provider_filter][service_name] = sorted(icons)

                        # If this is GCP provider, add enhanced icons
                        if provider_filter == "gcp":
                            enhanced_icons = _load_enhanced_gcp_icons()
                            if service_name in enhanced_icons:
                                enhanced_list = [icon["class_name"] for icon in enhanced_icons[service_name]]
                                # Merge enhanced icons with existing ones
                                providers[provider_filter][service_name].extend(enhanced_list)
                                providers[provider_filter][service_name] = sorted(set(providers[provider_filter][service_name]))

                except (ImportError, AttributeError, Exception) as e:
                    logger.error(f"Error processing {module_path}: {str(e)}")
                    continue

            return DiagramIconsResponse(
                providers=providers,
                filtered=True,
                filter_info={"provider": provider_filter},
            )

        # If both provider and service filters are specified
        elif provider_filter and service_filter:
            provider_path = os.path.join(diagrams_path, provider_filter)

            # Check if the provider exists
            if not os.path.isdir(provider_path) or provider_filter in exclude_dirs:
                return DiagramIconsResponse(
                    providers={},
                    filtered=True,
                    filter_info={
                        "provider": provider_filter,
                        "service": service_filter,
                        "error": "Provider not found",
                    },
                )

            # Add provider to the dictionary
            providers[provider_filter] = {}

            # Check if the service exists
            service_file = f"{service_filter}.py"
            service_path = os.path.join(provider_path, service_file)

            if not os.path.isfile(service_path):
                return DiagramIconsResponse(
                    providers={provider_filter: {}},
                    filtered=True,
                    filter_info={
                        "provider": provider_filter,
                        "service": service_filter,
                        "error": "Service not found",
                    },
                )

            # Import the service module
            module_path = f"diagrams.{provider_filter}.{service_filter}"
            try:
                service_module = importlib.import_module(  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                    module_path  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                )  # nosem: python.lang.security.audit.non-literal-import.non-literal-import

                # Find all classes in the module that are Node subclasses
                icons = []
                for name, obj in inspect.getmembers(service_module):
                    # Skip private members and imported modules
                    if name.startswith("_") or inspect.ismodule(obj):
                        continue

                    # Check if it's a class and likely a Node subclass
                    if inspect.isclass(obj) and hasattr(obj, "_icon"):
                        icons.append(name)

                # Add service and its icons to the provider
                if icons:
                    providers[provider_filter][service_filter] = sorted(icons)

                    # If this is GCP provider, add enhanced icons
                    if provider_filter == "gcp":
                        enhanced_icons = _load_enhanced_gcp_icons()
                        if service_filter in enhanced_icons:
                            enhanced_list = [icon["class_name"] for icon in enhanced_icons[service_filter]]
                            # Merge enhanced icons with existing ones
                            providers[provider_filter][service_filter].extend(enhanced_list)
                            providers[provider_filter][service_filter] = sorted(set(providers[provider_filter][service_filter]))

            except (ImportError, AttributeError, Exception) as e:
                logger.error(f"Error processing {module_path}: {str(e)}")
                return DiagramIconsResponse(
                    providers={provider_filter: {}},
                    filtered=True,
                    filter_info={
                        "provider": provider_filter,
                        "service": service_filter,
                        "error": f"Error loading service: {str(e)}",
                    },
                )

            return DiagramIconsResponse(
                providers=providers,
                filtered=True,
                filter_info={"provider": provider_filter, "service": service_filter},
            )

        # If only service filter is specified (not supported)
        elif service_filter:
            return DiagramIconsResponse(
                providers={},
                filtered=True,
                filter_info={
                    "service": service_filter,
                    "error": "Service filter requires provider filter",
                },
            )

        # Original implementation for backward compatibility
        else:
            # Dictionary to store all providers and their services/icons
            providers = {}

            # Get the base path of the diagrams package
            diagrams_path = os.path.dirname(diagrams.__file__)
            logger.debug(f"Diagrams package path: {diagrams_path}")

            # Iterate through all provider directories
            for provider_name in os.listdir(os.path.join(diagrams_path)):
                provider_path = os.path.join(diagrams_path, provider_name)

                # Skip non-directories and excluded directories
                if (
                    not os.path.isdir(provider_path)
                    or provider_name.startswith("_")
                    or provider_name in exclude_dirs
                ):
                    logger.debug(
                        f"Skipping {provider_name}: not a directory or in exclude list"
                    )
                    continue

                # Add provider to the dictionary
                providers[provider_name] = {}
                logger.debug(f"Processing provider: {provider_name}")

                # Iterate through all service modules in the provider
                for service_file in os.listdir(provider_path):
                    # Skip non-Python files and special files
                    if not service_file.endswith(".py") or service_file.startswith("_"):
                        logger.debug(
                            f"Skipping file {service_file}: not a Python file or starts with _"
                        )
                        continue

                    service_name = service_file[:-3]  # Remove .py extension
                    logger.debug(f"Processing service: {provider_name}.{service_name}")

                    # Import the service module
                    module_path = f"diagrams.{provider_name}.{service_name}"
                    try:
                        logger.debug(f"Attempting to import module: {module_path}")
                        service_module = importlib.import_module(  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                            module_path  # nosem: python.lang.security.audit.non-literal-import.non-literal-import
                        )  # nosem: python.lang.security.audit.non-literal-import.non-literal-import

                        # Find all classes in the module that are Node subclasses
                        icons = []
                        for name, obj in inspect.getmembers(service_module):
                            # Skip private members and imported modules
                            if name.startswith("_") or inspect.ismodule(obj):
                                continue

                            # Check if it's a class and likely a Node subclass
                            if inspect.isclass(obj) and hasattr(obj, "_icon"):
                                icons.append(name)
                                logger.debug(f"Found icon: {name}")

                        # Add service and its icons to the provider
                        if icons:
                            providers[provider_name][service_name] = sorted(icons)
                            logger.debug(
                                f"Added {len(icons)} icons for {provider_name}.{service_name}"
                            )

                            # If this is GCP provider, add enhanced icons
                            if provider_name == "gcp":
                                enhanced_icons = _load_enhanced_gcp_icons()
                                if service_name in enhanced_icons:
                                    enhanced_list = [icon["class_name"] for icon in enhanced_icons[service_name]]
                                    # Merge enhanced icons with existing ones
                                    providers[provider_name][service_name].extend(enhanced_list)
                                    providers[provider_name][service_name] = sorted(set(providers[provider_name][service_name]))
                                    logger.debug(f"Added {len(enhanced_list)} enhanced icons for gcp.{service_name}")
                        else:
                            logger.warning(
                                f"No icons found for {provider_name}.{service_name}"
                            )

                    except ImportError as ie:
                        logger.error(f"ImportError for {module_path}: {str(ie)}")
                        continue
                    except AttributeError as ae:
                        logger.error(f"AttributeError for {module_path}: {str(ae)}")
                        continue
                    except Exception as e:
                        logger.error(
                            f"Unexpected error processing {module_path}: {str(e)}"
                        )
                        continue

            logger.debug(f"Completed processing. Found {len(providers)} providers")
            return DiagramIconsResponse(
                providers=providers, filtered=False, filter_info=None
            )

    except Exception as e:
        logger.exception(f"Error in list_diagram_icons: {str(e)}")
        # Return empty response on error
        return DiagramIconsResponse(
            providers={}, filtered=False, filter_info={"error": str(e)}
        )
