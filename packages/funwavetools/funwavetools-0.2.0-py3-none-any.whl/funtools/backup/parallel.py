# Software is under the BSD 2-Clause "Simplified" License, see LICENSE file for further details. 

##
# @file simple.py
#
# @brief Wrapper function for executing embarrassingly parallel jobs 
#
# @section description_simplefile Description
# Something
#
# @section libraries_main Libraries/Modules
# - multiprocessing standard library (https://docs.python.org/3/library/multiprocessing.html)
#   - Access to Pool and asynchronous parallel execution
# - tqdm library (https://tqdm.github.io/)
#   - Provides progress bar and estimate time left for remaining jobs/tasks  
#
# @section author_doxygen_example Author(s)
# - Create by Michael-Angelo Y.-H. Lam on 08/23/2022.
# 

from multiprocessing import Pool

try:
    get_ipython()
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm

#from tqdm import tqdm_notebook as tqdm
def _simple(func, n_procs, args_list, p_bar=None ):

    """Internal function for executing jobs in embarrassingly parallel mode or serial mode

    :param func:      Function to be executed.
    :type  func:      function
    :param n_procs:   Number of processes to run in parallel. Setting to 1 run function in 
                      serial mode without multiprocessing module.   
    :type  n_procs:   int
    :param args_list: List of tuples corresponding to the arguments of each parallel job.
    :type  args_list: tuple list
    :param p_bar:     tqdm progress bar object.
    :type  p_bar:     tqdm.std.tqdm

    :rtype: tuple list or None list
    """

 
    # Setting up callback function for updating progress bar required for integration with pool.apply_async
    if p_bar is not None:
        def update_progress_bar(*dummy): p_bar.update()
    else:
        def update_progress_bar(*dummy): pass
            
    if n_procs > 1:        
        # Executing parallel jobs
        with Pool(n_procs) as pool:
            jobs = [pool.apply_async(func, args=(args), callback=update_progress_bar) for args in args_list]     
            # Collecting job results
            results = [ (job.get()) for job in jobs ]     
    else:
        # Executing jobs in serial mode if only one processor is specified     
        results = []
        for args in args_list:
            if type(args) is not tuple: args = (args,)
            results.append( func(*args)  )
            update_progress_bar()
            
    return results 
    
def _zip_args(args_list, common_args):

    """ Internal function for generating list of tuples from arguments for each parallel job
        and common arguments for all jobs 

    :param args_list  : List of objects (for parallel jobs with only one varying arguments) or list
                        of tuples (for parallel jobs with more than one varying arguments).
    :param args_list  : list
    :param common_args: Arguments common to all jobs. Either a tuple or single object. 

    :rtype: tuple list 
    """
    
    # If no common aruguments, i.e. None, converting to empty tuple
    if common_args is None: common_args = ()
    # If not a tuple, converting single object to tuple of one element
    if type(common_args) is not tuple: common_args = (common_args,)
 
    full_args_list = []
    for args in args_list:
        # Converting single object into tuple of one element
        if type(args) is not tuple: args = (args,)
        full_args_list.append( args + common_args )
            
    return full_args_list

def simple(func, n_procs, args_list, common_args=None, p_desc=None, is_p_bar=True):

    """ Function for executing a function in embarrassingly parallel mode or serial mode
  
    :param func:        Function to be executed.
    :type  func:        function
    :param n_procs:     Number of processes to run in parallel. Setting to 1 run function in 
                        serial mode without multiprocessing module.
    :type  n_procs:     int
    :param args_list:   List of objects (for parallel jobs with only one varying arguments) or list
                        of tuples (for parallel jobs with more than one varying arguments).
    :type  args_list:   list
    :param common_args: Arguments common to all jobs. Either a tuple or single object. 
    :type  common_args: None, Object, Tuple
    :param p_desc:      Custom text for tqdm progress bar
    :type  p_desc:      str
    :param is_p_bar:    Flag for turning off tqdm progress bar 
    :type  is_p_bar:    bool

    :rtype: tuple list or None list
    """

    # Creating tqdm progress bar  
    if is_p_bar:
        if p_desc is None: p_desc = 'Jobs'
        p_bar = tqdm(total=len(args_list), desc=p_desc)#, leave=False, position = tqdm._get_free_pos())
    else:
        p_bar = None
        
    # Wrapping _simple function in a try/except block to avoid parallel pool from
    # locking up if an exception is thrown by the function
    try:
        args_list = _zip_args( args_list, common_args )
        results = _simple( func, n_procs, args_list, p_bar)
    except Exception as e:
        # Cleaning up progress bar on error to avoid I/O issues
        if is_p_bar: p_bar.close()
        raise e
    
    # Cleaning up progress bar 
    if is_p_bar: p_bar.close()

    return results


def simple2(func, args_list, kwargs_list, n_procs, p_desc=None, is_p_bar=True):


    """ Function for executing a function in embarrassingly parallel mode or serial mode
  
    :param func:        Function to be executed.
    :type  func:        function
    :param n_procs:     Number of processes to run in parallel. Setting to 1 run function in 
                        serial mode without multiprocessing module.
    :type  n_procs:     int
    :param args_list:   List of objects (for parallel jobs with only one varying arguments) or list
                        of tuples (for parallel jobs with more than one varying arguments).
    :type  args_list:   list
    :param common_args: Arguments common to all jobs. Either a tuple or single object. 
    :type  common_args: None, Object, Tuple
    :param p_desc:      Custom text for tqdm progress bar
    :type  p_desc:      str
    :param is_p_bar:    Flag for turning off tqdm progress bar 
    :type  is_p_bar:    bool

    :rtype: tuple list or None list
    """

        
    # Wrapping _simple function in a try/except block to avoid parallel pool from
    # locking up if an exception is thrown by the function
    try:


        if isinstance(args_list, tuple):
            na = 1
        else:
            na = len(args_list)
        
        if isinstance(kwargs_list, dict):
            nk = 1
        else:
            nk = len(kwargs_list)

        if na > 1 and nk > 1:
            if not na == nk:
                raise Exception("Number of arugments (%d) does not match number of kwargs (%d)." % (na, nk))

        n = max(na, nk)
        if isinstance(func, list):
            nf = len(func)
        else:
            nf = 1

        if nf > 1 and n > 1:
            if not nf == n:
                raise Exception("Number of functions do not match number of arugments.")

        n = max(n, nf)
        if nf == 1:
            func = [func]*n

        if na == 1:
            args_list = [args_list]*n

        if nk == 1:
            kwargs_list = [kwargs_list]*n

            
        call_list = list(zip(func, args_list, kwargs_list))
        # Creating tqdm progress bar  
        if is_p_bar:
            if p_desc is None: p_desc = 'Jobs'
            p_bar = tqdm(total=len(call_list), desc=p_desc, leave=False)
            #remote_tqdm = ray.remote(tqdm_ray.tqdm)
            #p_bar = remote_tqdm.remote(total=len(call_list), desc=p_desc)
        else:
            p_bar = None


        results = _simple2(call_list, n_procs, p_bar)



    except Exception as e:
        # Cleaning up progress bar on error to avoid I/O issues
        if is_p_bar: p_bar.close()
        raise e
    
    # Cleaning up progress bar 
    if is_p_bar: p_bar.close()

    return results

def _simple2(call_list, n_procs, p_bar=None):

    """Internal function for executing jobs in embarrassingly parallel mode or serial mode

    :param func:      Function to be executed.
    :type  func:      function
    :param n_procs:   Number of processes to run in parallel. Setting to 1 run function in 
                      serial mode without multiprocessing module.   
    :type  n_procs:   int
    :param args_list: List of tuples corresponding to the arguments of each parallel job.
    :type  args_list: tuple list
    :param p_bar:     tqdm progress bar object.
    :type  p_bar:     tqdm.std.tqdm

    :rtype: tuple list or None list
    """

 
    # Setting up callback function for updating progress bar required for integration with pool.apply_async
    if p_bar is not None:
        def update_progress_bar(*dummy): p_bar.update()
    else:
        def update_progress_bar(*dummy): pass
            
    if n_procs > 1:        
        # Executing parallel jobs
        with Pool(n_procs) as pool:
            jobs = [pool.apply_async(f, a, kw,  callback=update_progress_bar) for f, a, kw in call_list]     
            # Collecting job results
            results = [ (job.get()) for job in jobs ]     
    else:
        # Executing jobs in serial mode if only one processor is specified     
        results = []
        for f, a, kw in call_list:
            results.append(f(*a, **kw))
            update_progress_bar()

            
    return results 

import ray
from ray.experimental import tqdm_ray

def _simple3(call_list, n_procs, p_bar=None):

    """Internal function for executing jobs in embarrassingly parallel mode or serial mode

    :param func:      Function to be executed.
    :type  func:      function
    :param n_procs:   Number of processes to run in parallel. Setting to 1 run function in 
                      serial mode without multiprocessing module.   
    :type  n_procs:   int
    :param args_list: List of tuples corresponding to the arguments of each parallel job.
    :type  args_list: tuple list
    :param p_bar:     tqdm progress bar object.
    :type  p_bar:     tqdm.std.tqdm

    :rtype: tuple list or None list
    """

 
    # Setting up callback function for updating progress bar required for integration with pool.apply_async
    if p_bar is not None:
        def update_progress_bar(*dummy): p_bar.update()
    else:
        def update_progress_bar(*dummy): pass
            
    if n_procs > 1:        
        # Executing parallel jobs
        #jobs = [pool.apply_async(f, a, kw,  callback=update_progress_bar) for f, a, kw in call_list]     
            # Collecting job results
        
        jobs = [retrieve_task.remote(p_bar, f, *a, **kw) for f, a, kw in call_list]
        results = ray.get(jobs)
        #[ (job.get()) for job in jobs ]     
    else:
        # Executing jobs in serial mode if only one processor is specified     
        results = []
        for f, a, kw in call_list:
            results.append(f(*a, **kw))
            update_progress_bar()

            
    return results 


@ray.remote
def retrieve_task(p_bar, func, *args, **kwargs):
    result = func(*args, **kwargs)
    p_bar.update.remote(1)
    return result 
