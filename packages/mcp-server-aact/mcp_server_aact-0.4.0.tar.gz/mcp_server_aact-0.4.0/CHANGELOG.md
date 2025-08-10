# Changelog

## [Unreleased] - 2025-01-09 (Docker Support)

### Added
- Docker support for containerized deployment
  - Optimized multi-stage `Dockerfile` using official uv image
  - 64% smaller images (180MB vs 514MB) through build optimization
  - Uses `ghcr.io/astral-sh/uv` for fast dependency installation
  - Security best practices with non-root user
  - Health check for database connectivity
  - Support for stdio, SSE, and streamable-http transports
- Docker Compose configuration
  - Easy local deployment with `docker-compose up`
  - Environment variable configuration
  - Network isolation and health checks
  - Optional development volume mounts
- `.dockerignore` file for optimized image builds
- `DOCKER_PUBLISHING.md` guide for Docker Hub deployment

## [Unreleased] - 2025-01-09

### Removed (Further Simplification)
- `schema://database` resource - not used by Claude Desktop, tools provide same functionality
- Resources directory and database schema JSON file - no longer needed
- Schema generation script - obsolete without schema resource
- Unused imports: `json` and `pathlib.Path` from server.py

## [0.4.0] - 2025-01-09

### Code Quality Improvements
- Removed unused `DateEncoder` class and related imports from database.py (7 lines of dead code)
- Moved dotenv loading to proper location (server.py entry point, not database.py)
- Improved dictionary access to use explicit checking instead of `.get()` with silent defaults
- Applied fail-hard principle consistently across codebase

### Changed
- Updated MCP dependency to >=1.12.4 (from >=1.5.0) to fix `report_progress` message parameter

### Removed
- `append_insight` tool - LLMs should rely on their own memory
- `memo://insights` resource - no longer needed without insights tracking
- MemoManager class - simplified architecture
- `InsightResponse` model - no longer needed

## [0.3.2] - 2024-08-09

### Added
- Structured output using Pydantic models for type-safe responses
- Context parameter to all tools for enhanced observability
- Progress reporting for large query results
- Resource change notifications when insights are updated
- Enhanced server instructions with strict data grounding requirement

### Changed
- All tools converted to async functions for better performance
- Improved error handling following fail-hard policy (no silent failures)
- Database initialization now explicitly checks for required environment variables
- Updated logging to use `logger.exception()` for cleaner exception handling

### New Models
- `TableInfo` - Structured table information
- `ColumnInfo` - Structured column metadata  
- `QueryResult` - Structured query responses with row count and truncation info
- `InsightResponse` - Structured insight recording responses