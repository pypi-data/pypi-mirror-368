# GCP Diagram MCP Server

Model Context Protocol (MCP) server for GCP Diagrams

This MCP server that seamlessly creates [diagrams](https://diagrams.mingrammer.com/) using the Python diagrams package DSL. This server allows you to generate GCP diagrams, sequence diagrams, flow diagrams, and class diagrams using Python code.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/mclabs/mcp/blob/main/src/gcp-diagram-mcp-server/tests/)

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. Install GraphViz https://www.graphviz.org/

## Installation

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/install-mcp?name=mclabs.gcp-diagram-mcp-server&config=eyJjb21tYW5kIjoidXZ4IG1jbGFicy5nY3AtZGlhZ3JhbS1tY3Atc2VydmVyIiwiZW52Ijp7IkZBU1RNQ1BfTE9HX0xFVkVMIjoiRVJST1IifSwiYXV0b0FwcHJvdmUiOltdLCJkaXNhYmxlZCI6ZmFsc2V9) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-4285F4?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=GCP%20Diagram%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mclabs.gcp-diagram-mcp-server%22%5D%2C%22env%22%3A%7B%22FASTMCP_LOG_LEVEL%22%3A%22ERROR%22%7D%2C%22autoApprove%22%3A%5B%5D%2C%22disabled%22%3Afalse%7D) |

Configure the MCP server in your MCP client configuration (e.g., for Google AI Studio CLI, edit your MCP client config):

```json
{
  "mcpServers": {
    "mclabs.gcp-diagram-mcp-server": {
      "command": "uvx",
      "args": ["mclabs.gcp-diagram-mcp-server"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "autoApprove": [],
      "disabled": false
    }
  }
}
```

or docker after a successful `docker build -t mclabs/gcp-diagram-mcp-server .`:

```json
  {
    "mcpServers": {
      "mclabs.gcp-diagram-mcp-server": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "--interactive",
          "--env",
          "FASTMCP_LOG_LEVEL=ERROR",
          "mclabs/gcp-diagram-mcp-server:latest"
        ],
        "env": {},
        "disabled": false,
        "autoApprove": []
      }
    }
  }
```

## 从本地源代码安装

如果你想从本地源代码安装和开发此 MCP 服务器，请按照以下步骤操作：

### 1. 克隆仓库

```bash
git clone <repository-url>
cd gcp-diagram-mcp-server
```

### 2. 安装依赖

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Python 和依赖
uv python install 3.10
uv sync
```

### 3. 本地开发安装

```bash
# 以可编辑模式安装
uv pip install -e .

# 或者安装开发依赖
uv pip install -e ".[dev]"
```

### 4. 配置 MCP 客户端

在你的 MCP 客户端配置中，使用本地安装的路径而不是 `uvx`：

```json
{
  "mcpServers": {
    "gcp-diagram-mcp-server-local": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/gcp-diagram-mcp-server", "mclabs.gcp_diagram_mcp_server"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "autoApprove": [],
      "disabled": false
    }
  }
}
```

或者，如果你已经将项目路径添加到 Python 路径中：

```json
{
  "mcpServers": {
    "gcp-diagram-mcp-server-local": {
      "command": "python",
      "args": ["-m", "mclabs.gcp_diagram_mcp_server"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "PYTHONPATH": "/path/to/gcp-diagram-mcp-server"
      },
      "autoApprove": [],
      "disabled": false
    }
  }
}
```

### 5. 验证安装

运行测试以确保一切正常工作：

```bash
# 运行所有测试
./run_tests.sh

# 或者直接使用 pytest
uv run pytest -xvs tests/
```

### 6. 热重载开发

在开发过程中，你可以使用以下命令直接运行服务器：

```bash
# 直接运行服务器
uv run python -m mclabs.gcp_diagram_mcp_server

# 或者使用调试模式
uv run python -m mclabs.gcp_diagram_mcp_server --debug
```

## Features

The Diagrams MCP Server provides the following capabilities:

1. **Generate Diagrams**: Create professional diagrams using Python code
2. **Multiple Diagram Types**: Support for GCP architecture, sequence diagrams, flow charts, class diagrams, and more
3. **Enhanced GCP Icons**: Access to 22+ additional GCP service icons not available in the standard diagrams package
4. **Customization**: Customize diagram appearance, layout, and styling
5. **Security**: Code scanning to ensure secure diagram generation

### Enhanced GCP Icons

This server now includes a curated collection of enhanced GCP service icons that are automatically available when generating diagrams. These icons are implemented as Custom classes and provide access to the latest GCP services:

**AI/ML Services:**
- Vertex AI, Vertex AI Agent Builder, Vertex AI Search
- Dataplex, Analytics Hub, Data QnA
- Looker, Looker Studio

**Database & Integration:**
- Datastream, Database Migration Service
- Cloud SQL (2nd Gen)

**DevOps & CI/CD:**
- Cloud Deploy, Artifact Registry, Batch
- Migrate to Containers, Infrastructure Manager

**Network & CDN:**
- Cloud CDN (new shield), Network Topology

**Security & Identity:**
- BeyondCorp Enterprise

**Management & Operations:**
- Cost Management, Cloud Monitoring (new)

**Maps & Geospatial:**
- Google Maps Platform

These enhanced icons are automatically loaded and can be used just like standard diagram icons:

```python
with Diagram("AI/ML Pipeline", show=False):
    # Enhanced icons - no import needed
    vertex_ai = VertexAI("Vertex AI")
    analytics_hub = AnalyticsHub("Analytics Hub")
    dataplex = Dataplex("Data Lake")
    
    # Standard icons
    from diagrams.gcp.storage import Storage
    storage = Storage("Data Source")
    
    storage >> dataplex >> analytics_hub >> vertex_ai
```

## Quick Example

```python
from diagrams import Diagram
from diagrams.gcp.compute import Functions
from diagrams.gcp.database import Firestore
from diagrams.gcp.network import LoadBalancing

with Diagram("Serverless Application", show=False):
    lb = LoadBalancing("Load Balancer")
    function = Functions("Cloud Function")
    database = Firestore("Firestore")

    lb >> function >> database
```

## Development

### Testing

The project includes a comprehensive test suite to ensure the functionality of the MCP server. The tests are organized by module and cover all aspects of the server's functionality.

To run the tests, use the provided script:

```bash
./run_tests.sh
```

This script will automatically install pytest and its dependencies if they're not already installed.

Or run pytest directly (if you have pytest installed):

```bash
pytest -xvs tests/
```

To run with coverage:

```bash
pytest --cov=mclabs.gcp_diagram_mcp_server --cov-report=term-missing tests/
```

For more information about the tests, see the [tests README](https://github.com/mclabs/mcp/blob/main/src/gcp-diagram-mcp-server/tests/README.md).

### Development Dependencies

To set up the development environment, install the development dependencies:

```bash
uv pip install -e ".[dev]"
```

This will install the required dependencies for development, including pytest, pytest-asyncio, and pytest-cov.

## Acknowledgments

This project is based on the excellent work from the [AWS Labs MCP project](https://github.com/awslabs/mcp). We are grateful to the AWS Labs team for creating the original AWS Diagram MCP Server, which served as the foundation for this GCP version.

### Original Project
- **Original Repository**: [awslabs/mcp](https://github.com/awslabs/mcp)
- **Original Package**: `awslabs.aws-diagram-mcp-server`
- **License**: Apache License 2.0

Special thanks to the AWS Labs team and all contributors to the original project for their innovative work in creating MCP servers for cloud architecture diagrams.
