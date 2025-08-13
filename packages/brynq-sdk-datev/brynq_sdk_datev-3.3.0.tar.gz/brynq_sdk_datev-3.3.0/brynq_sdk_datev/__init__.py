from .lohn_und_gehalt import DatevLohnUndGehalt, schemas
from .lodas import DatevLodas
from .lodas.datev_mapping import DatevMapping
from functools import cached_property


class Datev:
    def __init__(self, berater_nr: int = None, mandanten_nr: int = None, debug: bool = False):
        self.berater_nr = berater_nr
        self.mandanten_nr = mandanten_nr
        self.debug = debug

    @cached_property
    def lodas(self) -> DatevLodas:
        # runs only on the first access to `self.lodas`
        return DatevLodas(berater_nr=self.berater_nr, mandanten_nr=self.mandanten_nr)

    @cached_property
    def lohn_und_gehalt(self) -> DatevLohnUndGehalt:
        # runs only on the first access to `self.lohn_und_gehalt`
        return DatevLohnUndGehalt(debug=self.debug)
