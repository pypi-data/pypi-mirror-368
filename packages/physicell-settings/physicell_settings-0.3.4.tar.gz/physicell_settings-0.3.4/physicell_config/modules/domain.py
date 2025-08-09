"""Domain size and mesh configuration."""

from typing import Dict, Any, List, Optional, Tuple
import xml.etree.ElementTree as ET
from .base import BaseModule


class DomainModule(BaseModule):
    """Manage simulation bounds and mesh spacing."""
    
    def __init__(self, config):
        super().__init__(config)
        self.data = {
            'x_min': -500.0,
            'x_max': 500.0,
            'y_min': -500.0,
            'y_max': 500.0,
            'z_min': -10.0,
            'z_max': 10.0,
            'dx': 20.0,
            'dy': 20.0,
            'dz': 20.0,
            'use_2D': True
        }
    
    def set_bounds(self, x_min: float, x_max: float, y_min: float, y_max: float,
                   z_min: float = -10.0, z_max: float = 10.0) -> None:
        """Configure the physical extents of the simulation space.

        Parameters
        ----------
        x_min, x_max, y_min, y_max, z_min, z_max:
            Coordinates describing the box boundaries in microns.
        """
        self.data.update({
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max,
            'z_min': z_min,
            'z_max': z_max
        })
    
    def set_mesh(self, dx: float, dy: float, dz: float = 20.0) -> None:
        """Set the Cartesian mesh spacing in each dimension.

        Parameters
        ----------
        dx, dy, dz:
            Grid spacing in microns.
        """
        self._validate_positive_number(dx, "dx")
        self._validate_positive_number(dy, "dy")
        self._validate_positive_number(dz, "dz")
        
        self.data.update({
            'dx': dx,
            'dy': dy,
            'dz': dz
        })
    
    def set_2D(self, use_2D: bool = True) -> None:
        """Toggle 2‑D simulation mode.

        Parameters
        ----------
        use_2D:
            ``True`` for planar simulations, ``False`` for 3‑D.
        """
        self.data['use_2D'] = use_2D
    
    def add_to_xml(self, parent: ET.Element) -> None:
        """Append domain settings to the output XML tree.

        Parameters
        ----------
        parent:
            The root ``PhysiCell_settings`` XML element.
        """
        domain_elem = self._create_element(parent, "domain")
        
        # Add bounds (no units for basic elements)
        self._create_element(domain_elem, "x_min", self.data['x_min'])
        self._create_element(domain_elem, "x_max", self.data['x_max'])
        self._create_element(domain_elem, "y_min", self.data['y_min'])
        self._create_element(domain_elem, "y_max", self.data['y_max'])
        self._create_element(domain_elem, "z_min", self.data['z_min'])
        self._create_element(domain_elem, "z_max", self.data['z_max'])
        
        # Add mesh (no units)
        self._create_element(domain_elem, "dx", self.data['dx'])
        self._create_element(domain_elem, "dy", self.data['dy'])
        self._create_element(domain_elem, "dz", self.data['dz'])
        
        # Add 2D flag
        self._create_element(domain_elem, "use_2D", str(self.data['use_2D']).lower())
    
    def get_info(self) -> Dict[str, Any]:
        """Return a copy of the current domain configuration."""
        return self.data.copy()
