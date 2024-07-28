from siunits.predefined import Unit, FixedUnit
from siunits.types import UnitBase, ComplexUnit, Quantity
from abc import ABC

class helper(ABC):
    def find(self, symbol: str) -> Unit:
        """Find a unit with the given symbol.

        Args:
            symbol (str): The symbol of the unit to find.

        Raises:
            KeyError: If no unit with the given symbol is found.

        Returns:
            Unit: The unit with the given symbol.
        """
        
        for k in Unit._instances:
            if k[1] == symbol:
                return Unit._instances[k]

        raise KeyError(f"No unit with symbol '{symbol}'")
    
    def find_all(self, symbol: str) -> list[Unit]:
        """Find all units with the given symbol.

        Args:
            symbol (str): The symbol of the units to find.

        Raises:
            KeyError: If no unit with the given symbol is found.

        Returns:
            list[Unit]: The units with the given symbol.
        """
        
        found: list[Unit] = []
        for k in Unit._instances:
            if k[1] == symbol:
                found.append(Unit._instances[k])

        if len(found) == 0:
            raise KeyError(f"No unit with symbol '{symbol}'")
        
        return found

    # TODO: offset 고려해서 수정해야함
    def set(self, symbol: str, value: UnitBase | Quantity) -> FixedUnit:
        # TODO: kwargs로 offset, multiplier, latex_symbol 등 추가
        """Set a unit with the given symbol and value.

        Args:
            symbol (str): The symbol of the unit to set.
            value (UnitBase | Quantity): The value of the unit to set. It can be a Unit, FixedUnit, Quantity, or ComplexUnit.

        Returns:
            FixedUnit: The set unit.
        """
        
        if isinstance(value, Quantity):
            return FixedUnit(symbol, value.to_complex_unit())
        elif isinstance(value, ComplexUnit):
            return FixedUnit(symbol, value)
        elif isinstance(value, FixedUnit):
            return FixedUnit(symbol, value.base)
        elif isinstance(value, Unit):
            return FixedUnit(symbol, value**1)
    
    def __setitem__(self, symbol: str, value: UnitBase | Quantity):
        return self.set(symbol, value)
    
    def __getitem__(self, symbol: str) -> Unit | list[Unit]:
        found: list[Unit] = []
        for k in Unit._instances:
            if k[1] == symbol:
                found.append(Unit._instances[k])

        if len(found) == 0:
            raise KeyError(f"No unit with symbol '{symbol}'")
        elif len(found) == 1:
            return found[0]
        else:
            return found
        
    def __str__(self) -> str:
        return "Unit helper"
    
    def __repr__(self) -> str:
        return "Unit helper"

unit = helper()
unit.__doc__ = "Unit helper"

__all__ = ['unit']
