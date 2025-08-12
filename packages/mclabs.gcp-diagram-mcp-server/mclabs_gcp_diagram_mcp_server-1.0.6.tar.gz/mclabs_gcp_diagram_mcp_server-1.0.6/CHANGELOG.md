# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2025-01-12

### Added

- **Enhanced GCP Icons**: Added 22+ additional GCP service icons not available in the standard diagrams package
- Support for latest GCP services including Vertex AI, Analytics Hub, Dataplex, Cloud Deploy, Artifact Registry, and more
- Automatic integration of enhanced icons with `list_diagram_icons` method - icons are merged into appropriate GCP service categories
- Custom class generation for enhanced icons using `diagrams.custom.Custom` - icons are automatically available in diagram generation without manual imports
- Enhanced icons span multiple categories: AI/ML, Database & Integration, DevOps & CI/CD, Network & CDN, Security & Identity, Management & Operations, and Maps & Geospatial
- Updated documentation with comprehensive list of available enhanced icons and usage examples

### Enhanced

- `list_diagram_icons` method now includes curated GCP icons from the enhanced collection
- `generate_diagram` method automatically loads enhanced icons as Custom classes for immediate use
- Improved AI assistant experience with better icon discovery and usage

## [1.0.0] - 2025-05-26

### Removed

- **BREAKING CHANGE:** Server Sent Events (SSE) support has been removed in accordance with the Model Context Protocol specification's [backwards compatibility guidelines](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#backwards-compatibility)
- This change prepares for future support of [Streamable HTTP](https://modelcontextprotocol.io/specification/draft/basic/transports#streamable-http) transport

## Unreleased

### Added

- Initial project setup
