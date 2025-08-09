"""
Country-Specific Configuration Data

Comprehensive database of country-specific validation rules, formats,
and regulatory requirements for international ID validation support.

Features:
- ISO 3166-1 country codes and metadata
- Country-specific ID format variations
- Phone number country codes and prefixes
- Postal code format patterns
- Currency and locale information
- Regulatory framework mappings
- Regional validation rule variations

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Configure logging
logger = logging.getLogger('pyidverify.config.countries')


class Region(Enum):
    """Geographic regions for grouping countries."""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"
    CARIBBEAN = "caribbean"
    MIDDLE_EAST = "middle_east"


class RegulatoryFramework(Enum):
    """Regulatory frameworks applicable to countries."""
    GDPR = "gdpr"                    # General Data Protection Regulation (EU)
    CCPA = "ccpa"                    # California Consumer Privacy Act (US)
    PIPEDA = "pipeda"                # Personal Information Protection (Canada)
    DPA = "dpa"                      # Data Protection Act (UK)
    LGPD = "lgpd"                    # Lei Geral de Proteção de Dados (Brazil)
    PDPA_SG = "pdpa_singapore"       # Personal Data Protection Act (Singapore)
    PDPA_TH = "pdpa_thailand"        # Personal Data Protection Act (Thailand)
    APPs = "apps"                    # Australian Privacy Principles (Australia)


@dataclass
class PhoneNumberInfo:
    """Phone number information for a country."""
    country_code: str
    trunk_prefix: Optional[str] = None
    area_code_length: Optional[int] = None
    subscriber_number_length: Optional[int] = None
    mobile_prefixes: List[str] = field(default_factory=list)
    landline_prefixes: List[str] = field(default_factory=list)
    emergency_numbers: List[str] = field(default_factory=list)
    format_patterns: List[str] = field(default_factory=list)


@dataclass
class PostalCodeInfo:
    """Postal code information for a country."""
    format_pattern: Optional[str] = None
    length: Optional[int] = None
    example: Optional[str] = None
    case_sensitive: bool = False
    alphanumeric: bool = False


@dataclass
class IDFormatInfo:
    """ID format information for a country."""
    id_type: str
    pattern: Optional[str] = None
    length: Optional[int] = None
    check_digit_algorithm: Optional[str] = None
    example: Optional[str] = None
    description: Optional[str] = None
    required_for_citizens: bool = False
    expiration_period_years: Optional[int] = None


@dataclass
class CountryInfo:
    """Comprehensive country information."""
    
    # Basic country identification
    iso_alpha2: str
    iso_alpha3: str
    iso_numeric: str
    name: str
    official_name: str
    
    # Geographic and cultural info
    region: Region
    subregion: Optional[str] = None
    capital: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    currency_code: Optional[str] = None
    timezone: Optional[str] = None
    
    # Phone number information
    phone_info: Optional[PhoneNumberInfo] = None
    
    # Postal code information
    postal_code_info: Optional[PostalCodeInfo] = None
    
    # ID format information
    supported_id_types: List[IDFormatInfo] = field(default_factory=list)
    
    # Regulatory frameworks
    regulatory_frameworks: Set[RegulatoryFramework] = field(default_factory=set)
    
    # Additional metadata
    gdpr_applicable: bool = False
    high_risk_country: bool = False
    sanctions_applicable: bool = False
    data_localization_required: bool = False
    
    # Validation settings
    strict_validation_required: bool = False
    enhanced_security_required: bool = False
    audit_logging_required: bool = False


class CountryDatabase:
    """
    Comprehensive database of country-specific information.
    """
    
    def __init__(self):
        """Initialize country database."""
        self.countries: Dict[str, CountryInfo] = {}
        self.countries_by_alpha3: Dict[str, CountryInfo] = {}
        self.countries_by_numeric: Dict[str, CountryInfo] = {}
        self.countries_by_phone_code: Dict[str, List[CountryInfo]] = {}
        
        self._load_country_data()
    
    def _load_country_data(self) -> None:
        """Load comprehensive country data."""
        
        # North America
        self.add_country(CountryInfo(
            iso_alpha2="US",
            iso_alpha3="USA",
            iso_numeric="840",
            name="United States",
            official_name="United States of America",
            region=Region.NORTH_AMERICA,
            subregion="Northern America",
            capital="Washington, D.C.",
            languages=["en"],
            currency_code="USD",
            timezone="UTC-5 to UTC-10",
            phone_info=PhoneNumberInfo(
                country_code="1",
                trunk_prefix="1",
                area_code_length=3,
                subscriber_number_length=7,
                mobile_prefixes=["2", "3", "4", "5", "6", "7", "8", "9"],
                landline_prefixes=["2", "3", "4", "5", "6", "7", "8", "9"],
                emergency_numbers=["911"],
                format_patterns=[
                    "+1 (###) ###-####",
                    "1-###-###-####",
                    "###-###-####"
                ]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^\d{5}(-\d{4})?$',
                length=5,
                example="12345",
                alphanumeric=False
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="ssn",
                    pattern=r'^(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}$',
                    length=9,
                    example="123-45-6789",
                    description="Social Security Number",
                    required_for_citizens=True
                ),
                IDFormatInfo(
                    id_type="passport",
                    pattern=r'^\d{9}$',
                    length=9,
                    example="123456789",
                    description="US Passport Number",
                    expiration_period_years=10
                ),
                IDFormatInfo(
                    id_type="drivers_license",
                    description="State-specific driver's license formats",
                    required_for_citizens=False,
                    expiration_period_years=5
                )
            ],
            regulatory_frameworks={RegulatoryFramework.CCPA},
            strict_validation_required=True,
            enhanced_security_required=True,
            audit_logging_required=True
        ))
        
        self.add_country(CountryInfo(
            iso_alpha2="CA",
            iso_alpha3="CAN",
            iso_numeric="124",
            name="Canada",
            official_name="Canada",
            region=Region.NORTH_AMERICA,
            subregion="Northern America",
            capital="Ottawa",
            languages=["en", "fr"],
            currency_code="CAD",
            timezone="UTC-3.5 to UTC-8",
            phone_info=PhoneNumberInfo(
                country_code="1",
                trunk_prefix="1",
                area_code_length=3,
                subscriber_number_length=7,
                emergency_numbers=["911"],
                format_patterns=[
                    "+1 (###) ###-####",
                    "1-###-###-####"
                ]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^[A-Z]\d[A-Z] \d[A-Z]\d$',
                length=7,
                example="K1A 0A6",
                case_sensitive=False,
                alphanumeric=True
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="sin",
                    pattern=r'^\d{3}-\d{3}-\d{3}$',
                    length=9,
                    check_digit_algorithm="luhn",
                    example="123-456-782",
                    description="Social Insurance Number",
                    required_for_citizens=True
                ),
                IDFormatInfo(
                    id_type="passport",
                    pattern=r'^[A-Z]{2}\d{6}$',
                    length=8,
                    example="AB123456",
                    description="Canadian Passport Number",
                    expiration_period_years=10
                )
            ],
            regulatory_frameworks={RegulatoryFramework.PIPEDA}
        ))
        
        # United Kingdom
        self.add_country(CountryInfo(
            iso_alpha2="GB",
            iso_alpha3="GBR",
            iso_numeric="826",
            name="United Kingdom",
            official_name="United Kingdom of Great Britain and Northern Ireland",
            region=Region.EUROPE,
            subregion="Northern Europe",
            capital="London",
            languages=["en"],
            currency_code="GBP",
            timezone="UTC+0",
            phone_info=PhoneNumberInfo(
                country_code="44",
                trunk_prefix="0",
                emergency_numbers=["999", "112"],
                format_patterns=[
                    "+44 ### ### ####",
                    "0### ### ####"
                ]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$',
                example="SW1A 1AA",
                case_sensitive=False,
                alphanumeric=True
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="nino",
                    pattern=r'^[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z] \d{2} \d{2} \d{2} [A-D]$',
                    example="AB 12 34 56 C",
                    description="National Insurance Number",
                    required_for_citizens=True
                ),
                IDFormatInfo(
                    id_type="passport",
                    pattern=r'^\d{9}$',
                    length=9,
                    example="123456789",
                    description="UK Passport Number",
                    expiration_period_years=10
                )
            ],
            regulatory_frameworks={RegulatoryFramework.DPA},
            gdpr_applicable=False  # Post-Brexit
        ))
        
        # European Union countries with GDPR
        eu_countries = [
            ("DE", "DEU", "276", "Germany", "Federal Republic of Germany", "Berlin"),
            ("FR", "FRA", "250", "France", "French Republic", "Paris"),
            ("IT", "ITA", "380", "Italy", "Italian Republic", "Rome"),
            ("ES", "ESP", "724", "Spain", "Kingdom of Spain", "Madrid"),
            ("NL", "NLD", "528", "Netherlands", "Kingdom of the Netherlands", "Amsterdam"),
            ("BE", "BEL", "056", "Belgium", "Kingdom of Belgium", "Brussels"),
            ("AT", "AUT", "040", "Austria", "Republic of Austria", "Vienna"),
            ("SE", "SWE", "752", "Sweden", "Kingdom of Sweden", "Stockholm"),
            ("DK", "DNK", "208", "Denmark", "Kingdom of Denmark", "Copenhagen"),
            ("FI", "FIN", "246", "Finland", "Republic of Finland", "Helsinki"),
        ]
        
        for alpha2, alpha3, numeric, name, official_name, capital in eu_countries:
            self.add_country(CountryInfo(
                iso_alpha2=alpha2,
                iso_alpha3=alpha3,
                iso_numeric=numeric,
                name=name,
                official_name=official_name,
                region=Region.EUROPE,
                capital=capital,
                languages=["en"],  # Simplified - would need proper language data
                currency_code="EUR",
                timezone="UTC+1",
                phone_info=PhoneNumberInfo(
                    country_code="49" if alpha2 == "DE" else "33" if alpha2 == "FR" else "39" if alpha2 == "IT" else "34" if alpha2 == "ES" else "31",
                    emergency_numbers=["112"]
                ),
                regulatory_frameworks={RegulatoryFramework.GDPR},
                gdpr_applicable=True,
                strict_validation_required=True
            ))
        
        # Asia-Pacific countries
        self.add_country(CountryInfo(
            iso_alpha2="JP",
            iso_alpha3="JPN",
            iso_numeric="392",
            name="Japan",
            official_name="Japan",
            region=Region.ASIA,
            subregion="Eastern Asia",
            capital="Tokyo",
            languages=["ja"],
            currency_code="JPY",
            timezone="UTC+9",
            phone_info=PhoneNumberInfo(
                country_code="81",
                trunk_prefix="0",
                emergency_numbers=["110", "119"]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^\d{3}-\d{4}$',
                length=7,
                example="100-0001",
                alphanumeric=False
            ),
            enhanced_security_required=True
        ))
        
        self.add_country(CountryInfo(
            iso_alpha2="SG",
            iso_alpha3="SGP",
            iso_numeric="702",
            name="Singapore",
            official_name="Republic of Singapore",
            region=Region.ASIA,
            subregion="South-eastern Asia",
            capital="Singapore",
            languages=["en", "ms", "ta", "zh"],
            currency_code="SGD",
            timezone="UTC+8",
            phone_info=PhoneNumberInfo(
                country_code="65",
                emergency_numbers=["999", "995"]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^\d{6}$',
                length=6,
                example="018956",
                alphanumeric=False
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="nric",
                    pattern=r'^[STFG]\d{7}[A-Z]$',
                    length=9,
                    example="S1234567A",
                    description="National Registration Identity Card",
                    required_for_citizens=True
                )
            ],
            regulatory_frameworks={RegulatoryFramework.PDPA_SG},
            enhanced_security_required=True
        ))
        
        self.add_country(CountryInfo(
            iso_alpha2="AU",
            iso_alpha3="AUS",
            iso_numeric="036",
            name="Australia",
            official_name="Commonwealth of Australia",
            region=Region.OCEANIA,
            subregion="Australia and New Zealand",
            capital="Canberra",
            languages=["en"],
            currency_code="AUD",
            timezone="UTC+8 to UTC+11",
            phone_info=PhoneNumberInfo(
                country_code="61",
                trunk_prefix="0",
                emergency_numbers=["000", "112"]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^\d{4}$',
                length=4,
                example="2000",
                alphanumeric=False
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="tfn",
                    pattern=r'^\d{3} \d{3} \d{3}$',
                    length=9,
                    check_digit_algorithm="mod11",
                    example="123 456 782",
                    description="Tax File Number",
                    required_for_citizens=True
                )
            ],
            regulatory_frameworks={RegulatoryFramework.APPs}
        ))
        
        # Brazil
        self.add_country(CountryInfo(
            iso_alpha2="BR",
            iso_alpha3="BRA",
            iso_numeric="076",
            name="Brazil",
            official_name="Federative Republic of Brazil",
            region=Region.SOUTH_AMERICA,
            subregion="South America",
            capital="Brasília",
            languages=["pt"],
            currency_code="BRL",
            timezone="UTC-3 to UTC-5",
            phone_info=PhoneNumberInfo(
                country_code="55",
                trunk_prefix="0",
                emergency_numbers=["190", "193"]
            ),
            postal_code_info=PostalCodeInfo(
                format_pattern=r'^\d{5}-\d{3}$',
                length=8,
                example="01310-100",
                alphanumeric=False
            ),
            supported_id_types=[
                IDFormatInfo(
                    id_type="cpf",
                    pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                    length=11,
                    check_digit_algorithm="mod11",
                    example="123.456.789-01",
                    description="Cadastro de Pessoas Físicas",
                    required_for_citizens=True
                ),
                IDFormatInfo(
                    id_type="cnpj",
                    pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                    length=14,
                    check_digit_algorithm="mod11",
                    example="12.345.678/0001-90",
                    description="Cadastro Nacional da Pessoa Jurídica"
                )
            ],
            regulatory_frameworks={RegulatoryFramework.LGPD},
            data_localization_required=True
        ))
        
        # Add high-risk countries (for enhanced security)
        high_risk_countries = [
            ("AF", "AFG", "004", "Afghanistan"),
            ("IR", "IRN", "364", "Iran"),
            ("KP", "PRK", "408", "North Korea"),
            ("SY", "SYR", "760", "Syria"),
        ]
        
        for alpha2, alpha3, numeric, name in high_risk_countries:
            self.add_country(CountryInfo(
                iso_alpha2=alpha2,
                iso_alpha3=alpha3,
                iso_numeric=numeric,
                name=name,
                official_name=name,
                region=Region.ASIA if alpha2 in ["AF", "IR", "KP", "SY"] else Region.MIDDLE_EAST,
                high_risk_country=True,
                sanctions_applicable=True,
                enhanced_security_required=True,
                audit_logging_required=True,
                strict_validation_required=True
            ))
        
        self._build_indices()
        logger.info(f"Loaded {len(self.countries)} countries into database")
    
    def add_country(self, country: CountryInfo) -> None:
        """Add country to database."""
        self.countries[country.iso_alpha2] = country
        self.countries_by_alpha3[country.iso_alpha3] = country
        self.countries_by_numeric[country.iso_numeric] = country
        
        # Index by phone country code
        if country.phone_info and country.phone_info.country_code:
            code = country.phone_info.country_code
            if code not in self.countries_by_phone_code:
                self.countries_by_phone_code[code] = []
            self.countries_by_phone_code[code].append(country)
    
    def get_country_by_alpha2(self, alpha2: str) -> Optional[CountryInfo]:
        """Get country by ISO Alpha-2 code."""
        return self.countries.get(alpha2.upper())
    
    def get_country_by_alpha3(self, alpha3: str) -> Optional[CountryInfo]:
        """Get country by ISO Alpha-3 code."""
        return self.countries_by_alpha3.get(alpha3.upper())
    
    def get_country_by_numeric(self, numeric: str) -> Optional[CountryInfo]:
        """Get country by ISO numeric code."""
        return self.countries_by_numeric.get(numeric)
    
    def get_countries_by_phone_code(self, phone_code: str) -> List[CountryInfo]:
        """Get countries by phone country code."""
        return self.countries_by_phone_code.get(phone_code, [])
    
    def get_countries_by_region(self, region: Region) -> List[CountryInfo]:
        """Get all countries in a specific region."""
        return [country for country in self.countries.values() if country.region == region]
    
    def get_gdpr_countries(self) -> List[CountryInfo]:
        """Get all countries subject to GDPR."""
        return [country for country in self.countries.values() if country.gdpr_applicable]
    
    def get_high_risk_countries(self) -> List[CountryInfo]:
        """Get all high-risk countries."""
        return [country for country in self.countries.values() if country.high_risk_country]
    
    def get_countries_with_framework(self, framework: RegulatoryFramework) -> List[CountryInfo]:
        """Get countries subject to specific regulatory framework."""
        return [
            country for country in self.countries.values()
            if framework in country.regulatory_frameworks
        ]
    
    def search_countries(self, query: str) -> List[CountryInfo]:
        """Search countries by name or code."""
        query = query.lower()
        results = []
        
        for country in self.countries.values():
            if (query in country.name.lower() or
                query in country.official_name.lower() or
                query == country.iso_alpha2.lower() or
                query == country.iso_alpha3.lower() or
                query == country.iso_numeric):
                results.append(country)
        
        return results
    
    def validate_phone_number_country(self, phone_number: str) -> Optional[CountryInfo]:
        """Validate phone number and determine country."""
        # Remove common formatting
        clean_number = ''.join(c for c in phone_number if c.isdigit())
        
        # Check for country codes (1-4 digits)
        for code_length in range(1, 5):
            if len(clean_number) > code_length:
                potential_code = clean_number[:code_length]
                countries = self.get_countries_by_phone_code(potential_code)
                
                if countries:
                    # For now, return first match - could be enhanced with better logic
                    return countries[0]
        
        return None
    
    def get_validation_requirements(self, country_code: str) -> Dict[str, Any]:
        """Get validation requirements for a country."""
        country = self.get_country_by_alpha2(country_code)
        if not country:
            return {}
        
        return {
            "strict_validation_required": country.strict_validation_required,
            "enhanced_security_required": country.enhanced_security_required,
            "audit_logging_required": country.audit_logging_required,
            "high_risk_country": country.high_risk_country,
            "gdpr_applicable": country.gdpr_applicable,
            "data_localization_required": country.data_localization_required,
            "regulatory_frameworks": [f.value for f in country.regulatory_frameworks],
            "supported_id_types": [
                {
                    "type": id_info.id_type,
                    "pattern": id_info.pattern,
                    "required": id_info.required_for_citizens
                }
                for id_info in country.supported_id_types
            ]
        }
    
    def _build_indices(self) -> None:
        """Build search indices for efficient lookups."""
        # Already built in add_country method
        pass
    
    def export_country_data(self, file_path: str) -> None:
        """Export country data to JSON file."""
        export_data = {}
        
        for alpha2, country in self.countries.items():
            export_data[alpha2] = {
                "iso_alpha2": country.iso_alpha2,
                "iso_alpha3": country.iso_alpha3,
                "iso_numeric": country.iso_numeric,
                "name": country.name,
                "official_name": country.official_name,
                "region": country.region.value,
                "subregion": country.subregion,
                "capital": country.capital,
                "languages": country.languages,
                "currency_code": country.currency_code,
                "timezone": country.timezone,
                "phone_info": {
                    "country_code": country.phone_info.country_code,
                    "trunk_prefix": country.phone_info.trunk_prefix,
                    "emergency_numbers": country.phone_info.emergency_numbers,
                    "format_patterns": country.phone_info.format_patterns
                } if country.phone_info else None,
                "postal_code_info": {
                    "format_pattern": country.postal_code_info.format_pattern,
                    "length": country.postal_code_info.length,
                    "example": country.postal_code_info.example,
                    "alphanumeric": country.postal_code_info.alphanumeric
                } if country.postal_code_info else None,
                "supported_id_types": [
                    {
                        "id_type": id_info.id_type,
                        "pattern": id_info.pattern,
                        "length": id_info.length,
                        "example": id_info.example,
                        "description": id_info.description,
                        "required_for_citizens": id_info.required_for_citizens
                    }
                    for id_info in country.supported_id_types
                ],
                "regulatory_frameworks": [f.value for f in country.regulatory_frameworks],
                "gdpr_applicable": country.gdpr_applicable,
                "high_risk_country": country.high_risk_country,
                "enhanced_security_required": country.enhanced_security_required
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, sort_keys=True)
        
        logger.info(f"Country data exported to {file_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            "total_countries": len(self.countries),
            "countries_by_region": {},
            "gdpr_countries": len(self.get_gdpr_countries()),
            "high_risk_countries": len(self.get_high_risk_countries()),
            "countries_with_id_types": 0,
            "total_phone_codes": len(self.countries_by_phone_code),
            "regulatory_framework_coverage": {}
        }
        
        # Count by region
        for region in Region:
            stats["countries_by_region"][region.value] = len(self.get_countries_by_region(region))
        
        # Count countries with ID type definitions
        stats["countries_with_id_types"] = sum(
            1 for country in self.countries.values()
            if country.supported_id_types
        )
        
        # Count regulatory framework coverage
        for framework in RegulatoryFramework:
            stats["regulatory_framework_coverage"][framework.value] = len(
                self.get_countries_with_framework(framework)
            )
        
        return stats


# Global country database instance
_global_countries: Optional[CountryDatabase] = None


def get_countries() -> CountryDatabase:
    """Get global country database instance."""
    global _global_countries
    if _global_countries is None:
        _global_countries = CountryDatabase()
    return _global_countries


def set_countries(countries: CountryDatabase) -> None:
    """Set global country database instance."""
    global _global_countries
    _global_countries = countries
