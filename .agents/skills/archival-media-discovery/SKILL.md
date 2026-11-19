---
name: archival-media-discovery
description: Search, discover, rights-verify, and catalogue legally reusable historical imagery, maps, archival footage, and museum artifacts from Wikimedia Commons, Library of Congress, Smithsonian Open Access, Openverse, and public domain archives. Use when sourcing visual assets for documentaries, verifying copyright status, and generating licensing records.
license: MIT
metadata: {"archives": ["wikimedia_commons", "loc_gov", "smithsonian_open_access", "openverse", "nasa"], "license_types": ["public_domain", "cc0", "cc_by"]}
---

# Archival Media Discovery & Licensing Verification

This skill guides the discovery, rights clearance, download, and systematic logging of public domain and Creative Commons visual assets for historical documentaries.

## Legal Hierarchy for Commercial YouTube Production

To protect the channel from copyright strikes, demonetization, or takedowns:

| Priority | License Status | Reusability | Conditions / Attribution |
|---|---|---|---|
| **Tier 1** | **Public Domain (Pre-1929)** | 100% Safe | Works published before January 1, 1929 are in the US public domain. No permission or fee required. Good practice to cite creator. |
| **Tier 1** | **US Government Work** | 100% Safe | Works created by US federal government officers/employees as part of official duties (NASA, Library of Congress, USGS, NOAA) under 17 U.S.C. § 105. |
| **Tier 1** | **CC0 (Public Domain Dedication)** | 100% Safe | Waived all rights globally (e.g., Smithsonian Open Access, Met Open Access). |
| **Tier 2** | **CC BY (Attribution)** | Safe | Permitted for commercial YouTube video with explicit credit in description or end credits (Author, License, Link). |
| **Tier 2** | **CC BY-SA (ShareAlike)** | Conditionally Safe | Permitted, but may require sharing the derived video under ShareAlike. Use with caution or prefer pure CC BY. |
| **AVOID** | **CC BY-NC / CC BY-ND** | **STRICTLY PROHIBITED** | "NC" (Non-Commercial) prohibits monetized YouTube channels. "ND" (No Derivatives) prohibits video editing/remixing. |
| **AVOID** | **Unspecified / "Copyright Free"** | **STRICTLY PROHIBITED** | Never trust YouTube channels or blogs claiming footage is "copyright free" without verified license terms. |

## Approved Digital Archives & Retrieval Methods

### 1. Wikimedia Commons
The primary repository for historical photos, museum scans, and engravings.
- **API Endpoint**: `https://commons.wikimedia.org/w/api.php`
- **Query Strategy**: Search for artifact names, historical excavations, and 19th-century photographic surveys.
- **Verification**: Inspect the file page for copyright tags:
  - `{{PD-old-100}}` / `{{PD-1923}}` / `{{PD-US-expired}}`: Verified public domain.
  - `{{Cc-by-4.0}}` / `{{Cc-by-3.0}}`: Requires attribution.

### 2. Library of Congress (LOC.gov)
Vast digital repository of historical American and global prints, photographs, maps, and manuscripts.
- **Search URL**: `https://www.loc.gov/photos/?q=[query]&fo=json`
- **Rights Advisory**: Check the "Rights Advisory" section on the catalog page. Filter search with `"No known restrictions on publication"`.

### 3. Smithsonian Open Access
Over 4.5 million 2D and 3D digital collection records licensed under CC0.
- **Search URL**: `https://www.si.edu/openaccess`
- **API**: Open Access API allows querying CC0-designated high-resolution images across 20+ Smithsonian museums.

### 4. Openverse (Formerly Creative Commons Search)
Indexes over 700 million openly licensed images and audio.
- **API Endpoint**: `https://api.openverse.engineering/v1/images/?q=[query]&license_type=commercial`
- **Rule**: Always filter by `license_type=commercial` to exclude Non-Commercial (NC) assets.

### 5. NASA Image and Video Library
Public domain imagery and video for science, archaeology via satellite, cosmology, and planetary mysteries.
- **API Endpoint**: `https://images-api.nasa.gov/search?q=[query]&media_type=image,video`

## Asset Organization & Directory Structure

Store downloaded assets in the studio directory tree:
```
media-library/
├── images/
│   └── <project-slug>/
│       ├── raw/          # Original downloaded files
│       └── processed/    # Scaled, color-corrected, or cropped for video
├── videos/
│   └── <project-slug>/
```

## Mandatory Licensing Records Ledger

For every documentary, compile a comprehensive record saved in:
`licensing-records/<project-slug>_licensing_record.md`

```markdown
# Licensing Record: [Documentary Title]
**Project Slug**: antikythera-mechanism
**Date Created**: 2026-11-19
**Verification Agent**: Archival Media Discovery

| Asset ID | Local Filename | Source Repository | Direct Source URL | Original Author / Creator | Date of Creation | License Status | Required Attribution String |
|---|---|---|---|---|---|---|---|
| IMG_01 | antikythera_gear_fragment.jpg | Wikimedia Commons | https://commons.wikimedia.org/wiki/File:Antikythera_fragment_A.jpg | National Archaeological Museum, Athens (Photo: Marsyas) | 1902 / Photo 2005 | CC BY-SA 3.0 | "Photo by Marsyas via Wikimedia Commons (CC BY-SA 3.0)" |
| IMG_02 | greece_map_1880.png | Library of Congress | https://www.loc.gov/item/2007627495/ | Johnston, W. & A.K. | 1880 | Public Domain | "Public Domain, Library of Congress Geography and Map Division" |
```
