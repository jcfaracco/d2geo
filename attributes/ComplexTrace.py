# -*- coding: utf-8 -*-
"""
Complex Trace Attributes for Seismic Data

@author: Braden Fitz-Gerald
@email: braden.fitzgerald@gmail.com

"""

# Import Libraries
import dask.array as da
import numpy as np
from . import util
from .SignalProcess import SignalProcess as sp


class ComplexAttributes():
    """
    Description
    -----------
    Class object containing methods for computing complex trace attributes 
    from 3D seismic data.
    
    Methods
    -------
    create_array
    envelope
    instantaneous_phase 
    cosine_instantaneous_phase 
    relative_amplitude_change
    instantaneous_frequency 
    instantaneous_bandwidth
    dominant_frequency 
    frequency_change 
    sweetness 
    quality_factor 
    response_phase 
    response_frequency 
    response_amplitude 
    apparent_polarity
    """

    def __init__(self, *args, **kwargs):
        """
        Description
        -----------
        Constructor of the ComplexAttribute object

        Parameters
        ----------
        args : Array-like, positional parameters in array format
        kwargs : Dict-like, positional parameters in dict format
        """
        if "numpy_backend" in kwargs:
            self.xp = kwargs["numpy_backend"]
        if "hilbert_cb" in kwargs:
            self.hilbert_cb = kwargs["hilbert_cb"]

    @util.check_numpy
    def create_array(self, darray, kernel=None, hw=None, boundary='reflect',
                     preview=None):
        """
        Description
        -----------
        Convert input to Dask Array with ideal chunk size as necessary.  Perform
        necessary ghosting as needed for opertations utilizing windowed functions.
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        darray : Dask Array
        chunk_init : tuple (len 3), chunk size before ghosting.  Used in select cases
        """
        # Compute chunk size and convert if not a Dask Array
        if not isinstance(darray, da.core.Array):
            chunk_size = util.compute_chunk_size(darray.shape,
                                                 darray.dtype.itemsize,
                                                 kernel=kernel,
                                                 preview=preview)
            darray = da.from_array(darray, chunks=chunk_size)

        # Ghost Dask Array if operation specifies a kernel
        if kernel is not None:
            if hw is None:
                hw = tuple(np.array(kernel) // 2)
            if isinstance(boundary, da.core.Array): # if boundary is computed using a dask function
                boundary = boundary.compute()
            darray = da.overlap.overlap(darray, depth=hw, boundary=boundary)

        chunks_init = darray.chunks

        return (darray, chunks_init)

    @util.check_hilbert
    @util.check_numpy
    def hilbert(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Hilbert of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays

        Keywork Arguments
        -----------------
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """
        darray, chunks_init = self.create_array(darray, kernel, preview=preview)
        analytical_trace = darray.map_blocks(self.hilbert_cb, dtype=darray.dtype,
                                             meta=self.xp.array((),
                                                                dtype=darray.dtype))
        result = util.trim_dask_array(analytical_trace, kernel)

        return(result)

    @util.check_hilbert
    @util.check_numpy
    def envelope(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Envelope of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        darray, chunks_init = self.create_array(darray, kernel, preview=preview)
        analytical_trace = darray.map_blocks(self.hilbert_cb, dtype=darray.dtype,
                                             meta=self.xp.array((),
                                                                dtype=darray.dtype))
        result = da.absolute(analytical_trace)
        result = util.trim_dask_array(result, kernel)

        return(result)

    @util.check_hilbert
    def instantaneous_phase(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Phase of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        darray, chunks_init = self.create_array(darray, kernel, preview=preview)
        analytical_trace = darray.map_blocks(self.hilbert_cb, dtype=darray.dtype)
        result = da.rad2deg(da.angle(analytical_trace))
        result = util.trim_dask_array(result, kernel)
        
        return(result)
            
            
    def cosine_instantaneous_phase(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Cose of Instantaneous Phase of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)            
        phase = self.instantaneous_phase(darray, kernel=kernel)
        result = da.rad2deg(da.angle(phase))
        
        return(result)
            
    
    
    def relative_amplitude_change(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Relative Amplitude Change of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)        
        env = self.envelope(darray, kernel=kernel)
        env_prime = sp(**self.__dict__).first_derivative(env, axis=-1)
        result = env_prime / env
        result = da.clip(result, -1, 1)
            
        return(result)
            
    
    
    def amplitude_acceleration(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Amplitude Acceleration of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)
        rac = self.relative_amplitude_change(darray, kernel=kernel)
        result = sp(**self.__dict__).first_derivative(rac, axis=-1)
            
        return(result)

    @util.check_numpy
    def instantaneous_frequency(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Frequency of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        darray, chunks_init = self.create_array(darray, kernel=(1,1,25), preview=preview)
        
        fs = 1000 / sample_rate
        phase = self.instantaneous_phase(darray, kernel=kernel)
        phase = da.deg2rad(phase)
        phase = phase.map_blocks(self.xp.unwrap, dtype=darray.dtype)
        phase_prime = sp(**self.__dict__).first_derivative(phase, axis=-1)        
        result = da.absolute((phase_prime / (2.0 * self.xp.pi) * fs))
                   
        return(result)
        
        
    def instantaneous_bandwidth(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Bandwidth of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------    
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)                  
        rac = self.relative_amplitude_change(darray, kernel=kernel)
        result = da.absolute(rac) / (2.0 * self.xp.pi)        
        
        return(result)
            
    
    def dominant_frequency(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Dominant Frequency of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)
        inst_freq = self.instantaneous_frequency(darray, sample_rate, kernel=kernel)
        inst_band = self.instantaneous_bandwidth(darray, kernel=kernel)
        result = da.hypot(inst_freq, inst_band)

        return(result)
        
        
    def frequency_change(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Frequency Change of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)
        inst_freq = self.instantaneous_frequency(darray, sample_rate, kernel=kernel)
        result = sp(**self.__dict__).first_derivative(inst_freq, axis=-1)
                    
        return(result)
        
        
    def sweetness(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Sweetness of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        def func(chunk):
            chunk[chunk < 5] = 5
            return(chunk)
        
        darray, chunks_init = self.create_array(darray, preview=preview)                    
        inst_freq = self.instantaneous_frequency(darray, sample_rate, kernel=kernel)
        inst_freq = inst_freq.map_blocks(func, dtype=darray.dtype)
        env = self.envelope(darray, kernel=kernel)
        
        result = env / inst_freq
                            
        return(result)

    @util.check_numpy
    def quality_factor(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Quality Factor of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        darray, chunks_init = self.create_array(darray, preview=preview)
                    
        inst_freq = self.instantaneous_frequency(darray, sample_rate, kernel=kernel)
        rac = self.relative_amplitude_change(darray, kernel=kernel)
        
        result = (self.xp.pi * inst_freq) / rac
        
        return(result)       

    @util.check_numpy
    def response_phase(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Response Phase of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        
        def operation(chunk1, chunk2, chunk3):
            out = self.xp.zeros(chunk1.shape)
            for i,j in self.xp.ndindex(out.shape[:-1]):

                ints = self.xp.unique(chunk3[i, j, :])    

                for ii in ints:
                    
                    idx = self.xp.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]
                    
            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray, kernel=kernel)
        phase = self.instantaneous_phase(darray, kernel=kernel)
        troughs = env.map_blocks(util.local_events, comparator=self.xp.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, phase, troughs, dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)
        
    @util.check_numpy
    def response_frequency(self, darray, sample_rate=4, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Response Frequency of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        sample_rate : Number, sample rate in milliseconds (ms)
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        def operation(chunk1, chunk2, chunk3):
            out = self.xp.zeros(chunk1.shape)
            for i,j in self.xp.ndindex(out.shape[:-1]):

                ints = self.xp.unique(chunk3[i, j, :])    

                for ii in ints:

                    idx = self.xp.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray, kernel=kernel)
        inst_freq = self.instantaneous_frequency(darray, sample_rate, kernel=kernel)
        troughs = env.map_blocks(util.local_events, comparator=self.xp.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, inst_freq, troughs, dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

    @util.check_numpy
    def response_amplitude(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Response Amplitude of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        def operation(chunk1, chunk2, chunk3):
            out = self.xp.zeros(chunk1.shape)
            for i,j in self.xp.ndindex(out.shape[:-1]):

                ints = self.xp.unique(chunk3[i, j, :])

                for ii in ints:

                    idx = self.xp.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray, kernel=kernel)
        troughs = env.map_blocks(util.local_events, comparator=self.xp.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, darray, troughs, dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

    @util.check_numpy
    def apparent_polarity(self, darray, kernel=(1,1,25), preview=None):
        """
        Description
        -----------
        Compute the Apparent Polarity of the input data
        
        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask Arrays
        
        Keywork Arguments
        -----------------  
        kernel : tuple (len 3), operator size
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output
        
        Returns
        -------
        result : Dask Array
        """
        def operation(chunk1, chunk2, chunk3):
            
            out = self.xp.zeros(chunk1.shape)            
            for i,j in self.xp.ndindex(out.shape[:-1]):
                
                ints = self.xp.unique(chunk3[i, j, :])    
                
                for ii in ints:
                    
                    idx = self.xp.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk1[i, j, peak] * self.xp.sign(chunk2[i, j, peak])
                    
            return(out)
                    
        darray, chunks_init = self.create_array(darray, preview=preview)        
        env = self.envelope(darray, kernel=kernel)
        troughs = env.map_blocks(util.local_events, comparator=self.xp.less, 
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)        
        result = da.map_blocks(operation, env, darray, troughs, dtype=darray.dtype)        
        result[da.isnan(result)] = 0
        
        return(result)
