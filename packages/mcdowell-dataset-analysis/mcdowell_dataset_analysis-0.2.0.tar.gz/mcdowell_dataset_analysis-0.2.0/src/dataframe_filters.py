import pandas as pd
import dataset_satcat
import dataset_launch
    
class Filters:
    """
    This class contains all functions required for filtering the datasets. This includes filtering by date, launch vehicle, launch site, etc.
    """

    def __init__(self):
        pass

    def filter_column_by_contains(dataset_class, contains_pattern, column, case=False, negate=False):
        """
        Filter a DataFrame by a column containing a specific pattern.
        This is more general if no other filter suits your needs.
        Args:
            dataset_class: The dataset class to filter.
            column: The column to filter by.
            contains_pattern: The pattern to filter by.
            case: Whether the filter should be case-sensitive. Defaults to False.
            negate: If True, negate the condition (i.e., keep rows that do not contain the pattern). Defaults to False.
        """
        
        if (type(contains_pattern) == str):
            contains_pattern = [contains_pattern]
        
        condition = False
        for pattern in contains_pattern:
            condition = condition | dataset_class.df[column].str.contains(pattern, case=case, na=False)
            
        if negate:
            condition = ~condition
            
        dataset_class.df = dataset_class.df[condition]

    def filter_column_by_exact(dataset_class, exact_pattern, column, case=False, negate=False):
        """
        Filter a DataFrame by a column containing an exact pattern.
        This is more general if no other filter suits your needs.
        Args:
            dataset_class: The dataset class to filter.
            column: The column to filter by.
            contains_pattern: The exact pattern to filter by.
            case: Whether the filter should be case-sensitive. Defaults to False.
            negate: If True, negate the condition (i.e., keep rows that do not contain the pattern). Defaults to False.
        """
        
        if (type(exact_pattern) == str):
            exact_pattern = [exact_pattern]
        
        # Use regex for exact match
        condition = False
        for pattern in exact_pattern:
            condition = condition | dataset_class.df[column].str.contains(f"^{pattern}$", case=case, na=False, regex=True)
            
        if negate:
            condition = ~condition
            
        dataset_class.df = dataset_class.df[condition]

    def filter_by_mission(dataset_class, pattern, column="Mission", case=False, negate=False):
        """
        Filter by regex pattern in a specified column (e.g., 'Starlink' in Mission).
        Used to filter by mission type (eg. if you want all Starlink launches)
        """
        
        if (type(dataset_class) != dataset_launch.Launch):
            raise ValueError("Launch dataset expected by filter_by_mission(). Cannot sort by mission in satcat dataset.")
        
        condition = dataset_class.df[column].str.contains(pattern, case=case, na=False, regex=True)
        if negate:
            condition = ~condition
            
        dataset_class.df = dataset_class.df[condition]

    def filter_by_Object_Name(dataset_class, pattern, column="PLName", case=False, negate=False):
        """
        Filter by regex pattern in a specified column (e.g., 'Starlink' in Object_Name).
        Used to filter by objects of the same series, eg. all Starlink satellites
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("Satcat dataset expected by filter_by_Object_Name(). Cannot sort by object name in launch dataset.")
        
        condition = dataset_class.df[column].str.contains(pattern, case=case, na=False, regex=True)
        if negate:
            condition = ~condition
            
        dataset_class.df = dataset_class.df[condition]

    def filter_by_launch_category(dataset_class, launch_categories, negate=False):
        """
        Remove all launches that are not in the given launch categories.
        Args:
            launch_categories: List of launch categories to filter by. eg. ["O", "R", "M"]
            negate: If True, remove all launches that are in the given launch categories. Defaults to False.
            
        O: Orbital  
        S: Suborbital (non-missile)  
        D: Deep Space  
        M: Military Missile  
        T: Test Rocket  
        A: Atmospheric Rocket  
        H: High Altitude Sounding Rocket  
        R: Reentry Test  
        X: Launch from Non-Earth World  
        Y: Suborbital Spaceplane (Human Crew)  
        Source: https://planet4589.org/space/gcat/web/launch/lcols.html  
        """
        
        if (type(dataset_class) != dataset_launch.Launch):
            raise ValueError("Launch dataset expected by filter_by_launch_category(). Cannot sort by launch category in satcat dataset.")
        
        if (type(launch_categories) == str):
            launch_categories = [launch_categories]
        
        condition = dataset_class.df["LaunchCode"].str[0].isin(launch_categories)
        if negate:
            condition = ~condition
        
        # vectorized operation to filter the DataFrame
        # Faster than a for loop for some reason, kind vibe coding here tbh
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_launch_success_fraction(dataset_class, launch_success_fractions, negate=False):
        """
        Remove all launches that are not in the given launch success fractions.
        Args:
            launch_success_fractions: List of launch success fractions to filter by. eg. ["S", "F"]
            negate: If True, remove all launches that are in the given launch success fractions. Defaults to False.
            
        S: Success (propulsive success, regardless of payload data)  
        F: Failure  
        U: Unknown  
        E: Pad Explosion (no launch, included for completeness)  
        Source: https://planet4589.org/space/gcat/web/launch/lcols.html
        """
        
        if (type(dataset_class) != dataset_launch.Launch):
            raise ValueError("Launch dataset expected by filter_by_launch_success_fraction(). Cannot sort by launch success fraction in satcat dataset.")
        
        if (type(launch_success_fractions) == str):
            launch_success_fractions = [launch_success_fractions]
        
        condition = dataset_class.df["Launch_Code"].str[1].isin(launch_success_fractions)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_launch_vehicle_name_simplified(dataset_class, launch_vehicles, negate=False):
        """
        Remove all launches that are not in the given launch vehicles.
        Args:
            launch_vehicles: List of launch vehicles to filter by. eg. ["Falcon 9", "Starship", "Soyuz]
            negate: If True, remove all launches that are in the given launch vehicles. Defaults to False.
        """
        
        if (type(launch_vehicles) == str):
            launch_vehicles = [launch_vehicles]
        
        condition = dataset_class.df["Launch_Vehicle_Simplified"].isin(launch_vehicles)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_launch_vehicle_name_raw(dataset_class, launch_vehicles, negate=False):
        """
        Remove all launches that are not in the given launch vehicles.
        Args:
            launch_vehicles: List of launch vehicles to filter by. eg. ["Kosmos 11K65M", "Falcon 9", "Starship V1.0 Ship"]
            negate: If True, remove all launches that are in the given launch vehicles. Defaults to False.
        Launch Vehicle List: https://planet4589.org/space/gcat/data/tables/lv.html
        """
        
        if (type(launch_vehicles) == str):
            launch_vehicles = [launch_vehicles]
        
        condition = dataset_class.df["LV_Type"].isin(launch_vehicles)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_launch_vehicle_family(dataset_class, launch_vehicle_families, negate=False):
        """
        Remove all launches that are not in the given launch vehicle families.
        Args:
            launch_vehicle_families: List of launch vehicles to filter by. eg. ["Electron", "Falcon9"]
            negate: If True, remove all launches that are in the given launch vehicle families. Defaults to False.
        Launch Vehicle Family List: https://planet4589.org/space/gcat/data/tables/family.html  
        Launch Vehicle List (With Family): https://planet4589.org/space/gcat/data/tables/lv.html
        """
        
        if (type(launch_vehicle_families) == str):
            launch_vehicle_families = [launch_vehicle_families]
        
        condition = dataset_class.df["Launch_Vehicle_Family"].isin(launch_vehicle_families)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_launch_site_raw(dataset_class, launch_sites, negate=False):
        """
        Remove all launches that are not in the given launch sites.
        Args:
            launch_sites: List of launch sites to filter by. eg. ["VFSB", "KSC"]
            negate: If True, remove all launches that are in the given launch sites. Defaults to False.
        """
        
        if (type(launch_sites) == str):
            launch_sites = [launch_sites]
        
        condition = dataset_class.df["Launch_Site"].isin(launch_sites)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_launch_pad_raw(dataset_class, launch_pads, negate=False):
        """
        Remove all launches that are not in the given launch pads.
        Args:
            launch_pads: List of launch pads to filter by. eg. ["SLC4E", "LC39A"]
            negate: If True, remove all launches that are in the given launch pads. Defaults to False.
        """
        
        if (type(launch_pads) == str):
            launch_pads = [launch_pads]
        
        condition = dataset_class.df["Launch_Pad"].isin(launch_pads)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_sat_type_coarse(dataset_class, sat_types, negate=False):
        """
        Remove all launches that are not in the given launch categories.
        Args:
            launch_categories: List of launch categories to filter by. eg. ["P", "R"]
            negate: If True, remove all launches that are in the given launch categories. Defaults to False.
        """

        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_sat_type_coarse(). Cannot sort by sat type in launch dataset.")
        
        if (type(sat_types) == str):
            sat_types = [sat_types]
        
        condition = dataset_class.df["Type"].str[0].isin(sat_types)
        if negate:
            condition = ~condition
        
        # vectorized operation to filter the DataFrame
        # Faster than a for loop for some reason, kind vibe coding here tbh - nvm I've learned now python is not a real language
        dataset_class.df = dataset_class.df[condition]
    
    def filter_by_payload_category_raw(dataset_class, payload_categories, negate=False):
        """
        Remove all launches that are not in the given payload types.
        Args:
            payload_categories: List of payload types to filter by. eg. ["Other", "Communications"]
            negate: If True, remove all launches that are in the given payload types. Defaults to False.
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_payload_category_raw(). Cannot sort by sat type in launch dataset.")
        
        if (type(payload_categories) == str):
            payload_categories = [payload_categories]
        
        condition = dataset_class.df["Payload_Category"].isin(payload_categories)
        if negate:
            condition = ~condition
        dataset_class.df = dataset_class.df[condition]
    
    def filter_by_simple_payload_category(dataset_class, payload_categories, negate=False):
        """
        Remove all launches that are not in the given payload types.
        Args:
            payload_categories: List of payload types to filter by. eg. ["Other", "Communications"]
            negate: If True, remove all launches that are in the given payload types. Defaults to False.
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_simple_payload_type(). Cannot sort by sat type in launch dataset.")
        
        if (type(payload_categories) == str):
            payload_categories = [payload_categories]
        
        condition = dataset_class.df["Simple_Payload_Category"].isin(payload_categories)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_payload_program_raw(dataset_class, payload_programs, negate=False):
        """
        Remove all launches that are not in the given payload programs.
        Args:
            payload_programs: List of payload programs to filter by. eg. ["Other", "Communications"]
            negate: If True, remove all launches that are in the given payload programs. Defaults to False.
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_payload_program_raw(). Cannot sort by sat type in launch dataset.")
        
        if (type(payload_programs) == str):
            payload_programs = [payload_programs]
        
        condition = dataset_class.df["Payload_Program"].isin(payload_programs)
        if negate:
            condition = ~condition
        
        # vectorized operation to filter the DataFrame
        # Faster than a for loop for some reason, kind vibe coding here tbh
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_launch_date(dataset_class, start_date=None, end_date=None):
        """
        Remove all launches that are not in the given date range (inclusive range).
        Args:
            start_date: Start date to filter by. eg. "2000-01-01"
            end_date: End date to filter by. eg. "2020-01-01"
        """
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if start_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Launch_Date"] >= start_date]
        
        if end_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Launch_Date"] <= end_date]

    def filter_by_separation_date(dataset_class, start_date=None, end_date=None):
        """
        Remove all launches that are not in the given date range (inclusive range).
        Args:
            start_date: Start date to filter by. eg. "2000-01-01"
            end_date: End date to filter by. eg. "2020-01-01"
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_separation_date(). Cannot sort by separation date in launch dataset.")
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if start_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Separation_Date"] >= start_date]
        
        if end_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Separation_Date"] <= end_date]

    def filter_by_decay_date(dataset_class, start_date=None, end_date=None):
        """
        Remove all launches that are not in the given date range (inclusive range).
        Args:
            start_date: Start date to filter by. eg. "2000-01-01"
            end_date: End date to filter by. eg. "2020-01-01"
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset  expected by filter_by_decay_date(). Cannot sort by decay date in launch dataset.")
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if start_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Decay_Date"] >= start_date]
        
        if end_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Decay_Date"] <= end_date]

    def filter_by_orbit_canonical_date(dataset_class, start_date=None, end_date=None):
        """
        Remove all launches that are not in the given date range (inclusive range).
        Args:
            start_date: Start date to filter by. eg. "2000-01-01"
            end_date: End date to filter by. eg. "2020-01-01"
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset class expected by filter_by_orbit_canonical_date(). Cannot sort by orbit canonical date in launch dataset.")
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if start_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Orbit_Canonical_Date"] >= start_date]
        
        if end_date is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Orbit_Canonical_Date"] <= end_date]
    
    def filter_by_mass(dataset_class, min_mass=None, max_mass=None):
        """
        Remove all launches or satellties that are not in the given mass range (inclusive range).
        Args:
            dataset_class: launch or satcat
            min_mass (float, optional): Minimum mass (inclusive). Defaults to None.
            max_max (float, optional): Maximum mass (inclusive). Defaults to None.
        """
        
        mass_col = "Payload_Mass"
        if (type(dataset_class) == dataset_satcat.Satcat):
            mass_col = "Mass"
            
        if min_mass is not None:
            dataset_class.df = dataset_class.df[dataset_class.df[mass_col] >= min_mass]
        
        if max_mass is not None:
            dataset_class.df = dataset_class.df[dataset_class.df[mass_col] <= max_mass]
            
    def filter_by_orbit_raw(dataset_class, orbits, negate=False):
        """
        Remove all launches that are not in the given orbit. This uses Jonathan McDowell's raw orbit tags. Eg. "LLEO/I", "VHEO", "DSO", "GEO/NS"
        See https://planet4589.org/space/gcat/web/intro/orbits.html for more information.
        Args:
            dataset_class: launch or satcat
            orbit (string or string array): orbit tag, see: https://planet4589.org/space/gcat/web/intro/orbits.html
            negate (bool, optional): If True, remove all launches that are in the given orbit. Defaults to False.
        """
        
        if type(orbits) == str:
            orbits = [orbits]
        
        condition = dataset_class.df["OpOrbit"].isin(orbits)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_orbit(dataset_class, orbits, negate=False):
        """
        Remove all launches that are not in the given orbit. This uses simple orbit categories. Eg. "LEO", "MEO", "GTO", "BEO"
        Args:
            dataset_class: launch or satcat
            orbits (string or string array): simple orbit tags 
            negate (bool, optional): If True, remove all launches that are in the given orbit. Defaults to False.
        """
        
        if type(orbits) == str:
            orbits = [orbits]
        
        condition = dataset_class.df["Simple_Orbit"].isin(orbits)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_apogee(dataset_class, min_apogee=None, max_apogee=None):
        """
        Remove all launches that are not in the given apogee range (inclusive range).
        Args:
            dataset_class: launch or satcat
            min_apogee (float, optional): Minimum apogee (inclusive). Defaults to None.
            max_apogee (float, optional): Maximum apogee (inclusive). Defaults to None.
        """
        
        if min_apogee is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Apogee"] >= min_apogee]
        
        if max_apogee is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Apogee"] <= max_apogee]
    
    def filter_by_perigee(dataset_class, min_perigee=None, max_perigee=None):
        """
        Remove all launches that are not in the given perigee range (inclusive range).
        Args:
            dataset_class: launch or satcat
            min_perigee (float, optional): Minimum perigee (inclusive). Defaults to None.
            max_perigee (float, optional): Maximum perigee (inclusive). Defaults to None.
        """
        
        if min_perigee is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Perigee"] >= min_perigee]
        
        if max_perigee is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Perigee"] <= max_perigee]

    def filter_by_inclination(dataset_class, min_inclination=None, max_inclination=None):
        """
        Remove all launches that are not in the given inclination range (inclusive range).
        Args:
            dataset_class: launch or satcat
            min_inclination (float, optional): Minimum inclination (inclusive). Defaults to None.
            max_inclination (float, optional): Maximum inclination (inclusive). Defaults to None.
        """
        
        if min_inclination is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Inc"] >= min_inclination]
        
        if max_inclination is not None:
            dataset_class.df = dataset_class.df[dataset_class.df["Inc"] <= max_inclination]

    def filter_by_manufacturer(dataset_class, manufacturers, negate=False):
        """
        Remove all launches that are not in the given manufacturers.
        Args:
            dataset_class: launch or satcat
            manufacturers: List of manufacturers to filter by. eg. ["SpaceX", "Rocket Lab"]
            negate: If True, remove all launches that are in the given manufacturers. Defaults to False.
        """
        
        if (type(dataset_class) != dataset_satcat.Satcat):
            raise ValueError("satcat dataset expected by filter_by_manufacturer(). Cannot sort by manufacturer in launch dataset.")
        
        if (type(manufacturers) == str):
            manufacturers = [manufacturers]
        
        condition = dataset_class.df["Manufacturer"].isin(manufacturers)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_state_code(dataset_class, state_codes, negate=False):
        """
        Remove all launches that are not in the given state codes.
        Args:
            dataset_class: launch or satcat
            state_codes: List of state codes to filter by. eg. ["US", "ID"]
            negate: If True, remove all launches that are in the given state codes. Defaults to False.
        """
        
        if (type(state_codes) == str):
            state_codes = [state_codes]
        
        condition = dataset_class.df["State"].isin(state_codes)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]

    def filter_by_country(dataset_class, countries, negate=False):
        """
        Remove all launches that are not in the given country names.
        Args:
            dataset_class: launch or satcat
            countries: List of country names to filter by. eg. ["Canada", "Indonesia"]
            negate: If True, remove all launches that are in the given country names. Defaults to False.
        """
        
        if (type(countries) == str):
            countries = [countries]
        
        condition = dataset_class.df["Country"].isin(countries)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_launch_site(dataset_class, launch_sites, negate=False):
        """
        Remove all launches that are not in the given launch sites.
        Args:
            dataset_class: launch or satcat
            launch_sites: List of launch sites to filter by. eg. ["Vandenberg Space Force Base", "Kennedy Space Center"]
            negate: If True, remove all launches that are in the given launch sites. Defaults to False.
        See https://planet4589.org/space/gcat/data/tables/sites.html
        """
        
        if (type(launch_sites) == str):
            launch_sites = [launch_sites]
        
        condition = dataset_class.df["Launch_Site_Parent"].isin(launch_sites)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]
        
    def filter_by_launch_site_name(dataset_class, launch_site_names, negate=False):
        """
        Remove all launches that are not in the given launch site names.
        Args:
            dataset_class: launch or satcat
            launch_site_names: List of launch site names to filter by. eg. ["Vandenberg Space Force Base", "Canaveral"]
            negate: If True, remove all launches that are in the given launch site names. Defaults to False.
        See https://planet4589.org/space/gcat/data/tables/sites.html
        Note that this is done off of launch site parents, which groups based on the ShortName column of sites.tsv.
        It then converts into either the ShortEName or Name column if ShortEName is not present.
        """
        
        if (type(launch_site_names) == str):
            launch_site_names = [launch_site_names]
        
        condition = dataset_class.df["Launch_Site_Name"].isin(launch_site_names)
        if negate:
            condition = ~condition
        
        dataset_class.df = dataset_class.df[condition]