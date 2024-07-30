from siunits.predefined import Unit, FixedUnit
from siunits.types import UnitBase, ComplexUnit, Quantity
from abc import ABC

class UnitRegistry(ABC):
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

    def set(self, symbol: str, value: UnitBase | Quantity, **kwargs) -> FixedUnit:
        """Set a unit with the given symbol and value.

        Args:
            symbol (str): The symbol of the unit to set.
            value (UnitBase | Quantity): The value of the unit to set. It can be a Unit, FixedUnit, Quantity, or ComplexUnit.
            kwargs: Additional keyword arguments. <br>
                - offset (float): The offset of the unit.  <br>
                - multiplier (float): The multiplier of the unit. <br>
                - latex_symbol (str): The LaTeX symbol of the unit.

        Returns:
            FixedUnit: The set unit.
        """
        
        if isinstance(value, Quantity):
            return FixedUnit(symbol, value.to_complex_unit(), **kwargs)
        elif isinstance(value, ComplexUnit):
            return FixedUnit(symbol, value, **kwargs)
        elif isinstance(value, FixedUnit):
            return FixedUnit(symbol, value.base, **kwargs)
        elif isinstance(value, Unit):
            return FixedUnit(symbol, value**1, **kwargs)
        else:
            raise TypeError(f"Unsupported type '{type(value)}' for value")
    
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
        
    __str__ = __repr__ = lambda self: self.__class__.__name__

unit = UnitRegistry()
unit.__doc__ = UnitRegistry.__name__

__all__ = ['unit']
