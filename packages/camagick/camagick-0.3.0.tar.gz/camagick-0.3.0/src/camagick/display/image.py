#!/usr/bin/python3

from matplotlib import pyplot as plt
from matplotlib import transforms

import numpy as np
import xarray
import asyncio
import os, sys, time, logging, math

import argparse

from camagick.helpers import FpsCounter
from camagick.stash import ZarrStash

class ImageMplWidget:
    ''' Matplotlib-based image display widget '''

    def __init__(self):
        bgcolor='#404050'
        fgcolor='w'
    
        self.fig = plt.figure(facecolor=bgcolor)
        self.grid = self.fig.add_gridspec(2, 2, width_ratios=[4,1], height_ratios=[4,1])
        
        self.ax_pic = self.fig.add_subplot(self.grid[0,0], facecolor=bgcolor)
        self.obj_pic = self.ax_pic.imshow( (np.array([[0, 1], [1, 0]])*256).astype(np.uint64), aspect='auto')
        
        #ax_xsum = fig.add_subplot(grid[0,1], facecolor=bgcolor)
        #ax_ysum = fig.add_subplot(grid[1,0], facecolor=bgcolor)
        #ax_xsum.set(xticks=[])
        #ax_xsum.set_mouseover(True)
        #ax_ysum.set(yticks=[])
        #ax_ysum.set_mouseover(True)
        self.grid.tight_layout(self.fig)
    
        #obj_xsum = ax_xsum.plot([])[0]
        #obj_ysum = ax_ysum.plot([])[0]

        #obj_xstat = ax_xsum.plot([], marker='+', linestyle='solid')[0]
        #obj_ystat = ax_ysum.plot([], marker='+', linestyle='solid')[0]

        self.fig.show()
                
        #frm_shape = caget(prefix+"frameShape").astype(int)
        #print("Shape:", frm_shape)
    
        #obj_pic.set_extent((0, frm_shape[1], 0, frm_shape[0]))
        
        #axis_x = np.array(range(frm_shape[0]))
        #axis_y = np.array(range(frm_shape[1]))
        
        #ax_xsum.set_ylim(0, frm_shape[0])
        #ax_ysum.set_xlim(0, frm_shape[1])
        
        #ax_xsum.set_xlim(0, 1)
        #ax_ysum.set_ylim(0, 1)


    def update(self, image):
        #frm_flat = np.array(caget(prefix+"flatFrame"), dtype=int).reshape(frm_shape)

        #frm_x = np.array(caget(prefix+"frameSumX"), dtype=int)
        #frm_y = np.array(caget(prefix+"frameSumY"), dtype=int)

        #frm_com = caget(prefix+"centerOfMass")
        #frm_std = caget(prefix+"standardWidth")

        #frame = np.array(frm_flat)

        img = image[::-1,:]
        self.obj_pic.set_data(img)
        #self.obj_pic.set_extent((0, img.shape[0], 0, img.shape[1]))
        
        #obj_xsum.set_data(frm_x/frm_x.max(), axis_x)
        #obj_ysum.set_data(axis_y, frm_y/frm_y.max())


        #stdf = math.sqrt(2*math.log(2))

        #obj_ystat.set_data([frm_com[1]-stdf*frm_std[1],
        #                    frm_com[1],
        #                    frm_com[1]+stdf*frm_std[1]],
        #                   [0.5, 0.5, 0.5])

        #obj_xstat.set_data([0.5, 0.5, 0.5],
        #                   [frm_com[0]-stdf*frm_std[0],
        #                    frm_com[0],
        #                    frm_com[0]+stdf*frm_std[0]])

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


def get_options():
    parser = argparse.ArgumentParser(prog='camagick-display-image',
                                     description='Display a 2D data array using imshow()')

    parser.add_argument('--zarr', action='store',
                        help='ZARR file to watch for changes')
    parser.add_argument('--lock', action='store',
                        help='Lock key to use for synchronising access to data')

    parser.add_argument('-cdf', action='store',
                        help='netCDF4 file to watch for changes')

    return parser.parse_args()


def image_main():
    asyncio.run(async_main())

    
async def async_main():
    args = get_options()
    image_plot = ImageMplWidget()

    stash = ZarrStash(args.zarr or args.cdf, lockKey=args.lock)
        
    fps = FpsCounter(100)

    while True:
        try:
            ds = stash.load()
            image_plot.update(ds['flatFrame'])            
            
        except Exception as e:
            logging.error("Stash retrieve failed: %r", e)

        fps.mark()
        print("\r%r      " % fps, end='')    


if __name__ == "__main__":
    async_main()
