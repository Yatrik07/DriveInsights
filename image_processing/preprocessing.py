import cv2
import numpy as np
import matplotlib.pyplot as plt
from data_ingestion.data_ingestion import getImage
import os

def resizeAndScale(img, image_shape=(225, 225)):
    '''
    Function Accepts an image and rescale to 0 - 1 range and resizes it to the given IMAGE_SHAPE
    '''
    img = cv2.resize(img, image_shape)
    return img/255

def resize(img_path, size=(640,640)):
    img = cv2.imread(img_path)
    cv2.imwrite(r'static\files\resized_input_img.jpg', cv2.resize(img, size))
    return cv2.resize(img, size)

def getImageAndAnnot(imagePath, annot, image_shape=(225, 225)):
    '''
    Function accepts the imagePath, annotations, and image shape
    It reads the image
    extracts the annots from the arg

    AND RESCALES THE ANNOTATIONS TO THE GIVEN IMAGE SHAPE

    Returns 1. resized and rescaled image
            2. scaled xmin, xmax, ymin, ymax

    '''

    image = getImage(imagePath)
    xmin, ymin, xmax, ymax = annot

    # image =
    x_scale = image_shape[1] / image.shape[1]
    y_scale = image_shape[0] / image.shape[0]

    return resizeAndScale(image), np.array([
        np.round(xmin * x_scale),
        np.round(ymin * y_scale),
        np.round(xmax * x_scale),
        np.round(ymax * y_scale)
    ])



def showImageWithAnnot(imagePath, annot, title='Image', show=True, save=False, path=None, save_name = "imageWith_bbox.jpg"):
    '''
    Accepts image and annotations and annotations and shows image with the bounding box
    '''
    
    image = getImage(imagePath)
    image = resizeAndScale(image)
    plt.imshow(image)
    plt.savefig(os.path.join(path, "resizedImg_plt.jpg"))

    annot = list(annot[0].astype(int))
    image = cv2.rectangle(image, annot[:2], annot[2:], (0, 0, 1), 2)
    
    plt.imshow(image)
    plt.axis('off')
    plt.title(title)
    if show==True:
        # plt.show()
        pass
    if save==True:
        plt.savefig(os.path.join(path, "imageWith_bbox_plt.jpg"))
        cropped = image[int(annot[1]):int(annot[3]) , int(annot[0]):int(annot[2])]

        cv2.imwrite(os.path.join(path, save_name) , image*255)

        cv2.imwrite(os.path.join(path, 'cropped.jpg'), cropped*255)

    return os.path.join(path, save_name)
