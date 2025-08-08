import pandas as pd
from dataset_launch import Launch
from dataset_satcat import Satcat
from dataframe_filters import Filters
from translations import Translation
from chart_utils import ChartUtils

# Expose Launch and Satcat directly in this module's namespace
# This allows for "import mcdowell_dataset_analysis" to allow for Launch.preprocess_launch_df() to work without having to import Launch
# Ie. single import instead of the mess you see above
__all__ = ['Launch', 'Satcat', 'Filters', 'McdowellDataset', 'Translation', 'ChartUtils', "standard_chart_generation"]

class McdowellDataset:
    """
    This class serves as a wrapper for the Launch and Satcat classes, providing a unified interface for analysis.
    """
    
    def __init__(self, dataset_directory="./datasets"):
        self.translation = Translation(dataset_directory=dataset_directory)
        
        self.launch = Launch(self.translation, dataset_directory=dataset_directory)
        self.satcat = Satcat(self.translation, dataset_directory=dataset_directory)
        
        self.launch.process_satcat_dependent_columns(self.satcat)
        self.launch.add_custom_launch_types()
        
        self.satcat.process_launch_dependent_columns(self.launch)
        
        self.date_updated = self.launch.date_updated # Take date updated from the launch dataset arbitrarily
        
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
    
    def reload(self):
        self.launch.reload()
        self.satcat.reload()