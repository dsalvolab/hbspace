'''
Created on Jun 30, 2021

@author: uvilla
'''

import datetime
import numpy as np
from scipy import io as sio
from scipy import interpolate as sinterp


MAX_COUNT_VAL = 999999

def datenum_to_datetime(datenum):
    """

    https://gist.github.com/victorkristof/b9d794fe1ed12e708b9d

    Convert Matlab datenum into Python datetime.
    :param datenum: Date in datenum format
    :return:        Datetime object corresponding to datenum.
    """
    days = datenum % 1
    hours = days % 1 * 24
    minutes = hours % 1 * 60
    seconds = minutes % 1 * 60
    return datetime.datetime.fromordinal(int(datenum)) \
           + datetime.timedelta(days=int(days)) \
           + datetime.timedelta(hours=int(hours)) \
           + datetime.timedelta(minutes=int(minutes)) \
           + datetime.timedelta(seconds=round(seconds)) \
           - datetime.timedelta(days=366)
           
class CutPoints:
    def __init__(self, levels, vals, mode):
        self.levels = levels
        self.vals   = vals
        
        assert mode in ["VM", "AX1"]
        
        self.mode = mode 

        
    @classmethod
    def Evenson(cls):
        #0, 101, 2296, 4012, inf
        levels = np.array(['SED', 'LPA', 'MPA', 'VPA'], dtype='|S3')
        vals = np.array([0, 101, 2296, 4012, MAX_COUNT_VAL], dtype=np.float64)
        mode = 'AX1'
        return cls(levels, vals, mode)
    
    def classify(self, counts, epoch):
        levels = np.ndarray(counts.shape, dtype='|S3')
        vals = self.vals*epoch/60.
        for i, l in enumerate(self.levels):
            levels[ np.logical_and(counts >= vals[i], counts<vals[i+1]) ] = l
            
        return levels
        
        

class AccelerometerData:
    def __init__(self, partID, fname, local_dt, ax1_counts, vm_counts):
        self.partID = partID
        self.fname  = fname
        
        self.local_dt = local_dt
        self.ax1_counts = ax1_counts
        self.vm_counts = vm_counts
        self.epoch = (self.local_dt[1]-self.local_dt[0]).total_seconds()
        
        self.is_missing = None
        self.is_valid   = None
    
    @classmethod    
    def fromMatFile(cls, fname, partID):
        
        fname = fname[:-3]+'mat'
        
        mat_content = sio.loadmat(fname)
        data = mat_content['data']
        
        ax1_counts  = data[:,1]
        vm_counts = np.sqrt( np.sum(data[:,1:4]*data[:,1:4], axis=1) )
        
        datenums = data[:,0]
        local_dt = np.array([datenum_to_datetime(datenum) for datenum in datenums], dtype=datetime.datetime)
        
        return cls(partID, fname, local_dt, ax1_counts, vm_counts)
    
    def extract_and_interpolate(self, new_local_dt):
        start = new_local_dt[0]
        end   = new_local_dt[-1]
        new_epoch = (new_local_dt[1]-new_local_dt[0])
        indexis = np.logical_and( self.local_dt > start-new_epoch, self.local_dt < end+new_epoch )
        
        new_delta_dt = (new_local_dt-start)
        new_x = np.array([dt.item().total_seconds() for dt in new_delta_dt])
        delta_dt = (self.local_dt-start)
        x = np.array([dt.item().total_seconds() for dt in delta_dt])
        
        new_data = AccelerometerData(self.partID, fname = None, 
                                     local_dt = new_local_dt,
                                     ax1_counts = np.zeros_like(new_local_dt, dtype=self.ax1_counts.dtype), 
                                     vm_counts =  np.zeros_like(new_local_dt, dtype=self.vm_counts.dtype))
        
        new_data.is_valid  = np.zeros_like(new_local_dt, dtype=np.int)
        new_data.is_missing = np.ones_like(new_local_dt, dtype=np.int)
        
        new_data.epoch = self.epoch
        
        if np.sum(indexis)>1:
        
            yy = x[indexis]
            new_data.is_missing[:] = 0
            new_data.is_missing[new_x < yy[0]]  = 1
            new_data.is_missing[new_x > yy[-1]] = 1
            new_x[new_x < yy[0]] = yy[0]
            new_x[new_x > yy[-1]] = yy[0]
        
            interp_kind = 'previous'
        
            f_ax1 = sinterp.interp1d(x[indexis], self.ax1_counts[indexis], fill_value=0, kind=interp_kind)
            new_data.ax1_counts = f_ax1(new_x)
        
            f_vm = sinterp.interp1d(x[indexis], self.vm_counts[indexis], fill_value=0, kind=interp_kind)
            new_data.vm_counts = f_vm(new_x)
        
            if np.sum(self.vm_counts[indexis] > 0) > 2:
                new_data.is_valid[new_data.is_missing==0] = 1

        return new_data
        
        
    
    def classify(self, cp, indexes=None):
        if indexes is None:
            if cp.mode == 'AX1':
                counts = self.ax1_counts
            else:
                counts = self.vm_counts
        else:
            if cp.mode == 'AX1':
                counts = self.ax1_counts[indexes]
            else:
                counts = self.vm_counts[indexes]

    
        return cp.classify(counts, self.epoch)
    
    def getCountsStatsInterval(self, time_interval):
        one_hot = np.logical_and( self.local_dt >= time_interval[0], self.local_dt <= time_interval[0])
        indexes = np.where(one_hot)[0]

        if(indexes.shape[0] < 2):
            return '', '', ''

        duration = (self.local_dt[indexes[-1]] - self.local_dt[indexes[0]]).total_seconds()

        if duration < (time_interval[1] -  time_interval[0]).total_seconds() - 2*self.epoch:
            return '', '', ''
        

        totCounts = np.sum(self.ax1_counts[indexes])
        avg_counts_min = totCounts/duration*60
        counts_min90p  = np.percentile(self.ax1_counts[indexes], 90)*(60./self.epoch)

        return totCounts, avg_counts_min, counts_min90p
    
    def getIntensityStatsInterval(self, cp, time_interval):
        one_hot = np.logical_and( self.local_dt >= time_interval[0], self.local_dt <= time_interval[0])
        indexes = np.where(one_hot)[0]

        if(indexes.shape[0] < 2):
            intensity_median = ''
            intensity_90p = ''
            minutes = {}
            for l in cp.levels:
                minutes[l] = ''

            return intensity_median, intensity_90p, minutes

        duration = (self.local_dt[indexes[-1]] - self.local_dt[indexes[0]]).total_seconds()

        if duration < (time_interval[1] -  time_interval[0]).total_seconds() - 2*self.epoch:
            intensity_median = ''
            intensity_90p = ''
            minutes = {}
            for l in cp.levels:
                minutes[l] = ''
        else:
            levels = self.classify(cp, indexes)
            intensity_median = np.percentile(levels, 50, method = 'inverted_cdf')
            intensity_90p    = np.percentile(levels, 90, method = 'inverted_cdf')
            minutes = {}
            for l in cp.levels:
                minutes[l] = np.sum(levels == l)*(self.epoch/60.)

        return intensity_median, intensity_90p, minutes



