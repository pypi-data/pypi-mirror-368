from camagick.processor import ProcessorBase, SinkBase

import multiprocessing as mp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from camagick.executor import QuitApplication

import time, math, logging, concurrent, asyncio, pickle

logger = logging.getLogger(__name__)


def resample_array(data, num_bins):
    slices = np.linspace(0, data.shape[0], num_bins+1, True).astype(int)
    counts = np.diff(slices)
    mean = np.add.reduceat(data, slices[:-1]) / counts
    return mean


class MatplotlibDisplay:
    '''
    Stupidly simple class that uses Matplotlib to visualize numpy arrays.
    '''
    def __init__(self, rows=None, cols=None, flip_lr=True, transpose=False, sample_max=2056):
        self.flip_lr = flip_lr
        self.transpose = transpose
        self._rows = rows
        self._cols = cols
        self._sample_max = sample_max
        self.figure = plt.figure()
        #self.figure.show(True)
        self.panels = {}
        

    def _init_rows_cols(self, panel_names, rows, cols):
        self.panelNames = panel_names

        if rows is not None:
            self._rows = rows

        if cols is not None:
            self._cols = cols

        rows = self._rows if self._rows is not None else \
            (int(math.ceil(math.sqrt(len(self.panelNames)))))

        if rows == 0:
            logger.error(f'msg="ACHTUNG, no data"')
            rows += 1
        
        cols = self._cols if cols is not None else \
            int(math.ceil(len(self.panelNames)/rows))

        return rows, cols


    def init_display(self, *panel_names, rows=None, cols=None):
        rows, cols = self._init_rows_cols(panel_names, rows, cols)
        logger.info(f'geometry={rows}x{cols} displays={self.panelNames}')
        self.axes = { k: self.figure.add_subplot(rows, cols, i+1) \
                      for i,k in enumerate(self.panelNames) }
        self.last_update = {k:time.time() for k in self.panelNames }


    def _plot_norm_2d(self, img):
        mi = img.min()
        ma = img.max()
        return mi, ma, LogNorm(vmin=mi if mi > 0 else 1e-5,
                               vmax=ma if ma > 0 and ma > mi else 1)
    
        
        
    def _plot_2d(self, name, data, *kw):
        ax = self.axes[name]
        ax.set_title(name)

        if self.flip_lr:
            img = data[:,::-1]
        else:
            img = data

        if self.transpose:
            img = np.transpose(img)
        
        self._2d_norm = self._plot_norm_2d(img)

        return ax.imshow(img, norm=self._2d_norm[2], *kw)


    def _plot_1d(self, name, data, *kw):
        if len(data) > self._sample_max:
            d = resample_array(data, self._sample_max)
            logger.info(f'tag={name} msg="Data too large, rebinning" '
                        f'full_shape={data.shape} '
                        f'bin_shape={d.shape}')
        else:
            d = data
        ax = self.axes[name]
        ax.set_title(name)
        return ax.plot(d, *kw)


    def _update_1d(self, name, data, **kw):
        if len(data) > self._sample_max:
            d = resample_array(data, self._sample_max)
        else:
            d = data
        x = np.array(range(len(d)))
        
        self.panels[name][0].set_data((x, d))
        
        ax = self.axes[name]
        ylim = ax.get_ylim()
        
        #print(ylim)
        mi, ma = d.min(), d.max()
        
        if (ylim[0]<mi) or (ylim[1]>ma):
            ax.set_ylim(mi-(ma-mi)*0.05, ma+(ma-mi)*0.05)


    def _update_2d(self, name, data, **kw):
        if self.flip_lr:
            img = data[:,::-1]
        else:
            img = data

        if self.transpose:
            img = np.transpose(img)

        self.panels[name].set_data(img)

        mi, ma, norm = self._plot_norm_2d(img)
        if mi < self._2d_norm[0] or ma > self._2d_norm[1]:
            logger.info(f'msg="Updating norm" tag="{name}" vmin="{mi}", vmax="{ma}"')
            self.panels[name].set_norm(norm)
            self._2d_norm = (mi, ma, norm)


    def _panel_for_data(self, name, data):
        '''
        Returns the panel for data set `name`
        '''
        dims = len(data.shape)
        plot_func = getattr(self, f"_plot_{dims}d")
        plot_kwargs = {
            1: {},
            2: {}
        }[dims]

        if data is None:
            data = np.ndarray([2]*dims)

        pan = self.panels.get(name)
        if pan is None:
            pan = self.panels.setdefault(name, plot_func(name, data, **plot_kwargs))

        return plt
        

    @property
    def is_initialized(self):
        return hasattr(self, "axes")
        

    def update(self, panel, data=None):
        
        if data is None:
            return
        
        try:
            dims = len(data.shape)
            ax = self._panel_for_data(panel, data)
        except KeyError:
            logging.error("%s: no such display panel" % panel)
            return

        getattr(self, f"_update_{dims}d")(panel, data)
        self.figure.canvas.draw_idle()


    def run(self):
        plt.show()
        #pass


class ProcessPlotter:
    def terminate(self):
        plt.close('all')

    def callback(self):
        data = {}
        m0 = time.time()
        while self.pipe.poll():
            data = self.pipe.recv()
            if data is None:
                self.terminate()
                return False

        if (not self.display.is_initialized):
            if len(data)>0:
                self.display.init_display(*[k for k in data.keys()])

        #print('plot', [k for k in data.keys()])
        for name,val in data.items():            
            self.display.update(name, val)
            
        return True


    def __call__(self, pipe, period=0.03):
        self.pipe = pipe
        self.display = MatplotlibDisplay(transpose=True, flip_lr=False)
        intr = int(period*1000)
        logger.info(f'msg="Data refresh, milliseconds" interval={intr}')
        
        timer = self.display.figure.canvas.new_timer(interval=intr)
        timer.add_callback(self.callback)
        timer.start()
        
        self.display.run()


class Processor(SinkBase):
    '''
    Plots data as lines (1D arrays) or images (2D arrays).
    '''
    
    def __init__(self, only: str = ''):
        self._only = [ k for k in filter(lambda x: len(x)>0, only.split(',')) ]


    async def startup(self):
        self.my_pipe, other_pipe = mp.Pipe()
        self.plotter = ProcessPlotter()
        self.plotter_process = mp.Process(
            target=self.plotter, args=(other_pipe,), daemon=True
        )
        self.plotter_process.start()        


    async def shutdown(self):
        self.my_pipe.send(None)

    
    async def __call__(self, data=None, context=None):
        try:
            if self._only is not None and len(self._only) > 0:
                d = { k:v for k,v in \
                      filter(lambda x: x[0] in self._only, data.items()) }
            else:
                d = data

            with concurrent.futures.ProcessPoolExecutor() as pool:
                await asyncio.get_running_loop()\
                             .run_in_executor(pool, self.my_pipe.send, d)


            return { k:data[k] for k in \
                     filter(lambda x: x not in d, data.keys()) }
            
        except BrokenPipeError:
            logger.info(f'msg="Display closed by user"')
            raise QuitApplication(f'msg="Display closed by user"')
