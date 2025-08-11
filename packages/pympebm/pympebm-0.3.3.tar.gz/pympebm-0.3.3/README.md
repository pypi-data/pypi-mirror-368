# `pympebm`


## Installation


```bash
pip install pympebm
```


## Data generation

To run `gen.py` first. Then to generate partial ordering datasets. `gen_partial.py`. 

## Change Log

- 2025-07-16 (V 0.0.6)
    - Added `mp_method = BT` in `algorithm.py` and `run.py`. 
    - Added `PL`. 
    - Fixed the bug in `generate_data.py`. 

- 2025-07-19 (V 0.0.7)
    - Added the class of `PlackettLuce`. 

- 2025-07-20 (V 0.0.15)
    - Updated the definition and implementation of conflict and certainty. 
    - Made sure `data` folder exists after uploading to pypi. 
    - Made sure `fixed_biomarker_order = True` if we use mixed patholgy in data generation. 
    - Fixed a bug in the calculation of `conflict`. 
    - Made sure the `algorithm.py` is using the correct energy calculation functions. 
    - Added entropy and certainty calculation in `MCMC` sampler. 
    - Made sure in `generate_data.py`, `certainty` is calculated based upon the `mp_method`.
    - Made sure in `generate_data.py`, we can tweak the paramter of `mcmc_iterations`, otherwise it will super slow. This is because the time complexity is `mcmc_iterations * sample_count`. 
    - Tested obtaining `ordering_array` from separate disease data files. Made some modifcations in `algorithm.py` to allow this. 

- 2025-07-23 (V 0.0.16 -- didn't push to Pypi)
    - Implemented the conflict version of using only discordant pairs. 

- 2025-07-25 (V 0.0.16)
    - Updated `algorithm.py` to reflect changes in the class of `PlackettLuce`. 

- 2025-07-26 (V 0.0.17)
    - Updated `generate_data.py` to skip calculating certainty and conflict if `sample_count <= 1`. 
  
- 2025-08-04 (V 0.1.7)
    - Use `fastsaebm` codes. 
    - Finished testing and data generation. 
    - With `m_{variant}` when number of repitition is 1. 
    - Fixed overflow bug in `prob_accept=min(1.0, np.exp(current_energy - new_energy))`. 
  
- 2025-08-04 (V 0.2.9)
    - Implemented the new certainty measure.  
    - Used the same `rng` all throughout in generate data. 
    - Added `save_details` to `run.py`.
    - Solved the logic bug of `save_details` and `save_results`.
    - Ensured the randomness again in `generate_data.py`.
  
- 2025-08-09 (V 0.3.1)
    - Used 15 biomarkers. 
    - Dynamically adjust dirichlet multinomial alpha array based on the number of biomarkers.
  
- 2025-08-10 (V 0.3.3)
    - Use numpy and numba (whenever possible) in `mp_utils.py`.