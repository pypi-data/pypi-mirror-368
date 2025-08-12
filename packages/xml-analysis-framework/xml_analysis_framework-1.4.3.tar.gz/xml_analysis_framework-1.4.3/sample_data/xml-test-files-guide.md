# XML Test Files Collection Guide

## Overview
This guide lists all XML document types needed for testing the XML Analysis Framework, along with suggested searches to find real-world examples.

## ✅ Currently Implemented Handlers

### 1. SCAP Security Reports
**File Types**: `.xml` (usually large, 10-100MB)
**Search Queries**:
- `"asset-report-collection" filetype:xml site:github.com`
- `SCAP XCCDF benchmark filetype:xml`
- `"scap.nist.gov/schema" filetype:xml`
- `STIG SCAP results filetype:xml`

**Good Sources**:
- NIST National Checklist Program Repository
- DoD Cyber Exchange (public STIG benchmarks)
- GitHub repos with "scap" or "openscap" topics

### 2. RSS/Atom Feeds
**File Types**: `.xml`, `.rss`, `.atom`
**Search Queries**:
- `"rss version=" filetype:xml -site:w3.org`
- `atom feed example filetype:xml`
- `podcast RSS feed filetype:xml`
- `news RSS feed example github`

**Good Sources**:
- Major news sites (append `/rss` to URLs)
- Podcast platforms
- Blog platforms (WordPress, Medium exports)

### 3. Maven POM Files
**File Types**: `pom.xml`
**Search Queries**:
- `pom.xml site:github.com`
- `"modelVersion>4.0.0" filetype:xml`
- `maven project pom.xml example`
- `spring boot pom.xml site:github.com`

**Good Sources**:
- Any Java project on GitHub
- Maven Central examples
- Spring Initializr generated projects

### 4. Log4j Configuration
**File Types**: `log4j.xml`, `log4j2.xml`
**Search Queries**:
- `log4j2.xml site:github.com`
- `"Configuration status=" filetype:xml log4j`
- `log4j.xml example configuration`
- `"<Appenders>" "<Loggers>" filetype:xml`

**Good Sources**:
- Java projects on GitHub
- Apache Log4j documentation
- Enterprise Java application repos

### 5. Spring Configuration
**File Types**: `applicationContext.xml`, `*-context.xml`, `beans.xml`
**Search Queries**:
- `applicationContext.xml site:github.com`
- `"springframework.org/schema/beans" filetype:xml`
- `spring beans.xml example`
- `"<bean id=" class=" filetype:xml`

**Good Sources**:
- Legacy Spring projects
- Spring documentation archives
- Enterprise Java applications

### 6. DocBook Documentation
**File Types**: `.xml`, `.docbook`
**Search Queries**:
- `"<book xmlns" docbook filetype:xml`
- `"<chapter>" "<section>" docbook filetype:xml`
- `docbook 5.0 example filetype:xml`
- `technical documentation docbook github`

**Good Sources**:
- Open source documentation projects
- O'Reilly book sources
- Technical manual repositories

### 7. SVG Graphics
**File Types**: `.svg`
**Search Queries**:
- `"<svg" "viewBox" filetype:svg`
- `icon svg site:github.com`
- `"sodipodi" inkscape filetype:svg` (Inkscape files)
- `animated svg example`

**Good Sources**:
- Icon libraries (Font Awesome, Feather)
- Wikimedia Commons
- Design tool exports

### 8. XML Sitemaps
**File Types**: `sitemap.xml`, `sitemap_index.xml`
**Search Queries**:
- `sitemap.xml -site:sitemaps.org`
- `"<urlset" "sitemaps.org/schemas" filetype:xml`
- `sitemap_index.xml example`
- `"<loc>" "<lastmod>" filetype:xml`

**Good Sources**:
- Any website's `/sitemap.xml`
- WordPress sites
- E-commerce platforms

## 📋 Planned Handlers (Need Test Files)

### 9. WSDL (Web Services Description Language)
**File Types**: `.wsdl`, `.xml`
**Search Queries**:
- `"definitions" "xmlns:wsdl" filetype:wsdl`
- `SOAP WSDL example filetype:xml`
- `"<wsdl:portType" filetype:xml`
- `web service WSDL site:github.com`

**Good Sources**:
- Public web service directories
- Government service endpoints
- Legacy enterprise integrations

### 10. XSD (XML Schema Definition)
**File Types**: `.xsd`
**Search Queries**:
- `"<xs:schema" filetype:xsd`
- `"<xsd:complexType" filetype:xsd`
- `XML schema example site:github.com`
- `"targetNamespace" schema filetype:xsd`

**Good Sources**:
- W3C specifications
- Industry standard schemas
- API documentation

### 11. KML/KMZ (Geographic Data)
**File Types**: `.kml`, `.kmz`
**Search Queries**:
- `"<kml xmlns" filetype:kml`
- `Google Earth KML example`
- `"<Placemark>" coordinates filetype:kml`
- `GPS track KML site:github.com`

**Good Sources**:
- Google Earth community
- GIS data repositories
- GPS tracking apps exports

### 12. GPX (GPS Exchange)
**File Types**: `.gpx`
**Search Queries**:
- `"<gpx version" filetype:gpx`
- `GPS track GPX example`
- `Strava GPX export site:github.com`
- `hiking trail GPX file`

**Good Sources**:
- Outdoor activity platforms
- GPS device manufacturers
- OpenStreetMap exports

### 13. Ant/NAnt Build Files
**File Types**: `build.xml`
**Search Queries**:
- `build.xml ant project site:github.com`
- `"<project name=" default=" filetype:xml ant`
- `"<target name=" depends=" filetype:xml`
- `Apache Ant build.xml example`

**Good Sources**:
- Legacy Java projects
- Apache project archives
- Enterprise build systems

### 14. NuGet Package Specs
**File Types**: `.nuspec`
**Search Queries**:
- `"<package xmlns" filetype:nuspec`
- `nuspec example site:github.com`
- `"<metadata>" "<id>" nuget filetype:xml`
- `.nuspec file example`

**Good Sources**:
- .NET projects on GitHub
- NuGet.org package sources
- Visual Studio templates

### 15. WADL (Web Application Description Language)
**File Types**: `.wadl`
**Search Queries**:
- `"<application xmlns" wadl filetype:xml`
- `REST API WADL example`
- `"<resources base=" filetype:wadl`
- `Jersey WADL site:github.com`

**Good Sources**:
- Java REST services
- API documentation
- Jersey/JAX-RS projects

### 16. RelaxNG Schemas
**File Types**: `.rng`, `.rnc`
**Search Queries**:
- `"<grammar" relaxng filetype:rng`
- `RelaxNG schema example`
- `"datatypeLibrary" filetype:rng`
- `compact syntax .rnc file`

**Good Sources**:
- XML validation projects
- DocBook schemas
- TEI schemas

### 17. DITA (Darwin Information Typing Architecture)
**File Types**: `.dita`, `.ditamap`
**Search Queries**:
- `"<topic" dita filetype:xml`
- `"<map>" ditamap filetype:xml`
- `DITA documentation example`
- `"<!DOCTYPE topic" filetype:dita`

**Good Sources**:
- Technical documentation repos
- DITA Open Toolkit
- IBM documentation

### 18. TEI (Text Encoding Initiative)
**File Types**: `.xml`
**Search Queries**:
- `"<TEI xmlns" filetype:xml`
- `"tei-c.org" manuscript filetype:xml`
- `digital humanities TEI XML`
- `"<teiHeader>" filetype:xml`

**Good Sources**:
- Digital humanities projects
- University libraries
- Historical text projects

### 19. HL7 CDA (Clinical Document Architecture)
**File Types**: `.xml`
**Search Queries**:
- `"ClinicalDocument" HL7 filetype:xml`
- `"urn:hl7-org:v3" filetype:xml`
- `CDA R2 example document`
- `"<typeId root=" HL7 filetype:xml`

**Good Sources**:
- HL7 example repository
- Healthcare IT projects
- EHR vendor documentation

### 20. XBRL (Business Reporting)
**File Types**: `.xbrl`, `.xml`
**Search Queries**:
- `"<xbrl" financial filetype:xml`
- `XBRL instance document example`
- `"xbrl.org" context filetype:xml`
- `SEC XBRL filing example`

**Good Sources**:
- SEC EDGAR database
- XBRL.org examples
- Financial reporting tools

### 21. PMML (Predictive Models)
**File Types**: `.pmml`
**Search Queries**:
- `"<PMML" version filetype:pmml`
- `"DataDictionary" model filetype:xml`
- `machine learning PMML example`
- `"<RegressionModel" filetype:xml`

**Good Sources**:
- Data science projects
- ML model repositories
- PMML.org examples

### 22. XSLT (Transformations)
**File Types**: `.xsl`, `.xslt`
**Search Queries**:
- `"<xsl:stylesheet" filetype:xsl`
- `XSLT transformation example`
- `"<xsl:template match=" filetype:xsl`
- `XML to HTML XSLT site:github.com`

**Good Sources**:
- XML processing projects
- Documentation generators
- Web development repos

### 23. XSL-FO (Formatting Objects)
**File Types**: `.fo`, `.xml`
**Search Queries**:
- `"<fo:root" filetype:xml`
- `XSL-FO example PDF generation`
- `"fo:page-sequence" filetype:xml`
- `Apache FOP examples`

**Good Sources**:
- Apache FOP examples
- PDF generation projects
- Publishing workflows

## 🔍 General Search Tips

### GitHub Advanced Search
Use GitHub's advanced search with:
- `extension:xml path:/test`
- `extension:xml path:/sample`
- `extension:xml path:/example`
- `language:XML size:>1000`

### Google Dorks
- Add `-inurl:w3.org` to exclude specifications
- Use `site:raw.githubusercontent.com` for direct file access
- Add `"<?xml version"` to ensure valid XML
- Use date filters for recent examples

### File Size Considerations
- **Small files** (<100KB): Good for unit tests
- **Medium files** (100KB-10MB): Good for performance testing
- **Large files** (>10MB): Good for stress testing
- **Various encodings**: UTF-8, UTF-16, ISO-8859-1

## 📁 Recommended Test Set Structure

```
test_files/
├── small/          # <100KB files
│   ├── pom/
│   ├── rss/
│   ├── config/
│   └── ...
├── medium/         # 100KB-10MB files
│   ├── scap/
│   ├── docbook/
│   └── ...
├── large/          # >10MB files
│   ├── scap/
│   ├── xbrl/
│   └── ...
├── edge_cases/     # Malformed, unusual encodings, etc.
│   ├── malformed/
│   ├── encodings/
│   └── deeply_nested/
└── real_world/     # Actual production files
    ├── enterprise/
    ├── open_source/
    └── government/
```

## ⚠️ Legal Considerations

When collecting test files:
1. **Check licenses** - Ensure files are publicly available
2. **Remove sensitive data** - PII, credentials, internal URLs
3. **Attribute sources** - Keep track of where files came from
4. **Respect robots.txt** - When scraping websites
5. **Use synthetic data** - Generate files for sensitive domains (healthcare, finance)

## 🛠️ Test File Validation

After collecting files, validate them:
```bash
# Check if valid XML
xmllint --noout file.xml

# Check file size
ls -lh file.xml

# Check encoding
file -i file.xml

# Count elements (rough complexity check)
grep -c "<" file.xml
```

## 📊 Coverage Goals

Aim for at least:
- **3-5 examples** per handler
- **Different sizes** (small, medium, large)
- **Different versions** (where applicable)
- **Valid and invalid** examples
- **Real-world complexity** (not just tutorials)

---

This collection guide ensures comprehensive testing coverage for all current and planned XML document types in the framework.