import numpy as np
from scipy.interpolate import interp2d
from scipy.ndimage.interpolation import rotate
import matplotlib.pyplot as plt

def makeDiffractionSpikes(width, hw_spikes = 0, width_y = None, width_x = None, cen_x = None, cen_y = None):
    """Make all 1's array except the diagonals where are 0's.
    Input:
        width: width of the array.
        hw_spikes: half width of the diagonals.
        width_y: width in the y-direction. Default is None, i.e., width_y = width;
        width_x: width in the x-direction. Default is None, i.e., width_x = width;
        cen_x: center of the spikes in the x-direction. Default is None, i.e., cen_x = (width_x-1)/2.0;
        cen_y: center of the spikes in the y-direction. Default is None, i.e., cen_y = (width_y-1)/2.0;
    Output:
        diagonals: 2D array with properties described above.
    """
    if width_x is None:
        width_x = width
    if width_y is None:
        width_y = width
        
    spikes = np.ones((width_y, width_x))
    
    if hw_spikes == 0:
        return spikes
    
    if cen_x is None:
        cen_x = (width_x - 1)/2.0
    if cen_y is None:
        cen_y = (width_y - 1)/2.0

    for y in range(width_y):
        for x in range(width_x):
            if np.abs(np.abs(x-cen_x)-np.abs(y-cen_y)) <= hw_spikes:
                spikes[y, x] = 0
    return spikes

def occulterLocation(name_input):
    """Return the x and y locations for the default occulting positions.
    Input:
        name_input -- name of the occulter, allowed inputs: ['BAR5', 'BAR10', 
                    'WEDGEA0.6', 'WEDGEA1.0', 'WEDGEA1.8', 'WEDGEA2.0', 'WEDGEA2.5', 'WEDGEA2.8', 
                    'WEDGEB1.0', 'WEDGEB1.8', 'WEDGEB2.0', 'WEDGEB2.5', 'WEDGEB2.8']
    Output:
        x, y -- values of the locations
    """
    #The array below contains emperical postions from the public
    # STIS coronagraphic archive, measured by Bin Ren from ADS: 2017SPIE10400E..21R
    #
    #The only difference is that the values are the median of the centers
    #that are determined by fitting two lines to the diffraction spikes, rather
    #than using Radon transfrom in 2017SPIE10400E..21R
    array_name_values = np.array([
                        ['WEDGEA2.0', 311.48, 613.74],
                        ['WEDGEA1.8', 309.43, 534.17],
                        ['BAR10',     624.73, 844.17],
                        ['WEDGEB2.5', 802.73, 302.46],
                        ['WEDGEA1.0', 309.65, 213.33],
                        ['WEDGEA0.6', 307.98,  67.59],
                        ['WEDGEA2.8', 309.51, 933.82],
                        ['WEDGEB1.8', 528.05, 303.68],
                        ['WEDGEA2.5', 309.03, 813.59],
                        ['BAR5',      969.73, 697.81],
                        ['WEDGEB1.0', 214.37, 305.08],
                        ['WEDGEB2.8', 917.71, 303.47],
                        ['WEDGEB2.0', 606.84, 303.63]
                        ]) 

    names_occulters = array_name_values[:, 0]
    name = name_input.upper()
    if name not in names_occulters:
        raise ValueError(name_input + " is not a supported location by STIS.")
    else:
        return float(array_name_values[np.where(names_occulters == name), 1][0][0]), float(array_name_values[np.where(names_occulters == name), 2][0][0])


def occultedMask(image, occulting_location, halfSize = None, halfSizeX = None, halfSizeY = None, postarg1 = None, postarg2 = None, diffraction_spike = 5):
    """Cut and shift the input mask image. The center of the output is the chosen occulting location. The diffraction spikes are also displayed by default.
    Input:
        image -- 2D array, the mask to be cut.
        occulting_location -- string, supported locations by STIS.
        halfSize -- integer, half size of the output, default will be 1024 pixel, with output width (2*1024+1) pixel.
            halfSizeX -- integer, half size of output width, will override halfSize for width if provided
            halfSizeY -- integer, half size of output height, will override halfSize for height if provided
        postarg1 -- POSTARG1 input in units of arcsec along x-direction
        postarg2 -- POSTARG2 input in units of arcsec along y-direction
        diffraction_spike -- integer, half size of the diffraction spikes. Default is 5.
    """
    
    image = np.copy(image)
    
    x_cen, y_cen = occulterLocation(occulting_location)
    
    if halfSize is None:
        halfSize = 1024 #create a big field of view
    if halfSizeX is None:
        halfSizeX = halfSize
    if halfSizeY is None:
        halfSizeY = halfSize

    if postarg1 is not None:
        x_cen += postarg1/0.05072 #unit conversion from arcsec to pixel for the x-direction
    if postarg2 is not None:
        y_cen += postarg2/0.05072 #unit conversion from arcsec to pixel for the y-direction
    
    if x_cen < 0 or x_cen > 1024 or y_cen < 0 or y_cen > 1024:
        print(f"The input combination ({occulting_location} with POSTARG1 = {postarg1} and POSTARG2 = {postarg2})\nputs your target beyond the STIS Field of View!\n\nThis visiblity tool can still run, but keep an eye on your exposure time in your Phase 2!")
    else:
        if image[int(round(y_cen, 0)), int(round(x_cen, 0))] == 1:
            print(f"The input combination ({occulting_location} with POSTARG1 = {postarg1} and POSTARG2 = {postarg2})\ncannot put your target behind any STIS occulter!\n\nThis visiblity tool can still run, but keep an eye on your exposure time in your Phase 2!")

    image[np.isnan(image)] = 0 #in case there are nan values
    
    if diffraction_spike is not None:
        image *= makeDiffractionSpikes(1024, hw_spikes = 5, cen_x = x_cen, cen_y = y_cen) #mask out diffraction spikes region
    
    image_interp = interp2d(np.arange(image.shape[1]), np.arange(image.shape[0]), image, kind = 'cubic', fill_value = 0)

    newImage = np.zeros((int(2*halfSizeY+1), int(2*halfSizeX+1)))
    x_range = np.round(np.arange(x_cen - halfSizeX, x_cen + halfSizeX + 0.1, 1), decimals = 2)
    y_range = np.round(np.arange(y_cen - halfSizeY, y_cen + halfSizeY + 0.1, 1), decimals = 2)

    newImage = image_interp(x_range, y_range)

    newImage[np.where(newImage < 0.9)] = 0 #0.9 is a hard-coded threshold by Bin Ren
    newImage[np.where(newImage != 0)] = 1
    
    return newImage
    
def rotateMask(image_mask, angle = None, reshape = True, new_width = None, new_height = None):
    """Rotate a mask.
    Input:
        image_mask -- 2D binary mask to be rotated.
        angle -- float, rotation angle in degrees.
        reshape -- Boolean, whether to give a different shape for the output.
            new_width -- integer, width of new shape.
            new_height -- integer, height of new shape.
    Output:
        rotated_mask -- 2D binary array.
    """
    image_mask0 = np.copy(image_mask)
    height_original = image_mask0.shape[0]
    ycen_original = int( (height_original - 1) / 2) #x coordinate of original center
    width_original = image_mask0.shape[0]
    xcen_original = int( (width_original - 1) / 2) #x coordinate of orignal center


    #1. Prepare the Mask
    if reshape:
        if new_width is None and new_height is None:
            new_width = int(np.sqrt(np.sum(np.asarray(image_mask.shape)**2)))
            new_height = np.copy(new_width)

            if (width_original % 2) != (new_width % 2 == 1):
                new_width += 1
            if (height_original % 2) != (new_height % 2 == 1):
                new_height += 1
        else:
            if (new_width < width_original) or (new_height < height_original):
                raise NotImplementedError(f"New width ({new_width}) or height ({new_height}) smaller than that of input image ({width_original} or {height_original}, respectively), try a bigger value!")
                 
        image_mask = np.zeros((new_height, new_width))
        ycen_new = int( (new_height - 1) / 2)
        xcen_new = int( (new_width - 1) / 2)
                
        if new_height % 2 == 0: #even-shaped input
            image_mask[ycen_new - ycen_original : ycen_new + ycen_original + 2, xcen_new - xcen_original : xcen_new + xcen_original + 2] = image_mask0
        else: #odd-shaped input
            image_mask[ycen_new - ycen_original : ycen_new + ycen_original + 1, xcen_new - xcen_original : xcen_new + xcen_original + 1] = image_mask0
    else:
        image_mask = image_mask0

    #2. Rotate
    if angle is None:
        angle = 0
        return image_mask

    result = rotate(image_mask, angle, reshape = False)
    result[np.where(result < 0.9)] = 0 #0.9 is a hard-coded threshold by Bin Ren
    result[np.where(result != 0)] = 1

    return result

def drawCoverageAndFeature(coverage_map, fov = 20, orient = 80, pa_feature_start = 30, seperation_feature_start = 8, pa_feature_end = None, seperation_feature_end = None, save_address = None, white_for_zero_coverage = False):
    """Draw feature on coverage map for given Field of View (FOV), ORIENT, and feature info (i.e., position angle, radial separation).
    Input:
        coverage_map -- 2D coverage map, created from `rotateMask` or `occultedMask`.
        fov -- float, field of view in arcseconds.
        orient -- float, ORIENT parameter (i.e., Position angle of the U3 axis from North to East).
        pa_feature_start -- float, position angle of the feature (start).
            pa_feature_end -- float, position angle of the feature (end). If not provided, it will be equal to `pa_feature_start`.
        seperation_feature_start -- float, radial separation of the feature from the center (start) in arcseconds.
            seperation_feature_end -- float, radial separation of the feature from the center (end) in arcseconds.  If not provided, it will be equal to `seperation_feature_start`.
        save_address -- None or a string addess. If not provided, it will just display on the screen.
        white_for_zero_coverage -- Boolean (Default: false), replace zero coverage with np.nan to make it white?
    Output:
        A 2D image on screen. If `save_address` is provided, then the image will be stored there.
    """
    coverage_map = np.copy(coverage_map)

    if white_for_zero_coverage: 
        coverage_map[coverage_map == 0] = np.nan #this makes zero coverage white
        
    if pa_feature_end is None:
        pa_feature_end = pa_feature_start

    if seperation_feature_end is None:
        seperation_feature_end = seperation_feature_start
        
    fig = plt.figure(figsize = [12, 12])
    rect = [0.1, 0.1, 0.8, 0.8] #plot Polar onto Cartesian, see https://stackoverflow.com/a/18834555
    # the carthesian axis:
    ax_carthesian  = fig.add_axes(rect)
    # the polar axis:
    ax_polar = fig.add_axes(rect, polar=True, frameon=False, alpha = 0.5)

    ext = np.array([-coverage_map.shape[1], coverage_map.shape[1], -coverage_map.shape[0], coverage_map.shape[0]])/2 * 0.05072
    im = ax_carthesian.imshow(coverage_map, origin='lower', extent = ext, interpolation='nearest')
    ax_carthesian.set_xlim(-fov/2,fov/2)
    ax_carthesian.set_ylim(-fov/2,fov/2)
    plt.xlabel('arcsec', labelpad=5)
    plt.ylabel('arcsec', labelpad=15)


    #plot colorbar for coverage map, see https://stackoverflow.com/a/59973687
    bothaxes = [ax_carthesian, ax_polar]
    cbar     = plt.colorbar(im, ax = bothaxes, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('Coverage Count')

    #draw arrows on Polar coordinates
    ax_polar.set_xticklabels([])
    #draw U3 axis, which is the upper-left diffraction spike
    ax_polar.set_theta_offset(np.deg2rad(135)) #rotate 135 deg counterclockwise
    ax_polar.set_rlim(0, fov/2)
    u3_vector = plt.arrow(0, 0, 0, fov/2, length_includes_head=True, head_length = fov/40, color = 'w', head_width = 0.05)
    u3_text = plt.text(0, fov/2, 'U3 Ref', color = 'k', fontsize = 20,
                          bbox=dict(facecolor='w', edgecolor='k', alpha = 0.5))

    #draw North vector
    orient_vector = plt.arrow(-np.deg2rad(orient), 0, 0, fov/2*0.9, length_includes_head=True, head_length = fov/40, color = 'r', head_width = 0.05)
    orient_text = plt.text(-np.deg2rad(orient), fov/2*0.9, 'North', color = 'k', fontsize = 20,
                          bbox=dict(facecolor='w', edgecolor='k', alpha = 0.5))
    #draw ORIENT definition
    plt.plot(np.linspace(-np.deg2rad(orient), 0, 20), [fov/4]*20, color = 'w')
    plt.text(np.linspace(-np.deg2rad(orient), 0, 20)[10], fov/4, 'ORIENT', fontsize = 20, rotation = np.linspace(-orient, 0, 20)[10]+45,
            va = 'center', ha = 'center', color = 'k', bbox=dict(facecolor='w', edgecolor='k', alpha = 0.5))
    plt.plot(0, fov/4, marker = (3, 0, 135), color = 'w')
    plt.plot(-np.deg2rad(orient), fov/4, 'wo')
    #draw East vector
    orient_vector = plt.arrow(-np.deg2rad(orient-90), 0, 0, fov/2*0.9, length_includes_head=True, 
                              head_length = fov/40, color = 'w', head_width = 0.05, ls = ':')
    orient_text = plt.text(-np.deg2rad(orient-90), fov/2*0.9, 'East', color = 'k', fontsize = 20,
                          bbox=dict(facecolor='w', edgecolor='k', alpha = 0.5))

    #draw feature
    feature = plt.plot([np.deg2rad(pa_feature_start - orient), np.deg2rad(pa_feature_end - orient)], 
                       [seperation_feature_start, seperation_feature_end],
                       'c-', lw = 5, zorder = 5)
    feature_center = plt.plot((np.deg2rad(pa_feature_start - orient) + np.deg2rad(pa_feature_end - orient)) / 2, 
                       (seperation_feature_start + seperation_feature_end) / 2,
                       'kp', lw = 5, zorder = 5)
    #draw position angle definition
    plt.plot(np.linspace(np.deg2rad(pa_feature_start+pa_feature_end)/2-np.deg2rad(orient), -np.deg2rad(orient), 20), [(seperation_feature_start + seperation_feature_end)/2]*20, 'y--')
    plt.text((np.deg2rad(pa_feature_start+pa_feature_end)/4-np.deg2rad(orient)), (seperation_feature_start + seperation_feature_end)/2, 
             'PA', fontsize = 20, rotation = np.linspace((pa_feature_start+pa_feature_end)/2 - orient, -orient, 20)[10] + 45,
            va = 'center', ha = 'center', color = 'k', bbox=dict(facecolor='w', edgecolor='y', alpha = 0.5))
    plt.plot(-np.deg2rad(orient), (seperation_feature_start + seperation_feature_end)/2, 
            marker = (3, 0, 135 - orient), color = 'y')
    
    #plot star
    plt.plot(0, 0, '*', ms = 10, color = 'y')
    
    if save_address is not None:
        plt.savefig(save_address, bbox_inches = 'tight', dpi = 300)
