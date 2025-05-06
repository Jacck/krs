#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mock Responses for KRS API

This module provides mock responses for the KRS API client.
"""

# Mock responses for the KRS API
mock_responses = {
    # Cyfrowy Polsat (example data)
    "details:0000010078": {
        "krs": "0000010078",
        "nazwa": "CYFROWY POLSAT SPĂ“Ĺ�KA AKCYJNA",
        "nip": "7961810732",
        "regon": "670925160",
        "status": "Aktywny",
        "adres": "ul. Ĺ�UBINOWA 4A, 03-878 WARSZAWA",
        "formaFrawna": "SPĂ“Ĺ�KA AKCYJNA",
        "dataRejestracji": "2001-04-03",
    },
    
    # Cyfrowy Polsat representatives
    "reprezentanci:0000010078": {
        "reprezentanci": [
            {
                "imie": "Jan",
                "nazwisko": "Kowalski",
                "funkcja": "PREZES ZARZÄ„DU"
            },
            {
                "imie": "Anna",
                "nazwisko": "Nowak",
                "funkcja": "CZĹ�ONEK ZARZÄ„DU"
            },
            {
                "imie": "Piotr",
                "nazwisko": "WiĹ›niewski",
                "funkcja": "CZĹ�ONEK ZARZÄ„DU"
            }
        ]
    },
    
    # Cyfrowy Polsat shareholders
    "wspolnicy:0000010078": {
        "wspolnicy": [
            {
                "nazwa": "TIVI FOUNDATION",
                "typ": "corporate",
                "udzialy": "57.66%"
            },
            {
                "nazwa": "REDDEV INVESTMENTS LIMITED",
                "typ": "corporate",
                "udzialy": "0.27%"
            },
            {
                "nazwa": "AKCJE WĹ�ASNE",
                "typ": "corporate",
                "udzialy": "7.86%"
            },
            {
                "nazwa": "POZOSTALI AKCJONARIUSZE",
                "typ": "corporate",
                "udzialy": "34.21%"
            }
        ]
    },
    
    # Search by KRS
    "search:krs:0000010078": {
        "wyniki": [
            {
                "krs": "0000010078",
                "nazwa": "CYFROWY POLSAT SPĂ“Ĺ�KA AKCYJNA",
                "nip": "7961810732",
                "regon": "670925160",
                "status": "Aktywny",
                "adres": "ul. Ĺ�UBINOWA 4A, 03-878 WARSZAWA"
            }
        ],
        "liczbaWynikow": 1
    },
    
    # Search by name
    "search:name:Cyfrowy Polsat": {
        "wyniki": [
            {
                "krs": "0000010078",
                "nazwa": "CYFROWY POLSAT SPĂ“Ĺ�KA AKCYJNA",
                "nip": "7961810732",
                "regon": "670925160",
                "status": "Aktywny",
                "adres": "ul. Ĺ�UBINOWA 4A, 03-878 WARSZAWA"
            }
        ],
        "liczbaWynikow": 1
    },
    
    # Empty search results
    "search:default": {
        "wyniki": [],
        "liczbaWynikow": 0
    },
    
    # Polkomtel (example data for relationship testing)
    "details:0000419430": {
        "krs": "0000419430",
        "nazwa": "POLKOMTEL SPĂ“Ĺ�KA Z OGRANICZONÄ„ ODPOWIEDZIALNOĹšCIÄ„",
        "nip": "5271037727",
        "regon": "011307968",
        "status": "Aktywny",
        "adres": "ul. KONSTRUKTORSKA 4, 02-673 WARSZAWA",
        "formaFrawna": "SPĂ“Ĺ�KA Z OGRANICZONÄ„ ODPOWIEDZIALNOĹšCIÄ„",
        "dataRejestracji": "2012-01-03",
    },
    
    # Telewizja Polsat (example data for relationship testing)
    "details:0000388216": {
        "krs": "0000388216",
        "nazwa": "TELEWIZJA POLSAT SPĂ“Ĺ�KA Z OGRANICZONÄ„ ODPOWIEDZIALNOĹšCIÄ„",
        "nip": "1130054762",
        "regon": "930171612",
        "status": "Aktywny",
        "adres": "ul. OSTROBRAMSKA 77, 04-175 WARSZAWA",
        "formaFrawna": "SPĂ“Ĺ�KA Z OGRANICZONÄ„ ODPOWIEDZIALNOĹšCIÄ„",
        "dataRejestracji": "2011-07-19",
    }
}
