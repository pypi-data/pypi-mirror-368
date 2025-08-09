"""
Standard HLA alleles for ImmunoForge

This module provides curated lists of HLA alleles for epitope prediction,
organized by population frequency and coverage.
"""

# Most common HLA Class I alleles globally (top 10)
TOP_10_ALLELES = [
    "A0101", "A0201", "A0301", "A1101", "A2402",
    "B0702", "B0801", "B3501", "B4001", "B4402"
]

# Extended common alleles (top 20)
TOP_20_ALLELES = [
    "A0101", "A0201", "A0301", "A1101", "A2402",
    "A2601", "A3201", "A6801", "A2902", "A3401",
    "B0702", "B0801", "B3501", "B4001", "B4402",
    "B1501", "B1801", "B5101", "B5701", "B2705"
]

# Comprehensive panel for population coverage (34 alleles)
COMPREHENSIVE_PANEL = [
    # HLA-A
    "A0101", "A0201", "A0301", "A1101", "A2402",
    "A2601", "A2902", "A3401", "A6801", "A3201", 
    "A0204", "A0212", "A3303",
    # HLA-B  
    "B0702", "B0801", "B1521", "B1525", "B1501", 
    "B1801", "B3501", "B4001", "B4002", "B5601", 
    "B4402", "B4403", "B5001", "B5701", "B5801",
    # HLA-C
    "C0102", "C0202", "C0304", "C0401", "C0602", 
    "C0701", "C0702"
]

# Quick test panel (9 alleles) - balanced coverage
QUICK_PANEL = [
    "A0101", "A0201", "A0301",
    "B1525", "B1501", "B1801",
    "C0102", "C0202", "C0304"
]

# Population-specific panels
CAUCASIAN_PANEL = [
    "A0101", "A0201", "A0301", "A1101", "A2402",
    "B0702", "B0801", "B4402", "B3501", "B5101",
    "C0102", "C0401", "C0501", "C0602", "C0701"
]

ASIAN_PANEL = [
    "A0201", "A1101", "A2402", "A3303", "A3101",
    "B1301", "B1501", "B3501", "B4001", "B5801",
    "C0102", "C0302", "C0304", "C0801", "C1402"
]

AFRICAN_PANEL = [
    "A0201", "A2301", "A3001", "A3401", "A6802",
    "B0702", "B1510", "B3501", "B4201", "B5301",
    "C0202", "C0401", "C0602", "C1601", "C1701"
]

# Research panels
SUPERTYPES_PANEL = [
    # A01 supertype
    "A0101", "A2601", "A2902",
    # A02 supertype  
    "A0201", "A0202", "A6802",
    # A03 supertype
    "A0301", "A1101", "A3101",
    # B07 supertype
    "B0702", "B3501", "B5101",
    # B44 supertype
    "B4001", "B4402", "B4403"
]

# Default alleles (alias for comprehensive panel)
DEFAULT_ALLELES = COMPREHENSIVE_PANEL

# Main export - can be used as: from immunoforge import alleles
alleles = COMPREHENSIVE_PANEL


def get_allele_panel(panel_name: str = "comprehensive"):
    """
    Get a specific allele panel by name
    
    Parameters
    ----------
    panel_name : str
        Name of the panel: 'top10', 'top20', 'comprehensive', 'quick',
        'caucasian', 'asian', 'african', 'supertypes', 'default'
        
    Returns
    -------
    list[str]
        List of HLA alleles in the requested panel
    """
    panels = {
        'top10': TOP_10_ALLELES,
        'top20': TOP_20_ALLELES,
        'comprehensive': COMPREHENSIVE_PANEL,
        'quick': QUICK_PANEL,
        'caucasian': CAUCASIAN_PANEL,
        'asian': ASIAN_PANEL,
        'african': AFRICAN_PANEL,
        'supertypes': SUPERTYPES_PANEL,
        'default': DEFAULT_ALLELES
    }
    
    panel = panels.get(panel_name.lower())
    if panel is None:
        raise ValueError(f"Unknown panel: {panel_name}. Available: {list(panels.keys())}")
    
    return panel.copy()  # Return copy to prevent accidental modification


def format_alleles(alleles_list, format_type='standard'):
    """
    Format allele names for different tools
    
    Parameters
    ----------
    alleles_list : list[str]
        List of alleles in standard format (e.g., 'A0201')
    format_type : str
        'standard' (A0201), 'netmhcpan' (HLA-A02:01), 'mhcflurry' (A*02:01)
        
    Returns
    -------
    list[str]
        Formatted allele names
    """
    formatted = []
    
    for allele in alleles_list:
        if format_type == 'standard':
            formatted.append(allele)
        elif format_type == 'netmhcpan':
            # A0201 -> HLA-A02:01
            if len(allele) >= 5:
                formatted.append(f"HLA-{allele[0]}{allele[1:3]}:{allele[3:5]}")
            else:
                formatted.append(allele)
        elif format_type == 'mhcflurry':
            # A0201 -> A*02:01
            if len(allele) >= 5:
                formatted.append(f"{allele[0]}*{allele[1:3]}:{allele[3:5]}")
            else:
                formatted.append(allele)
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    return formatted