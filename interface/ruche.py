from math import sin, cos, pi
import os
import numpy as np
from math import cos, sin, sqrt, pi
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from numpy import arange, sin, pi
from matplotlib import cm, colors
import matplotlib.animation as animation
import sys
import matplotlib.image as image
from matplotlib.patches import Polygon

def draw_camera_pixel_ids(xs_center, ys_center, pixels_id, axes):
    """draw the camera pixels id in the camera"""

    axes.text(xs_center, ys_center, pixels_id, fontsize=10, ha='center')
def pointy_top_hex(center_x, center_y, size_edge_to_edge, i):
    """Define coordinate of edges' pixels with pointy up """
    rayon = size_edge_to_edge / 2
    angle_deg = 60 * i + 30
    angle_rad = pi / 180 * angle_deg
    Point = (center_x + rayon * cos(angle_rad),
             center_y + rayon * sin(angle_rad))
    return Point
def make_mini_cam_mathieu_with_node(size_edge_to_edge):
    '''
    Create and Make the mapping of minicamera
    '''

    mini_cam_mathieu_with_node = {}
    with open("/home/mathias/Documents/unige/UNIGE/2eme/appliInfo/script/folder_result_acquisition_babymind/MappingTable_MiniCamera.txt","r") as file:
        line=file.readline()
        line = file.readline().split("\n")[0].split("\t")
        while line[0] != "":
            pixel_id = float(line[6])
            pixel_center = (float(line[7]), float(line[8]))

            xs = []
            ys = []
            for i in range(6):
                Point = pointy_top_hex(pixel_center[0], pixel_center[1], size_edge_to_edge, i)
                xs.append(Point[0])
                ys.append(Point[1])

            mini_cam_mathieu_with_node[pixel_id] = [(xs, ys), pixel_center]


            line = file.readline().split("\n")[0].split("\t")
    dict_pixels_ids_1 = {117: 0, 84: 1, 116: 2, 113: 3, 111: 4, 86: 5, 85: 6, 90: 7, 119: 8, 112: 9, 110: 10, 129: 11,
                         72: 12, 87: 13, 88: 14, 91: 15, 118: 16, 115: 17, 109: 18, 128: 19, 125: 20, 123: 21,
                         74: 22, 73: 23, 78: 24, 89: 25, 95: 26, 94: 27, 105: 28, 114: 29, 108: 30, 131: 31,
                         124: 32, 122: 33, 75: 34, 76: 35, 79: 36, 93: 37, 92: 38, 48: 39, 104: 40, 101: 41,
                         99: 42, 130: 43, 127: 44, 121: 45, 77: 46, 83: 47, 82: 48, 50: 49, 49: 50, 54: 51,
                         107: 52, 100: 53, 98: 54, 141: 55, 126: 56, 120: 57, 81: 58, 80: 59, 60: 60, 51: 61, 52: 62,
                         55: 63, 106: 64, 103: 65, 97: 66, 140: 67, 137: 68, 135: 69, 62: 70, 61: 71, 66: 72, 53: 73,
                         59: 74, 58: 75, 10: 76, 102: 77, 96: 78, 143: 79, 136: 80, 134: 81, 63: 82, 64: 83, 67: 84,
                         57: 85, 56: 86, 6: 87, 7: 88, 11: 89, 8: 90, 142: 91, 139: 92, 133: 93, 65: 94, 71: 95,
                         70: 96, 46: 97, 0: 98, 1: 99, 4: 100, 5: 101, 9: 102, 22: 103, 138: 104, 132: 105,
                         69: 106, 68: 107, 42: 108, 43: 109, 47: 110, 44: 111, 2: 112, 3: 113, 18: 114, 19: 115,
                         23: 116, 20: 117, 36: 118, 37: 119, 40: 120, 41: 121, 45: 122, 34: 123, 12: 124, 13: 125,
                         16: 126, 17: 127, 21: 128, 38: 129, 39: 130, 30: 131, 31: 132, 35: 133, 32: 134, 14: 135,
                         15: 136, 24: 137, 25: 138, 28: 139, 29: 140, 33: 141, 26: 142, 27: 143}
    dict_pixels_ids_1=dict((item,key) for (key,item) in dict_pixels_ids_1.items())
    mini_cam_mathieu_with_node=dict((dict_pixels_ids_1[key],item) for (key,item) in mini_cam_mathieu_with_node.items())



    return mini_cam_mathieu_with_node

def Makeruche(choice,data_electronics_HG,data_electronics_LG,data_electronics_tot,figPlace):
    fig_fen1 = plt.figure(facecolor="green")
    ruche =fig_fen1.add_subplot(111)
    #canvas_fen1 = FigureCanvasTkAgg(self.fig_fen1, master=self.fen1)
    #canvas_fen1.get_tk_widget().grid(row=1, column=6, rowspan=8, padx=10, pady=5, sticky='NSEW')
    #toolbar_frame_fen1 = Frame(fen1, highlightcolor="red", highlightthickness=1, highlightbackground="blue")
    #toolbar_frame_fen1.grid(row=1, column=6)
    #toolbar_fen1 = NavigationToolbar2Tk(self.canvas_fen1, self.toolbar_frame_fen1)
    #canvas_fen1._tkcanvas.grid(row=1, column=6, rowspan=8, padx=10, pady=5, sticky='NSEW')
    if choice =="HG":
        norm1 = matplotlib.colors.Normalize(np.min(data_electronics_HG), np.max(data_electronics_HG))
        data_from_electronics=data_electronics_HG
    elif choice=="LG":
        norm1 = matplotlib.colors.Normalize(np.min(data_electronics_LG), np.max(data_electronics_LG))
        data_from_electronics=data_electronics_LG
    else:
        norm1 = matplotlib.colors.Normalize(np.min(data_electronics_tot), np.max(data_electronics_tot))
        data_from_electronics=data_electronics_tot

    # if box_choice.get() == "Temp":
    #     norm1 = matplotlib.colors.Normalize(0, 35)
    # else:
    #     if value_hg_or_lg.get() == "HG":
    #         self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_HG), np.max(self.data_electronics_HG))
    #     elif self.value_hg_or_lg.get() == "LG":
    #         self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_LG), np.max(self.data_electronics_LG))
    #     elif self.value_hg_or_lg.get() == "TOT":
    #         self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_tot), np.max(self.data_electronics_tot))
    cmap1 = matplotlib.cm.ScalarMappable(norm=norm1, cmap=matplotlib.cm.jet)
    cmap1.set_array([])
    cb_fen1 = fig_fen1.colorbar(cmap1)  # , ticks=facecolor)
    reatribute_id_pixels = make_mini_cam_mathieu_with_node(23.2)

    dict_polygones={}
    list_centers_xs = []
    list_centers_ys = []
    for pixels_id, polygons_data in reatribute_id_pixels.items():
        list_xs_ys = [(polygons_data[0][0][i], polygons_data[0][1][i]) for i in range(6)]

        list_centers_xs.append(polygons_data[1][0])
        list_centers_ys.append(polygons_data[1][1])


        # if you want to draw the camera pixels id in the camera
        draw_camera_pixel_ids(polygons_data[1][0], polygons_data[1][1], pixels_id, ruche)#ok

        polygon = Polygon(list_xs_ys, closed=True, edgecolor="blue")
        ruche.add_patch(polygon)
        dict_polygones[pixels_id]=polygon

    #this part of the code replace the plots_hex_in_canvas_pdp() function
    #but is not use, transformation from the choice to wich data to use is made in the first if

    # if self.box_choice.get() == "Temp":
    #
    #     self._update_box_messages("We are reading temperature of PDP")
    #     print(self.usb2can.data_temperature)
    #     self.plot_pixels_grid_bis(self.reatribute_id_pixels,self.usb2can.data_temperature)
    #     self.fen1.after(3000, self.start_it)

    # if choice == "HG":
    #     plot_pixels_grid_bis(reatribute_id_pixels, data_electronics_HG)
    # elif choice == "LG":
    #     plot_pixels_grid_bis(reatribute_id_pixels,data_electronics_LG)
    # elif choice == "TOT":
    #     plot_pixels_grid_bis(reatribute_id_pixels, data_electronics_tot)

    ##This part of the code replace the plot_pixels_grid_bis() function

    data_from_electronics=data_from_electronics.tolist()
    norm1 = matplotlib.colors.Normalize(np.min(data_from_electronics), np.max(data_from_electronics))
    cmap1 = matplotlib.cm.ScalarMappable(norm=norm1, cmap=matplotlib.cm.jet)
    cmap1.set_array([])

    for pixel_id,polygones in dict_polygones.items():
        polygones.set_facecolor(cmap1.to_rgba(data_from_electronics[int(pixel_id)])) #traduit chaque pixel (polygone) en la course
        ruche.add_patch(polygones)
    cb_fen1.update_normal(cmap1)
    cb_fen1.draw_all()
    ruche.axis('equal')
    fig_fen1.savefig(figPlace+"/fig_ruche.svg",format='svg')
