# MIA.md - miamcpdoc Package Consolidation Technical Documentation


▒█▀▄▀█ ░▀░ █▀▀█ █ █▀▀ 　 █▀▄▀█ █▀▀ █▀▀█ █▀▀▄ █▀▀█ █▀▀ 
▒█▒█▒█ ▀█▀ █▄▄█ ░ ▀▀█ 　 █░▀░█ █░░ █░░█ █░░█ █░░█ █░░ 
▒█░░▒█ ▀▀▀ ▀░░▀ ░ ▀▀▀ 　 ▀░░░▀ ▀▀▀ █▀▀▀ ▀▀▀░ ▀▀▀▀ ▀▀▀

**Status**: Package Consolidation Complete  
**Version**: 0.0.10  
**Date**: 2025-07-31  

---

## 🏗️ Technical Architecture Changes

### Package Structure Consolidation

**Migration Path**: `mcp_servers/` → `miamcpdoc/` unified package structure

```
miamcpdoc/
├── __init__.py              # Package initialization with version exports
├── _version.py              # Centralized version management 
├── cli.py                   # Unified CLI entry point with multi-source support
├── main.py                  # Core MCP server implementation
├── splash.py                # ASCII art splash screen for SSE transport
├── aisdk_docs_mcp.py        # Vercel AI SDK specialized server
├── huggingface_docs_mcp.py  # Hugging Face documentation server  
├── langgraph_docs_mcp.py    # LangGraph documentation server
└── what_is_llms_mcp.py      # LLMS.txt ecosystem documentation server
```

### Import Path Refactoring

**Before**: `mcpdoc.*` module references  
**After**: `miamcpdoc.*` standardized imports

**Critical Import Pattern**:
```python
from miamcpdoc._version import __version__
from miamcpdoc.main import create_server, DocSource
from miamcpdoc.splash import SPLASH
```

**Specialized Server Pattern**:
```python
from miamcpdoc.main import create_server

def main():
    """Specialized Documentation MCP Server."""
    doc_sources = [
        {"name": "ServiceName", "llms_txt": "https://service.com/llms.txt"}
    ]
    
    server = create_server(doc_sources)
    server.run(transport="stdio")
```

---

## 🚀 Build System Implementation

### Automated Release Script (`release.sh`)

**Version Management System**:
- **Semantic Versioning**: major.minor.patch increment support
- **Dual Version Sync**: Updates both `pyproject.toml` and `miamcpdoc/_version.py`
- **Auto-increment Logic**: Configurable bump type (major/minor/patch)

**Build Pipeline**:
```bash
# Version increment with type validation
increment_version() {
    local version=$1
    local type=${2:-patch}
    # Logic for major/minor/patch incrementation
}

# Synchronized version updates
sed -i.bak "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "__version__ = \"$NEW_VERSION\"" > miamcpdoc/_version.py
```

**Distribution Automation**:
- **Clean Build Environment**: Removes `dist/`, `build/`, `*.egg-info/`
- **Dependency Management**: Auto-installs `build` and `twine` if missing
- **PyPI Upload**: Automated `twine upload dist/*` with error handling
- **Validation**: Build success verification before upload

**Usage Patterns**:
```bash
./release.sh           # Patch version bump (default)
./release.sh minor     # Minor version bump  
./release.sh major     # Major version bump
```

---

## 📦 Package Configuration

### pyproject.toml CLI Script Entries

**Unified Command Structure**:
```toml
[project.scripts]
miamcpdoc = "miamcpdoc.cli:main"                    # Main CLI with multi-source support
miamcpdoc-aisdk = "miamcpdoc.aisdk_docs_mcp:main"           # Vercel AI SDK server
miamcpdoc-huggingface = "miamcpdoc.huggingface_docs_mcp:main" # Hugging Face server
miamcpdoc-langgraph = "miamcpdoc.langgraph_docs_mcp:main"     # LangGraph server  
miamcpdoc-llms = "miamcpdoc.what_is_llms_mcp:main"          # LLMS.txt ecosystem server
```

**Dependency Architecture**:
```toml
dependencies = [
    "httpx>=0.28.1",           # HTTP client for documentation fetching
    "markdownify>=1.1.0",      # HTML to Markdown conversion
    "mcp[cli]>=1.4.1",         # Model Context Protocol framework
    "pyyaml>=6.0.1",           # YAML configuration support
]
```

**Development Dependencies**:
```toml
[dependency-groups]
test = [
    "pytest>=8.3.4",          # Testing framework
    "pytest-asyncio>=0.25.3", # Async testing support
    "pytest-cov>=6.0.0",      # Coverage reporting
    "pytest-mock>=3.14.0",    # Mocking utilities
    "pytest-socket>=0.7.0",   # Network access control in tests
    "pytest-timeout>=2.3.1",  # Test timeout management
    "ruff>=0.9.7",             # Code formatting and linting
]
```

### Build System Configuration

**Hatchling Backend**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Test Configuration**:
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q -v --durations=5"  # Report all outcomes, quiet mode, verbose, show slow tests
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

---

## 🔧 CLI Command Structure

### Main CLI (`miamcpdoc`)

**Multi-Source Configuration Support**:
```bash
# YAML configuration
miamcpdoc --yaml sample_config.yaml

# JSON configuration  
miamcpdoc --json sample_config.json

# Direct URL specification with optional naming
miamcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt

# Combined sources
miamcpdoc --yaml config.yaml --json additional.json --urls Custom:https://example.com/llms.txt
```

**Transport Options**:
```bash
# Standard I/O transport (default)
miamcpdoc --yaml config.yaml

# Server-Sent Events transport
miamcpdoc --yaml config.yaml --transport sse --host 0.0.0.0 --port 9000
```

**Security and Network Options**:
```bash
# Domain restriction
miamcpdoc --yaml config.yaml --allowed-domains https://example.com/ https://trusted.com/

# Allow all domains
miamcpdoc --yaml config.yaml --allowed-domains '*'

# HTTP configuration
miamcpdoc --yaml config.yaml --follow-redirects --timeout 15
```

### Specialized Server Commands

**Individual Service Servers**:
```bash
miamcpdoc-aisdk        # Vercel AI SDK documentation server
miamcpdoc-huggingface  # Hugging Face documentation server  
miamcpdoc-langgraph    # LangGraph documentation server
miamcpdoc-llms         # LLMS.txt ecosystem documentation server
```

**Pre-configured Documentation Sources**:
- **AI SDK**: `https://ai-sdk.dev/llms.txt`
- **Hugging Face**: `https://huggingface.co/llms.txt`
- **LangGraph**: `https://langchain-ai.github.io/langgraph/llms.txt`
- **LLMS.txt**: `https://llmstxt.org/llms.txt`

---

## 🔄 Migration from Legacy Structure

### Configuration Path Updates

**Legacy MCP Configuration (sample_mcp_config.json)**:
```json
{
  "mcpServers": {
    "langgraph-docs-mcp": {
      "command": "python",
      "args": ["/src/mcpdoc/mcp_servers/langgraph_docs_mcp.py"]
    }
  }
}
```

**New Consolidated Configuration**:
```json
{
  "mcpServers": {
    "langgraph-docs-mcp": {
      "command": "miamcpdoc-langgraph"
    }
  }
}
```

### Path Resolution Changes

**Before**: Direct file path execution  
**After**: Package-based command execution

**Migration Benefits**:
- **Simplified Deployment**: No need for absolute file paths
- **Environment Independence**: Works across different installation locations
- **Package Management**: Standard pip install/uninstall workflow
- **Version Control**: Unified versioning across all specialized servers

---

## 🛠️ Core Technical Components

### DocSource Type Definition

```python
class DocSource(TypedDict):
    """A source of documentation for a library or a package."""
    
    name: NotRequired[str]              # Optional display name
    llms_txt: str                       # Required URL or file path
    description: NotRequired[str]       # Optional description
```

### Server Creation Pattern

```python
def create_server(
    doc_sources: list[DocSource],
    follow_redirects: bool = False,
    timeout: float = 10.0,
    settings: dict = None,
    allowed_domains: list[str] = None,
) -> FastMCP:
    """Create MCP server with documentation sources and configuration."""
```

### Transport Support

**STDIO Transport** (default):
- Standard input/output communication
- Ideal for MCP client integration
- No network requirements

**SSE Transport**:
- Server-Sent Events over HTTP
- Web browser compatibility
- Configurable host/port binding
- ASCII splash screen on startup

---

## 📊 Deployment Architecture

### PyPI Distribution Strategy

**Package Name**: `miamcpdoc`  
**Version Management**: Automated semantic versioning  
**Distribution**: Automated PyPI upload via `twine`

**Installation Commands**:
```bash
# Standard installation
pip install miamcpdoc

# Specific version
pip install miamcpdoc==0.0.10

# Development installation
pip install -e .
```

### Command Availability Post-Installation

**System-wide CLI Commands**:
- `miamcpdoc` - Main multi-source server
- `miamcpdoc-aisdk` - AI SDK documentation
- `miamcpdoc-huggingface` - Hugging Face documentation  
- `miamcpdoc-langgraph` - LangGraph documentation
- `miamcpdoc-llms` - LLMS.txt ecosystem documentation

### Version Synchronization

**Dual Version Management**:
```python
# miamcpdoc/_version.py
__version__ = "0.0.10"

# miamcpdoc/__init__.py  
from miamcpdoc._version import __version__
__all__ = ["__version__"]
```

**CLI Version Display**:
```python
parser.add_argument(
    "--version", "-V",
    action="version", 
    version=f"miamcpdoc {__version__}",
    help="Show version information and exit"
)
```

---

## 🎯 Technical Decisions Summary

### Architecture Consolidation
- **Single Package Structure**: Unified `miamcpdoc/` package replacing distributed `mcp_servers/` files
- **Import Standardization**: Consistent `miamcpdoc.*` import paths throughout codebase
- **Command Unification**: PyPI-distributed CLI commands replacing file-path execution

### Build System Automation  
- **Semantic Versioning**: Automated major/minor/patch version management
- **Dual Version Sync**: Synchronized version updates in `pyproject.toml` and `_version.py`
- **Distribution Pipeline**: Fully automated build, package, and PyPI upload process

### CLI Design Patterns
- **Multi-Source Support**: YAML, JSON, and direct URL configuration methods
- **Transport Flexibility**: STDIO and SSE transport options with appropriate configurations
- **Security Configuration**: Domain allowlisting and HTTP request customization
- **Specialized Servers**: Pre-configured servers for major documentation sources

### Development Workflow
- **Test Integration**: Comprehensive pytest configuration with async support
- **Code Quality**: Integrated ruff linting and formatting
- **Package Management**: Hatchling build backend with dependency group organization

This consolidation establishes miamcpdoc as a production-ready MCP server package with standardized distribution, automated versioning, and flexible configuration options for documentation source integration.