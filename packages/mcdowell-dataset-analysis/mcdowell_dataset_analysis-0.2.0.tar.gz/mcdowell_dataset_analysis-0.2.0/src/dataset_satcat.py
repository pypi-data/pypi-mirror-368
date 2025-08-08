import pandas as pd
import translations

class Satcat:
    """
    This contains all functions required for using McDowell's satellite catalog dataset.
    """

    def __init__(self, translation=None, dataset_directory="./datasets"):
        """
        Load the raw satcat dataset into a pandas DataFrame.
        
        satcat.tsv column descriptions: https://planet4589.org/space/gcat/web/cat/cols.html
        """
        
        self.dataset_directory = dataset_directory
        self.satcat_path = f"{dataset_directory}/satcat.tsv"
        self.psatcat_path = f"{dataset_directory}/psatcat.tsv"
        self.translation = translation or translations.Translation()
        self.date_updated = None
        
        self.df = pd.read_csv(self.satcat_path, sep="\t", encoding="utf-8", low_memory=False) # load satcat tsv into dataframe
        self.psatcat_df = pd.read_csv(self.psatcat_path, sep="\t", encoding="utf-8", low_memory=False) # load psatcat tsv into dataframe
        
        self.preprocess_satcat_df()
        
        self.process_psatcat_dependent_columns(self.psatcat_df)

    def reload(self):
        """ 
        Undo all filters
        """
        self.__init__(translation=self.translation, dataset_directory=self.dataset_directory)

    def preprocess_satcat_df(self):
        """
        Create new columns from existing columns in satcat dataframe to make it more pandas friendly.
        Lots of string manipulation to get the dates into a format that pandas can understand.
        """
        
        self.date_updated = " ".join(self.df.iloc[0, 0].strip().replace("  ", " ").split(" ")[2:5])
        
        # Remove second row of tsv, signifies date of last update
        self.df = self.df.drop(index=0).reset_index(drop=True)

        # Rename column "#Launch_Tag" to "Launch_Tag"
        self.df.rename(columns={"#JCAT": "JCAT"}, inplace=True)
        
        # Strip Launch_Tags & Piece & JCAT
        self.df["Launch_Tag"] = self.df["Launch_Tag"].astype(str).str.upper().str.strip()
        self.df["Piece"] = self.df["Piece"].astype(str).str.upper().str.strip()
        self.df["JCAT"] = self.df["JCAT"].astype(str).str.upper().str.strip()
        
        date_cols = ["LDate", "SDate", "DDate", "ODate"]
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
        
        # Rename date columns
        self.df.rename(columns={"LDate": "Launch_Date", "SDate": "Separation_Date", "DDate": "Decay_Date", "ODate": "Orbit_Canonical_Date"}, inplace=True)

        # Convert numeric fields to int or float and handle NaN
        self.df["Mass"] = pd.to_numeric(self.df["Mass"], errors="coerce").fillna(0)
        self.df["DryMass"] = pd.to_numeric(self.df["DryMass"], errors="coerce").fillna(0)
        self.df["TotMass"] = pd.to_numeric(self.df["TotMass"], errors="coerce").fillna(0)
        self.df["Length"] = pd.to_numeric(self.df["Length"], errors="coerce").fillna(0)
        self.df["Diameter"] = pd.to_numeric(self.df["Diameter"], errors="coerce").fillna(0)
        self.df["Span"] = pd.to_numeric(self.df["Span"], errors="coerce").fillna(0)
        self.df["Perigee"] = pd.to_numeric(self.df["Perigee"], errors="coerce").fillna(0)
        self.df["Apogee"] = pd.to_numeric(self.df["Apogee"], errors="coerce").fillna(0)
        self.df["Inc"] = pd.to_numeric(self.df["Inc"], errors="coerce").fillna(0)
        
        # Create Simple Orbit Column
        # Orbits: https://planet4589.org/space/gcat/web/intro/orbits.html
        self.df["Simple_Orbit"] = self.df["OpOrbit"].str.strip()
        self.df["Simple_Orbit"] = self.df["Simple_Orbit"].replace(self.translation.opOrbit_to_simple_orbit)
        
        self.df["Country"] = self.df["State"].map(self.translation.state_code_to_state_name).map(self.translation.state_name_to_americanized_state_names)
    
    def process_psatcat_dependent_columns(self, psatcat):
        """
        Create columns in satcat dataframe derived from psatcat data:
        - Payload_Name (Name)
        - Payload_Program (Program)
        - Payload_Class (Class)
        - Payload_Category (Category)
        - Payload_Discipline (Discipline)
        - Payload_Result (Result)
        - Payload_Comment (Comment)
        Args:
            psatcat: dataframe containing psatcat tsv
        Psatcat: https://planet4589.org/space/gcat/data/cat/psatcat.html  
        Psatcat column descriptions: https://planet4589.org/space/gcat/web/cat/pscols.html
        """
        
        psatcat_df = psatcat.copy()
        
        # Rename to avoid confusion with satcat columns
        psatcat_df.rename(columns={"#JCAT": "JCAT", "Name": "Payload_Name", "Program": "Payload_Program", "Class": "Payload_Class", "Category": "Payload_Category", "Discipline": "Payload_Discipline", "Result": "Payload_Result", "Comment": "Payload_Comment"}, inplace=True)
        
        # Strip JCAT
        psatcat_df["JCAT"] = psatcat_df["JCAT"].astype(str).str.upper().str.strip()
        
        # Merge satcat_df with psatcat_df to get Name, using left join to keep all satellites
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Name"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Program"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Class"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Category"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Discipline"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Result"]],
            on="JCAT",
            how="left"
        )
        
        self.df = self.df.merge(
            psatcat_df[["JCAT", "Payload_Comment"]],
            on="JCAT",
            how="left"
        )
        
        self.df["Simple_Payload_Category"] = self.df["Payload_Category"].str.strip()
        self.df["Simple_Payload_Category"] = self.df["Simple_Payload_Category"].replace(self.translation.payload_category_to_simple_payload_category)
        
    
    def process_launch_dependent_columns(self, launch):
        """
        Create columns in satcat_df derived from launch data:
        - LV_Type: The tag of the launch that the satellite was launched on
        - Agency: The launch provider
        - Launch Site
        - Launch Pad
        Args:
            launch_df: DataFrame containing the launch class.
        """
        
        # For every satellite, get the corresponding launch vehicle from the launch_df by using the Launch_Tag column to merge the two dataframes
        launch_df = launch.df.copy()
        
        launch_df.rename(columns={"State": "Launch_State", "Country": "Launch_Country"}, inplace=True)
        
        # Merge satcat_df with launch_df to get LV_Type, using left join to keep all satellites
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "LV_Type"]],
            on="Launch_Tag",
            how="left"
        )
        
        # Merge satcat_df with launch_df to get Agency, using left join to keep all satellites
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Agency"]],
            on="Launch_Tag",
            how="left"
        )
        
        # Merge satcat_df with launch_df to get Launch_Site, using left join to keep all satellites
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Site"]],
            on="Launch_Tag",
            how="left"
        )
        
        # Merge satcat_df with launch_df to get Launch_Pad, using left join to keep all satellites
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Pad"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Vehicle_Family"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Vehicle_Simplified"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Site_Parent"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Site_Name"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_State"]],
            on="Launch_Tag",
            how="left"
        )
        
        self.df = self.df.merge(
            launch_df[["Launch_Tag", "Launch_Country"]],
            on="Launch_Tag",
            how="left"
        )
        
        # Fill NaN with empty string for unmatched launches
        self.df["LV_Type"] = self.df["LV_Type"].fillna("")
        self.df["Agency"] = self.df["Agency"].fillna("")
        self.df["Launch_Site"] = self.df["Launch_Site"].fillna("")
        self.df["Launch_Pad"] = self.df["Launch_Pad"].fillna("")
        self.df["Launch_Vehicle_Family"] = self.df["Launch_Vehicle_Family"].fillna("")
        self.df["Launch_Vehicle_Simplified"] = self.df["Launch_Vehicle_Simplified"].fillna("")
        self.df["Launch_Site_Parent"] = self.df["Launch_Site_Parent"].fillna("")
        self.df["Launch_Site_Name"] = self.df["Launch_Site_Name"].fillna("")
        self.df["Launch_State"] = self.df["Launch_State"].fillna("")
        self.df["Launch_Country"] = self.df["Launch_Country"].fillna("")
