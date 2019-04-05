Portfolio Optimization
===========================================================================

Optimization of product portfolio filtering SKUs with gross margin below a threshold set by the user.
Removed SKUs reduce the asset utilization of production plant where the SKUs are produced.
To run the dashboard is necessary to
  1. Edit Tableau configuration (see next Section)
  2. Edit Python script configuration (see next Section)
  
The Python script is optimized for execution speed:
	1. Plant and SKUs databases are loaded once, the first time the script is executed by Tableau
	2. The product portfolio optimization occurs only if the relevant parameter (SKU GM% threshold) is changed. 
	   Changes are detected comparing parameter stored last value with current one value

Tableau configuration (Retail.co_v04.twb)
---------------------------------------------------------------------------

The path where the Python script is located must be configured.
In the Tableau worksheet (e.g. Original SKU) right click on the 'Python package path' in the 'Parameters' left pane and select edit.
In the Current value insert the directory where the Python package is located.
Please notice that backslash character '\' must replaced with forward slash '/'.

Python script configuration (config.yml)
---------------------------------------------------------------------------

Edit the config.yml file to set path where the input databases are located.
The full path of both db (database.xlsx) and plant (plant utilization.xlsx) must be set.

Dashboard execution
---------------------------------------------------------------------------

Dashboard 'Optimization impact on SKU' show impact of Portfolio optimization strategy to a SKU level
Dashboard 'Optimization impact on subcategories' show impact of Portfolio optimization strategy to a subcategory level
Dashboard 'Optimization impact on plant' show impact of Portfolio optimization strategy on plant asset utilization

How to use the documentation
---------------------------------------------------------------------------
Documentation is available in docstrings provided within the code, altogether with thorough commenting of code steps

References
---------------------------------------------------------------------------
Author: Davide Guatta, guatta.davide@bcg.com