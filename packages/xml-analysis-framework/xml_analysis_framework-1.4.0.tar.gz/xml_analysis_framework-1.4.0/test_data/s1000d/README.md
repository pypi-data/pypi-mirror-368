# S1000D Test Data

This directory contains real S1000D technical documentation files for testing the S1000D handler.

## File Organization

### Procedures (DA1*251A*, DA2*520A*)
- **DMC-BRAKE-AAA-DA1-10-00-00AA-251A-A_003-00_EN-US.XML** - Brake system procedure
- **DMC-S1000DBIKE-AAA-DA1-10-00-00AA-251A-A_009-00_EN-US.XML** - Bike system procedure  
- **DMC-S1000DBIKE-AAA-DA2-10-00-00AA-520A-A_010-00_EN-US.XML** - DA2 system procedure
- **DMC-S1000DBIKE-AAA-DA2-20-00-00AA-520A-A_010-00_EN-US.XML** - DA2 system procedure  
- **DMC-S1000DBIKE-AAA-DA2-30-00-00AA-520A-A_010-00_EN-US.XML** - DA2 system procedure

### Descriptions (*041A*, *341A*)
- **DMC-BRAKE-AAA-DA1-00-00-00AA-041A-A_003-00_EN-US.XML** - Brake system description
- **DMC-BRAKE-AAA-DA1-00-00-00AA-341A-A_003-00_EN-US.XML** - Brake system description  
- **DMC-S1000DBIKE-AAA-D00-00-00-00AA-041A-A_011-00_EN-US.XML** - Bike system description
- **DMC-S1000DBIKE-AAA-D00-00-01-00AA-341A-A_003-00_EN-US.XML** - Bike system description
- **DMC-S1000DBIKE-AAA-DA0-00-00-00AA-041A-A_010-00_EN-US.XML** - DA0 system description
- **DMC-S1000DBIKE-AAA-DA1-00-00-00AA-041A-A_009-00_EN-US.XML** - DA1 system description
- **DMC-S1000DBIKE-AAA-DA1-00-00-00AA-341A-A_009-00_EN-US.XML** - DA1 system description
- **DMC-S1000DBIKE-AAA-DA2-00-00-00AA-041A-A_010-00_EN-US.XML** - DA2 system description
- **DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-341A-A_009-00_EN-US.XML** - Lighting system description

### Equipment Lists (*056A*)
- **DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-056A-A_010-00_EN-US.XML** - Lighting equipment list

## S1000D Information Code Meanings

- **041A** - Description/Descriptive information
- **056A** - Maintenance support equipment list  
- **251A** - Maintenance procedures
- **341A** - Description/Illustrated parts breakdown
- **520A** - Operational procedures

## Data Module Code (DMC) Structure

DMC format: `DMC-{modelIdentCode}-{systemDiffCode}-{systemCode}-{subSystemCode}-{subSubSystemCode}-{assyCode}-{disassyCode}-{disassyCodeVariant}-{infoCode}-{infoCodeVariant}-{itemLocationCode}_{issueNumber}-{inWork}_{languageIsoCode}-{countryIsoCode}.XML`

Examples:
- **BRAKE** - Brake system model
- **S1000DBIKE** - S1000D Bike demonstration model  
- **S1000DLIGHTING** - S1000D Lighting system model
- **DA0/DA1/DA2** - Different data assembly codes

## Usage

These files can be used to test:
1. S1000D document type detection
2. DMC code parsing and analysis
3. Cross-reference extraction
4. Procedural step analysis
5. Parts and equipment list processing
6. Safety information extraction
7. Chunking strategies for RAG applications

## Source

Files sourced from: `/Users/wjackson/developer/AI-test-data/xml/bike_dataset/S1000D Issue 5.0/Bike Data Set for Release number 5.0/`

This is the official S1000D demonstration dataset provided by the S1000D consortium.