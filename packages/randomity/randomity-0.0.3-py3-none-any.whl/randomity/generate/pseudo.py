import os

from .._utils.draw_histogram import draw_histogram

from .algos.algo_MersenneTwister import _MersenneTwister
from .algos.algo_XORShift import _XORShift
from .algos.algo_MTNumpy import _MTNumpy
from .algos.algo_LCG import _LCG
from .algos.algo_BlumBlumShub import _BlumBlumShub

def prandom(min_val:int=0,
            max_val:int=10,
            num_out:int=1,
            algo:str="MersenneTwister",
            seed:int|None=None,
            hist=False) -> list[int]:
    """
    Generate a random number using a pseudo-random number generator (PRNG).

    Args:
        min_val (integer): Minimum value of the random number. Default is 0.
        max_val (integer): Maximum value of the random number. Default is 10.
        num_out (integer): Number of numbers to generate. Default is 1.
        algo (string): Algorithm to use for generating random numbers. Options are:
                        - "MersenneTwister" (or "MT"), 
                        - "XORShift" (or "XOR"), 
                        - "LCG" (or "LinearCongruentialGenerator"),
                        - "MTNumpy" (or "MersenneTwisterNumpy" or "Numpy"),
                        - "BlumBlumShub" (or "BBS").
                    Default is "MersenneTwister".
        seed (integer): Seed for the random number generator. Default is current system's time.
        hist (boolean): Whether to display a histogram of the generated numbers. Default is False.

    Returns:
         A list of random integers.
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder='big')
        
    if algo == "MersenneTwister" or algo == "MT":
        random_numbers = MersenneTwister(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "XORShift" or algo == "XOR":
        random_numbers = XORShift(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "LCG" or algo == "LinearCongruentialGenerator":
        random_numbers = LCG(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "MTNumpy" or algo == "MersenneTwisterNumpy" or algo == "Numpy":
        random_numbers = MTNumpy(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    elif algo == "BlumBlumShub" or algo == "BBS":
        random_numbers = BlumBlumShub(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)
    else:
        random_numbers = MersenneTwister(min_val=min_val, max_val=max_val, num_out=num_out, seed=seed)

    if hist:
        draw_histogram(random_numbers, 
             bins=10, 
             title='Histogram of Random Numbers', 
             xlabel='Value', 
             ylabel='Frequency', 
             color='tab:blue', 
             alpha=0.7, 
             edgecolor='black',
             grid=True)
        
    return random_numbers


def MersenneTwister(min_val:int, max_val:int, num_out:int, seed:int):
    rng = _MersenneTwister(seed)
    random_numbers = []

    range_size = max_val - min_val + 1
    max_32bit = 2**32 - 1
    for _ in range(num_out):
        raw_number = rng.extract_number()
        scaled_number = min_val + int((raw_number / max_32bit) * range_size)
        random_numbers.append(scaled_number)

    return random_numbers

def XORShift(min_val:int, max_val:int, num_out:int, seed:int):
    rng = _XORShift(seed)
    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)
        
    return random_numbers

def LCG(min_val:int, max_val:int, num_out:int, seed:int):
    rng = _LCG(seed)
    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)

    return random_numbers

def MTNumpy(min_val:int, max_val:int, num_out:int, seed:int):
    rng = _MTNumpy(seed)
    random_numbers = [min_val + (rng.extract_number() % (max_val - min_val + 1)) for _ in range(num_out)]

    return random_numbers

def BlumBlumShub(min_val:int, max_val:int, num_out:int, seed:int):
    try:
        rng = _BlumBlumShub(seed)
    except ValueError as e:
        print(f"Error initializing BlumBlumShub: {e}")
        return []

    random_numbers = []
    range_size = max_val - min_val + 1
    
    for _ in range(num_out):
        raw_number = rng.next_int()
        scaled_number = min_val + (raw_number % range_size)
        random_numbers.append(scaled_number)
        
    return random_numbers