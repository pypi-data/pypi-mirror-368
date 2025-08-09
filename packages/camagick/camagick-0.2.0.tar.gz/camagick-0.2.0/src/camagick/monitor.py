#!/usr/bin/python3

from matplotlib import pyplot as plt
from matplotlib import transforms
from epics import caget

import numpy as np

import os, sys, time, logging, math

import lmfit.models as fitmod
from lmfit import create_params

def model_fit(data, modelName, **params):    
    
    Model = getattr(fitmod, modelName)
    model = Model()
    x = np.linspace(0, len(data)-1, num=len(data))

    if len(params) > 0:
        par = create_params(**params)
    else:
        par = model.guess(data=data, x=x)

    return model.fit(data, par, x=x)


if __name__ == "__main__":

    prefix = sys.argv[1] if len(sys.argv)>1 else "KMC3:XPP:GONIOCAM:"

    bgcolor='#404050'
    fgcolor='w'
    
    fig = plt.figure(facecolor=bgcolor)
    grid = fig.add_gridspec(2, 2, width_ratios=[4,1], height_ratios=[4,1])
    ax_pic = fig.add_subplot(grid[0,0], facecolor=bgcolor)
    ax_xsum = fig.add_subplot(grid[0,1], facecolor=bgcolor)
    ax_ysum = fig.add_subplot(grid[1,0], facecolor=bgcolor)
    ax_xsum.set(xticks=[])
    ax_xsum.set_mouseover(True)
    ax_ysum.set(yticks=[])
    ax_ysum.set_mouseover(True)
    grid.tight_layout(fig)
    
    obj_pic = ax_pic.imshow( (np.array([[0, 1], [1, 0]])*256).astype(np.uint64), aspect='equal')
    obj_xsum = ax_xsum.plot([])[0]
    obj_ysum = ax_ysum.plot([])[0]
    obj_xfit = ax_xsum.plot([], linestyle='dotted')[0]
    obj_yfit = ax_ysum.plot([], linestyle='dotted')[0]
    

    obj_xstat = ax_xsum.plot([], marker='+', linestyle='solid')[0]
    obj_ystat = ax_ysum.plot([], marker='+', linestyle='solid')[0]

    fig.show()
                
    frm_shape = caget(prefix+"frameShape").astype(int)
    print("Shape:", frm_shape)
    
    obj_pic.set_extent((0, frm_shape[1], 0, frm_shape[0]))

    axis_x = np.array(range(frm_shape[0]))
    axis_y = np.array(range(frm_shape[1]))
   
    ax_xsum.set_ylim(0, frm_shape[0])
    ax_ysum.set_xlim(0, frm_shape[1])

    ax_xsum.set_xlim(0, 1)

    ax_ysum.set_ylim(0, 1)
            
    
    while True:
        try:
            frm_flat = np.array(caget(prefix+"flatFrame"), dtype=int).reshape(frm_shape)
            
            frm_x = np.array(caget(prefix+"frameSumX"), dtype=int)
            frm_y = np.array(caget(prefix+"frameSumY"), dtype=int)

            try:
                if len(frm_x) and len(frm_y):
                    fit_x = model_fit(frm_x, "GaussianModel")
                    ff_x = fit_x.eval()
                    
                    fit_y = model_fit(frm_y, "GaussianModel")
                    ff_y = fit_y.eval()

                    frm_com = np.array([f.params['center'].value for f in (fit_x, fit_y)])
                    frm_std = np.array([f.params['fwhm'].value for f in (fit_x, fit_y)])
                    #print ("fit_x", fit_x.params)

                    print("\rFWHM:"
                          " %.0f×%.0f μm, " % tuple([f.params['fwhm'].value * 3.45 for f in (fit_x, fit_y)]),
                          "σ: %.0f×%.0f μm" % tuple([f.params['sigma'].value * 3.45 for f in (fit_x, fit_y)]),
                          "                            ",
                          end='')
            except Exception as ee:
                print("No fit:", str(ee))
            
            #frm_com = caget(prefix+"centerOfMass")
            #frm_std = caget(prefix+"standardWidth")
            #print("com:", frm_com, "std:", frm_std)
            
            frame = np.array(frm_flat)
            
            obj_pic.set_data(frame[::-1,:])
            
            obj_xsum.set_data(frm_x/frm_x.max(), axis_x)
            obj_ysum.set_data(axis_y, frm_y/frm_y.max())

            obj_xfit.set_data(ff_x/ff_x.max(), axis_x)
            obj_yfit.set_data(axis_y, ff_y/ff_y.max())

            
            stdf = 0.5#math.sqrt(2*math.log(2))
            
            obj_ystat.set_data([frm_com[1]-stdf*frm_std[1],
                                frm_com[1],
                                frm_com[1]+stdf*frm_std[1]],
                               [0.5, 0.5, 0.5])
            
            obj_xstat.set_data([0.5, 0.5, 0.5],
                               [frm_com[0]-stdf*frm_std[0],
                                frm_com[0],
                                frm_com[0]+stdf*frm_std[0]])
            
        except Exception as e:
            logging.error(e)
            raise
    
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        time.sleep(0.01)
