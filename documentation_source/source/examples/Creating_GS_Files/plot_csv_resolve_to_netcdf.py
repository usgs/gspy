"""
CSV to NetCDF
-------------

This example demonstrates how to convert comma-separated values (CSV) data to the GS NetCDF format. Specifically this example includes:

1. Raw AEM data, from the Resolve system
2. Inverted resistivity models

Dataset Reference:
Burton, B.L., Minsley, B.J., Bloss, B.R., and Kress, W.H., 2021, Airborne electromagnetic, magnetic, and radiometric survey of the Mississippi Alluvial Plain, November 2018 - February 2019: U.S. Geological Survey data release, https://doi.org/10.5066/P9XBBBUU.

"""
#%%
import matplotlib.pyplot as plt
from os.path import join
from gspy import Survey

#%%
# Convert the CSV data to NetCDF
# ++++++++++++++++++++++++++++++

#%%
# Initialize the Survey

# Path to example files
data_path = '..//..//supplemental//region//MAP'

# Survey metadata file
metadata = join(data_path, "data//Resolve_survey_md.json")

# Establish the Survey
survey = Survey(metadata)

#%%
# Import raw AEM data from CSV-format.
# Define input data file and associated metadata file
d_data = join(data_path, 'data//Resolve.csv')
d_supp = join(data_path, 'data//Resolve_data_md.json')

# Add the raw AEM data as a tabular dataset
survey.add_tabular(type='csv', data_filename=d_data, metadata_file=d_supp)

#%%
# Import inverted AEM models from CSV-format.
# Define input model file and associated metadata file
m_data = join(data_path, 'model//Resolve_model.csv')
m_supp = join(data_path, 'model//Resolve_model_md.json')

# Add the inverted AEM models as a tabular dataset
survey.add_tabular(type='csv', data_filename=m_data, metadata_file=m_supp)

#%%
# Save to NetCDF file
d_out = join(data_path, 'model//Resolve.nc')
survey.write_netcdf(d_out)

#%%
# Reading back in the GS NetCDF file
new_survey = Survey().read_netcdf(d_out)

# Check the Survey information
print(new_survey.xarray)

#%%
# Plotting

# Make a scatter plot of a specific data variable, using GSPy's plotter 
plt.figure()
new_survey.tabular[0].gs_tabular.scatter('DTM', vmin=30, vmax=50)
plt.show()

# Make a scatter plot of a specific model variable, using GSPy's plotter 
plt.figure()
new_survey.tabular[1].gs_tabular.scatter('DOI_STANDARD')
plt.show()

# Check the model dataset
print(new_survey.tabular[1])