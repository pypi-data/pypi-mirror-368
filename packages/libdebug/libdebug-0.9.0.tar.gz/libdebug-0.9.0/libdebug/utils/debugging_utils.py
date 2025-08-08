#
# This file is part of libdebug Python library (https://github.com/libdebug/libdebug).
# Copyright (c) 2023-2025 Gabriele Digregorio, Roberto Alessandro Bertolini, Francesco Panebianco. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for details.
#

from libdebug.data.memory_map import MemoryMap
from libdebug.data.memory_map_list import MemoryMapList
from libdebug.data.symbol_list import SymbolList
from libdebug.liblog import liblog
from libdebug.utils.elf_utils import is_pie, resolve_address, resolve_symbol


def normalize_and_validate_address(address: int, maps: MemoryMapList[MemoryMap]) -> int:
    """Normalizes and validates the specified address.

    Args:
        address (int): The address to normalize and validate.
        maps (MemoryMapList[MemoryMap]): The memory maps.

    Returns:
        int: The normalized address.

    Throws:
        ValueError: If the specified address does not belong to any memory map.
    """
    if not maps:
        raise ValueError("No memory maps available to resolve the address. Did you specify a valid backing file?")
    if address < maps[0].start:
        # The address is lower than the base address of the lowest map. Suppose it is a relative address for a PIE binary.
        address += maps[0].start

    for vmap in maps:
        if vmap.start <= address < vmap.end:
            return address

    raise ValueError(f"Address {hex(address)} does not belong to any memory map.")


def resolve_symbol_in_maps(symbol: str, maps: MemoryMapList[MemoryMap]) -> int:
    """Returns the address of the specified symbol in the specified memory maps.

    Args:
        symbol (str): The symbol whose address should be returned.
        maps (MemoryMapList[MemoryMap]): The memory maps.

    Returns:
        int: The address of the specified symbol in the specified memory maps.

    Throws:
        ValueError: If the specified symbol does not belong to any memory map.
    """
    mapped_files = {}

    if "+" in symbol:
        symbol, offset_str = symbol.split("+")
        offset = int(offset_str, 16)
    else:
        offset = 0

    for vmap in maps:
        if vmap.backing_file and vmap.backing_file not in mapped_files and vmap.backing_file[0] != "[":
            mapped_files[vmap.backing_file] = vmap.start

    for file, base_address in mapped_files.items():
        try:
            address = resolve_symbol(file, symbol)

            if is_pie(file):
                address += base_address

            return address + offset
        except (OSError, RuntimeError) as e:
            liblog.debugger(f"Error while resolving symbol {symbol} in {file}: {e}")
        except ValueError:
            pass

    raise ValueError(f"Symbol {symbol} not found in the specified mapped file. Please specify a valid symbol.")


def resolve_address_in_maps(address: int, maps: MemoryMapList[MemoryMap]) -> str:
    """Returns the symbol corresponding to the specified address in the specified memory maps.

    Args:
        address (int): The address whose symbol should be returned.
        maps (MemoryMapList[MemoryMap]): The memory maps.

    Returns:
        str: The symbol corresponding to the specified address in the specified memory maps.

    Throws:
        ValueError: If the specified address does not belong to any memory map.
    """
    mapped_files = {}

    for vmap in maps:
        file = vmap.backing_file
        if not file or file[0] == "[":
            continue

        if file not in mapped_files:
            mapped_files[file] = (vmap.start, vmap.end)
        else:
            mapped_files[file] = (mapped_files[file][0], vmap.end)

    for file, (base_address, top_address) in mapped_files.items():
        # Check if the address is in the range of the current section
        if address < base_address or address >= top_address:
            continue

        try:
            return resolve_address(file, address - base_address) if is_pie(file) else resolve_address(file, address)
        except OSError as e:
            liblog.debugger(f"Error while resolving address {hex(address)} in {file}: {e}")
        except ValueError:
            pass

    return hex(address)


def resolve_symbol_name_in_maps_util(
    address: int,
    external_symbols: SymbolList,
) -> str:
    """Resolves the address."""
    if not external_symbols:
        return f"{address:#x}"

    matching_symbols = external_symbols._search_by_address(address)

    if len(matching_symbols) == 0:
        return f"{address:#x}"
    elif len(matching_symbols) > 1:
        liblog.warning(f"Multiple symbols found for address {address:#x}. Taking the first one.")

    return matching_symbols[0].name
