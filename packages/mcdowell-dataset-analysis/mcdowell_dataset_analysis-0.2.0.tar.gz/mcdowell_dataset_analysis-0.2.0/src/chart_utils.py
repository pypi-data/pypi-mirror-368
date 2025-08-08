import pandas as pd
import plotly.express as px
import plotly.io as pio
import copy
import os

class ChartUtils:
    """
    This class contains utility functions for working with dataframes and generating charts.
    """
    
    orbit_color_map = {
        'LEO': '#ffc000',
        'SSO': "#ffdf80",
        'MEO': '#cc0000',
        'GTO': '#3d85c6',
        'GEO': '#1155cc',
        'HEO': "#51606e",
        'BEO': '#3c4043'
    }
    
    f9_site_color_map={
        'LC40': '#fbbc04',
        'LC39A': '#cc0000',
        'SLC4E': '#3c78d8',
    }
    
    general_launch_payload_type_color_map = {
        'Starlink': "#005eff",
        'Commercial': "#fbbc04",
        'Chinese Commercial': '#ffd966',
        'Government': "#008F11",
        'Eastern Government': "#2b700d",
        'Military': "#ff0000",
        'Eastern Military': '#cc0000',
        'Unknown': "#202020",
    }
    
    simple_payload_category_color_map = {
        'Observation': "#1155cc",
        'Communications': "#fbbc04",
        'Science': "#3ba735",
        'Tech Demo': "#ee1111",
        'Other': "#434343",
    }

    # https://planet4589.org/space/gcat/web/cat/pcols.html
    payload_operator_color_map = {
        "Academic": "#005eff",  # A (Amateur / Academic)
        "Commercial": "#fbbc04",  # B (Business)
        "Government": "#008F11",  # C (Civil)
        "Military": "#ff0000",  # D (Defense)
    }
    
    # Naming scheme: color_sequence_{number}_{length}
    color_sequence_1_10 = [
        "#9e0142",
        "#d53e4f",
        "#f46d43",
        "#fdae61",
        "#fee08c",
        "#e6f598",
        "#abdda4",
        "#66c2a5",
        "#5e4fa2",
    ]
    
    color_sequence_2_10 = [
        "#970c10",
        "#eb1700",
        "#ff8000",
        "#ecad00",
        "#ecdeb5",
        "#93d1bc",
        "#069495",
        "#005f72",
        "#413b93", 
        "#781c81",
        "#00101b",
    ]
    
    color_sequence_2_8 = [
        "#970c10",
        "#ff8000",
        "#ecad00",
        "#ecdeb5",
        "#93d1bc",
        "#069495",
        "#413b93", 
        "#00101b",
    ]
    
    color_sequence_2_6 = [
        "#970c10",
        "#ff8000",
        "#ecdeb5",
        "#069495",
        "#413b93", 
        "#00101b",
    ]
    
    color_sequence_3_12 = [
        "#ff2702",
        "#fc6313",
        "#f79f24",
        "#f8c70e",
        "#fff001",
        "#7fd100",
        "#05b206",
        "#02c1af",
        "#016fc4",
        "#3b48ba",
        "#7322af",
        "#d3288e",
    ]
    
    color_sequence_4_12 = [
       "#c02e1d",
       "#d94e1f", 
       "#f16c20",
       "#ef8b2c", 
       "#ecaa38", 
       "#ebc844",
       "#a2b86c", 
       "#5ca793", 
       "#1395ba", 
       "#117899", 
       "#0f5b78", 
       "#0d3c55", 
    ]
    
    color_sequence_5_12 = [
        "#d92120", 
        "#e6642c", 
        "#e68e34", 
        "#d9ad3c", 
        "#b5bd4c", 
        "#7fb972", 
        "#63ad99", 
        "#55a1b1", 
        "#488bc2", 
        "#4065b1", 
        "#413b93", 
        "#781c81"
    ]
    
    color_sequence_6_11 = [
        "#970c10",
        "#eb1700",
        "#ff8000",
        "#ebc844",
        "#ecdeb5",
        "#93d1bc",
        "#44c09f", 
        "#069495",
        "#005f72",
        "#413b93", 
        "#00101b",
    ]
    
    def pivot_dataframe(df, index_col, column_col, value_col):
        """
        Index_col is used as the row index of the pivoted dataframe.
        Column_col specifies the values that become the new columns of the pivoted dataframe.
        Value_col specifies the values that fill the new DataFrame, at the interscetion of the index and column values.
        
        Example:
        >>> df = pd.DataFrame({
        ...     'Launch_Date': ['2020-01-01', '2020-01-01', '2020-02-01'],
        ...     'Launch_Pad': ['SLC4E', 'LC39A', 'SLC4E'],
        ...     'Apogee': [550, 600, 560]
        ... })
        >>> pivot_dataframe(df, 'Launch_Date', 'Launch_Pad', 'Apogee')
           Launch_Date  LC39A  SLC4E
        0  2020-01-01  600.0  550.0
        1  2020-02-01    NaN  560.0
        
        Raises:
            ValueError: If the pivot operation results in duplicate entries for an index-column combination.
        
        See Pandas documentation for more details:
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html
        """
        pivoted = df.pivot_table(index=index_col, columns=column_col, values=value_col) # pivot_table supports duplicate indexes, unlike pd.pivot
        pivoted = pivoted.reset_index().sort_values(by=index_col)
        return pivoted

    def count_values_into_bins(dataframe, value_col, bins, labels, count_values=False, bin_column=None):
        """
        Sort groups (then, count totals if count_values) into discrete bins (eg. intervals of payload mass) and count how many data points fall into each bin.
        
        Args:
            dataframe (Pandas dataframe): Dataframe containing the data to be binned
            value_col (str): Column to be used for binning, eg. 'Payload_Mass'.
            bins (list int): List of bin edges, eg. [0, 1000, 2000, 3000] for payload mass bins.
            labels (list str): List of bin labels, eg. ['0-1T', '1-2T', '2-3T'] for payload mass bins.
            count_values (bool, optional): If True, counts the number of values in each bin and returns this instead of the bin itself. Defaults to False.
            bin_column (str, optional): If provided, adds a new column to the dataframe for the bin of each row. Defaults to None.
            
        Note what bin_column does. If you don't provide a value, it will returns something like this:
        70696      2-3t
        70795      3-4t
        71078      4-5t
        71159      5-6t
        71260      6-7t
        71406      0-1t
        Notice each row only has one value, the bin it belongs to.
        
        If you provide a bin_column, then each row will retain all of its original data, but will have a new column with the bin it belongs to.
        
        Notice that labels are between the bins. The bins variable specifies the edges of the bins.
        """
        
        if bin_column:
            dataframe[bin_column] = pd.cut(dataframe[value_col], bins=bins, labels=labels, include_lowest=True)
            binned = dataframe
        else:
            binned = pd.cut(dataframe[value_col], bins=bins, labels=labels, include_lowest=True)
        if count_values:
            binned = binned.value_counts().reindex(labels)
        return binned
 
    def bin_dataset_into_dictionary_by_filter_function(dataset, filter_function, filter_function_parameters_list, value_col, bins, bin_labels, keys=None, count_values=True, bin_column=None, filter_function_additional_parameter=None):
        """Filters a dataset by a given filter function and returns a dataframe for each filter function parameter.
        
        Eg. You can filter by orbit and get a dictionary of dataframes, one for each orbit.
        
        If it doesn't make sense, read Pandas documentation.
        
        Args:
            dataset (launch or satcat): Launch or Satcat dataset (notice this isn't the McDowellDataset, so use dataset.launch or dataset.satcat)
            filter_function (mda.Filters...): Filter function to be applied
            filter_function_parameters_list (list): List of paramters, eg. ['LEO', 'SSO, ... , 'BEO'] for orbits or ['Falcon9', 'Electron'] for launch vehicles.
            value_col (str): Column to be used for binning, eg. 'Payload_Mass'.
            bins (list int): List of bin edges, eg. [0, 1000, 2000, 3000] for payload mass bins.
            bin_labels (list str): List of bin labels, eg. ['0-1T', '1-2T', '2-3T'] for payload mass bins.
            keys (list str, optional): Use if keys should be different from filter_function_parameters. Eg. for orbits if you want 'Low Earth Orbit' instead of 'LEO'. Must be in same order as filter_function_parameters. Defaults to None.
            count_values (bool, optional): If True, counts the number of values in each bin and returns this instead of the bin itself. Defaults to True.
            bin_column (str, optional): See count_values_into_bins(). If provided, adds a new column to the dataframe for the bin of each row. Defaults to None.

        Returns:
            dictionary(key, binned dataframe): A dictionary where each key is a filter function parameter and the value is a dataframe with binned values.
        """

        if keys is None:
            keys = filter_function_parameters_list
        output_dict = {}
        for filter_function_parameter, key in zip(filter_function_parameters_list, keys):
            new_dataset = copy.deepcopy(dataset)  # Create a copy of the dataframe to avoid modifying the original, bad solution tbh. Deep copy is required bc dataset is part of another class (i think this is why).
            if filter_function_additional_parameter is not None: # This is getting ugly
                filter_function(new_dataset, filter_function_parameter, filter_function_additional_parameter)
            else:
                filter_function(new_dataset, filter_function_parameter)  # Apply the filter function
            output_dict[key] = ChartUtils.count_values_into_bins(new_dataset.df, value_col, bins, bin_labels, count_values, bin_column)
        return output_dict
 
    def group_dataset_into_dictionary_by_filter_function(dataset, filter_function, groups, groupby_col, keys=None, count_values=False, filter_function_additional_parameter=None):
        """Groups a dataset by a given filter function and returns a dataframe for each group.
        
        This is used instead of binning when you want to group by a column, eg. 'Launch_Year' or 'Launch_Vehicle_Simplified_Name'.
        
        Example use:
        If using count_values, you coul filter by simple_payload_category and group by launch year to get the number of payloads launched each year for each simple payload category.
        
        Bins are for continuous data (eg. payload mass), while groups are for discrete data (eg. launch year, launch vehicle).
        
        Note that groups and groupby_col are not the same thing. Groups are the values you want to filter by, while groupby_col is the column you want to group by. Eg. Orbits and Launch_Year.
        
        Args:
            dataset (launch or satcat): Launch or Satcat dataset (notice this isn't the McDowellDataset, so use dataset.launch or dataset.satcat)
            filter_function (mda.Filters...): Filter function to be applied
            groups (list): List of groups, eg. ['LEO', 'SSO, ... , 'BEO'] for orbits or ['Falcon9', 'Electron'] for launch vehicles.
            groupby_col (str): Column to group by, eg. 'Launch_Year'.
            keys (list str, optional): Use if keys should be different from groups. Defaults to None.
            count_values (bool, optional): If True, counts the number of values in each group and returns this instead of the group itself. Defaults to None.
            filter_function_additional_parameter (any, optional): Additional parameter for the filter function. Defaults to None.
        
        Returns:
            dictionary(key, grouped dataframe): A dictionary where each key is a group and the value is a dataframe with grouped values.
        """
        if keys is None:
            keys = groups
        output_dict = {}
        for group in groups:
            new_dataset = copy.deepcopy(dataset)
            if filter_function_additional_parameter is not None: # This is getting ugly
                filter_function(new_dataset, group, filter_function_additional_parameter)
            else:
                filter_function(new_dataset, group)  # Apply the filter function
            if count_values:
                counts = new_dataset.df.groupby(groupby_col).size()
            else:
                counts = new_dataset.df.groupby(groupby_col)
            output_dict[group] = counts.rename(group)
        return output_dict
 
    # Combines individual dataframes as columns into a single dataframe, with keys as column names.
    def combine_dictionary_of_dataframes(dataframes):
        # .values gives us a list-like object of the counts for each year
        # Concat axis=1 combines each individual dataframe into columns of a single dataframe
        output_df = pd.concat(dataframes.values(), axis=1)
        output_df.columns = dataframes.keys() # Name columns by the orbits
        output_df.fillna(0, inplace=True)
        return output_df

    # Histograms are designed for continuous data, while bar charts are for discrete data.
    def plot_histogram(dataframe, title, subtitle, x_label, y_label, output_path, color_map=None, barmode='stack', bargap=0):
        fig = px.histogram(dataframe,
                    x=dataframe.index,
                    y=dataframe.columns,
                    title=f'<b>{title}</b><br><sup>{subtitle}</sup>',
                    labels={'x': f'{x_label}', 'y': f'{y_label}'},
                    barmode=barmode,
                    color_discrete_map=color_map,
                    )

        fig.update_layout(
            # Font settings
            font=dict(family='Arial, sans-serif', size=20, color="#000000"),
            title=dict(font=dict(size=40, family='Arial, sans-serif', color="#000000"), x=0.025, xanchor="left"),
            # Background and borders
            plot_bgcolor="white",
            paper_bgcolor="white",
            # Gridlines
            xaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                tickangle=45,
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=x_label,
            ),
            yaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                rangemode='tozero',           # <— force start at 0
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=y_label,
            ),
            # Legend
            showlegend=True,
            legend=dict(
                font=dict(size=24, family="Arial, sans-serif"),
                bordercolor="white",
                borderwidth=1,
                bgcolor="white",
                title=dict(text=""),  # Add this line to remove title: "variable"
            ),
            # Remove hover effects and other embellishments
            hovermode="x",
            bargap=bargap,
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pio.write_image(fig, output_path, format='png', width=1280, height=720)
        
        ChartUtils.log_and_save_df("png", os.path.basename(output_path))
    
    def plot_bar(dataframe, title, subtitle, x_label, y_label, output_path, color_map=None, barmode='stack', bargap=0, x_tick0=0, x_tick_step_size=1):
        """
        Create a bar chart using Plotly Express.
        Args:
            dataframe (Pandas dataframe): Dataframe containing the data to be plotted
            title (string): Title of the chart
            subtitle (string): Subtitle of the chart, best to include the date of the data cut-off "Date Cutoff: YYYY-MM-DD"
            x_label (string): Label for the x-axis
            y_label (string): Label for the y-axis
            output_path (string): Full path including filename to save the plot
            color_map (dictionary): Column name to color mapping, eg. {'LC40': '#ff0000', 'LC39A': '#00ff00'}. Or, color sequence list ['#ff0000', '#00ff00', '#0000ff'].s
            barmode (string): 'stack' or 'group'
            bargap (float): Gap between bars, 0-1
            x_tick0 (int): First tick on the x axis (x_label). 0 = first index.
            x_tick_step_size (int): tick step size
        """
        
        fig = px.bar(dataframe,
                     x=dataframe.index,
                     y=dataframe.columns,
                     title=f'<b>{title}</b><br><sup>{subtitle}</sup>',
                     labels={'x': f'{x_label}', 'y': f'{y_label}'},
                     barmode=barmode,
                     color_discrete_map=color_map if type(color_map) == dict else None, # Cursed Python but it's beautiful in its own way
                     color_discrete_sequence=color_map if type(color_map) == list else None, # We either want a color map dict or color sequence list
                     # wait this is actually retarded just make two variables, oh well it looks cool I like Python (HOW TF DO YOU ADD A PYOBJECT IN CPYTHON?!?)
                     )
        
        fig.update_layout(
            # Font settings
            font=dict(family='Arial, sans-serif', size=20, color="#000000"),
            title=dict(font=dict(size=40, family='Arial, sans-serif', color="#000000"), x=0.025, xanchor="left"),
            # Background and borders
            plot_bgcolor="white",
            paper_bgcolor="white",
            # Gridlines
            xaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                tickangle=45,
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=x_label,
                tick0=x_tick0,
                dtick=x_tick_step_size # step size
            ),
            yaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                rangemode='tozero',           # <— force start at 0
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=y_label,
            ),
            # Legend
            showlegend=True,
            legend=dict(
                font=dict(size=24, family="Arial, sans-serif"),
                bordercolor="white",
                borderwidth=1,
                bgcolor="white",
                title=dict(text=""),  # Add this line to remove title: "variable"
            ),
            # Remove hover effects and other embellishments
            hovermode="x",
            bargap=bargap,
        )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pio.write_image(fig, output_path, format='png', width=1280, height=720)
        
        ChartUtils.log_and_save_df("png", os.path.basename(output_path))
    
    def plot_scatter(dataframe, x_col, y_cols, title, subtitle, x_label, y_label, dot_diameter, output_path, color_map=None, y_scaling_factor=1, x_tick0=None, x_tick_step_size=None, x_axis_type=None):
        """
        Create a scatter plot using Plotly Express.
        Args:
            dataframe (Pandas dataframe): Dataframe containing the x_col and y_cols data
            x_col (string): Title of the column to be used for the x-axis
            y_cols (string): Titles of the column to be used for the series data
            title (string): It's simple
            subtitle (string): Best to include the date of the data cut-off "Date Cutoff: YYYY-MM-DD"
            x_label (string): It's simple
            y_label (string): It's simple
            y_scaling_factor (float/int): Multiplicative factor to scale the y-axis
            output_path (string): Full path including filename to save the plot
            color_map (dictionary): y_col to color mapping, eg. {'LC40': '#ff0000', 'LC39A': '#00ff00'}
            x_axis_type (string): Use 'date' if you want it formatted correctly as a date. Otherwise, None or don't use it.
        """
        
        df = dataframe.copy()
        df[x_col] = pd.to_datetime(df[x_col]) if x_axis_type == 'date' else df[x_col]  # Convert x_col to datetime if x_axis_type is 'date'
        if y_scaling_factor != 1:
            for col in y_cols:
                df[col] = df[col] * y_scaling_factor

        fig = px.scatter(df,
                         x=x_col,
                         y=y_cols,
                         title=f'<b>{title}</b><br><sup>{subtitle}</sup>',
                         color_discrete_map=color_map,
                         )
        
        # Set diameter
        fig.update_traces(marker=dict(size=dot_diameter))
        
        fig.update_layout(
            # Font settings
            font=dict(family='Arial, sans-serif', size=20, color="#000000"),
            title=dict(font=dict(size=40, family='Arial, sans-serif', color="#000000"), x=0.025, xanchor="left"),
            # Background and borders
            plot_bgcolor="white",
            paper_bgcolor="white",
            # Gridlines
            xaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                tickangle=45,
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=x_label,
                tick0=x_tick0,
                dtick=x_tick_step_size,
            ),
            yaxis=dict(
                gridcolor="rgba(200, 200, 200, 0.5)",
                linecolor="#000000",
                rangemode='tozero',           # <— force start at 0
                title_font=dict(size=24, family="Arial, sans-serif"),
                title_text=y_label,
            ),
            # Legend
            showlegend=True,
            legend=dict(
                font=dict(size=24, family="Arial, sans-serif"),
                bordercolor="white",
                borderwidth=1,
                bgcolor="white",
                title=dict(text=""),  # Add this line to remove title: "variable"
            ),
            # Remove hover effects and other embellishments
            hovermode="x",
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pio.write_image(fig, output_path, format='png', width=1280, height=720)
        
        ChartUtils.log_and_save_df("png", os.path.basename(output_path))
    
    def log_and_save_df(log_type, output_name, output_prefix=None, save_dataframe=None):
        if log_type == "dataframe":
            os.makedirs(f'examples/outputs/raw_dataframes/{output_prefix}', exist_ok=True)
            save_dataframe.to_csv(f'examples/outputs/raw_dataframes/{output_prefix}/raw_dataframe_{output_name}.csv', index=False)
            print(f"\r(1/3) {output_name} dataframe saved", end="")
        elif log_type == "csv":
            os.makedirs(f'examples/outputs/csv/{output_prefix}/', exist_ok=True)
            save_dataframe.to_csv(f'examples/outputs/csv/{output_prefix}/{output_name}.csv', index=True)
            print(f"\r(2/3) {output_name} csv saved      ", end="")
        elif log_type == "png":
            print(f"\r(3/3) {output_name} saved      ")
            