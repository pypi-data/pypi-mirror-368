import math

def get_weighting_function(weighting_type):
    """
    Returns a weighting function based on the specified type.

    Parameters:
        weighting_type (str): The type of weighting function. 
                              Options: 'inverse', 'sqrt_inverse', 'power_law', 
                                       'exponential', 'logarithmic', 'linear', 'constant'

    Returns:
        function: A function that computes the weight given an input x.
    """
    if weighting_type == 'inverse':
        return lambda x: 1 / x if x != 0 else float('inf')
    elif weighting_type == 'sqrt_inverse':
        return lambda x: 1 / math.sqrt(x) if x > 0 else float('inf')
    elif weighting_type == 'logarithmic':
        return lambda x: 1 / math.log(x + 1) if x > 0 else float('inf')
    elif weighting_type == 'power_law':
        return lambda x, a=2: 1 / (x ** a) if x > 0 else float('inf')  # Default power a=2
    elif weighting_type == 'exponential':
        return lambda x, a=1: math.exp(-a * x)  # Default decay rate a=1
    elif weighting_type == 'linear':
        return lambda x, a=1, b=0: a * x + b  # Default linear function y = ax + b
    elif weighting_type == 'constant':
        return lambda x: 1  # y = 1
    else:
        raise ValueError(f"Unknown weighting type: {weighting_type}")