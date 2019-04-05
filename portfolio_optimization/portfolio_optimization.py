"""
=====
TabPy webinar supporting material
=====

Provides

- Portfolio optimization routines

How to use the documentation
----------------------------
Documentation is available in docstrings provided with the code

Required external packages
--------
`numpy`, `pandas`
"""
# =============================================================================
# Module attributes
# =============================================================================
# Documentation format
__docformat__ = 'NumPy'
# Copyright information
__copyright__ = "Copyright (C) 2019, The Boston Consulting Group"
# License type (e.g. 'GPL', 'MIT', 'Proprietary', ...)
__license__ = 'Proprietary'
# Status ('Prototype', 'Development' or 'Pre-production')
__status__ = 'Prototype'
# Version (0.0.x='Prototype', 0.x.x='Development', x.x.x='Pre-production')
__version__ = '1.0.0'
# Release date
__releasedate__ = '06/02/2019'
# Authors (e.g. code writers)
__author__ = ('Davide Guatta <guatta.davide@bcg.com>')
# Credits (e.g. content contributors)
__credits__ = ('')
# Maintainer
__maintainer__ = 'Davide Guatta'
# Email of the maintainer
__email__ = 'guatta.davide@bcg.com'
# Dependencies of the module (tuple of tuples (module_name, module_version))
__dependencies__ = (('pandas', '0.23.0'), ('yaml', '3.13'),
                    ('logging', '0.5.1.2'))

# =============================================================================
# Import modules
# =============================================================================
# Import general purpose module(s)
import pandas as pd
import logging
import yaml
import os


# =============================================================================
# Module global constants
# =============================================================================
# Configuration files
FNAME_CONFIG = 'config.yml'


# =============================================================================
# Module logger configuration
# =============================================================================
module_logger = logging.getLogger(name=__name__)
module_logger.setLevel(level=logging.INFO)


# =============================================================================
# One-time operations
# =============================================================================
# Check if module is initialized looking into variable space
if 'db' not in locals():
    # =========================================================================
    # Load configuration file
    # =========================================================================
    # File path, assuming config file is in the same path as the script
    fpath = os.path.dirname(os.path.realpath(__file__))
    fpath += '/' + FNAME_CONFIG
    print(fpath)
    # Read the configuration file
    if os.path.isfile(fpath) and os.access(fpath, os.R_OK):
        with open(fpath, 'r') as stream:
            try:
                cfg = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    else:
        raise FileNotFoundError

    # =========================================================================
    # Load data set
    # =========================================================================
    # Print information to the console
    module_logger.info('Read databases')
    # Read SKU and plant database
    db = pd.read_excel(cfg['path']['db'])
    db_plant = pd.read_excel(cfg['path']['plant'])
    # Init global persistent variables
    plant_pcs = db.groupby('PLANT ID')['VOLUMES'].sum()
    plant_rate = db_plant.groupby('NAME')['UTILIZATION'].first()
    last_parameter = None
    db_filt = db.copy()
    cat = db_filt.groupby('CATEGORY')
    subcat = db_filt.groupby('SUBCATEGORY')
    sku = db_filt.groupby('SKU ID')
    last_parameter = 0


# =============================================================================
# Common operations when parameters change
# =============================================================================
def parameter_handler(parameter: list):
    """
    Handle a change in SKU GM% threshold, updating global variables
    Notice that the update occurs only if parameter is changed wrt last value

    Attributes
    ----------

    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global last_parameter, cat, subcat, sku, db, db_filt

    # =========================================================================
    # Global variables update logic
    # =========================================================================
    # Verify if parameters changed
    if float(parameter[0]) != last_parameter:
        # Print out message
        module_logger.info('Parameter changed from {} to {}'.
                           format(last_parameter, float(parameter[0])))
        # Update the parameter set
        last_parameter = float(parameter[0])
        # Copy data to a temporary db
        db_filt = db.copy()
        # Set discarded SKUs to zero (avoid filer, ensure to have same index)
        db_filt.loc[db_filt['GROSS MARGIN'] * 100 < last_parameter,
                    'REVENUES'] = 0
        db_filt.loc[db_filt['GROSS MARGIN'] * 100 < last_parameter,
                    'COST'] = 0
        db_filt.loc[db_filt['GROSS MARGIN'] * 100 < last_parameter,
                    'GROSS MARGIN'] = 0
        db_filt.loc[db_filt['GROSS MARGIN'] * 100 < last_parameter,
                    'VOLUMES'] = 0
        # Group data to support various aggregation levels
        cat = db_filt.groupby('CATEGORY')
        subcat = db_filt.groupby('SUBCATEGORY')
        sku = db_filt.groupby('SKU ID')


# =============================================================================
# Revenues by SKU aggregation level
# =============================================================================
def sku_revs(indexer: list, parameter: list) -> list:
    """
    Revenues by SKU aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of SKU that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Revenues aggregated by SKU

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global sku

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = sku['REVENUES'].sum()
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Volumes by subcategory aggregation level
# =============================================================================
def sku_vols(indexer: list, parameter: list) -> list:
    """
    Volumes by SKU aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of SKU that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Volumes aggregated by SKU

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global sku

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = sku['VOLUMES'].sum()
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Margins by SKU aggregation level
# =============================================================================
def sku_margins(indexer: list, parameter: list) -> list:
    """
    Margins by SKU aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of SKU that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Margins aggregated by SKU

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global sku

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = (1 - (sku['COST'].sum() / sku['REVENUES'].sum())) * 100
    # Ensure to Fill NaNs
    y.fillna(0, inplace=True)
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Revenues by subcategory aggregation level
# =============================================================================
def subcat_revs(indexer: list, parameter: list) -> list:
    """
    Revenues by subcategory aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of subcategory that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Revenues aggregated by subcategory

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global subcat

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = subcat['REVENUES'].sum()
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Volumes by subcategory aggregation level
# =============================================================================
def subcat_vols(indexer: list, parameter: list) -> list:
    """
    Volumes by subcategory aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of subcategory that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Volumes aggregated by subcategory

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global subcat

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = subcat['VOLUMES'].sum()
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Margins by subcategory aggregation level
# =============================================================================
def subcat_margins(indexer: list, parameter: list) -> list:
    """
    Margins by subcategory aggregation level
    SKU with GM% lower than the threshold are filtered
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of subcategory that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Margins aggregated by subcategory

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global subcat

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    y = (1 - (subcat['COST'].sum() / subcat['REVENUES'].sum())) * 100
    # Ensure to Fill NaNs
    y.fillna(0, inplace=True)
    y = y.loc[indexer]
    y = y.values.tolist()

    return y


# =============================================================================
# Plant rate utilization
# =============================================================================
def utilization(indexer: list, parameter: list) -> list:
    """
    Plant utilization rate having removed SKU with GM% lower than the threshold
    Results are sorted in the Tableau presentation order

    Attributes
    ----------

    indexer: list
        List of plants that will be used as index to sort output
    parameter: list
        List of SKU GM% removal threshold, in the range [0, 100]

    Returns
    --------

    y: list
        Plant utilization rates

    References
    ----------

    :Authors: Davide Guatta <guatta.davide@bcg.com>
    """
    # =========================================================================
    # Global variables declaration
    # =========================================================================
    global db_filt, plant_pcs, plant_rate

    # =========================================================================
    # Output calculation
    # =========================================================================
    # Check if parameters changed and update
    parameter_handler(parameter)
    # Groupby and return sorted data
    opt_pcs = db_filt.groupby('PLANT ID')['VOLUMES'].sum()
    y = opt_pcs.loc[indexer] / plant_pcs.loc[indexer] * plant_rate.loc[indexer]
    y = y.values.tolist()

    return y
