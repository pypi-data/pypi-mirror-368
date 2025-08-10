"""
Copyright URL mappings for Bible Gateway translations.

This module provides mappings from translation codes to their corresponding
Bible Gateway copyright URLs based on the actual URL patterns used on
biblegateway.com/versions/
"""

# Mapping of translation codes to their Bible Gateway copyright URLs
# Format: https://www.biblegateway.com/versions/{translation-name}-{translation-code}-Bible/
COPYRIGHT_URLS = {
    # Major English Translations
    "ESV": "https://www.biblegateway.com/versions/English-Standard-Version-ESV-Bible/",
    "NIV": "https://www.biblegateway.com/versions/New-International-Version-NIV-Bible/",
    "KJV": "https://www.biblegateway.com/versions/King-James-Version-KJV-Bible/",
    "NKJV": "https://www.biblegateway.com/versions/New-King-James-Version-NKJV-Bible/",
    "NASB": "https://www.biblegateway.com/versions/New-American-Standard-Bible-NASB/",
    "NLT": "https://www.biblegateway.com/versions/New-Living-Translation-NLT-Bible/",
    "CSB": "https://www.biblegateway.com/versions/Christian-Standard-Bible-CSB/",
    "AMP": "https://www.biblegateway.com/versions/Amplified-Bible-AMP/",
    "HCSB": "https://www.biblegateway.com/versions/Holman-Christian-Standard-Bible-HCSB/",
    "NET": "https://www.biblegateway.com/versions/New-English-Translation-NET-Bible/",
    "RSV": "https://www.biblegateway.com/versions/Revised-Standard-Version-RSV/",
    "NRSV": "https://www.biblegateway.com/versions/New-Revised-Standard-Version-NRSV/",
    "CEB": "https://www.biblegateway.com/versions/Common-English-Bible-CEB/",
    "ERV": "https://www.biblegateway.com/versions/Easy-to-Read-Version-ERV/",
    "GW": "https://www.biblegateway.com/versions/GODS-WORD-Translation-GW/",
    "ICB": "https://www.biblegateway.com/versions/International-Childrens-Bible-ICB/",
    "ISV": "https://www.biblegateway.com/versions/International-Standard-Version-ISV/",
    "MSG": "https://www.biblegateway.com/versions/The-Message-MSG/",
    "MEV": "https://www.biblegateway.com/versions/Modern-English-Version-MEV/",
    "PHILLIPS": "https://www.biblegateway.com/versions/JB-Phillips-New-Testament-PHILLIPS/",
    "TLB": "https://www.biblegateway.com/versions/The-Living-Bible-TLB/",
    "VOICE": "https://www.biblegateway.com/versions/The-Voice-VOICE/",
    "WEB": "https://www.biblegateway.com/versions/World-English-Bible-WEB/",
    "YLT": "https://www.biblegateway.com/versions/Youngs-Literal-Translation-YLT/",
    # Spanish Translations
    "LBLA": "https://www.biblegateway.com/versions/La-Biblia-de-las-Amricas-LBLA/",
    "NVI": "https://www.biblegateway.com/versions/Nueva-Version-Internacional-NVI/",
    "DHH": "https://www.biblegateway.com/versions/Dios-Habla-Hoy-DHH/",
    "RVR1960": "https://www.biblegateway.com/versions/Reina-Valera-1960-RVR1960/",
    # French Translations
    "LSG": "https://www.biblegateway.com/versions/Louis-Segond-LSG/",
    "BDS": "https://www.biblegateway.com/versions/La-Bible-du-Semeur-BDS/",
    # German Translations
    "HOF": "https://www.biblegateway.com/versions/Hoffnung-fur-Alle-HOF/",
    "LUTH1545": "https://www.biblegateway.com/versions/Luther-Bibel-1545-LUTH1545/",
    # Other Languages
    "B21": "https://www.biblegateway.com/versions/Bible-21-B21/",
    "BB": "https://www.biblegateway.com/versions/BasisBijbel-BB/",
    "HTB": "https://www.biblegateway.com/versions/Het-Boek-HTB/",
    # Fallback for unknown translations
    "DEFAULT": "https://www.biblegateway.com/versions/",
}


def get_copyright_url(translation_code: str) -> str:
    """
    Get the copyright URL for a given translation code.

    Args:
        translation_code: The translation code (e.g., 'ESV', 'NIV')

    Returns:
        The copyright URL for the translation, or the default URL if not found
    """
    return COPYRIGHT_URLS.get(translation_code.upper(), COPYRIGHT_URLS["DEFAULT"])


def get_all_copyright_urls() -> dict:
    """
    Get all available copyright URLs.

    Returns:
        Dictionary mapping translation codes to copyright URLs
    """
    return COPYRIGHT_URLS.copy()
