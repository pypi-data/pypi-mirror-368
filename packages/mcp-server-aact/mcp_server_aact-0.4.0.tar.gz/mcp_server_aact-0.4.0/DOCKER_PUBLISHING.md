# Docker Hub Publishing Guide

This guide explains how to publish the AACT MCP server to Docker Hub.

## Prerequisites
- Docker Desktop installed
- Docker Hub account (create at https://hub.docker.com)
- Repository access to navisbio/mcp-server-aact

## Publishing Steps

### 1. Login to Docker Hub
```bash
docker login --username navisbio
# Enter your Docker Hub password when prompted
```

### 2. Build the Image
```bash
# Ensure you're in the project root directory
docker build -t mcp-server-aact:latest .
```

### 3. Tag the Image
```bash
# Tag with latest
docker tag mcp-server-aact:latest navisbio/mcp-server-aact:latest

# Tag with version (update version number as needed)
docker tag mcp-server-aact:latest navisbio/mcp-server-aact:0.4.0
```

### 4. Push to Docker Hub
```bash
# Push both tags
docker push navisbio/mcp-server-aact:latest
docker push navisbio/mcp-server-aact:0.4.0
```

### 5. Verify on Docker Hub
Visit https://hub.docker.com/r/navisbio/mcp-server-aact to verify the push was successful.

## Automated Publishing (GitHub Actions)

For automated publishing on release, you can add this GitHub Action workflow:

Create `.github/workflows/docker-publish.yml`:
```yaml
name: Docker Publish

on:
  release:
    types: [published]
  push:
    branches: [main]
    tags:
      - 'v*'

env:
  REGISTRY: docker.io
  IMAGE_NAME: navisbio/mcp-server-aact

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### Setting up GitHub Secrets
1. Go to Settings � Secrets and variables � Actions in your GitHub repository
2. Add the following secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username (navisbio)
   - `DOCKER_TOKEN`: Docker Hub access token (create at https://hub.docker.com/settings/security)

## Version Management

When releasing a new version:
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Commit changes
4. Tag the release: `git tag v0.4.0`
5. Push tag: `git push origin v0.4.0`
6. Build and push Docker image with new version tag

## Testing Published Image

After publishing, test the image:
```bash
# Pull the published image
docker pull navisbio/mcp-server-aact:latest

# Test run
docker run --rm -i \
  --env DB_USER=test_user \
  --env DB_PASSWORD=test_pass \
  navisbio/mcp-server-aact:latest
```

## Troubleshooting

### Permission Denied
If you get "denied: requested access to the resource is denied":
- Ensure you're logged in: `docker login`
- Verify you have push access to the repository
- Check that the image name matches exactly

### Image Not Found
If users report "image not found":
- Check that the image is public on Docker Hub
- Verify the correct image name: `navisbio/mcp-server-aact`
- Ensure users have Docker installed and running