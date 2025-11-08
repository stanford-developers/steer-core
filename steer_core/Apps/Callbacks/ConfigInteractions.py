from typing import List, Tuple
from dash import no_update


def generate_parameters_and_ranges(object, config) -> Tuple[List[float], List[float], List[float]]:
    """
    Generate parameter value lists and their corresponding min/max ranges for any object.
    
    This function extracts parameter values from an object based on a configuration's
    parameter list, and retrieves the minimum and maximum values for each parameter
    if range attributes exist (e.g., '{param}_range'), otherwise uses the current
    value as both min and max.
    
    Parameters
    ----------
    object : Any
        The object from which to extract parameter values. Must have attributes
        corresponding to the parameters listed in config.parameter_list.
    config : Type
        Configuration class or object that contains a 'parameter_list' attribute
        specifying which parameters to extract from the object.
    
    Returns
    -------
    Tuple[List[float], List[float], List[float]]
        A tuple containing three lists:
        - parameter_values: Current values of each parameter
        - min_values: Minimum values for each parameter (from {param}_range[0] 
          or current value if no range exists)
        - max_values: Maximum values for each parameter (from {param}_range[1] 
          or current value if no range exists)
    
    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.temperature = 25.0
    ...         self.temperature_range = (0.0, 100.0)
    ...         self.pressure = 1.0
    >>> 
    >>> class Config:
    ...     parameter_list = ['temperature', 'pressure']
    >>> 
    >>> obj = MyObject()
    >>> values, mins, maxs = generate_parameter_and_list_ranges(obj, Config)
    >>> print(values)  # [25.0, 1.0]
    >>> print(mins)    # [0.0, 1.0]
    >>> print(maxs)    # [100.0, 1.0]
    
    Notes
    -----
    - If an object has a '{param}_range' attribute, it should be a tuple/list
      with exactly two elements: (min_value, max_value)
    - If no range attribute exists for a parameter, the current value is used
      for both minimum and maximum values
    - All extracted values are expected to be numeric (convertible to float)
    """
    parameter_values = []
    min_values = []
    max_values = []

    parameter_list = config.parameter_list

    for param in parameter_list:

        value = getattr(object, param)
        parameter_values.append(value)

        if hasattr(object, f"{param}_range"):
            min_values.append(getattr(object, f"{param}_range")[0])
            max_values.append(getattr(object, f"{param}_range")[1])
        else:
            min_values.append(value)
            max_values.append(value)

    return parameter_values, min_values, max_values



def generate_rangeslider_parameters_and_ranges(object, config) -> Tuple[
    List[float],
    List[float],
    List[float],
    List[float],
]:
    """
    Generate range slider parameter values and their corresponding min/max bounds for any object.
    
    This function extracts range parameter values from an object based on a configuration's
    range_slider_parameters list. Each parameter is expected to be a tuple/list representing 
    a range (start, end). It also retrieves the absolute minimum and maximum bounds for each 
    parameter from corresponding '{param}_range' attributes, or uses the current range values
    as bounds if no range attribute exists.
    
    Parameters
    ----------
    object : Any
        The object from which to extract range parameter values. Must have attributes
        corresponding to the parameters listed in config.range_slider_parameters, where 
        each attribute contains a tuple/list of (start, end) values. Optionally has 
        '{param}_range' attributes defining the absolute bounds for each parameter.
    config : Any
        Configuration class or object that contains a 'range_slider_parameters' attribute
        specifying which range parameters to extract from the object.
    
    Returns
    -------
    Tuple[List[float], List[float], List[float], List[float]]
        A tuple containing four lists:
        - start_values: Start values for each range parameter (from param[0])
        - end_values: End values for each range parameter (from param[1])
        - min_values: Absolute minimum bounds for each parameter (from {param}_range[0] 
          or param[0] if no range exists)
        - max_values: Absolute maximum bounds for each parameter (from {param}_range[1] 
          or param[1] if no range exists)
    
    Examples
    --------
    >>> class MyCollector:
    ...     def __init__(self):
    ...         self.voltage_window = (2.5, 4.2)  # Current range setting
    ...         self.voltage_window_range = (0.0, 5.0)  # Absolute bounds
    ...         self.current_limit = (0.1, 2.0)  # Current range setting
    ...         # No current_limit_range, so uses current values as bounds
    >>> 
    >>> class Config:
    ...     range_slider_parameters = ['voltage_window', 'current_limit']
    >>> 
    >>> collector = MyCollector()
    >>> starts, ends, mins, maxs = generate_rangeslider_parameters_and_ranges_from_config(
    ...     collector, Config)
    >>> print(starts)  # [2.5, 0.1]
    >>> print(ends)    # [4.2, 2.0]
    >>> print(mins)    # [0.0, 0.1]  # Uses range for voltage, current value for current
    >>> print(maxs)    # [5.0, 2.0]  # Uses range for voltage, current value for current
    
    Notes
    -----
    - If config.range_slider_parameters is empty, returns four empty lists
    - Each parameter in range_slider_parameters must exist as an attribute on the object
      and contain exactly two elements: (start_value, end_value)
    - If a parameter has a corresponding '{param}_range' attribute, those bounds are used
    - If no range attribute exists for a parameter, the current start/end values are used
      as the minimum/maximum bounds respectively
    - All values are expected to be numeric (convertible to float)
    - This function is typically used for range slider UI components where
      users can select a range within predefined bounds
    
    Raises
    ------    
    AttributeError
        If the object doesn't have the required parameter attributes or if config
        doesn't have range_slider_parameters attribute
    IndexError
        If parameter values don't contain exactly two elements
    """
    start_values = []
    end_values = []
    min_values = []
    max_values = []

    parameter_list = config.range_slider_parameters

    for param in parameter_list:
        
        value = getattr(object, param)
        start_values.append(value[0])
        end_values.append(value[1])

        if hasattr(object, f"{param}_range"):
            min_values.append(getattr(object, f"{param}_range")[0])
            max_values.append(getattr(object, f"{param}_range")[1])
        else:
            min_values.append(value[0])
            max_values.append(value[1])

    return start_values, end_values, min_values, max_values


def validate_dependent_properties(object, config) -> None:
    """
    Validate and clamp dependent properties to their valid hard ranges for any object.
    
    This function validates parameter values from an object based on a configuration's
    parameter list, checking each parameter against its corresponding '{param}_hard_range'
    attribute. If a parameter value falls outside its hard range, it is automatically
    clamped to the nearest valid boundary (minimum or maximum).
    
    Parameters
    ----------
    object : Any
        The object whose parameter values will be validated and potentially modified.
        Must have attributes corresponding to the parameters listed in config.parameter_list.
        Should have '{param}_hard_range' attributes defining the valid bounds for validation.
    config : Any
        Configuration class or object that contains a 'parameter_list' attribute
        specifying which parameters to validate on the object.
    
    Returns
    -------
    None
        This function modifies the object in-place and does not return any values.
        
    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.temperature = 150.0  # Outside valid range
    ...         self.temperature_hard_range = (0.0, 100.0)
    ...         self.pressure = 0.5  # Within valid range
    ...         self.pressure_hard_range = (0.0, 10.0)
    >>> 
    >>> class Config:
    ...     parameter_list = ['temperature', 'pressure']
    >>> 
    >>> obj = MyObject()
    >>> print(obj.temperature)  # 150.0 (before validation)
    >>> validate_dependent_properties(obj, Config)
    >>> print(obj.temperature)  # 100.0 (clamped to maximum)
    >>> print(obj.pressure)     # 0.5 (unchanged, within range)
    
    Notes
    -----
    - Only parameters with corresponding '{param}_hard_range' attributes are validated
    - Parameters without hard range attributes are silently skipped (no validation performed)
    - Hard range attributes should be tuples/lists with exactly two elements: (min_value, max_value)
    - Values are clamped to the nearest boundary if they fall outside the valid range
    - This function modifies the object in-place, changing parameter values as needed
    - Typically used after parameter updates to ensure all values remain within valid bounds
    
    Raises
    ------
    AttributeError
        If the object doesn't have a parameter attribute listed in config.parameter_list,
        or if config doesn't have a parameter_list attribute
    IndexError
        If a hard_range attribute doesn't contain exactly two elements
    """
    parameter_list = config.parameter_list
    
    for param in parameter_list:
        try:
            # Get the hard range and current value for this parameter
            param_range = getattr(object, f"{param}_hard_range")
            param_value = getattr(object, param)
            
            # Clamp value to valid range if necessary
            if param_value < param_range[0]:
                setattr(object, param, param_range[0])
            elif param_value > param_range[1]:
                setattr(object, param, param_range[1])
                
        except AttributeError:
            # Parameter or hard range doesn't exist, skip validation
            continue


def create_no_update_response(
    config=None,
    existing_warnings: List[str] = [],
    n: int = None,
    n_rangeslider: int = None,
) -> Tuple:
    """
    Create a no-update response tuple for Dash callbacks based on configuration parameters.
    
    This function generates a standardized response tuple containing `no_update` values
    for all UI components defined in a configuration object. This is typically used in
    Dash callbacks when no updates should be made to the UI components, preserving
    their current state while potentially updating warning messages.
    
    Parameters
    ----------
    config : Any, optional
        Configuration object that defines the UI components and their parameters.
        Should contain attributes like 'parameter_list', 'range_slider_parameters',
        'dropdown_menu', 'radioitem_parameters', and 'text_parameters'.
        If None, only basic response structure is created.
    existing_warnings : List[str], default []
        List of existing warning messages to include in the response.
        These warnings will be preserved in the callback output.
    n : int, optional
        Number of regular slider/input parameters. If None, determined from
        config.parameter_list length. Used to create the correct number of
        no_update responses for sliders and inputs.
    n_rangeslider : int, optional
        Number of range slider parameters. If None, determined from
        config.range_slider_parameters length. Used to create the correct
        number of no_update responses for range sliders.
    
    Returns
    -------
    Tuple
        A tuple containing warning messages followed by no_update responses for all
        UI components defined in the configuration:
        - warnings: List[str] - Warning messages (first element)
        - cache_key: no_update - Cache key for callback optimization
        - slider_values: List[no_update] - Current slider values
        - slider_mins: List[no_update] - Slider minimum values
        - slider_maxs: List[no_update] - Slider maximum values
        - slider_marks: List[no_update] - Slider tick marks
        - slider_steps: List[no_update] - Slider step sizes
        - input_steps: List[no_update] - Input field step sizes
        
        Additional elements based on config attributes:
        - dropdown_value: no_update (if config.dropdown_menu exists)
        - range_slider_*: List[no_update] (if config.range_slider_parameters exists)
        - radioitem_values: List[no_update] (if config.radioitem_parameters exists)
        - text_values: List[no_update] (if config.text_parameters exists)
    
    Examples
    --------
    >>> class Config:
    ...     parameter_list = ['temperature', 'pressure']
    ...     dropdown_menu = True
    ...     range_slider_parameters = ['voltage_window']
    ...     radioitem_parameters = ['mode']
    ...     text_parameters = ['label']
    >>> 
    >>> config = Config()
    >>> warnings = ['Temperature out of range']
    >>> response = create_no_update_response(config, warnings)
    >>> print(len(response))  # Number of response elements
    >>> print(response[0])    # ['Temperature out of range']
    >>> print(response[1])    # no_update (cache_key)
    
    Notes
    -----
    - This function is primarily used in Dash callback error handling or when
      callback conditions are not met and no UI updates should occur
    - The response tuple structure must match the callback's Output specification
    - Optional UI components (dropdown, range sliders, radio items, text inputs)
      are only included in the response if they exist in the configuration
    - All UI component responses use Dash's `no_update` to preserve current state
    - The function automatically determines response tuple length based on config
    
    Raises
    ------
    AttributeError
        If config object doesn't have expected attributes when accessed
    """
    n = len(config.parameter_list) if n is None else n

    response = (
        no_update,  # cache_key
        [no_update] * n,  # slider values
        [no_update] * n,  # slider mins
        [no_update] * n,  # slider maxs
        [no_update] * n,  # slider marks
        [no_update] * n,  # slider steps
        [no_update] * n,  # input steps
    )

    if hasattr(config, "dropdown_menu") and config.dropdown_menu:
        response += (no_update,)

    if hasattr(config, "range_slider_parameters") and config.range_slider_parameters:
        n_rangeslider = len(config.range_slider_parameters) if n_rangeslider is None else n_rangeslider
        response += (
            [no_update] * n_rangeslider,  # range_slider_values
            [no_update] * n_rangeslider,  # range slider mins
            [no_update] * n_rangeslider,  # range slider maxs
            [no_update] * n_rangeslider,  # range slider marks
            [no_update] * n_rangeslider,  # range slider steps
            [no_update] * n_rangeslider,  # range slider start values
            [no_update] * n_rangeslider,  # range slider end values
        )

    if hasattr(config, "radioitem_parameters") and config.radioitem_parameters:
        num_radioitem_params = len(config.radioitem_parameters)
        response += ([no_update] * num_radioitem_params,)  # radioitem values

    if hasattr(config, "text_parameters") and config.text_parameters:
        num_text_params = len(config.text_parameters)
        response += ([no_update] * num_text_params,)  # text item values

    return (existing_warnings,) + tuple(response)