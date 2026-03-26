# Kyron Medical Applied Software Round - Deliverable 1

## Dataset: Orthopedic Surgery Practices in the United States

### Summary

This dataset contains **12,183 orthopedic surgery practices** across **57 US states and territories**, collected programmatically from the NPPES NPI Registry API (National Plan and Provider Enumeration System), maintained by the Centers for Medicare & Medicaid Services (CMS).

Every row has a practice name, phone number, and full location. Additional metadata includes taxonomy classification, NPI number, authorized official information, and estimated physician counts where available.

---

### Data Source

**NPPES NPI Registry** (https://npiregistry.cms.hhs.gov)

This is the official CMS database of every healthcare provider in the United States. It is explicitly public, free to access, requires no API key, and is intended for data dissemination per CMS guidelines. The API endpoint used is `https://npiregistry.cms.hhs.gov/api/?version=2.1`.

### Approach

The task was approached as a software engineering problem, not manual research.

**Tool:** A Python script (`scrape_ortho_practices.py`) was built to systematically query the NPPES API across all 56 US states and territories, using 8 orthopedic surgery taxonomy descriptions. The script handles pagination (the API returns max 200 results per call, up to 1200 per query combination), deduplication by NPI number, rate limiting, and has built-in resume support via a progress file.

**Phase 1 - Organization collection:** Queried the API for Type 2 (Organization) NPIs, which represent practices, clinics, and medical groups rather than individual physicians. Each of the 8 taxonomy descriptions was searched against each of the 56 states/territories.

**Phase 2 - Physician count enrichment:** Queried Type 1 (Individual) NPIs for the general "Orthopaedic Surgery" taxonomy, grouped by practice address, and used that to estimate how many orthopedic surgeons work at each practice location.

**Phase 3 - Export:** Filtered for active practices with valid phone numbers, formatted phone numbers, and exported to both CSV and Excel.

### Taxonomy Descriptions Searched

The NPPES API's `taxonomy_description` parameter was used with the following values, which correspond to NUCC Healthcare Provider Taxonomy classifications:

| Description | Taxonomy Code |
|---|---|
| Orthopaedic Surgery | 207X00000X |
| Adult Reconstructive Orthopaedic Surgery | 207XS0114X |
| Foot and Ankle Surgery | 207XX0004X |
| Hand Surgery | 207XS0106X |
| Orthopaedic Surgery of the Spine | 207XS0117X |
| Orthopaedic Trauma | 207XX0801X |
| Pediatric Orthopaedic Surgery | 207XP3100X |
| Sports Medicine | 207XX0005X |

Note: The API matches these against any taxonomy listed for an organization, not just the primary taxonomy. This means the dataset includes multi-specialty practices that have orthopedic surgery as one of their services, which is desirable since these practices still handle orthopedic scheduling calls.

### Output Schema

| Column | Description | Fill Rate |
|---|---|---|
| practice_name | Organization name as registered with CMS | 100% |
| phone | Main phone number, formatted (XXX) XXX-XXXX | 100% |
| fax | Fax number | 68% |
| address_line_1 | Street address | 100% |
| address_line_2 | Suite, floor, etc. | 31% |
| city | City | 100% |
| state | State abbreviation | 100% |
| zip_code | ZIP code (9-digit) | 100% |
| primary_taxonomy | Primary specialty description | 100% |
| taxonomy_code | NUCC taxonomy code for primary specialty | 100% |
| estimated_physician_count | Estimated ortho surgeons at this address | 100% (17.7% non-zero) |
| physician_names_sample | Sample of individual ortho surgeon names at address | 17.7% |
| npi | National Provider Identifier (unique) | 100% |
| enumeration_type | NPI-2 (Organization) | 100% |
| enumeration_date | Date NPI was first issued | 100% |
| last_updated | Date record was last updated | 100% |
| authorized_official_name | Practice admin/owner name | 100% |
| authorized_official_title | Title of authorized official | 100% |
| all_taxonomies | All taxonomy descriptions for this NPI | 100% |
| country | Country | 100% |

### Coverage by State (Top 15)

| State | Practices |
|---|---|
| FL | 807 |
| CA | 769 |
| TX | 630 |
| NY | 527 |
| NJ | 485 |
| AZ | 435 |
| PA | 423 |
| MI | 403 |
| NC | 388 |
| CO | 379 |
| OH | 370 |
| IL | 359 |
| GA | 351 |
| MA | 333 |
| TN | 309 |

### How to Reproduce

```bash
pip install requests pandas openpyxl
python scrape_ortho_practices_v2.py
```

The script includes a connectivity test at startup, saves progress to `progress_v2.json` (so it can resume if interrupted), and outputs to the `output/` directory.

### Ethical Considerations

- NPPES data is explicitly designated as public information by CMS and intended for dissemination
- The API is free and does not require authentication
- Rate limiting (0.3s between calls) was implemented to avoid overloading the server
- No scraping of sites that prohibit it; no terms of service were violated
- No personal health information was collected (NPI records contain only provider/organization information, not patient data)

### Technical Decisions and Tradeoffs

- **Why NPPES over web scraping:** NPPES is the authoritative source for US healthcare provider data. It's structured, complete, and legal. Alternatives like scraping Healthgrades or Google Maps would require more engineering effort, run into ToS issues, and produce messier data.
- **Why organizations (NPI-2) not individuals (NPI-1):** The task asks for "practices," which are organizations. Individual surgeon records don't have a practice phone number in the same way. NPI-2 records give us the practice-level view with the main phone line, which is what's needed for Step 2 (calling).
- **Why multiple taxonomy descriptions instead of just a wildcard:** Using specific taxonomy text ensures precise matches. A wildcard like "Orthopaedic*" could work but might miss "Sports Medicine" practices that don't have "Orthopaedic" in their description.
- **Physician count limitations:** The estimated_physician_count field is based on how many individual NPI-1 ortho surgeons share the same street address as the practice. This is an approximation since the API caps results at 1200 per query, so large states may be undercounted. For a production system, the NPPES bulk download file (~8GB CSV) would give exact counts.

### Files

- `orthopedic_practices_dataset.csv` - Main dataset (active practices with valid phone numbers)
- `orthopedic_practices_dataset.xlsx` - Same data, formatted Excel workbook with filters
- `scrape_ortho_practices_v2.py` - The collection script
