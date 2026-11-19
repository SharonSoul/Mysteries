---
name: licensing-verification
description: Audit and verify commercial reusability, copyright status, and attribution requirements for visual and audio media used in documentaries. Use when clearing assets for production, rejecting incompatible licenses (e.g. NC, ND), compiling asset licensing reports, and ensuring YouTube copyright safety.
license: MIT
metadata: {"scope": "licensing-records", "mandatory_fields": 10}
---

# Licensing Verification

This skill enforces strict copyright compliance, commercial usability verification, and attribution tracking for all assets used in the studio.

## Non-Negotiable Clearance Rules

1. **Automatic Approval Categories**:
   - **Public Domain**: Published before January 1, 1929; works of the US Federal Government (17 U.S.C. § 105); expired term.
   - **CC0 (Creative Commons Zero)**: Dedicated to the public domain without conditions.
   - **CC BY**: Requires proper attribution string in the video description or end credits.
   - **Pixabay Content License**: Permitted for commercial YouTube video without attribution (attribution encouraged).
2. **Conditional Review**:
   - **CC BY-SA (ShareAlike)**: Permitted only with explicit review to ensure the channel's derivative terms are satisfied.
3. **Strictly Prohibited Categories**:
   - **CC BY-NC / CC BY-NC-SA**: Prohibits commercial exploitation (monetized YouTube channels).
   - **CC BY-ND / CC BY-NC-ND**: Prohibits derivative works, editing, resizing, or cropping.
   - **Unknown / Unverified**: Never assume an image is reusable simply because it is accessible on Google, Pinterest, or YouTube.

## The 10 Mandatory Asset Record Fields

Every downloaded and ingested media asset MUST have a corresponding record containing:

1. **File Name**: Local filename on disk.
2. **Asset Title**: Original descriptive title.
3. **Creator / Author**: Photographer, artist, or creating institution.
4. **Original URL**: Direct link to the asset catalog entry.
5. **Source Repository**: Name of the archive (e.g., Wikimedia Commons, LOC, Smithsonian).
6. **License**: Exact license name (e.g., `Public Domain`, `CC0`, `CC BY 4.0`).
7. **License URL**: Direct link to the official legal code or license terms.
8. **Download Date**: ISO timestamp (`YYYY-MM-DD`).
9. **Intended Scene**: Scene ID in the storyboard (e.g., `scene_03`).
10. **Attribution Requirements**: Exact formatted citation required in the YouTube description.

## Licensing Audit Report

All project assets must be compiled into `licensing-records/<project-slug>_licensing_record.md`:

```markdown
# Asset Licensing Report: [Project Title]

| File Name | Asset Title | Creator | Source | License | Intended Scene | Attribution Text |
|---|---|---|---|---|---|---|
| gear_fragment.jpg | Antikythera Fragment A | Marsyas | Wikimedia Commons | CC BY-SA 3.0 | scene_02 | "Photo by Marsyas via Wikimedia Commons (CC BY-SA 3.0)" |
| athens_map_1890.jpg | Map of Attica and Islands | Kiepert, H. | Library of Congress | Public Domain | scene_04 | "Public Domain, Library of Congress" |
```
