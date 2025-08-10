"""
Bible translations constants.

This module contains the mapping of translation codes to their full names and languages.
"""

# Supported Bible translations for download
SUPPORTED_BIBLE_TRANSLATIONS = {
    "AMP": {"name": "Amplified Bible", "language": "English"},
    "ASV": {"name": "American Standard Version", "language": "English"},
    "AKJV": {"name": "Authorized King James Version", "language": "English"},
    "BRG": {"name": "BRG Bible", "language": "English"},
    "CSB": {"name": "Christian Standard Bible", "language": "English"},
    "EHV": {"name": "Evangelical Heritage Version", "language": "English"},
    "ESV": {"name": "English Standard Version", "language": "English"},
    "ESVUK": {"name": "English Standard Version UK", "language": "English"},
    "GNV": {"name": "Geneva Bible", "language": "English"},
    "GW": {"name": "God's Word Translation", "language": "English"},
    "ISV": {"name": "International Standard Version", "language": "English"},
    "JUB": {"name": "Jubilee Bible", "language": "English"},
    "KJV": {"name": "King James Version", "language": "English"},
    "KJ21": {"name": "21st Century King James Version", "language": "English"},
    "LEB": {"name": "Lexham English Bible", "language": "English"},
    "LSB": {"name": "Legacy Standard Bible", "language": "English"},
    "MEV": {"name": "Modern English Version", "language": "English"},
    "NASB": {"name": "New American Standard Bible", "language": "English"},
    "NASB1995": {"name": "New American Standard Bible 1995", "language": "English"},
    "NET": {"name": "New English Translation", "language": "English"},
    "NIV": {"name": "New International Version", "language": "English"},
    "NIVUK": {"name": "New International Version UK", "language": "English"},
    "NKJV": {"name": "New King James Version", "language": "English"},
    "NLT": {"name": "New Living Translation", "language": "English"},
    "NLV": {"name": "New Life Version", "language": "English"},
    "NOG": {"name": "Names of God Bible", "language": "English"},
    "NRSV": {"name": "New Revised Standard Version", "language": "English"},
    "NRSVUE": {"name": "New Revised Standard Version Updated Edition", "language": "English"},
    "RSV": {"name": "Revised Standard Version", "language": "English"},
    "WEB": {"name": "World English Bible", "language": "English"},
    "YLT": {"name": "Young's Literal Translation", "language": "English"},
}

# Unsupported Bible translations (not available for download)
UNSUPPORTED_BIBLE_TRANSLATIONS = {
    "CEV": {"name": "Contemporary English Version", "language": "English"},
    "ERV": {"name": "Easy-to-Read Version", "language": "English"},
    "HCSB": {"name": "Holman Christian Standard Bible", "language": "English"},
    "ICB": {"name": "International Children's Bible", "language": "English"},
    "MSG": {"name": "The Message", "language": "English"},
    "NCV": {"name": "New Century Version", "language": "English"},
    "NIRV": {"name": "New International Reader's Version", "language": "English"},
    "NMB": {"name": "New Matthew Bible (New Testament only)", "language": "English"},
    "TLB": {"name": "The Living Bible", "language": "English"},
    "TLV": {"name": "Tree of Life Version", "language": "English"},
    "VOICE": {"name": "The Voice", "language": "English"},
    "WYC": {"name": "Wycliffe Bible", "language": "English"},
}

# All available Bible translations (supported + unsupported)
BIBLE_TRANSLATIONS = {**SUPPORTED_BIBLE_TRANSLATIONS, **UNSUPPORTED_BIBLE_TRANSLATIONS}
