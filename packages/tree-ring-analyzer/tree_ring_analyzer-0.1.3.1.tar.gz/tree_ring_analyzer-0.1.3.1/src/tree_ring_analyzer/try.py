import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import tifffile
import os
from scipy.ndimage import binary_dilation
import numpy as np
import cv2
import pandas as pd
from scipy.stats import ttest_ind, f_oneway
import csv
import glob

def createRingSeg(mask):
    gtRings = []
    for i in np.unique(mask)[1:]:
        _image = np.zeros_like(mask)
        _image[(mask == i) & (mask != 0)] = 1
        gtRing, _ = cv2.findContours(_image.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        gtRing = np.concatenate(gtRing)
        gtRings.append(gtRing[:, 0, :])

    gtRingSeg = np.zeros_like(mask)
    sortedRadius = np.argsort([len(ring) for ring in gtRings])[::-1]
    for i in range(len(sortedRadius)):
        cv2.drawContours(gtRingSeg, [gtRings[sortedRadius[i]][:, None, :]], 0, 1, 1)
    return gtRingSeg

cmap = ListedColormap(['#0072B2', '#56B4E9', '#F0E442', '#E69F00', '#CC79A7', '#000000', '#999999', '#332288', '#117733', '#882255',
                       '#661100', '#44AA99', '#DDCC77', '#AA4499', '#88CCEE', '#009E73'])

# image_folders = ['/home/khietdang/Documents/khiet/treeRing/input',
#                  '/home/khietdang/Documents/khiet/treeRing/predictions_bigDisRingAugGray16',
#                  '/home/khietdang/Documents/khiet/treeRing/MO_bigDisRingAugGray16',
#               '/home/khietdang/Documents/khiet/treeRing/predictions_bigDisRingAugGrayWH16',
#               '/home/khietdang/Documents/khiet/treeRing/MO_bigDisRingAugGrayWH16']
# title_list = ['Input', 'Predicted results\nNo augmented holes', 'Morphology results\nNo augmented holes', 
#               'Predicted results\nAugmented holes', 'Morphology results\nAugmented holes']
# denotation_list = ['(A)', '(B)', '(C)']
# image_list = ['12 E 3 t_8µm_x50.tif',
#               '4 E 3 t_8µm_x50 2.tif',
#               '8 E 5 b_8µm_x50.tif']

# plt.figure(figsize=(5.04, 3.09))
# i = 1
# for k in range(len(image_list)):
#     for j in range(len(image_folders)):
#         plt.subplot(3, 5, i)
#         image = tifffile.imread(os.path.join(image_folders[j], image_list[k]))
#         image = cv2.resize(image, (image.shape[0], image.shape[0]))
#         if j in [0]:
#             plt.imshow(image)
#         elif j in [2, 4]:
#             plt.imshow(binary_dilation(image, iterations=23), cmap='gray')
#         else:
#             image = (image - np.min(image))/(np.max(image) - np.min(image))
#             plt.imshow(image ** 0.5, cmap='gray')
#         plt.axis('off')
#         if j == 0:
#             plt.text(-int(image.shape[1] / 5), int(image.shape[0] / 2), denotation_list[k], fontsize=6, va='center', ha='left', clip_on=False)
#         if i <= 5:
#             plt.title(title_list[i - 1], fontsize=6)
#         i += 1
# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.04, right=1, bottom=0, top=0.91)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_distancemap.png', dpi=300)

#####################################################################################################################""

# image_folders = ['/home/khietdang/Documents/khiet/treeRing/input',
#                  '/home/khietdang/Documents/khiet/treeRing/maskSeg',
#               '/home/khietdang/Documents/khiet/treeRing/predictedSeg_A',
#               '/home/khietdang/Documents/khiet/treeRing/predictedSeg_MOE',
#               '/home/khietdang/Documents/khiet/treeRing/predictedSeg_H0']
# title_list = ['Input', 'Ground truth', 'Active contour', 'Morphology + Endpoints', 'A-star algorithm']
# denotation_list = ['(A)', '(B)', '(C)']
# image_list = ['12 E 3 t_8µm_x50.tif',
#               '4 E 3 t_8µm_x50 2.tif',
#               '8 E 5 b_8µm_x50.tif']

# plt.figure(figsize=(5.04, 3.06))
# i = 1
# for k in range(len(image_list)):
#     for j in range(len(image_folders)):
#         plt.subplot(3, 5, i)
#         image = tifffile.imread(os.path.join(image_folders[j], image_list[k]))
#         image = cv2.resize(image, (image.shape[0], image.shape[0]))
#         if j in [0]:
#             plt.imshow(image)
#         else:
#             plt.imshow(image, cmap=cmap, vmin=0, vmax=15)
#         plt.axis('off')
#         if j == 0:
#             plt.text(-int(image.shape[1] / 5), int(image.shape[0] / 2), denotation_list[k], fontsize=6, va='center', ha='left', clip_on=False)
#         if i <= 5:
#             plt.title(title_list[i - 1], fontsize=6)
#         i += 1
# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.04, right=1, bottom=0, top=0.94)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_postprocessing_annotated.png', dpi=300)

######################################################################################""

# image_folders = ['/home/khietdang/Documents/khiet/treeRing/Liudmila/input',
#                  '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictions_ring',
#                  '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictedSeg_H0',
#               '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictedSeg_H01',
#               '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictedSeg_H02',
#               '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictedSeg_H0R',
#               '/home/khietdang/Documents/khiet/treeRing/Liudmila/predictedSeg_H0RR']
# title_list = ['Input', 'Predicted results', 'H0', 'H0 + H1', 'H0 + H2', 'H0 + FDRS', 'H0 + FDRS + IRR']
# denotation_list = ['(A)', '(B)', '(C)', '(D)', '(E)']
# image_list = ['98m_x50_8 µm.tif',
#               '74b_x50_8 µm.tif',
#               '21(5)_x50_8 µm.tif',
#               '15(4)_x50_8 µm.tif',
#               '53b_x50_8 µm.tif']

# plt.figure(figsize=(7.04, 5.06))
# i = 1
# for k in range(len(image_list)):
#     for j in range(len(image_folders)):
#         plt.subplot(5, 7, i)
#         image = tifffile.imread(os.path.join(image_folders[j], image_list[k]))
#         image = cv2.resize(image, (image.shape[0], image.shape[0]))
#         if j == 0:
#             plt.imshow(image)
#         elif j == 1:
#             image = (image - np.min(image))/(np.max(image) - np.min(image))
#             plt.imshow(image ** 0.5, cmap='gray')
#         else:
#             plt.imshow(image, cmap=cmap, vmin=0, vmax=15)
#         plt.axis('off')
#         if j == 0:
#             plt.text(-int(image.shape[1] / 5), int(image.shape[0] / 2), denotation_list[k], fontsize=8, va='center', ha='left', clip_on=False)
#         if i <= 7:
#             plt.title(title_list[i - 1], fontsize=8)
#         i += 1
# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.04, right=1, bottom=0, top=0.94)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_postprocessing_unannotated.png', dpi=300)

#######################################################################################################

# image_folders = ['/home/khietdang/Documents/khiet/treeRing/input',
#                  '/home/khietdang/Documents/khiet/treeRing/masks',
#                  '/home/khietdang/Documents/khiet/INBD/inference/INBD_Our_train',
#                  '/home/khietdang/Documents/khiet/unetr/UNETR_2D/output2',
#                  '/home/khietdang/Documents/khiet/treeRing/output_H0RR']

# title_list = ['Input', 'Masks', 'INBD', 'UNETR', 'Ours']
# denotation_list = ['(A)', '(B)', '(C)']
# image_list = ['4E_4milieu8microns_x40.tif',
#               '3Tmilieu8microns_x40.tif',
#               '12 E 2 t_8µm_x50.tif']

# plt.figure(figsize=(5.04, 3.06))
# i = 1
# for k in range(len(image_list)):
#     for j in range(len(image_folders)):
#         plt.subplot(3, 5, i)
#         if j == 2:
#             image = np.load(os.path.join(image_folders[j], image_list[k] + '.labelmap.npy'))
#             image = createRingSeg(image)
#         else:
#             image = tifffile.imread(os.path.join(image_folders[j], image_list[k]))
#         image = cv2.resize(image, (image.shape[0], image.shape[0]))

#         if j == 0:
#             plt.imshow(image)
#         else:
#             if j != 1:
#                 image = binary_dilation(image, iterations=23)
#             else:
#                 image = binary_dilation(image, iterations=20)
#             plt.imshow(image, cmap='gray')

#         plt.axis('off')
#         if k == 0:
#             plt.title(title_list[j], fontsize=6)
#         if j == 0:
#             plt.text(-int(image.shape[1] / 5), int(image.shape[0] / 2), denotation_list[k], fontsize=6, va='center', ha='left', clip_on=False)
#         i +=1

# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.04, right=1, bottom=0, top=0.94)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_compare_other.png', dpi=300) 

####################################################################################################
# image_folders = ['/home/khietdang/Documents/khiet/INBD/dataset/{}/inputimages',
#                  '/home/khietdang/Documents/khiet/INBD/dataset/{}/annotations',
#                  '/home/khietdang/Documents/khiet/INBD/inference/INBD_{}_',
#                  '/home/khietdang/Documents/khiet/INBD/dataset/{}/predictedSeg']
# data_list = ['DO', 'EH', 'VM']
# image_list = ['DO_0033.jpg',
#               'EH_0037.jpg',
#               'VM_0036.jpg']
# title_list = ['Input', 'Masks', 'INBD', 'Ours']
# plt.figure(figsize=(4.05,3.06))
# i = 1
# for k in range(len(image_list)):
#     for j in range(len(image_folders)):
#         plt.subplot(3, 4, i)
#         if j == 2:
#             image = np.load(os.path.join(image_folders[j].format(data_list[k]), image_list[k] + '.labelmap.npy'))
#         elif j == 1:
#             image = tifffile.imread(os.path.join(image_folders[j].format(data_list[k]), image_list[k]).split('.')[0] + '.tiff')
#             image[image == -1] = 0
#         else:
#             image = cv2.imread(os.path.join(image_folders[j].format(data_list[k]), image_list[k]))
#             if j == 3:
#                 image = image[:, :, 0]

#         image = cv2.resize(image.astype(np.uint8), (image.shape[0], image.shape[0]))
#         if j == 0:
#             plt.imshow(image)
#         else:
#             plt.imshow(image, cmap=cmap, vmin=0, vmax=15)
#         plt.axis('off')
#         if k == 0:
#             plt.title(title_list[j], fontsize=5)
#         if j == 0:
#             plt.text(-int(image.shape[1] / 5), int(image.shape[0] / 2), data_list[k], fontsize=5, va='center', ha='left', clip_on=False)
#         i += 1

# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.05, right=1, bottom=0, top=0.94)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_compare_other2.png', dpi=300)

#####################################################################################################
# image_folders = ['/home/khietdang/Documents/khiet/treeRing/input',
#                  '/home/khietdang/Documents/khiet/treeRing/masks']
# title_list = ['Images', 'Masks']
# denotation_list = ['(A)', '(B)', '(C)']
# image_list = ['12 E 3 t_8µm_x50.tif',
#               '4 E 3 t_8µm_x50 2.tif',
#               '8 E 5 b_8µm_x50.tif']

# plt.figure(figsize=(3.12, 2.1))
# i = 1
# for k in range(len(image_folders)):
#     for j in range(len(image_list)):
#         plt.subplot(2, 3, i)
#         image = tifffile.imread(os.path.join(image_folders[k], image_list[j]))
#         image = cv2.resize(image, (image.shape[0], image.shape[0]))
#         if k == 1:
#             image = binary_dilation(image, iterations=20)
#             plt.imshow(image, cmap='gray')
#         else:
#             plt.imshow(image)
#         plt.axis('off')
#         if j == 0:
#             plt.text(-int(image.shape[1] * 0.4), int(image.shape[0] / 2), title_list[k], fontsize=6, va='center', ha='left', clip_on=False)
#         if i <= 3:
#             plt.title(denotation_list[j], fontsize=6)
#         i += 1
# plt.subplots_adjust(wspace=0.01, hspace=0.01, left=0.12, right=1, bottom=0, top=0.9)
# plt.savefig('/home/khietdang/Documents/khiet/treeRing/doc/fig_dataset_annotated.png', dpi=300)
####################################################################################################"
output_csv = '/home/khietdang/Documents/khiet/treeRing/doc/statistics.csv'
with open(output_csv, 'w') as f:
    write = csv.writer(f)
    write.writerow(['Position', 'Parameters', 'Object types', 'Number of Control', 'Number of Pressure', 'Control', 'Pressure', 'p-value'])
list_control_top = ['T 2 t', 'T 4 t', 'SCD 1 t', 'T 5 t']
list_control_middle = ['T 2 m', 'T 4 m', 'SCD 1 m', 'T 5 m',
    '3Tmilieu8microns_x40', '4Tmilieu8microns_x40', '5Tmilieu8microns_x40']
list_control_bottom = ['T 2 b', 'T 4 b', 'SCD 1 b', 'T 5 b']
list_control = [list_control_top, list_control_middle, list_control_bottom]
list_pressure_top = ['4 E 1 t', '4 E 2 t', '4 E 3 t', '4 E 4 t', '4 E 5 t', 'CC1 t', 
                 '8 E 1 t', '8 E 2 t', '8 E 3 t', '8 E 4 t', '8 E 5 t',
                 '12 E 1 t', '12 E 2 t', '12 E 3 t', '12 E 4 t', '12 E 5 t',
                 '12 t']
list_pressure_middle = ['4 E 1 m', '4 E 2 m', '4 E 3 m', '4 E 4 m', '4 E 5 m', 'CC1 m', 
                 '8 E 1 m', '8 E 2 m', '8 E 3 m', '8 E 4 m', '8 E 5 m',
                 '12 E 1 m', '12 E 2 m', '12 E 3 m', '12 E 4 m', '12 E 5 m',
                 '3E_4milieu8microns_x40', '4E_4milieu8microns_x40', '1E_4milieu8microns_x40']
list_pressure_bottom = ['4 E 1 b', '4 E 2 b', '4 E 3 b', '4 E 4 b', '4 E 5 b', 'CC1 b', 
                 '8 E 1 b', '8 E 2 b', '8 E 3 b', '8 E 4 b', '8 E 5 b',
                 '12 E 1 b', '12 E 2 b', '12 E 3 b', '12 E 4 b', '12 E 5 b']
list_pressure = [list_pressure_top, list_pressure_middle, list_pressure_bottom]

df_list = glob.glob('/home/khietdang/Documents/khiet/treeRing/output/*_parameters.csv')
for df_path in df_list:
    if df_path == df_list[0]:
        df = pd.read_csv(df_path)
    else:
        df = pd.concat([df, pd.read_csv(df_path)])

df = df[df['base unit'] == 'micrometer']
positions = {0: 'Top', 1: 'Middle', 2: 'Bottom', 3: 'Whole'}
parameters = ['perimeter', 'area', 'area_convex', 'axis_major_length', 'axis_minor_length', 'eccentricity', 'feret_diameter_max', 'orientation', 'area_growth']
object_types = ['pith', 'ring', 'trunk']

for position in range(0, 4):
    if position != 3:
        mask_control = df['image'].apply(lambda x: any(k in x for k in list_control[position]) if isinstance(x, str) else False)
        mask_pressure = df['image'].apply(lambda x: any(k in x for k in list_pressure[position]) if isinstance(x, str) else False)
    else:
        mask_control = df['image'].apply(lambda x: any(k in x for k in list_control[0] + list_control[1] + list_control[2]) if isinstance(x, str) else False)
        mask_pressure = df['image'].apply(lambda x: any(k in x for k in list_pressure[0] + list_pressure[1] + list_pressure[2]) if isinstance(x, str) else False)
    df_control = df[mask_control]
    df_pressure = df[mask_pressure]
    list_image_control = np.unique(np.array(df_control['image']))
    list_image_pressure = np.unique(np.array(df_pressure['image']))
    
    for parameter in parameters:
        for object_type in object_types:
            if object_type != 'ring':
                a = np.array(df_control[df_control['object_type'] == object_type][parameter])
                b = np.array(df_pressure[df_pressure['object_type'] == object_type][parameter])
                with open(output_csv, 'a') as f:
                    write = csv.writer(f)
                    write.writerow([positions[position], parameter, object_type, len(a), len(b), np.mean(a), np.mean(b), ttest_ind(a, b).pvalue])
            else:
                group0c, group1c, group2c = [], [], []
                for image in list_image_control:
                    a = df_control[df_control['object_type'] == object_type]
                    a = np.array(a[a['image'] == image][parameter])
                    group2c.append(a[-1])
                    group1c.append(a[-2])
                    if len(a) >= 3:
                        group0c.append(a[-3])
                group0p, group1p, group2p = [], [], []
                for image in list_image_pressure:
                    a = df_pressure[df_pressure['object_type'] == object_type]
                    a = np.array(a[a['image'] == image][parameter])
                    group2p.append(a[-1])
                    group1p.append(a[-2])
                    if len(a) >= 3:
                        group0p.append(a[-3])
                    else:
                        print(image)
                with open(output_csv, 'a') as f:
                    write = csv.writer(f)
                    write.writerow([positions[position], parameter, 'Last ring -2', len(group0c), len(group0p), np.mean(np.array(group0c)), np.mean(np.array(group0p)), 
                                    ttest_ind(np.array(group0c), np.array(group0p)).pvalue])
                    write.writerow([positions[position], parameter, 'Last ring -1', len(group1c), len(group1p), np.mean(np.array(group1c)), np.mean(np.array(group1p)), 
                                    ttest_ind(np.array(group1c), np.array(group1p)).pvalue])
                    write.writerow([positions[position], parameter, 'Last ring', len(group2c), len(group2p), np.mean(np.array(group2c)), np.mean(np.array(group2p)), 
                                    ttest_ind(np.array(group2c), np.array(group2p)).pvalue])
df_out = pd.read_csv(output_csv)
pvalue = np.array(df_out['p-value'])
df_out['Significance'] = np.where(pvalue < 0.001, '***', np.where(pvalue < 0.01, '**', np.where(pvalue < 0.05, '*', '')))
df_out.to_csv(output_csv)