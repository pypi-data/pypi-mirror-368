import os
from pathlib import Path
import streamlit
import streamlit.components.v1 as components


if (os.getenv('DEV_MODE') == 'true' and os.getenv('FRONTEND_HOST')):
    _component_func = components.declare_component(        
        "st_organogramRTR",        
        url="http://localhost:5173",
    )
else:    
    # parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = Path(__file__).parent.absolute() / "frontend/dist"
    _component_func = components.declare_component("st_organogramRTR", path=str(build_dir))

def st_organogramRTR(data, key=None):
    component_value = _component_func(data=data, key=key, default=None)   
    return component_value
