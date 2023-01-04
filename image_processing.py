#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
from cmath import inf
import math
from turtle import color
from webbrowser import get
from PIL import Image


# VARIOUS FILTERS
#lab 1 stuff!
def get_pixel(image, x, y, boundary_behavior='zero'):
    if x in range(image['width']) and y in range(image['height']):
        index = image['width']*(y)+(x)
        return image['pixels'][index]
    else:
        if boundary_behavior == 'zero':
          return 0
        elif boundary_behavior == 'wrap':
            newx = 0
            newy = 0
            if x >= image['width'] or x < 0:
                newx = x % image['width']
            else:
                newx = x
            if y>= image['height'] or y < 0:
                newy = y % image['height']
            else:
                newy = y
            return get_pixel(image, newx, newy, 'wrap')
        elif boundary_behavior == "extend":
            newx = 0
            newy = 0
            if x >= image['width']:
                newx = image['width']-1
            elif x < 0:
                newx = 0
            else:
                newx = x
            if y >= image['height']:
                newy = image['height']-1
            elif y < 0:
                newy = 0
            else:
                newy = y
            return get_pixel(image, newx, newy, 'extend')

def set_pixel(image, x, y, c):
    index = image['width']*(y)+(x)
    image['pixels'][index] = c

def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    result['pixels'] = image['pixels'].copy()
    for y in range(image['height']):
        for x in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

def get_coordinates(image, pixel_index):
    y_value = int((pixel_index)/image['width'])
    x_value = ((pixel_index) % image['width'])
    return x_value, y_value

def correlate(image, kernel, boundary_behavior):

    kernel_dimension = len(kernel)**(1/2)
    kernel_range = int((kernel_dimension-1)/2)
    new_values = []
    for i in range(0, len(image['pixels'])):
        pixel_index = i
        x, y = get_coordinates(image, pixel_index)
        result = 0
        index = -1
        term = False
        for j in range(y-kernel_range, y+kernel_range+1):
            currenty = j
            for k in range(x-kernel_range, x+kernel_range+1):
                currentx = k
                index += 1
                if index >= len(kernel):
                    term = True
                    break
                result += get_pixel(image, currentx, currenty, boundary_behavior) * kernel[index]
            if term:
                break
        new_values.append(result)
    return {
            'height': image['height'],
            'width': image['width'],
            'pixels': new_values
    }

def round_and_clip_image(image):
    length = image['height']*image['width']
    for i in range(0, length):
        if image['pixels'][i] <= 0:
            image['pixels'][i] = 0
        if image['pixels'][i] >= 255:
            image['pixels'][i] = 255
        else:
            image['pixels'][i] = round(image['pixels'][i])
    return image

def blur_kernel_creator(n):
    kernel_size = n**2
    kernel_entry = 1/kernel_size
    kernel = []
    for i in range(0, kernel_size):
        kernel.append(kernel_entry)
    return kernel

def blurred(image, n):
    kernel = blur_kernel_creator(n)
    correlated = correlate(image, kernel, 'extend')
    final_blur = round_and_clip_image(correlated)
    return final_blur

def sharpened(image, n):
    blur = blurred(image, n)
    new_image = {'height': image['height'],
                'width': image['width'],
                'pixels': image['pixels'][:]}
    # sharpened = 2*image['pixels'] - blur
    for i in range(0, len(new_image['pixels'])):
        new_image['pixels'][i] = 2*new_image['pixels'][i]
    sharpened = []
    for item1, item2 in zip(new_image['pixels'], blur['pixels']):
        item = item1 - item2
        sharpened.append(item)
    new_image['pixels'] = sharpened
    final_sharpened = round_and_clip_image(new_image)
    return final_sharpened

def edges(image):
    x_kernel = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    y_kernel = [-1, -2, -1, 0, 0, 0, 1, 2, 1]
    ox = correlate(image, x_kernel, 'extend')
    oy = correlate(image, y_kernel, 'extend') 
    new_values = []
    for l in range(0, len(ox['pixels'])):
        new_values.append(round((ox['pixels'][l]**2 + oy['pixels'][l]**2)**(1/2)))
    return round_and_clip_image({'height': image['height'],
            'width': image['width'],
            'pixels': new_values
            })


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError("Unsupported image mode: %r" % img.mode)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

#lab 2 stuff!

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color(image):
        """Returns color image with a filter applied to it."""
        # go to grey scale
        # apply filt()
        # take back to color
        r, g, b = list_of_colors(image)
        filtered_r = filt(r)
        filtered_g = filt(g)
        filtered_b = filt(b)
        return {'width': image['width'],
         'height': image['height'],
         'pixels': [(filtered_r['pixels'][i], filtered_g['pixels'][i], filtered_b['pixels'][i]) for i in range(len(image['pixels']))]
        }
    return color

def list_of_colors(image):
    """
    Helper function that returns three greyscale images g, r, b
    """
    r = {'width': image['width'],
         'height': image['height'],
         'pixels': [image['pixels'][i][0] for i in range(len(image['pixels']))]
    }
    g = {'width': image['width'],
         'height': image['height'],
         'pixels': [image['pixels'][i][1] for i in range(len(image['pixels']))]
    }
    b = {'width': image['width'],
         'height': image['height'],
         'pixels': [image['pixels'][i][2] for i in range(len(image['pixels']))]
    }
    return r, g, b

def make_blur_filter(n):
    """
    Return function that blurs an image
    """
    def blur(image):
        blurred_image = blurred(image, n)
        return blurred_image
    return blur



def make_sharpen_filter(n):
    """
    Return function that sharpens an image
    """
    def sharpen(image):
        sharpened_image = sharpened(image, n)
        return sharpened_image
    return sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter_combiner(image):
        for i in filters:
            #apply new filters to cumulative image iteratively
            image = i(image)
        return image
    return filter_combiner

    

            



# SEAM CARVING

# Main Seam Carving Implementation



# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    #separate color into three greyscales
    return {'width': image['width'],
         'height': image['height'],
         'pixels': [round(.299*r + .587*g + .114*b) for r,g,b in image['pixels']] }

    
def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_image
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    #create copy of given image with all zeros in it
    empty_cem = {'height': energy['height'],
                'width': energy['width'],
                'pixels': [0 for i in energy['pixels']]}
    #get the coordinates of the pixel
    for i in range(len(empty_cem['pixels'])):
        x, y = get_coordinates(empty_cem, i)
        #make the top row of the image equal to the top row of the energy map
        if y == 0:

            empty_cem['pixels'][i] += get_pixel(energy, x, y)
        #cumulatively add the energies by adding the current energy to the lowest adjacent top energy value
        else:
            minimum = float('inf')
            for j in {x-1, x, x+1}:
                if get_pixel(empty_cem, j, y-1, 'extend') < minimum:
                    minimum = get_pixel(empty_cem, j, y-1, 'extend')
            empty_cem['pixels'][i] += minimum + get_pixel(energy, x, y)
    return empty_cem
                

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-image
    seam (computed as described in the lab 2 writeup).
    """
    #establish coordinates +index of bottom min
    min_energy_seam = []
    bottom_row = cem['height']-1
    minimum = float('inf')
    for i in range(0, cem['width']):
        if get_pixel(cem, i, bottom_row)< minimum:
            minimum = get_pixel(cem, i, bottom_row)
            bottom_index = i
    min_energy_seam.append(index_returner(cem, bottom_index, bottom_row))
    #backtrack the energy seam from the second to bottom row to the top row
    current_index = bottom_index
    for l in range(bottom_row-1, -1, -1):
        new_min = float('inf')
        for k in (current_index-1, current_index, current_index+1):
            if get_pixel(cem, k, l) < new_min and k >= 0 and k <= (cem['width']-1):
                new_min = get_pixel(cem,  k, l)
                current_index = k
                x = k
        min_energy_seam.append(index_returner(cem, x, l))
    return min_energy_seam[::-1]
    

    
    
def index_returner(image, x, y):
    """
    Given an image and coordinates, return the index of the pixel in the list
    """
    return (image['width'] * y) + x


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    new_image = {'width': image['width'],
         'height': image['height'],
         'pixels': image['pixels'][:]}
    new_image['width'] -= 1
    for i in range(len(seam)):
        new_image['pixels'].pop(seam[i]-i)
    return new_image

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    count = 0
    new_image = {'width': image['width'],
         'height': image['height'],
         'pixels': image['pixels'].copy()}
    while count < ncols: 
        grey = greyscale_image_from_color_image(new_image)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        seamless_image =  image_without_seam(new_image, seam)
        new_image = seamless_image
        count += 1
    return new_image



def custom_feature(image):
    """ 
    Takes a color image and swaps the rgb colors such that r is now g, g is now b,
    and b is now r. Uses helper function list_of_colors_swapped.
    Returns a new color image
    """
    new_rgb = [(swap[2], swap[0], swap[1]) for swap in image['pixels']]
    return {'width': image['width'],
         'height': image['height'],
         'pixels': new_rgb }




if __name__ == "__main__":
    d = 1

    #cat
    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # inverted_color_cat = color_inverted(load_color_image('test_images/cat.png'))
    # saved_cat = save_color_image(inverted_color_cat, 'test_images/inverted_cat.png')

    # python
    # blur_color = color_filter_from_greyscale_filter(make_blur_filter(9))
    # python9 = blur_color(load_color_image('test_images/python.png'))
    # saved_python = save_color_image(python9, 'test_images/blurred_python.png')

    # #sparrowchick.png
    # sharpen_color = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sparrowchick7 = sharpen_color(load_color_image('test_images/sparrowchick.png'))
    # saved_sparrow = save_color_image(sparrowchick7, 'test_images/sharpened_sparrow.png')

    # #cascadefilter
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog_filter = filt(load_color_image('test_images/frog.png'))
    # save_frog = save_color_image(frog_filter, 'test_images/frog_filter.png')

    #twocats
    # two_cats = load_color_image('test_images/twocats.png')
    # seam_cats = seam_carving(two_cats, 100)
    # save_cats = save_color_image(seam_cats, 'test_images/seam_cats.png')

    #custom_img
    # chess = load_color_image('test_images/chess.png')
    # chess_swap = color_swap(chess)
    # chess_save = save_color_image(chess_swap, 'test_images/chess_swap.png')
