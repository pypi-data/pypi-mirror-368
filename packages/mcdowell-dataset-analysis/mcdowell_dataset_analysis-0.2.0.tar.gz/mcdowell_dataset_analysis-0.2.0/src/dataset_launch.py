import pandas as pd
import translations
import custom_launch_types

class Launch:
    """
    This contains all functions required for using McDowell's launch dataset.
    """

    def __init__(self, translation=None, dataset_directory="./datasets"):
        """
        Initialize launch tsv file path and load the dataset into a pandas DataFrame.
        
        Launch.tsv column descriptions: https://planet4589.org/space/gcat/web/launch/lcols.html
        """
    
        self.dataset_directory = dataset_directory
        self.launch_path = f"{dataset_directory}/launch.tsv"
        self.auxcat_path = f"{dataset_directory}/auxcat.tsv"
        self.translation = translation or translations.Translation() # beautiful Pythonic syntax!
        self.date_updated = None
        
        self.df = pd.read_csv(self.launch_path, sep="\t", encoding="utf-8", low_memory=False) # load tsv into dataframe
        self.auxcat_df = pd.read_csv(self.auxcat_path, sep="\t", encoding="utf-8", low_memory=False) # load psatcat tsv into dataframe
        
        self.preprocess_launch_df()

    def reload(self):
        """ 
        Undo all filters
        """
        self.__init__(translation=self.translation, dataset_directory=self.dataset_directory)
    
    def preprocess_launch_df(self):
        """
        Create new columns from existing columns in satcat dataframe to make it more pandas friendly.
        Lots of string manipulation to get the dates into a format that pandas can understand.
        """
        
        self.date_updated = " ".join(self.df.iloc[0, 0].strip().replace("  ", " ").split(" ")[2:5])
        
        # Remove second row of tsv, signifies date of last update
        self.df = self.df.drop(index=0).reset_index(drop=True)
        
        # Rename column "#Launch_Tag" to "Launch_Tag"
        self.df.rename(columns={"#Launch_Tag": "Launch_Tag"}, inplace=True)
        
        # Strip Launch_Tags
        self.df["Launch_Tag"] = self.df["Launch_Tag"].astype(str).str.upper().str.strip()
        self.df["LV_Type"] = self.df["LV_Type"].astype(str).str.strip()
        
        date_cols = ["Launch_Date"]
        for col in date_cols:
            # Remove problematic characters from date columns (?, -) and handle NaN
            self.df[col] = self.df[col].str.strip().fillna("").str.replace(r"[?-]", "", regex=True).str.strip()
            # Replace double space "  " with single space " " - Sputnik 1 edge case!
            self.df[col] = self.df[col].str.replace(r"\s{2,}", " ", regex=True).str.strip()
            # Only include characters before the third space in all date columns (Remove hour/min/sec as unneeded and messes with data frame time formatting)
            self.df[col] = self.df[col].str.split(" ", n=3).str[:3].str.join(" ").str.strip()
            # Add " 1" to the end of all dates that only contain year and month (assuming this is all 8 character dates) eg. "2023 Feb" -> "2023 Feb 1"
            self.df[col] = self.df[col].where(self.df[col].str.len() != 8, self.df[col] + " 1")
            # Convert Mcdowell's Vague date format to pandas datetime format
            self.df[col] = pd.to_datetime(self.df[col], format="%Y %b %d", errors="coerce")

        self.df["Simple_Orbit"] = self.df["Category"].str.split(" ").str[1].str.strip() # Extract orbit from category eg. "Sat SSO SD 0"
        self.df["Simple_Orbit"] = self.df["Simple_Orbit"].where(self.df["Simple_Orbit"].isin(self.translation.launch_category_to_simple_orbit.keys()), float("nan")) # If raw orbit not present in dictionary keys, NaN
        self.df["Simple_Orbit"] = self.df["Simple_Orbit"].replace(self.translation.launch_category_to_simple_orbit) # Translate to simple orbit

        self.df["Launch_Vehicle_Family"] = self.df["LV_Type"].map(self.translation.lv_type_to_lv_family) # Translate LV_Type to LV_Family using the translation dictionary
        self.df["Launch_Vehicle_Simplified"] = self.df["LV_Type"].map(self.translation.orbital_lv_name_to_lv_simplified) # Translate LV_Type to LV_Simplified using the translation dictionary
        
        self.df["State"] = self.df["Launch_Site"].map(self.translation.launch_site_to_state_code) # Translate Launch_Site to State using the translation dictionary
        self.df["Country"] = self.df["State"].map(self.translation.state_code_to_state_name).map(self.translation.state_name_to_americanized_state_names)
        
        self.df["Launch_Site_Parent"] = self.df["Launch_Site"].map(self.translation.launch_site_to_launch_site_parent)
        self.df["Launch_Site_Name"] = self.df["Launch_Site_Parent"].map(self.translation.launch_site_to_launch_site_name) # Translate Launch_Site to Launch_Site_Name using the translation dictionary

    def process_satcat_dependent_columns(self, satcat):
        """
        Create columns in launch_df derived from satcat data:
        - Payload_Mass: Sum of masses for all payloads in a launch
        - Canonical Orbit Parameters: [ODate, Ap, Pe, Inc, OpOrbit, Simple Orbit]
        Args:
            satcat_df: DataFrame containing the satcat class.
        """
        
        satcat_df = satcat.df.copy()
        
        payload_masses = (
            satcat_df
            .loc[satcat_df['Type'].str.startswith('P', na=False)] # Keep only payloads from satcat
            .groupby('Launch_Tag')['Mass'] # Group by launch tag and sum the masses of the payloads
            .sum()
        )
        
        # Create new column in launch_df for payload mass
        self.df['Payload_Mass'] = self.df['Launch_Tag'].map(payload_masses)
        
        #pick the first payload row for every Launch_Tag
        first_payload = (
            satcat_df
              .loc[satcat_df['Type'].str.startswith('P', na=False)]
              .drop_duplicates('Launch_Tag', keep='first')
              .set_index('Launch_Tag')
        )
        
        # Note that here we make the first payload listed on the launch the simple payload category.
        first_payload.rename(columns={'Simple_Payload_Category': 'First_Simple_Payload_Category', 'Payload_Class': 'First_Payload_Class'}, inplace=True)
        
        # Create new columns in launch_df for canonical orbit data
        for col in ['Orbit_Canonical_Date', 'Perigee', 'Apogee', 'Inc', 'OpOrbit', 'First_Simple_Payload_Category', 'First_Payload_Class']:
            self.df[col] = self.df['Launch_Tag'].map(first_payload[col])
        
        # make pandas show it all
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
            
    def process_auxcat_dependent_columns(self):
        """
        If the given launch has a second stage auxcat entry, use this as the canonical orbit.
        - Canonical Orbit Parameters: [ODate, Ap, Pe, Inc, OpOrbit, Simple Orbit]
        Args:
            auxcat: DataFrame containing the auxcat class.
            
        See this to find out why this is required: https://x.com/planet4589/status/1913770672565764139
        ie. Use the second stage auxcat entry for Falcon 9 launches to get the correct initial orbit parameters.
        Especially Starlink satelites start moving quickly, so we can't just use the first satellite as the initial orbit, since this data seems to be delayed a couple days after launch. Instead, S2.
        From testing, seems to be a 1km difference, but not a useless improvement.
        Future Chris: I took notes for this I pasted the images onto Discord. 
        """
        
        auxcat_df = self.auxcat_df.copy()
        
        # Strip Launch_Tags
        auxcat_df["Launch_Tag"] = auxcat_df["Launch_Tag"].astype(str).str.upper().str.strip()
        
        auxcat_df.rename(columns={"ODate": "Orbit_Canonical_Date"}, inplace=True)
        
        # Filter auxcat for second stage entries (Type starts with 'R', and go with highest proceeding number (stage number I think))
        # Only for Falcon 9 for now
        second_stage_auxcat = (
            auxcat_df
            .loc[auxcat_df['Name'].str.contains('Falcon 9', na=False)]
            .loc[auxcat_df['Type'].str.startswith('R', na=False)]
            .sort_values(by='Type', ascending=False)
            .drop_duplicates(subset='Launch_Tag', keep='first')
        )
        
        # Convert numeric columns to float64 to match self.df dtypes
        for col in ['Apogee', 'Perigee', 'Inc']:
            second_stage_auxcat[col] = pd.to_numeric(second_stage_auxcat[col], errors='coerce')
        
        second_stage_auxcat["Simple_Orbit"] = second_stage_auxcat["OpOrbit"].replace(self.translation.opOrbit_to_simple_orbit) # Translate to simple orbit
        
        # Update existing columns in self.df with values from second_stage_auxcat, overwriting all matching entries
        for col in ['Orbit_Canonical_Date', 'Apogee', 'Perigee', 'Inc', 'OpOrbit', 'Simple_Orbit']:
            mapping = second_stage_auxcat.set_index('Launch_Tag')[col] # Create a mapping from Launch_Tag to the column value
            self.df.loc[self.df['Launch_Tag'].isin(mapping.index), col] = self.df['Launch_Tag'].map(mapping) # Update self.df[col] where Launch_Tag exists in mapping
            
    def add_custom_launch_types(self):
        self.df = custom_launch_types.add_general_launch_payload_type(self.df)