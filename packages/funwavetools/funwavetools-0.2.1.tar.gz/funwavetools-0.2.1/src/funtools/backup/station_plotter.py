
from pathlib import Path
from bokeh.io import export_png
from funtools.io import read_input_file, load_data
from funtools import waves
import pickle

import numpy as np
from pathlib import Path
import holoviews as hv

from tqdm import tqdm

def load_chromedriver(): #driver_fpath):
    """Loads chromedriver (for bokeh svg export), if found"""


    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=2000x2000")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--disable-dev-shm-usage')
        service = webdriver.ChromeService()#executable_path=driver_fpath)
        webdriver = webdriver.Chrome(service=service, options=options)
        #print('Chromedriver loaded. Svg output enabled.')
    except Exception as e:
        raise e
        logging.warning('Chromedriver not found. Disabling svg output.')
        webdriver = None
    return webdriver

def save_plot(plt, fpath):

    bplt = hv.renderer('bokeh').get_plot(plt).state
    bplt.toolbar_location = None
    webdriver = load_chromedriver()
    export_png(bplt, filename=fpath)#, webdriver=webdriver)

class Stations():


    def __init__(self, sim_dpath, n_profiles):


        sim_dpath = Path(sim_dpath)
        input_fpath = sim_dpath / 'input.txt'
        params = read_input_file(input_fpath)


        
        output_dpath = sim_dpath/params['RESULT_FOLDER']

        dt = params['PLOT_INTV_STATION']

        post_dpath = sim_dpath/ 'postprocessing'
        post_dpath.mkdir(exist_ok=True)

        station_fpath = sim_dpath/params['STATIONS_FILE']


        # NOTE: -1 to offset FORTANT 1 starting index
        idxs = np.loadtxt(station_fpath).astype(int) - 1

        n, _ = idxs.shape
        self.i = idxs[:,0]
        self.j = idxs[:,1]

        self.nums = np.arange(1, n +1)

        mglob  = params['Mglob']
        nglob  = params['Nglob']

        depth = -load_data(output_dpath, 'dep.out', nglob, mglob)

        x = np.arange(mglob)*params['DX']
        y = np.arange(nglob)*params['DY']


    

        self.x = x[self.i]
        self.y = y[self.j]
        self.h = depth[self.j, self.i]
        n_sta = n//n_profiles

        def get_profile(i):
            j0 = i*n_sta
            j1 = j0 + n_sta
            sl = slice(j0, j1) 
            return Profile(i, output_dpath, post_dpath, dt, self.x[sl], self.y[sl],  self.h[sl], self.nums[sl])


        self.profiles = [ get_profile(i) for i in range(n_profiles)]


    def compute_profile_spectra(self, **kwargs):
        self.profiles[0].compute_profile_spectra(**kwargs)


    def compute_runup(self, **kwargs):
        self.profiles[0].compute_runup(**kwargs)

class Profile():

    def __init__(self, i, output_dpath,  post_dpath, dt, x, y, h, nums):
        
        profile_dname = "profile_%02d" % i
        profile_dpath = post_dpath / profile_dname
        self.x = x
        self.y = y
        self.h = h
        self.nums = nums
        self.stations = [Station(output_dpath, profile_dpath, dt,  *a) for a in zip(x, y, h, nums)]
        self.profile_dpath = profile_dpath
        profile_dpath.mkdir(exist_ok=True)


    def compute_runup(self, gbl_kwargs={}, x_kwargs={}, h_kwargs={}):


        n_sta = len(self.x)

        t = self.stations[0].t
        nt = len(t)


        data = np.zeros([n_sta, nt])
        
        for i, p in enumerate(self.stations):
            data[i,:] = p.dump_data()

        # NOTE: transposing to have profile as a function of time
        data = data.T

        x0_cut = 1500
        x1_cut = 1800

        i0 = np.argmin(np.abs(self.x-x0_cut))
        i1 = np.argmin(np.abs(self.x-x1_cut)) + 1


        data = data[:,i0:i1]
        x = self.x[i0:i1]
        h = self.h[i0:i1]
        nt, nx = data.shape

        data_diff = data.copy()

        for i in range(nt):
            data_diff[i,:] = data_diff[i,:] - h


        sign_chg = data_diff[:,:-1]*data_diff[:,1:] < 0

        sign_chgs = np.sum(sign_chg,axis=1)

        #if np.any(sign_chgs > 1):
            #raise Exception()

        def interp_zero(j, idxs, sta_x0, data, data_diff):


            i0 = idxs[j][0] 

            x0 = sta_x0[i0]
            x1 = sta_x0[i0+1]
            y0 = data_diff[j, i0],
            y1 = data_diff[j, i0+1]

            m = (y1-y0)/(x1-x0)
            c = y0 - m*x0

            xc = -c/m
            xc = xc[0]

            if xc > x1: xc = x1
            if xc < x0: xc = x0

            y0 = h[i0]
            y1 = h[i0+1]

            etac = y0 + (y1-y1)*(xc-x0)/(x1-x0)


            return xc, etac 
        

        idxs = [ np.arange(0, nx-1)[x] for x in sign_chg]
        args = [interp_zero(j, idxs, x, data, data_diff) for j in range(nt)]

        x_run_up, h_run_up = zip(*args)

        x_run_up = np.array(x_run_up)
        h_run_up = np.array(h_run_up)

        x_run_up = x_run_up - x_run_up[0]

        plt_x = hv.Curve(zip(t, x_run_up) )
        plt_x.opts(**x_kwargs, **gbl_kwargs)
        fpath = self.profile_dpath / 'run_up_x.png'
        save_plot(plt_x, fpath)


        plt_h = hv.Curve(zip(t, h_run_up) )
        plt_h.opts(**h_kwargs, **gbl_kwargs)
        fpath = self.profile_dpath / 'run_up_h.png'
        save_plot(plt_h, fpath)

        data = dict(
            t = t,
            x = x_run_up,
            h = h_run_up,
        )

        fpath = self.profile_dpath / 'runup.pkl'
        with open(fpath, 'wb') as f:
            pickle.dump(data, f)


    def compute_spectra(self, gbl_kwargs={}, sta_kwargs={}, spec_kwargs={}, all_plots=False, tlim=None):


        def wrapper(s):
            return s.compute_spectra(sta_kwargs=sta_kwargs, spec_kwargs=spec_kwargs, tlim=tlim) 
        iter_list = tqdm(self.stations, desc='Stations')
        args = [wrapper(s) for s in iter_list]


        hmos, tps, peak_lengths =[np.array(a) for a in zip(*args)]


    def compute_profile_spectra(self, gbl_kwargs={}, sta_kwargs={}, spec_kwargs={}, hmo_kwargs={}, dep_kwargs={}, tp_kwargs={}, k_kwargs={}, all_plots=False, tlim=None):

        
        hmos, tps, peak_lengths = self.compute_spectra(gbl_kwargs=gbl_kwargs, sta_kwargs=sta_kwargs, spec_kwargs=spec_kwargs, tlim=tlim)

        data = dict(
            x = x,
            h = h,
            hmo = hmos,
            tp = tps,
            k = peak_lengths,
            sta_nums = self.nums,
            tlim = tlim,
        )

        fpath = profile_dpath / 'statistics.pkl'
        with open(fpath, 'wb') as f:
            pickle.dump(data, f)
 
        
        x = self.x
        h = self.h

        plt_h = hv.Curve(zip(x, h) , label='Depth')
        plt_h.opts(**dep_kwargs)


        trg_val = 5
        plt_target = hv.Curve([(x[0], trg_val),(x[-1], trg_val)] , label='Target')
        plt_hmos = hv.Curve(zip(x, hmos) , label='Hmo')


        plt_hmos.opts(**hmo_kwargs)
        plt_hmos_scat = hv.Scatter(zip(x, hmos))
        plt_hmos_scat.opts(size=4)
        profile_dpath = self.profile_dpath

        fpath = profile_dpath / 'peak_hmo.png'

        plt = plt_hmos*plt_hmos_scat*plt_target*plt_h
        plt.opts(**gbl_kwargs)
        save_plot(plt, fpath)

        def make_plot(data, trg_val, label, fname, kwargs):
            plt_target = hv.Curve([(x[0], trg_val),(x[-1], trg_val)], label='Target')
            plt_data = hv.Curve(zip(x, data))#, label=label)

            plt_data.opts(**kwargs)
            plt = plt_data#*plt_target
            plt.opts(**gbl_kwargs)
            fpath = profile_dpath / fname
            save_plot(plt, fpath)





        trg_val = 20
    
        make_plot(tps, trg_val, 'Peak Period', 'peak_period.png', tp_kwargs)
        make_plot(peak_lengths, trg_val, 'Peak Wavelength', 'peak_length.png', k_kwargs)





class Station():

    def _load_data(self):
        sta_name = "sta_%04d"  % self.num 
        sta_fpath = self.output_dpath / sta_name
        del self.output_dpath

        data = np.loadtxt(sta_fpath)
        t =  data[:,0]
        i = np.argmin(np.diff(t)) 
        self._t =  data[:i,0]
        self._eta = data[:i,1]
        
    @property
    def t(self):
        if self._t is None: self._load_data()
        return self._t

    @property
    def eta(self):
        if self._eta is None: self._load_data()
        return self._eta

    def __init__(self, output_dpath, post_dpath, dt, x, y, h, num):

        self.x = x
        self.y = y
        self.h = h
        self.num = num
        self.output_dpath = output_dpath

        sta_dpath = post_dpath / 'stations'
        self.sta_dpath = sta_dpath
        self.dt = dt
        self._t = None
        self._eta = None

    def dump_data(self):
        t = self._t
        eta = self._eta
        self._t = None
        self._eta = None
        return eta

    def compute_spectra(self,sta_kwargs={}, spec_kwargs={}, tlim=None, is_plot=True):


        f, spec_den, Hmo, energy = waves.compute_spectra(self.eta, self.dt, t=self.t, tlim=tlim)

        if self.h > 0:
            Hmo = np.nan
            tp = np.nan
            lp = np.nan

        else:

            idx = np.argmax(spec_den)
        
            if idx == 0:
                tp = 0
                lp = 0
            else:
                tp = 1/f[idx]
                wp = 2*np.pi*f[idx]
                kp = waves.solve_dispersion(h=np.abs(self.h), w=wp)
                lp = 2*np.pi/kp


        if is_plot:

            spec_den[0] = 0
            self.sta_dpath.mkdir(exist_ok=True)
            fpath = self.sta_dpath / ( "sta_%04d.png" % self.num )


            plt_eta= hv.Curve(zip(self.t, self.eta))
            plt_eta.opts(**sta_kwargs)

            plt_spec = hv.Curve(zip(f, spec_den))
            plt_spec.opts(**spec_kwargs)

            plt = plt_eta + plt_spec
            plt.opts(
                shared_axes=False,          
                fontsize=dict(
                    title  = 20, 
                    labels = 18, 
                    xticks = 15, 
                    yticks = 15,
                    cticks = 15
                ),
            )

            
            save_plot(plt, fpath)

        return Hmo, tp, lp