import pandas as pd
import matplotlib.pyplot as plt

class GalMorph:
    """
    A class for analyzing and visualizing galaxy morphology data from numerical simulations.

    Attributes:
        data (pd.DataFrame): DataFrame containing galaxy morphology data loaded from a pickle file.
    Parameters: 
            file_path (str): Path to the pickle file containing galaxy morphology data.
            snapshot_values (list): List of unique snapshot values from the data.
            galaxies_count (list): List of counts of galaxies for each snapshot.
            galaxy_type_count_dict (dict): Dictionary to count the number of galaxies of each type in a snapshot.
        
    """

    def __init__(self, file_path):
        """
        Initializes the GalMorph object by loading data from a pickle file.

        
        """
        self.data = pd.read_pickle(file_path)

    def _assign_galaxy_type(self, row, thresholds:dict={
    'elliptical': 0.7,'spiral': 0.6,'irregular': 0.5}) -> str:
        """
        Assigns a galaxy type based on the highest value among three input columns.

        Parameters:
            row (pd.Series): A row from a DataFrame, containing columns "P_Spheroid", "P_Disk", & "P_Irr"
            thresholds (dict): Dictionary of critical values, e.g., {'elliptical': 0.7, 'spiral': 0.6, 'irregular': 0.5}
        Returns:
            str: 'elliptical', 'spiral', or 'irregular' depending on which value is highest.
        
        """
        values = {
            'elliptical': row["P_Spheroid"],
            'spiral': row["P_Disk"],
            'irregular': row["P_Irr"]
        }
        max_type = max(values, key=values.get)
        max_value = values[max_type]
        
        if max_value >= thresholds[max_type]:
            return max_type
        else:
            return 'unknown'

    def Galaxy_count(self, file_name="galaxy_count.png"):
        """
        Plots the number of galaxies for each snapshot and saves the plot as an image.

        Parameters:
            file_name (str): Name of the output image file for the plot. Default is "galaxy_count.png".
        
        """
        self.snapshot_values = self.data["Snapshot"].drop_duplicates().to_list()
        galaxies_count = []
        for val in self.snapshot_values:
            galaxies_count.append(self.data[self.data["Snapshot"]==val].shape[0])

        plt.figure(figsize = [6, 5])
        plt.plot(self.snapshot_values, galaxies_count, ls = "-.")
        plt.scatter(self.snapshot_values, galaxies_count, marker="o", color = "red")
        plt.minorticks_on()
        plt.xlabel("Snapshot")
        plt.ylabel("Galaxy Count")
        plt.savefig(f"{file_name}", dpi = 130)
        plt.show()

    def Galaxy_type_snap(self, snapshot_num:int=25, output_fname = "bar.png"):
        """
        Plots a bar chart of galaxy type counts for a specific snapshot and saves the plot as an image.

        Parameters:
            snapshot_num (int): The snapshot number to analyze. Default is 25.
            output_fname (str): Name of the output image file for the plot. Default is "bar.png".

        Returns:
            None: The function saves the plot as an image file.
       
         Note:
            This creates a bar plot to visualize the counts of each galaxy type.
             -The x-axis represents the galaxy types, and the y-axis represents the counts.

             -The y-axis is set to a logarithmic scale for better visibility of differences.
             
             -The bars are colored differently for each type.
        
        """
        self.data["Galaxy_type"] = self.data.apply(self._assign_galaxy_type, axis=1)
        snapshot_galaxy = self.data[self.data["Snapshot"]==snapshot_num].reset_index()

        
        # Create a dictionary to count the number of galaxies of each type in the snapshot.
        
    
        galaxy_type_count_dict = {}
        for gal_type in snapshot_galaxy["Galaxy_type"].drop_duplicates().values:
            galaxy_type_count_dict[gal_type] = snapshot_galaxy[snapshot_galaxy["Galaxy_type"] == gal_type].shape[0]
        

        bar_colors = ['red', 'green', 'blue', 'purple']
        fig, ax = plt.subplots()
        ax.set_ylim(1, 1000)
        bars = ax.bar(list(galaxy_type_count_dict.keys()), list(galaxy_type_count_dict.values()), color = bar_colors, width = 0.5)
        ax.bar_label(bars, label_type='edge', padding=2, color='black', fontsize=10)
        ax.set_title(f"Galaxy Type Count of Snapshot {snapshot_num}")
        ax.set_ylabel(r"Number $\longrightarrow$")
        ax.set_xlabel("Galaxy Type")
        ax.tick_params(axis='y', which = 'major', length = 10, direction = "in")
        ax.tick_params(axis='y', which = 'minor', length = 5, direction = "in")
        ax.set_yscale('log')
        print(ax.get_ylim())
        plt.savefig(f"{output_fname}", dpi = 200)
        plt.show()


if __name__ == "__main__":
    """
    Example usage of the GalMorph class.
    Loads galaxy morphology data and generates a bar plot for a specific snapshot.
    
    """
    GalSim = GalMorph(file_path="data/morphologies_snapshot_data.pkl")
    GalSim.Galaxy_type_snap()