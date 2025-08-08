import csv
import sys

class Translation:
    """
    This class contains all functions required for translating columns into more pandas or user friendly formats.
    
    This is a class because some translation dictionaries like lv_translation require a file to be read in.
    """
    
    # Define static translation dictionaries that don't require reading a tsv
    opOrbit_to_simple_orbit = {
        "ATM": "SO",      # Atmospheric
        "SO": "SO",        # Suborbital
        "TA": "SO",        # Trans-Atmospheric
        "LLEO/E": "LEO",   # Lower LEO/Equatorial
        "LLEO/I": "LEO",   # Lower LEO/Intermediate
        "LLEO/P": "SSO",   # Lower LEO/Polar
        "LLEO/S": "SSO",   # Lower LEO/Sun-Sync
        "LLEO/R": "LEO",   # Lower LEO/Retrograde
        "LEO/E": "LEO",    # Upper LEO/Equatorial
        "LEO/I": "LEO",    # Upper LEO/Intermediate
        "LEO/P": "SSO",    # Upper LEO/Polar
        "LEO/S": "SSO",    # Upper LEO/Sun-Sync
        "LEO/R": "LEO",    # Upper LEO/Retrograde
        "MEO": "MEO",      # Medium Earth Orbit
        "HEO": "HEO",      # Highly Elliptical Orbit
        "HEO/M": "HEO",    # Molniya
        "GTO": "GTO",      # Geotransfer
        "GEO/S": "GEO",    # Stationary
        "GEO/I": "GEO",    # Inclined GEO
        "GEO/T": "GEO",    # Synchronous
        "GEO/D": "GEO",    # Drift GEO
        "GEO/SI": "GEO",   # Inclined GEO (same as GEO/I)
        "GEO/ID": "GEO",   # Inclined Drift
        "GEO/NS": "GEO",   # Near-sync
        "VHEO": "HEO",    # Very High Earth Orbit
        "DSO": "BEO",      # Deep Space Orbit
        "CLO": "BEO",      # Cislunar/Translunar
        "EEO": "BEO",      # Earth Escape
        "HCO": "BEO",      # Heliocentric
        "PCO": "BEO",      # Planetocentric
        "SSE": "BEO"       # Solar System Escape
    }
    
    # Note:
    # There might be some edge cases where a satcat simple orbit is SSO
    # while launch simple orbit is LEO.
    # Eg. satcat raw orbit "LEO/P" while launch raw orbit "LEO"
    launch_category_to_simple_orbit = {
        "DSO": "BEO",    # Deep space orbit
        "EEO": "BEO",    # Earth escape orbit
        "GEO": "GEO",    # Direct geosync insertion
        "GTO": "GTO",    # Geosync transfer orbit
        "HEO": "HEO",    # Highly elliptical orbit
        "ISS": "LEO",    # International Space Station
        "LEO": "LEO",    # Low Earth Orbit
        "LSS": "LEO",    # LEO space station other than ISS
        "MEO": "MEO",    # Medium Earth Orbit
        "MOL": "HEO",    # Molniya orbit
        "MTO": "MEO",    # MEO transfer orbit
        "SSO": "SSO",    # Sun-sync orbit
        "STO": "GTO",    # Supersync transfer orbit
        "XO": "BEO"      # Extraterrestrial launch
    }
    
    # See https://planet4589.org/space/gcat/web/cat/pcols.html
    # Todo update
    payload_category_to_simple_payload_category = {
        "AST": "Observation",
        "IMG": "Observation",
        "IMGR": "Observation",
        "MET": "Observation",
        "METRO": "Observation",
        "COM": "Communications",
        "NAV": "Communications",
        "BIO": "Science",
        "GEOD": "Science",
        "MGRAV": "Science",
        "SCI": "Science",
        "TECH": "Tech Demo",
        "EW": "Observation",
        "SIG": "Observation",
        "TARG": "Other",
        "WEAPON": "Other",
        "CAL": "Other",
        "EDU": "Other",
        "INF": "Other",
        "MISC": "Other",
        "RB": "Other",
        "RV": "Other",
        "PLAN": "Other",
        "SS": "Other"
    }
    
    # Dictionary to store rocket name mappings to a more friendly format
    # Note: I distinguish between H and M, use family otherwise
    # Note: LVM3 is GSLV here
    # Note: All Roman numerals are converted to Arabic numerals, eg. not Saturn V or Minotaur IV, but 5 and 4
    # Note: Soyuz includes Kourou Soyuz, just fun point
    orbital_lv_name_to_lv_simplified = {
        "Saturn V": "Saturn 5",
        "Starship V1.0": "Starship",
        "Starship V2": "Starship",
        "Starship V3": "Starship",
        "Space Shuttle": "Space Shuttle",
        "SLS Block 1": "SLS",
        "Energiya": "Energia",
        "Energiya/Buran": "Energia",
        "UR-500": "Proton",
        "UR-500K": "Proton",
        "UR-500K/Blok D": "Proton",
        "Proton-K": "Proton",
        "Proton-K/D": "Proton",
        "Proton-K/D-1": "Proton",
        "Proton-K/D-2": "Proton",
        "Proton-K/DM": "Proton",
        "Proton-K/DM-2": "Proton",
        "Proton-M": "Proton",
        "Proton-M/DM-2": "Proton",
        "Proton-M/DM-3": "Proton",
        "Proton-K/DM-2M": "Proton",
        "Proton-K/17S40": "Proton",
        "Proton-K/Briz-M": "Proton",
        "Proton-M/Briz-M": "Proton",
        "Neutron": "Neutron",
        "New Glenn": "New Glenn",
        "Saturn C-1": "Saturn 1",
        "Saturn I": "Saturn 1",
        "Saturn IB": "Saturn 1",
        "Uprated Saturn I": "Saturn 1",
        "Vulcan Centaur VC0S": "Vulcan",
        "Vulcan Centaur VC2S": "Vulcan",
        "Vulcan Centaur VC4S": "Vulcan",
        "Vulcan Centaur VC6S": "Vulcan",
        "Ariane 5G": "Ariane 5",
        "Ariane 5G+": "Ariane 5",
        "Ariane 5GS": "Ariane 5",
        "Ariane 5ES/ATV": "Ariane 5",
        "Ariane 5ES": "Ariane 5",
        "Ariane 5ECA": "Ariane 5",
        "Ariane 5ECA+": "Ariane 5",
        "Ariane 62": "Ariane 6",
        "Ariane 64": "Ariane 6",
        "H3-30S": "H3",
        "H3-22S": "H3",
        "H3-22L": "H3",
        "H3-24L": "H3",
        "H-IIB": "H2",
        "Chang Zheng 5": "Long March 5",
        "Chang Zheng 5B": "Long March 5",
        "Chang Zheng 5/YZ-2": "Long March 5",
        "Chang Zheng 5B/YZ-2": "Long March 5",
        "Delta 4H": "Delta 4H",
        "Delta 4H/Star 48BV": "Delta 4H",
        "Delta 4M": "Delta 4M",
        "Delta 4M+(4,2)": "Delta 4M",
        "Delta 4M+(5,4)": "Delta 4M",
        "Delta 4M+(5,2)": "Delta 4M",
        "H-II": "H2",
        "H-IIA 202": "H2",
        "H-IIA 204": "H2",
        "H-IIA 2022": "H2",
        "H-IIA 2024": "H2",
        "GSLV Mk III": "GSLV",
        "LVM3": "GSLV",
        "Antares 110": "Antares",
        "Antares 120": "Antares",
        "Antares 130": "Antares",
        "Antares 230": "Antares",
        "Antares 230+": "Antares",
        "Zenit-2": "Zenit",
        "Zenit-2M": "Zenit",
        "Zenit-2 11K77.05": "Zenit",
        "Zenit-3SL": "Zenit",
        "Zenit-2SB": "Zenit",
        "Zenit-3F": "Zenit",
        "Zenit-3SLB": "Zenit",
        "Zenit-3SLBF": "Zenit",
        "Atlas V 401": "Atlas 5",
        "Atlas V 411": "Atlas 5",
        "Atlas V 421": "Atlas 5",
        "Atlas V 431": "Atlas 5",
        "Atlas V 501": "Atlas 5",
        "Atlas V 521": "Atlas 5",
        "Atlas V 511": "Atlas 5",
        "Atlas V 531": "Atlas 5",
        "Atlas V 541": "Atlas 5",
        "Atlas V 551": "Atlas 5",
        "Atlas V N22": "Atlas 5",
        "Ariane 1": "Ariane 1",
        "Ariane 2": "Ariane 2",
        "Ariane 3": "Ariane 3",
        "Ariane 40": "Ariane 4",
        "Ariane 42L": "Ariane 4",
        "Ariane 42P": "Ariane 4",
        "Ariane 44L": "Ariane 4",
        "Ariane 44LP": "Ariane 4",
        "Ariane 44P": "Ariane 4",
        "Tianlong-3": "Tianlong",
        "Tianlong-3 S1": "Tianlong",
        "Chang Zheng 12": "Long March 12",
        "LM AS": "LM AS",
        "Falcon Heavy": "Falcon Heavy",
        "Falcon 9": "Falcon 9",
        "Falcon 9R": "Falcon 9",
        "Nuri": "Nuri",
        "Vega C": "Vega",
        "Zhuque-2": "Zhuque-2",
        "Zhuque-2E": "Zhuque-2",
        "Feng Bao 1": "Feng Bao 1",
        "Chang Zheng 2": "Long March 2",
        "Chang Zheng 2C": "Long March 2",
        "Chang Zheng 2C/YZ-1S": "Long March 2",
        "Chang Zheng 2C-III/SD": "Long March 2",
        "Chang Zheng 2D": "Long March 2",
        "Chang Zheng 2D/YZ-3": "Long March 2",
        "Chang Zheng 2E": "Long March 2",
        "Chang Zheng 2F": "Long March 2",
        "Chang Zheng 3": "Long March 3",
        "Chang Zheng 3A": "Long March 3",
        "Chang Zheng 3B": "Long March 3",
        "Chang Zheng 3C": "Long March 3",
        "Chang Zheng 3C/YZ-1": "Long March 3",
        "Chang Zheng 3B/YZ-1": "Long March 3",
        "Chang Zheng 6": "Long March 6",
        "Chang Zheng 6A": "Long March 6",
        "Chang Zheng 6C": "Long March 6",
        "Chang Zheng 7": "Long March 7",
        "Chang Zheng 7A": "Long March 7",
        "Chang Zheng 7/YZ-1A": "Long March 7",
        "Chang Zheng 8": "Long March 8",
        "Chang Zheng 8A": "Long March 8",
        "Chang Zheng 4": "Long March 4",
        "Chang Zheng 4B": "Long March 4",
        "Chang Zheng 4C": "Long March 4",
        "Tianlong-2": "Tianlong",
        "Titan II GLV": "Titan 2", # Note that Titan 1 never went to orbit so isn't here
        "Titan II SLV": "Titan 2",
        "Titan IIIA": "Titan 3",
        "Titan IIIB": "Titan 3",
        "Titan IIIC": "Titan 3",
        "Titan IIID": "Titan 3",
        "Titan IIIE": "Titan 3",
        "Titan 23B": "Titan 3",
        "Titan 24B": "Titan 3",
        "Titan 33B": "Titan 3",
        "Titan 34B": "Titan 3",
        "Titan 34D": "Titan 3",
        "Titan 34D/Transtage": "Titan 3",
        "Titan 34D/IUS": "Titan 3",
        "Commercial Titan 3": "Titan 3",
        "Titan 401A/Centaur": "Titan 4",
        "Titan 402A/IUS": "Titan 4",
        "Titan 403A": "Titan 4",
        "Titan 404A": "Titan 4",
        "Titan 405A": "Titan 4",
        "Titan 401B/Centaur": "Titan 4",
        "Titan 402B/IUS": "Titan 4",
        "Titan 403B": "Titan 4",
        "Titan 404B": "Titan 4",
        "Titan 405B": "Titan 4",
        "ELDO A": "Europa",
        "Europa I": "Europa",
        "Europa II": "Europa",
        "Atlas B": "Atlas 1",
        "Atlas D": "Atlas 1",
        "Atlas E": "Atlas 1",
        "Atlas F": "Atlas 1",
        "Atlas C Able": "Atlas 1",
        "Atlas F/Agena D": "Atlas 1",
        "Atlas F/MSD": "Atlas 1",
        "Atlas E/MSD": "Atlas 1",
        "Atlas E Altair": "Atlas 1",
        "Atlas F/OIS": "Atlas 1",
        "Atlas E/OIS": "Atlas 1",
        "Atlas F/PTS": "Atlas 1",
        "Atlas E/SVS": "Atlas 1",
        "Atlas F/SVS": "Atlas 1",
        "Atlas E/SGS-2": "Atlas 1",
        "Atlas SLV-3": "Atlas 1",
        "Atlas G Centaur": "Atlas 1",
        "Atlas H": "Atlas 1",
        "Atlas Able": "Atlas 1",
        "Atlas Agena A": "Atlas 1",
        "Atlas Agena B": "Atlas 1",
        "Atlas Agena D": "Atlas 1",
        "Atlas SLV-3 Agena B": "Atlas 1",
        "Atlas SLV-3 Agena D": "Atlas 1",
        "Atlas SLV-3A Agena D": "Atlas 1",
        "Atlas Burner 2": "Atlas 1",
        "Atlas Burner 2A": "Atlas 1",
        "Atlas Centaur": "Atlas 1",
        "Atlas Centaur D": "Atlas 1",
        "Atlas SLV-3C Centaur": "Atlas 1",
        "Atlas SLV-3D Centaur": "Atlas 1",
        "Atlas I": "Atlas 1",
        "Atlas II": "Atlas 2",
        "Atlas IIA": "Atlas 2",
        "Atlas IIAS": "Atlas 2",
        "Atlas 3A": "Atlas 3",
        "Atlas 3B": "Atlas 3",
        "New Shepard": "New Shepard",
        "Vega": "Vega",
        "R-36O 8K69": "Tsyklon",
        "R-36O 8K69M": "Tsyklon",
        "Tsiklon-2A": "Tsyklon",
        "Tsiklon-2": "Tsyklon",
        "Tsiklon-3": "Tsyklon",
        "Dnepr": "Dnepr",
        "Sputnik 8K71PS": "Soyuz",
        "Sputnik 8A91": "Soyuz",
        "Voskhod 11A57": "Soyuz",
        "Vostok-L 8K72": "Soyuz",
        "Vostok 8K72": "Soyuz",
        "Vostok 8A92": "Soyuz",
        "Vostok 8A92M": "Soyuz",
        "Polyot 11A59": "Soyuz",
        "Vostok-2A 11A510": "Soyuz",
        "Soyuz 11A511": "Soyuz",
        "Soyuz 11A511L": "Soyuz",
        "Soyuz 11A511M": "Soyuz",
        "Soyuz-U": "Soyuz",
        "Soyuz-U-PVB": "Soyuz",
        "Soyuz-U2": "Soyuz",
        "Soyuz-2-1A": "Soyuz",
        "Soyuz-2-1B": "Soyuz",
        "Soyuz-2-1V": "Soyuz",
        "Soyuz-ST-A": "Soyuz",
        "Soyuz-ST-B": "Soyuz",
        "Soyuz-FG": "Soyuz",
        "Molniya 8K78": "Molniya",
        "Molniya 8K78M": "Molniya",
        "Molniya 8K78M-PVB": "Molniya",
        "Angara A5": "Angara",
        "Angara A5/Persei": "Angara",
        "Angara A5/Orion": "Angara",
        "Angara-1.2PP": "Angara",
        "Angara-1.2": "Angara",
        "Naro-1": "Naro",
        "PSLV": "PSLV",
        "PSLV-DL": "PSLV",
        "PSLV-QL": "PSLV",
        "PSLV-XL": "PSLV",
        "GSLV Mk I": "GSLV",
        "GSLV Mk II": "GSLV",
        "Juno II": "Juno 2",
        "Lijian-1": "Lijian-1",
        "Jielong-3": "Jielong-3",
        "Yinli-1": "Yinli-1",
        "Epsilon": "Epsilon",
        "Strela": "Strela",
        "Rokot": "Rokot",
        "M-V": "M-V",
        "Thor Able I": "Thor",
        "Thor Able II": "Thor",
        "Thor Able III": "Thor",
        "Thor Able IV": "Thor",
        "Thor Ablestar": "Thor",
        "Thor Agena A": "Thor",
        "Thor Agena B": "Thor",
        "Thor Agena D": "Thor",
        "Thor SLV-2 Agena B": "Thor",
        "Thor SLV-2 Agena D": "Thor",
        "Thor SLV-2A Agena B": "Thor",
        "Thor SLV-2A Agena D": "Thor",
        "Thorad SLV-2G Agena D": "Thor",
        "Thorad SLV-2H Agena D": "Thor",
        "Thor Delta": "Thor",
        "Thor Delta A": "Thor",
        "Thor Delta B": "Thor",
        "Thor Delta C": "Thor",
        "Thor Delta C1": "Thor",
        "Thor Delta D": "Thor",
        "Thor Delta E": "Thor",
        "Thor Delta E1": "Thor",
        "Thor Delta G": "Thor",
        "Thor Delta J": "Thor",
        "Thor Delta L": "Thor",
        "Thor Delta M": "Thor",
        "Thor Delta M6": "Thor",
        "Thor Delta N": "Thor",
        "Thor Delta N6": "Thor",
        "Thor DSV-2U": "Thor",
        "Thor MG-18": "Thor",
        "Thor Burner 1": "Thor",
        "Thor Burner 2": "Thor",
        "Thor Burner 2A": "Thor",
        "Delta 0300": "Delta 1",
        "Delta 0900": "Delta 1",
        "Delta 1410": "Delta 1",
        "Delta 1604": "Delta 1",
        "Delta 1900": "Delta 1",
        "Delta 1910": "Delta 1",
        "Delta 1913": "Delta 1",
        "Delta 1914": "Delta 1",
        "Delta 2310": "Delta 1",
        "Delta 2910": "Delta 1",
        "Delta 2313": "Delta 1",
        "Delta 2913": "Delta 1",
        "Delta 2914": "Delta 1",
        "Delta 3910": "Delta 1",
        "Delta 3910/PAM": "Delta 1",
        "Delta 3913": "Delta 1",
        "Delta 3914": "Delta 1",
        "Delta 3920-8": "Delta 1",
        "Delta 3920": "Delta 1",
        "Delta 3920/PAM": "Delta 1",
        "Delta 3924": "Delta 1",
        "Delta 4925-8": "Delta 1",
        "Delta 5920-8": "Delta 1",
        "Delta 6920-8": "Delta 2",
        "Delta 6920-10": "Delta 2",
        "Delta 6925-8": "Delta 2",
        "Delta 6925": "Delta 2",
        "Delta 7320-10": "Delta 2",
        "Delta 7320-10C": "Delta 2",
        "Delta 7326-9.5": "Delta 2",
        "Delta 7420-10C": "Delta 2",
        "Delta 7425-9.5": "Delta 2",
        "Delta 7425-10": "Delta 2",
        "Delta 7426-9.5": "Delta 2",
        "Delta 7920-8": "Delta 2",
        "Delta 7920-10": "Delta 2",
        "Delta 7920-10C": "Delta 2",
        "Delta 7920-10L": "Delta 2",
        "Delta 7925": "Delta 2",
        "Delta 7925H": "Delta 2",
        "Delta 7920H": "Delta 2",
        "Delta 7925-8": "Delta 2",
        "Delta 7925-9.5": "Delta 2",
        "Delta 7925-10": "Delta 2",
        "Delta 7925-10C": "Delta 2",
        "Delta 7925-10L": "Delta 2",
        "Delta 8930": "Delta 3",
        "N-1": "Delta 1",
        "N-2": "Delta 2",
        "H-1": "H 1",
        "Cheonlima-1": "Cheonlima-1",
        "NK Kerolox LV": "NK Kerolox LV",
        "Unha-2": "Unha-2",
        "Unha-3": "Unha-3",
        "Kwangmyongsong": "Kwangmyongsong",
        "Simorgh": "Simorgh",
        "Kosmos 65S3": "Kosmos",
        "Kosmos 11K65": "Kosmos",
        "Kosmos 11K65M": "Kosmos",
        "K65M-RB": "Kosmos",
        "ARPA Taurus": "Taurus",
        "Taurus 2110": "Taurus",
        "Taurus 2210": "Taurus",
        "Taurus 3210": "Taurus",
        "Taurus 3110": "Taurus",
        "Taurus 1110": "Taurus",
        "Minotaur-C 3210": "Minotaur",
        "LLV-1": "LLV-1",
        "LMLV-1": "LMLV-1",
        "Athena-1": "Athena",
        "Athena-2": "Athena",
        "Minotaur V": "Minotaur 4",
        "Minotaur IV": "Minotaur 4",
        "Minotaur IV+": "Minotaur 4",
        "Chang Zheng 1": "Long March 1",
        "Chang Zheng 1D": "Long March 1",
        "Chang Zheng 11": "Long March 11",
        "KT-2": "KT-2",
        "ADD TV2": "ADD TV2",
        "Hyunmoo-5": "Hyunmoo-5",
        "Spectrum": "Spectrum",
        "Black Arrow": "Black Arrow",
        "Eris Block 1": "Eris",
        "SSLV": "SSLV",
        "Shtil'-1": "Shtil'-1",
        "LauncherOne": "LauncherOne",
        "RS1": "RS1",
        "Firefly Alpha": "Firefly Alpha",
        "Start": "Start",
        "Start-1": "Start",
        "Start-1.2": "Start",
        "SPARTA": "SPARTA",
        "Jupiter C": "Jupiter C",
        "Falcon 1": "Falcon 1",
        "Minotaur I": "Minotaur 1",
        "Minotaur I Lite": "Minotaur 1",
        "Kosmos 63S1": "Kosmos",
        "Kosmos 11K63": "Kosmos",
        "CE-5 SSQ": "Long March 5",
        "Mu-4S": "Mu",
        "Mu-3C": "Mu",
        "Mu-3H": "Mu",
        "Mu-3S": "Mu",
        "Mu-3S-II": "Mu",
        "Diamant A": "Diamant",
        "Diamant B": "Diamant",
        "Diamant BP.4": "Diamant",
        "Shuang Quxian 1": "Shuang Quxian 1",
        "Gushenxing 1": "Gushenxing 1",
        "Kairos": "Kairos",
        "KT-1": "KT-1",
        "Kuaizhou": "Kuaizhou",
        "Kuaizhou-1A": "Kuaizhou",
        "Zhuque-1": "Zhuque-1",
        "Shavit": "Shavit",
        "Shavit 1": "Shavit",
        "Shavit 2": "Shavit",
        "Astra Rocket 3.1": "Astra Rocket 3",
        "Astra Rocket 3.2": "Astra Rocket 3",
        "Astra Rocket 3.3": "Astra Rocket 3",
        "Qaem-100": "Qaem-100",
        "Paektusan 1": "Paektusan 1",
        "Pegasus": "Pegasus",
        "Pegasus/HAPS": "Pegasus",
        "Pegasus H": "Pegasus",
        "Pegasus XL": "Pegasus",
        "Pegasus XL/HAPS": "Pegasus",
        "Electron": "Electron",
        "HASTE": "Electron",
        "Jielong-1": "Jielong-1",
        "Super Strypi": "Super Strypi",
        "Vanguard": "Vanguard",
        "Scout D-1": "Scout",
        "Scout E-1": "Scout",
        "Scout F-1": "Scout",
        "Scout G-1": "Scout",
        "Blue Scout II": "Scout",
        "Scout X-1": "Scout",
        "Scout X-2": "Scout",
        "Scout X-2B": "Scout",
        "Scout X-2M": "Scout",
        "Scout X-3": "Scout",
        "Scout X-3M": "Scout",
        "Scout X-4": "Scout",
        "Scout A": "Scout",
        "Scout A-1": "Scout",
        "Scout B": "Scout",
        "Scout B-1": "Scout",
        "Conestoga 1620": "Conestoga 1620",
        "VLS-1": "VLS-1",
        "ASLV": "ASLV",
        "SLV-3": "SLV-3",
        "OS-M1": "OS-M1",
        "NOTS EV1": "NOTS EV1",
        "Lambda 4S": "Lambda 4S",
        "SS-520": "SS-520",
        "E-8-5 VA": "E-8-5 VA"
    }
    
    state_name_to_americanized_state_names = {
        "Aus. Antarctic": "Australian Antarctic Territory",
        "Afghanistan": "Afghanistan",
        "Antigua": "Antigua and Barbuda",
        "Hayastan": "Armenia",
        "Ned. Antillen": "Netherlands Antilles",
        "Angola": "Angola",
        "Antartica": "Antarctica",
        "Argentina": "Argentina",
        "Antardida Arg.": "Argentine Antarctica",
        "Osterreich": "Austria",
        "Australia": "Australia",
        "Azerbaycan": "Azerbaijan",
        "Belgique": "Belgium",
        "BAT": "British Antarctic Territory",
        "Barbados": "Barbados",
        "Bangladesh": "Bangladesh",
        "Balgariya": "Bulgaria",
        "NR Balgariya": "Bulgaria",
        "Bahrain": "Bahrain",
        "UK/Bermuda": "Bermuda",
        "Bolivia": "Bolivia",
        "Brasil": "Brazil",
        "Bahamas": "Bahamas",
        "Druk Yul": "Bhutan",
        "BVI": "British Virgin Islands",
        "Botswana": "Botswana",
        "Belarus'": "Belarus",
        "Canada": "Canada",
        "Suisse": "Switzerland",
        "Cote d'Ivoire": "Ivory Coast",
        "Cook Islands": "Cook Islands",
        "Chile": "Chile",
        "Cameroun": "Cameroon",
        "Zhongguo": "China",
        "Colombia": "Colombia",
        "Costa Rica": "Costa Rica",
        "Ceskoslovensko": "Czechoslovakia",
        "Cuba": "Cuba",
        "Cayman Islands": "Cayman Islands",
        "Ceska Rep.": "Czech Republic",
        "BRD": "West Germany",
        "DDR": "East Germany",
        "Djibouti": "Djibouti",
        "Danmark": "Denmark",
        "Dronning Maud": "Queen Maud Land",
        "Deutsches Reich": "German Reich",
        "Deutschland": "Germany",
        "Al Jazair": "Algeria",
        "Espana": "Spain",
        "Earth": "Earth",
        "Ecuador": "Ecuador",
        "Eesti": "Estonia",
        "Misr": "Egypt",
        "Ethiopia": "Ethiopia",
        "France": "France",
        "Suomi": "Finland",
        "Sakartvelo": "Georgia",
        "Ghana": "Ghana",
        "Gibraltar": "Gibraltar",
        "Kalaallit Nunaat": "Greenland",
        "Ellas": "Greece",
        "Grenada": "Grenada",
        "Guatemala": "Guatemala",
        "Guahan": "Guam",
        "Guyane": "French Guiana",
        "Zhongguo/XG": "Hong Kong",
        "Hrvatska": "Croatia",
        "Magyarorzag": "Hungary",
        "Italia": "Italy",
        "Arabsat": "Arabsat",
        "COSPAS-SARSAT": "COSPAS-SARSAT",
        "COSPAS-SARSAT (I)": "COSPAS-SARSAT",
        "ELDO": "European Launcher Development Organisation",
        "ESA": "European Space Agency",
        "ESRO": "European Space Research Organisation",
        "EU": "European Union",
        "EUMETSAT": "European Organisation for the Exploitation of Meteorological Satellites",
        "EUTELSAT": "European Telecommunications Satellite Organization",
        "INMARSAT": "International Maritime Satellite Organization",
        "INTELSAT": "International Telecommunications Satellite Organization",
        "ISS": "International Space Station",
        "NATO": "North Atlantic Treaty Organization",
        "RASCOM": "Regional African Satellite Communication Organization",
        "Indonesia": "Indonesia",
        "Eire": "Ireland",
        "Yisra'el": "Israel",
        "India": "India",
        "Al Iraq": "Iraq",
        "Iran": "Iran",
        "Island": "Iceland",
        "Nippon": "Japan",
        "Jordan": "Jordan",
        "Kenya": "Kenya",
        "Kyrgyzstan": "Kyrgyzstan",
        "Kampuchea": "Cambodia",
        "Kiribati": "Kiribati",
        "Korsou": "Curaçao",
        "Choson": "North Korea",
        "Hanguk": "South Korea",
        "Kuwayt": "Kuwait",
        "Qazaqstan": "Kazakhstan",
        "Luxembourg": "Luxembourg",
        "Pathet Lao": "Laos",
        "Liban": "Lebanon",
        "SriLanka": "Sri Lanka",
        "Lietuva": "Lithuania",
        "Luna": "Moon",
        "Latvija": "Latvia",
        "Al Libiyyah": "Libya",
        "Al Maghrib": "Morocco",
        "Monaco": "Monaco",
        "Moldova": "Moldova",
        "Marshall Is.": "Marshall Islands",
        "Mongol": "Mongolia",
        "Macao": "Macau",
        "Al Muritaniyyah": "Mauritania",
        "Malta": "Malta",
        "Maurice": "Mauritius",
        "Divehi": "Maldives",
        "Mexico": "Mexico",
        "Malaysia": "Malaysia",
        "Myanmar": "Myanmar",
        "Norge": "Norway",
        "Nigeria": "Nigeria",
        "Northern Ireland": "Northern Ireland",
        "Nederland": "Netherlands",
        "Nepal": "Nepal",
        "New Zealand": "New Zealand",
        "Ross Dependency": "Ross Dependency",
        "Oman": "Oman",
        "Portugal": "Portugal",
        "Panama": "Panama",
        "Panama Canal Zone": "Panama Canal Zone",
        "Peru": "Peru",
        "Papua Niugini": "Papua New Guinea",
        "Pilipinas": "Philippines",
        "Pakistan": "Pakistan",
        "Polska": "Poland",
        "Puerto Rico": "Puerto Rico",
        "Palau": "Palau",
        "Paraguay": "Paraguay",
        "Qatar": "Qatar",
        "Romania": "Romania",
        "Rossiya": "Russia",
        "Rwanda": "Rwanda",
        "Sverige": "Sweden",
        "Al Arabiyah": "Saudi Arabia",
        "Sudan": "Sudan",
        "Singapore": "Singapore",
        "St Helena": "Saint Helena",
        "Slovenija": "Slovenia",
        "Slovakia": "Slovakia",
        "Senegal": "Senegal",
        "Suriname": "Suriname",
        "Solar System": "Solar System",
        "SSSR": "Soviet Union",
        "Suriya": "Syria",
        "Prathet Thai": "Thailand",
        "Turks and Caicos": "Turks and Caicos Islands",
        "TAAF": "French Southern and Antarctic Lands",
        "Tajikistan": "Tajikistan",
        "Turkmenistan": "Turkmenistan",
        "Tunisiyah": "Tunisia",
        "Tonga": "Tonga",
        "Turkiye": "Turkey",
        "TTPI": "Trust Territory of the Pacific Islands",
        "Taiwan": "Taiwan",
        "Ukraina": "Russia States",
        "Al Imarat": "United Arab Emirates",
        "Uganda": "Uganda",
        "UK": "United Kingdom",
        "Johnston Atoll": "British Atoll",
        "Wake Iland": "Island",
        "USA": "United States",
        "Uruguay": "Uruguay",
        "Uzbekistan": "Uzbekistan",
        "Vatican": "Vatican City",
        "Venezuela": "Venezuela",
        "Vietnam": "Vietnam",
        "UNKNOWN": "Unknown",
        "al-Yamaniyyah": "Yemen",
        "South Africa": "South Africa",
        "Zaire": "Democratic Republic of the Congo",
        "Zimbabwe": "Zimbabwe"
    }
    
    def __init__(self, dataset_directory="./datasets"):
        self.generate_lv_type_to_lv_family(dataset_directory=dataset_directory)
        self.generate_launch_site_to_state_code(dataset_directory=dataset_directory)
        self.generate_org_to_state_code(dataset_directory=dataset_directory)
        self.generate_state_code_to_state_name(dataset_directory=dataset_directory)
        self.generate_launch_site_to_launch_site_parent(dataset_directory=dataset_directory)
        self.generate_launch_site_to_launch_site_name(dataset_directory=dataset_directory)

    def generate_lv_type_to_lv_family(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate LV_Type to LV_Family.
        This requires lv.tsv file
        Launch Vehicle Families Text File: https://planet4589.org/space/gcat/web/lvs/family/index.html
        """
        
        file_path = f"{dataset_directory}/lv.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            self.lv_type_to_lv_family = {row[0].strip(): row[1].strip() for row in reader}
            
    def generate_launch_site_to_state_code(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate Launch_Site to State_Code.
        This requires launch_site.tsv file
        Launch Sites Text File: https://planet4589.org/space/gcat/data/tables/sites.html
        """
        
        file_path = f"{dataset_directory}/sites.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            self.launch_site_to_state_code = {row[0].strip(): row[4].strip() for row in reader}
            
    def generate_org_to_state_code(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate Launch_Site to State_Code.
        This requires orgs.tsv file
        Launch Sites Text File: https://planet4589.org/space/gcat/data/tables/orgs.html
        """
        
        file_path = f"{dataset_directory}/orgs.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            self.org_to_state_code = {row[0].strip(): row[2].strip() for row in reader}
            
    def generate_state_code_to_state_name(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate State_Code to State_Name.
        This requires orgs.tsv file
        Launch Sites Text File: https://planet4589.org/space/gcat/data/tables/orgs.html
        """
        
        file_path = f"{dataset_directory}/orgs.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            self.state_code_to_state_name = {row[0].strip(): row[7].strip() for row in reader}
    
    def generate_launch_site_to_launch_site_parent(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate Launch_Site to Launch_Site_Parent.
        This requires launch_site.tsv file
        Launch Sites Text File: https://planet4589.org/space/gcat/data/tables/sites.html
        """
        
        file_path = f"{dataset_directory}/sites.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            self.launch_site_to_launch_site_parent = {row[0].strip(): row[7].replace("-","").strip() for row in reader}
    
    def generate_launch_site_to_launch_site_name(self, dataset_directory = "./datasets"):
        """
        Generate a dictionary that translate Launch_Site to Launch_Site_Name.
        This requires launch_site.tsv file
        Launch Sites Text File: https://planet4589.org/space/gcat/data/tables/sites.html
        """
        
        file_path = f"{dataset_directory}/sites.tsv"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            reader.__next__() # Skip the index row
            reader.__next__() # Skip the header row
            # If short name is "-", use default name instead
            self.launch_site_to_launch_site_name = {
                row[0].strip(): row[14].strip() if row[14].strip() != "-" else row[8].strip()
                for row in reader if len(row) > 14
            }
