from .mpl_plotting import Grid, Scatter, Trajectory
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib import pyplot as plt
import functools


def find_figure(start_doc, num_subplots):
    '''Determines where the figure should be plotted and returns the figure and
    axes references.
    This section checks to see if a current figure exists that the plots can be
    added too, and if not creates the figure to be plotted on. It is designed
    to be used in all of the plotting related callback_factories.

    Parameters
    ----------
    start_doc : dict
        the start document issued by the `Run_Engine` when starting a new 'run'
    num_subplots : int
        the number of axes pairs to return (i.e. the num of subplots required)

    Returns
    -------
    fig : matplotlib fig reference
        the reference to the figure we should use to plot.
    axes : list
        list of matplotlib axes references.
    '''
    # I am proposing placing here all of the mechanisms associated with
    # checking if we can use an existing figure, how many subplots should be
    # used and how to arrange them. I prefer this as otherwise there would be
    # a lot of similar code being employed in each of the figure based
    # callback_factories. In addition most of this will probably end up living
    # on the databrowser what do people think?

    # For now this will always return a new `matplotlib.pyplot.figure` and
    # `matplotlib.pyplot.axes` object.

    # Determine the grid shape to use.
    if num_subplots == 1:
        fig, ax = plt.subplots()
    else:
        if num_subplots > 12:
            shape = (math.ceil(num_subplots/4), 4)
        elif num_subplots > 6:
            shape = (math.ceil(num_subplots/3), 3)
        else:
            shape = (math.ceil(num_subplots/2), 2)

        fig, ax = plt.subplots(*shape, sharex='col', sharey='row')

    return fig, ax


def hinted_fields_start_doc(start_doc):
    # Figure out which columns to put in the table and/or to plot from the
    # start doc.
    columns = []
    for det in start_doc['detectors']:
        columns.extend([det])
    return columns


def scatter_factory(start_doc):
    '''
    This is a callback factory for 'scatter' plots. It takes in a start_doc and 
    return a list of callbacks that have been initialized based on its contents.
    '''
    hints = start_doc.get('hints', {}) 
    callbacks = []
    #dim_names are the x axis and y axis 
    dim_names = [fields[0]
                 for fields, stream_name in hints['dimensions']]
    I_names = start_doc['detectors']
    #In case multi dectectors is using here
    axes = []
    for i in range(len(I_names)):
        fig, ax = plt.subplots()
        axes.append(ax)
    for I_name, ax in zip(I_names, axes):
        # This section defines the function for the scatter callback
        def func(bulk_event):
            #NOTE: the order of motor(dimensions) in RE is reversed here
            x_vals = bulk_event['data'][dim_names[1]]
            y_vals = bulk_event['data'][dim_names[0]]
            I_vals = bulk_event['data'][I_name]
            return x_vals, y_vals, I_vals
        scatter_callback = Scatter(start_doc, func, ax=ax)
        callbacks.append(scatter_callback)
    return callbacks


def grid_factory(start_doc):
    '''
    This is a callback factory for 'grid' or 'image' plots. It takes in a
    start_doc and returns a list of callbacks that have been initialized based
    on its contents.
    '''
    hints = start_doc.get('hints', {})
    callbacks = []

    # below are some preliminary values required to generate the required
    # parameters.

    # define some required parameters for setting up the grid plot.
    # NOTE: THIS NEEDS WORK, in order to allow for plotting of non-grid type
    # scans the following parameters need to be passed down to here from the RE
    # This is the minimum information required to create the grid plot.
    dim_names = [fields[0] for fields, stream_name in hints['dimensions']]
    I_names = hinted_fields_start_doc(start_doc)
    extent = start_doc['extents']
    shape = start_doc['shape']
    origin = 'lower'

    # The next line is supposed to take care of where to plot, it can get that
    # info from anywhere (like the new proposed data-browser) I am expecting
    # the length of axes to match the number of self.I_names.
    fig, axes = find_figure(start_doc, len(I_names))

    # This section adjusts extents so that the values are centered on the grid
    # pixels
    data_range = np.array([float(np.diff(e)) for e in extent])
    y_step, x_step = data_range / [max(1, s - 1) for s in shape]
    adjusted_extent = [extent[1][0] - x_step / 2,
                       extent[1][1] + x_step / 2,
                       extent[0][0] - y_step / 2,
                       extent[0][1] + y_step / 2]

    # This section is where the scan path is defined, if the x_trajectory and
    # y_trajectory are 'None' it is not overlayed.
    # NOTE: we need to decide how to pass this info down to here.
    x_trajectory = None  # This should be able to take in the path info here.
    y_trajectory = None  # This should be able to take in the path info here.

    for I_num, I_name in enumerate(I_names):
        # Work out which axis to use from axes
        if len(I_names) > 1:
            y = math.floor(I_num / axes.shape[0])
            x = I_num - y
            ax = axes[x][y]
        else:
            ax = axes

        # This section defines the function for the grid callback
        def func(bulk_event, extent=None, shape=None):
            '''This functions takes in a bulk event and returns x_coords,
            y_coords, I_vals lists.
            '''
            # start by working out the scaling between grid pixels and axes
            # units
            data_range = np.array([float(np.diff(e)) for e in extent])
            y_step, x_step = data_range / [max(1, s - 1) for s in shape]
            x_min = extent[0][0]
            y_min = extent[1][0]
            # define the lists of relevant data from the bulk_event
            x_vals = bulk_event['data'][dim_names[0]]
            y_vals = bulk_event['data'][dim_names[1]]
            I_vals = bulk_event['data'][I_name]
            x_coords = []
            y_coords = []

            for x_val, y_val in zip(x_vals, y_vals):
                x_coords.append(int(round((x_val-x_min)/x_step)))
                y_coords.append(int(round((y_val-y_min)/y_step)))
            return x_coords, y_coords, I_vals  # lists to be returned

        grid_callback = Grid(start_doc,
                             functools.partial(func, extent=extent,
                                               shape=shape),
                             shape, ax=ax, extent=adjusted_extent,
                             origin=origin)
        callbacks.append(grid_callback)

        # This section defines the callback for the overlayed path.
        def trajectory_func(self, bulk_event):
            '''This functions takes in a bulk event and returns x_vals, y_vals
            lists.
            '''
            x_vals = bulk_event['data'][dim_names[1]]
            y_vals = bulk_event['data'][dim_names[0]]
            return x_vals, y_vals

        if x_trajectory is not None:
            trajectory_callback = Trajectory(start_doc, trajectory_func,
                                             x_trajectory, y_trajectory, ax=ax)

            callbacks.append(trajectory_callback)

    return callbacks
