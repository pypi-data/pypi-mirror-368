import pytest

from scientific_spinbox.backend.interfaces import PintInterface
from scientific_spinbox.defaults import set_default_interface, get_default_interface


def test_get_default_interface(backend):
    dummy_interface = PintInterface('SI')

    assert id(get_default_interface()) == id(backend)
    assert id(get_default_interface()) != id(dummy_interface)

def test_set_default_interface(backend):
    new_interface = PintInterface('SI')
    old_interface = get_default_interface()

    set_default_interface(new_interface)

    assert id(get_default_interface()) == id(new_interface)
    assert id(get_default_interface()) != id(old_interface)