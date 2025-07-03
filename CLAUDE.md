# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

OneZoom is a web-based fractal tree of life explorer built with Web2py framework. It visualizes evolutionary relationships through an interactive tree interface that allows users to zoom into different taxonomic groups, view species information, and explore the tree of life.

## Development Commands

### Setup and Installation
- `npm ci` - Install npm dependencies
- `grunt dev` - Full development build (clean, web2py setup, compile JS/CSS, docs)
- `grunt web2py` - Configure web2py environment and virtual environment
- `./web2py-run` - Start local development server

### Building and Compilation
- `grunt compile-js` - Compile JavaScript with webpack (production)
- `grunt compile-js_dev` - Compile JavaScript with webpack (development)
- `npm run compile_js_dev:watch` - Compile JS with source maps and watch for changes
- `grunt css` - Compile SCSS to CSS
- `grunt docs` - Generate documentation from JSDoc comments

### Testing
- `grunt test` - Run all tests (server + client)
- `grunt test-server` - Run Python server unit tests
- `grunt test-client` - Run JavaScript client tests (`npm run test`)
- `grunt test-server-functional` - Run Selenium-based functional tests
- `grunt exec:test_server:test_filename.py` - Run individual server test

### Production
- `grunt prod` - Full production build with optimization and compression
- `grunt compile-python` - Compile Python bytecode for performance

### Specialized Builds
- `grunt partial-install` - Create standalone viewer that uses OneZoom APIs
- `grunt partial-local-install` - Create standalone viewer using local server

## Architecture

### Web2py Framework Structure
- **controllers/**: Main application logic
  - `default.py` - Public pages and core functionality
  - `API.py` - REST API endpoints
  - `tree.py` - Tree-specific operations
  - `treeviewer.py` - Tree viewer interface
- **models/**: Database models and configuration
  - `db.py` - Database setup and table definitions
  - `_OZglobals.py` - Global variables and utilities
- **views/**: HTML templates organized by controller
- **static/**: Static assets (CSS, JS, images)
  - `FinalOutputs/data/` - Tree data files (completetree_*.js, cut_position_map_*.js)
  - `OZTreeModule/` - Compiled JavaScript tree viewer

### JavaScript Tree Viewer (OZTreeModule)
Located in `OZprivate/rawJS/OZTreeModule/src/`:
- **Entry Points**: `OZentry.js` (main viewer), `OZui.js` (UI components)
- **Core Systems**:
  - `controller/` - Main application controller and interaction handling
  - `projection/` - Tree layout algorithms and rendering projections
  - `factory/` - Node creation and data management
  - `themes/` - Color schemes and visual themes
  - `api/` - Communication with backend APIs
  - `tour/` - Guided tour functionality
- **Build Process**: Uses webpack to bundle and optimize JavaScript, outputs to `dist/`

### Database Architecture
- Main tree data stored in `ordered_nodes` and `ordered_leaves` tables
- Image metadata in `images_by_ott` and `images_by_name` tables
- Sponsorship data in `reservations` table
- IUCN conservation status in `iucn` table
- Vernacular names in `vernacular_by_ott` and `vernacular_by_name` tables

### Tree Data Pipeline
- Tree topology and metadata stored as JavaScript files in `static/FinalOutputs/data/`
- Files named with timestamps (e.g., `completetree_28585326.js`)
- Cut position maps determine which parts of tree to load at different zoom levels
- Background scripts in `OZprivate/ServerScripts/` handle data updates

## Key Configuration Files
- `private/appconfig.ini` - Main configuration (database, APIs, features)
- `package.json` - npm dependencies and build scripts
- `Gruntfile.js` - Build task definitions
- `webpack.config.js` - JavaScript bundling configuration
- `requirements.txt` - Python dependencies

## Development Workflow
1. Edit `private/appconfig.ini.example` → `private/appconfig.ini` with database credentials
2. Run `grunt dev` for initial setup and build
3. Start server with `./web2py-run`
4. For JS development: `npm run compile_js_dev:watch` for live compilation
5. Run tests with `grunt test` before committing

## Important Notes
- Set `is_testing = False` in `models/db.py` for production
- Database migration controlled by `migrate` setting in `appconfig.ini`
- Tree data files are large and typically loaded from external sources
- Sponsorship functionality requires specific licensing and should remain disabled (`allow_sponsorship = 0`)