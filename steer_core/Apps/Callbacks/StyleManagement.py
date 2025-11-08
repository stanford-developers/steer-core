from dash import no_update
from typing import List

def update_style_display(current_style, target_display):
    """
    Helper function to update style display property with safe None handling.
    
    Args:
        current_style: Current style dict or None
        target_display: Target display value ("block" or "none")
        
    Returns:
        no_update if style already has target display, otherwise updated style dict
    """
    current_display = (current_style or {}).get("display")
    if current_display == target_display:
        return no_update
    return {**(current_style or {}), "display": target_display}



def update_tab_styles(active_tab: str, tab_names: List[str], current_styles: List[dict]) -> List:
    """
    Helper function to update tab styles based on the active tab.
    Only updates styles when the display property needs to change.
    
    Parameters
    ----------
    active_tab : str
        The currently active tab name
    tab_names : List[str]
        List of all tab names to check against
    current_styles : List[dict]
        List of current style dictionaries for each tab
        
    Returns
    -------
    List
        List of updated styles or no_update for each tab
    """
    updated_styles = []
    
    for tab_name, current_style in zip(tab_names, current_styles):
        # Determine what the display should be
        should_display = "block" if active_tab == tab_name else "none"
        
        # Get current display value (handle None style case)
        current_display = (current_style or {}).get("display")
        
        # If display is already correct, return no_update
        if current_display == should_display:
            updated_styles.append(no_update)
        else:
            # Create new style preserving existing properties
            new_style = {**(current_style or {}), "display": should_display}
            updated_styles.append(new_style)
    
    return updated_styles


