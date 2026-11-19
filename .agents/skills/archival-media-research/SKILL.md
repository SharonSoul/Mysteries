---
name: archival-media-research
description: Discover and query authentic historical imagery, archival photographs, antique maps, museum scans, and CC0/public domain video from Pixabay, Wikimedia Commons, Library of Congress, Smithsonian Open Access, and Openverse. Use when searching for visual evidence, querying cultural heritage APIs, and matching scenes to authentic historical assets.
license: MIT
metadata: {"apis": ["pixabay", "wikimedia_commons", "loc_gov", "smithsonian", "openverse"]}
---

# Archival Media Research

This skill governs querying the five primary visual media sources for the **Mysteries & Unexplained History Documentary Studio**.

## Media Sources & API Policies

### 1. Pixabay API
- **Endpoint**: `https://pixabay.com/api/`
- **Use Case**: Atmospheric historical landscapes, starry night skies, archaeological textures, and ambient B-roll.
- **Constraints**: 
  - Respect request limits (100 requests per minute).
  - Cache API responses for 24 hours.
  - Prohibit systematic mass downloads. Only download assets selected for specific scenes.

### 2. Wikimedia Commons API
- **Endpoint**: `https://commons.wikimedia.org/w/api.php`
- **Use Case**: Specific museum artifacts, historical excavation photographs, antique engravings, and manuscript folios.
- **Rules**:
  - Always include a custom `User-Agent` header with contact info.
  - Query image metadata (`imageinfo`, `extmetadata`) to inspect creator, publication date, and license tags.

### 3. Library of Congress (LOC) API
- **Endpoint**: `https://www.loc.gov/`
- **Use Case**: 19th- and early 20th-century expedition records, high-resolution historic maps, and architectural photographs.
- **Rules**:
  - Query JSON endpoints (`https://www.loc.gov/photos/?q={query}&fo=json`).
  - Filter for items marked "No known restrictions on publication".

### 4. Smithsonian Open Access API
- **Endpoint**: `https://api.si.edu/openaccess/api/v1.0/`
- **Use Case**: Authentic artifacts from 20+ Smithsonian museums, anthropology collections, and geological surveys.
- **Rules**:
  - Filter search requests with `online_media_type=Images` and `rows=20`.
  - Only download assets confirmed under the CC0 designation.

### 5. Openverse API
- **Endpoint**: `https://api.openverse.org/v1/images/`
- **Use Case**: Broad Creative Commons search across global libraries and open collections.
- **Rules**:
  - Filter strictly with `license_type=commercial` to exclude Non-Commercial (NC) and No-Derivatives (ND) media.

## Asset Ingestion Pipeline

1. **Query Formulation**: Convert storyboard visual descriptions into targeted keyword queries (e.g., *"Antikythera gear excavation"*, *"18th century Aegean sea map"*).
2. **Metadata Inspection**: Check license, author, and resolution before downloading.
3. **Ingestion**: Save downloaded assets into `media-library/images/<project-slug>/raw/`.
4. **Licensing Registration**: Immediately register the asset in the project's licensing manifest.
