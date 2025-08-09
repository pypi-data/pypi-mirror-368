"""
Defaults module.

Provides constants, dictionaries and default values
to be used in the project.

Since:
  2024/02/06

Authors:
  - Breno H. Pelegrin S. <breno.pelegrin@usp.br>
"""

THOUSAND_SEPARATOR = ' '
UNIT_SEPARATOR = ' '
_default_interface = None

multiplier_symbols = {
    "micro": {
        "preferred": "u",
        "possibles": ['u', 'µ', 'μ']
    },
}
"""
dict: A dictionary of symbols that can be used to replace possible multiplier symbols e.g. greek characters
with preferred characters.
"""

def set_default_interface(interface):
    """Sets the default backend interface.
    
    Args:
        interface (BackendInterface): The interface to be set as the default.
    """
    global _default_interface
    _default_interface = interface

def get_default_interface():
    """Returns the default backend interface.

    Returns:
        BackendInterface: The default backend interface.
    """
    global _default_interface
    return _default_interface