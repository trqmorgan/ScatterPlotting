from sklearn import preprocessing
import pandas as pd
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt
import numpy as np
from sklearn.preprocessing import minmax_scale
import seaborn as sns
from scipy.spatial import distance
from scipy.cluster import hierarchy
import matplotlib.patches as mpatches
import sklearn.neighbors.typedefs
import ternary


def closure(mat):
    mat = np.atleast_2d(mat)
    if np.any(mat < 0):
        raise ValueError("Cannot have negative proportions")
    if mat.ndim > 2:
        raise ValueError("Input matrix can only have two dimensions or less")
    if np.all(mat == 0, axis=1).sum() > 0:
        raise ValueError("Input matrix cannot have rows with all zeros")
    mat = mat / mat.sum(axis=1, keepdims=True)
    return mat.squeeze()

def clr(mat):
    # calculate center log ratio
    mat = closure(mat)
    lmat = np.log(mat)
    gm = lmat.mean(axis=-1, keepdims=True)
    return (lmat - gm).squeeze()

def pca_(data_in, key_headers, fig, clr_scaling, arrows_on, samples_on, colors, shapes):

    ax = fig.gca()
    PC_x = int(key_headers[0][-1])-1 # PC1 string passed but need integer to
    #  extract correct PC from analysis (0) so take last element - 1 and
    # convert to integer
    PC_y = int(key_headers[1][-1])-1
    elements= key_headers[2]
    colorOn = key_headers[3]
    size = key_headers[4]
    shapeOn = key_headers[5]
    labelOn = key_headers[6]


    cols = list(elements)

    if len(colorOn) > 0:
        labs = data_in[colorOn]
    if len(shapeOn) > 0:
        labs_shape = data_in[shapeOn]
    if len(labelOn) > 0:
        labs_labs = data_in[labelOn]

    data = data_in[cols]

    colmin = data[data > 0].loc[:, cols].min(axis=0)
    halfcolmin = colmin/2 #calculate half in above 0
    data = data.mask(data <= 0) # mask values of 0 and below as nan
    data = data.fillna(halfcolmin) # replace nan with half mins
    xlabs = list(data.columns.values)

    if clr_scaling:
        data = clr(data) #clr transformation
    #else:
        #data = preprocessing.StandardScaler().fit_transform(data)
    pca = PCA(n_components = 4)
    pca.fit(data)

    ## project data into PC space
    # 0,1 denote PC1 and PC2; change values for other PCs
    xvector = pca.components_[PC_x] # see 'prcomp(my_data)$rotation' in R
    yvector = pca.components_[PC_y]

    xs = pca.transform(data)[:,PC_x] # see 'prcomp(my_data)$x' in R
    ys = pca.transform(data)[:,PC_y]

    data = pd.DataFrame(data, columns=xlabs)

    data['xs'] = xs
    data['ys'] = ys
    data['NoFilter'] = ['All'] * len(data)

    if len(colorOn) > 0:
        data[colorOn] = data_in[colorOn]
        data[colorOn] = data[colorOn].astype('str')
    if len(shapeOn) > 0:
        data[shapeOn] = data_in[shapeOn]
        data[shapeOn] = data[shapeOn].astype('str')

    if len(colorOn) == 0:
        colorOn = 'NoFilter'

    if len(shapeOn) == 0:
        shapeOn = 'NoFilter'

    colour_items = data[colorOn].unique()
    shape_items = data[shapeOn].unique()

    if len(colorOn) > 0:
        if colors is None:
            colors = sns.color_palette("hls", len(colour_items))

    ## visualize projections
    if arrows_on:
        for i in range(len(xvector)):
        # arrows project features (ie columns from csv) as vectors onto PC axes
            ax.annotate(xlabs[i],
                    xy=(0,0), xycoords='data',
                    xytext=(xvector[i]*max(xs), yvector[i]*max(ys)), textcoords='data',
                    arrowprops=dict(arrowstyle="<-", connectionstyle="arc3"))
    else:
        for i in range(len(xvector)):
        # arrows project features (ie columns from csv) as vectors onto PC axes
            ax.annotate(xlabs[i],
                    xy=(0,0), xycoords='data',
                    xytext=(xvector[i]*max(xs), yvector[i]*max(ys)), textcoords='data')
        ax.scatter(xvector*max(xs), yvector*max(ys),
                   edgecolors='k',
                   color='blue', s=size)
    if samples_on:
        for i, item in enumerate(colour_items):
            filtered_data = data[data[colorOn] == item]
            for s, shape in enumerate(shape_items):
                filtered_data1 = filtered_data[filtered_data[shapeOn] == shape]
                if len(filtered_data1) > 0:
                    c = colors.get(item)
                    marktup = shapes.get(shape)
                    mark = marktup[1]
                    ax.scatter(filtered_data1['xs'], filtered_data1['ys'],
                               edgecolors='k',
                               color=c, s=size, marker=mark, label=item +", "+ shape)
    ax.legend()

    vecxmax, vecxmin = max(xvector)*max(xs), min(xvector)*max(xs)
    vecymax, vecymin = max(yvector)*max(ys), min(yvector)*max(ys)
    xsmax, xsmin = max(xs), min(xs)
    ysmax, ysmin = max(ys), min(ys)

    if samples_on:
        xmax, xmin = max(vecxmax, xsmax), min(vecxmin, xsmin)
        ymax, ymin = max(vecymax, ysmax), min(vecymin, ysmin)
    else:
        xmax, xmin = vecxmax, vecxmin
        ymax, ymin = vecymax, vecymin


    ax.set_ylim(ymin*1.1, ymax*1.1)
    ax.set_xlim(xmin*1.1, xmax*1.1)
    ax.set_ylabel(key_headers[1], fontsize=14, fontweight='bold')
    ax.set_xlabel(key_headers[0], fontsize=14, fontweight='bold')

    if len(labelOn) > 0:
        for label, x_, y_ in zip(labs_labs,  xs, ys):
            ax.annotate(label, xy=(x_, y_), xytext=(2, 2),
                                         textcoords='offset points', ha='right',
                                         va='bottom', size=8, color = 'k', zorder=3)


    #plt.show()

    return fig


def blank_scatter_plot(data_in, key_headers, limits, fig, log_scales, colors, shapes):
    no_color_dict = False
    ax = fig.gca()

    colorOn = key_headers[0]
    x_header = key_headers[1]
    y_header = key_headers[2]
    z_header = key_headers[3]
    x1_header = key_headers[4]
    y1_header = key_headers[5]
    z1_header = key_headers[6]
    size = key_headers[7]
    shapeOn = key_headers[8]
    labelOn  = key_headers[9]

    user_x_low = limits[0]
    user_x_high = limits[1]
    user_y_low = limits[2]
    user_y_high = limits[3]
    log_x = log_scales[0]
    log_y = log_scales[1]


    x = data_in[x_header]
    y = data_in[y_header]

    if not len(x1_header) == 0:
        x = x / data_in[x1_header]

    if not len(y1_header) == 0:
        y = y / data_in[y1_header]

    #if log_x:
        #x = np.log(x)
    #if log_y:
        #y = np.log(y)

    z = size

    if not len(z_header) == 0:
        z = data_in[z_header]
        z = minmax_scale(z, feature_range=(1, 2))
        z = z * size

    if not len(z1_header) == 0:
        z = z/data_in[z1_header]
        z = minmax_scale(z, feature_range=(0, 1))
        z = z * size

    data_in['x'] = x
    data_in['y'] = y
    data_in['z'] = z
    data_in['NoFilter'] = ['All']*len(data_in)

    if len(colorOn) == 0:
        colorOn = 'NoFilter'

    if len(shapeOn) == 0:
        shapeOn = 'NoFilter'

    if len(colorOn) > 0:
        colour_items = data_in[colorOn].unique()
        if colors is None:
            colors = sns.color_palette("hls", len(colour_items))
            no_color_dict = True
    if len(shapeOn) > 0:
        shape_items = data_in[shapeOn].unique()



    for i, item in enumerate(colour_items):
        filtered_data = data_in[data_in[colorOn] == item]
        for s, shape in enumerate(shape_items):
            filtered_data1 = filtered_data[filtered_data[shapeOn] == shape]
            if len(filtered_data1)>0:
                c = colors.get(item)
                marktup = shapes.get(shape)
                mark = marktup[1]
                ax.scatter(filtered_data1['x'], filtered_data1['y'],
                           edgecolors='k', s=filtered_data1['z'], color=c, marker=mark, label=item +", "+ shape)
    if log_y:
        ax.set_yscale('log')
    if log_x:
        ax.set_xscale('log')
    ax.legend()



    if len(user_x_low) == 0:
        xmin = min(x) *0.9
    else:
        xmin = float(user_x_low)

    if len(user_x_high) == 0:
        xmax = max(x) *1.1
    else:
        xmax = float(user_x_high)

    if len(user_y_low) == 0:
        ymin = min(y) *0.9
    else:
        ymin = float(user_y_low)

    if len(user_y_high) == 0:
        ymax = max(y) *1.1
    else:
        ymax = float(user_y_high)

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    if len(x1_header) == 0:
        x_label = x_header
    else:
        x_label = '%s/%s' % (x_header, x1_header)

    if log_x:
        x_label = 'log(%s)'% (x_label)

    if len(y1_header) == 0:
        y_label = y_header
    else:
        y_label = '%s/%s' % (y_header, y1_header)
    if log_y:
        y_label = 'log(%s)'% (y_label)

    ax.set_ylabel(y_label, fontsize=14, fontweight='bold')
    ax.set_xlabel(x_label, fontsize=14, fontweight='bold')

    if len(labelOn) > 0:
        labs_labs = data_in[labelOn]
        for label, x_, y_ in zip(labs_labs, data_in['x'], data_in['y']):
            ax.annotate(label, xy=(x_, y_), xytext=(2, 2),
                        textcoords='offset points', ha='right',
                        va='bottom', size=8, color='k', zorder=3)

    return fig


def ternary_(data, headers, filepath, scalers, size, colors, shapedict):
    top = data[headers[1]]
    left = data[headers[2]]
    right = data[headers[3]]


    top_label = headers[1]
    left_label = headers[2]
    right_label = headers[3]

    data['NoFilter'] = ['All'] * len(data)

    if len(scalers[0]) > 0:
        multiply_left = float(scalers[0])
    else:
        multiply_left = 1

    if len(scalers[1]) > 0:
        multiply_right = float(scalers[1])
    else:
        multiply_right = 1

    if len(scalers[2]) > 0:
        multiply_top = float(scalers[2])
    else:
        multiply_top = 1

    if len(headers[4]) > 0:
        top = top / data[headers[4]]
        top_label = '%s/%s' % (headers[1], headers[4])
    if not multiply_top == 1:
        top_label = '%s x %s' % (top_label, multiply_top)
    if len(headers[5]) > 0:
        left = left / data[headers[5]]
        left_label = '%s/%s' % (headers[2], headers[5])
    if not multiply_left == 1:
        left_label = '%s x %s' % (left_label, multiply_left)
    if len(headers[6]) > 0:
        right = right / data[headers[6]]
        right_label = '%s/%s' % (headers[3], headers[6])
    if not multiply_right == 1:
        right_label = '%s x %s' % (right_label, multiply_right)

    s = size
    if len(headers[7]) > 0:
        size_scale_on = data[headers[7]]
        s = size_scale_on
        s = minmax_scale(s, feature_range=(0, 1))
        s = s * size
    else:
        s = [s]*len(data)

    if len(headers[0]) == 0:
        colorOn = 'NoFilter'
    else:
        colorOn = headers[0]

    if len(headers[8]) == 0:
        shapeOn = 'NoFilter'
    else:
        shapeOn = headers[8]

    colour_items = data[colorOn].unique()
    shape_items = data[shapeOn].unique()


    c = data[colorOn]
    shape = data[shapeOn]
    stacked_data = np.vstack((c,shape, top*multiply_top, left*multiply_left,
                              right*multiply_right))
    summed_rows = np.sum(stacked_data[2:], axis=0)
    stacked_data = np.vstack((stacked_data, summed_rows, s))

    scale = 100
    fig, tax = ternary.figure(scale=scale)
    fig.set_size_inches(10, 8)
    tax.boundary(linewidth=1.0)
    tax.left_axis_label(left_label, fontsize=12, fontweight='bold',
                        offset=0.05)
    tax.right_axis_label(top_label, fontsize=12, fontweight='bold', offset=0.05)
    tax.bottom_axis_label(right_label,fontsize=12, fontweight='bold', offset=0)
    tax.gridlines(color="black", multiple=10, linewidth=0.25, ls='--', alpha=0.1)
    tax.set_axis_limits({'b': [0, 100], 'l': [0, 100], 'r': [0, 100]})
    tax.get_ticks_from_axis_limits(multiple=20)
    tick_formats = {'b': "%.2f", 'r': "%d", 'l': "%.1f"}
    tax.set_custom_ticks(fontsize=8, offset=0.012, tick_formats=tick_formats)
    tax.ax.axis("equal")
    tax.ax.axis("off")
    tax.clear_matplotlib_ticks()


    for t, item in enumerate(colour_items):
        filter_data =stacked_data[:,np.in1d(stacked_data[0],[colour_items[t]])]
        for s, shape in enumerate(shape_items):
            filter_data1 =filter_data[:,np.in1d(filter_data[1],[shape_items[s]])]
            if filter_data1.shape[1] > 0:
                th_filter = (filter_data1[2] / filter_data1[5] * 100)
                co_filter = (filter_data1[3] / filter_data1[5] *  100)
                zr_filter = (filter_data1[4] / filter_data1[5] * 100)
                points = zip(zr_filter, th_filter, co_filter)
                points_c = tax.convert_coordinates(points, axisorder='brl')
                final_size = filter_data1[6]
                final_size = list(final_size)
                c = colors.get(item)
                marktup = shapedict.get(shape)
                mark = marktup[1]
                tax.scatter(points_c, marker=mark, s=final_size, lw=1, edgecolor='black',
                                label=filter_data1[0][0]+", "+filter_data[1][0], color=c, zorder=2)


    tax.legend()
    tax._redraw_labels()
    tax.resize_drawing_canvas()

    plt.plot()
    plt.close()
    tax.close()
    return fig



