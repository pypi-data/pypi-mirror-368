"""
IDA Pro Database to ELF Converter.

This module provides functionality to convert an IDA Pro database into an ELF
(Executable and Linkable Format) file. It extracts segments, functions, and
symbols from the IDA database and reconstructs them into a valid ELF binary.

Typical usage example:
    elf_data = build_elf()
    with open("output.elf", "wb") as f:
        f.write(elf_data)
"""

from typing import Optional

import ida_idp
import ida_segment
import ida_funcs
import ida_bytes
import ida_ida
import ida_segregs
import ida_idaapi
import ida_entry

from gaudit import elfbuilder


class ELFBuilderException(Exception):
    """Exception raised when an error occurred while building ELF.

    This exception is raised when the ELF builder encounters an unsupported
    architecture or other critical errors during the conversion process.

    Attributes:
        message: Explanation of the error.
    """

    pass


def build_elf() -> bytes:
    """Build an ELF file from the current IDA Pro database.

    This function extracts all segments, functions, and symbols from the current
    IDA Pro database and reconstructs them into an ELF binary. The function
    automatically detects the target architecture and sets appropriate ELF
    machine type.

    The function performs the following steps:
    1. Detects the processor architecture and sets the ELF machine type
    2. Retrieves the entry point address
    3. Iterates through all segments and adds them to the ELF
    4. Extracts function symbols from each segment
    5. Handles special cases (e.g., ARM Thumb mode)

    Returns:
        bytes: The complete ELF file as a byte string, ready to be written to disk.

    Raises:
        ELFBuilderException: If the processor architecture is not supported.
            Currently supported architectures are:
            - x86 (32-bit and 64-bit)
            - ARM (including Thumb mode)
            - MIPS
            - PowerPC (32-bit and 64-bit)

    Example:
        >>> try:
        ...     elf_data = build_elf()
        ...     with open("recovered.elf", "wb") as f:
        ...         f.write(elf_data)
        ... except ELFBuilderException as e:
        ...     print(f"Failed to build ELF: {e}")

    Note:
        This function requires an active IDA Pro session with a loaded database.
        The quality of the output ELF depends on the completeness of the IDA
        analysis. Ensure that IDA has properly identified all functions and
        segments before running this conversion.
    """
    # Determine the target architecture
    ph_id: int = ida_idp.ph_get_id()
    machine: int

    if ph_id == ida_idp.PLFM_386:
        if ida_ida.inf_is_64bit():
            machine = elfbuilder.EM_AMD64
        else:
            machine = elfbuilder.EM_X86
    elif ph_id == ida_idp.PLFM_ARM:
        machine = elfbuilder.EM_ARM
    elif ph_id == ida_idp.PLFM_MIPS:
        machine = elfbuilder.EM_MIPS
    elif ph_id == ida_idp.PLFM_PPC:
        if ida_ida.inf_is_64bit():
            machine = elfbuilder.EM_PPC64
        else:
            machine = elfbuilder.EM_PPC
    else:
        raise ELFBuilderException("machine is not supported")

    # Get the entry point address
    entry_point: int = ida_entry.get_entry(ida_entry.get_entry_ordinal(0))
    if entry_point == ida_idaapi.BADADDR:
        entry_point = 0

    # Create the ELF builder instance
    elf: elfbuilder.Elf = elfbuilder.Elf(e_entry=entry_point, e_machine=machine)

    # Get the first segment
    seg: Optional[ida_segment.segment_t] = ida_segment.get_first_seg()

    # Iterate through all segments
    while seg is not None:
        # Extract segment information
        seg_name: str = ida_segment.get_segm_name(seg)
        seg_data: bytes = ida_bytes.get_bytes(seg.start_ea, seg.end_ea - seg.start_ea)

        # Add segment to ELF based on permissions
        if seg.perm & ida_segment.SEGPERM_EXEC == ida_segment.SEGPERM_EXEC:
            # Executable segment (code)
            elf.add_progbits_section(seg_name, seg_data, seg.start_ea)
        else:
            # Data segment
            elf.add_data_section(seg_name, seg_data, seg.start_ea)

        # Extract function symbols from this segment
        f: Optional[ida_funcs.func_t] = ida_funcs.get_func(seg.start_ea)
        if f is None:
            f = ida_funcs.get_next_func(seg.start_ea)

        while f is not None:
            # Check if function is still within segment bounds
            if f.start_ea > seg.end_ea:
                break

            # Get function name
            f_name: str = ida_funcs.get_func_name(f.start_ea)

            # Skip auto-generated names (sub_XXXXXX)
            if f_name.startswith("sub_"):
                f_name = ""

            # Handle ARM Thumb mode functions
            if machine == elfbuilder.EM_ARM and ida_segregs.get_sreg(f.start_ea, ida_idp.str2reg("T")):
                # For Thumb functions, set LSB of address to 1
                elf.add_exported_symbol(f_name, f.start_ea + 1)
            else:
                # Regular function address
                elf.add_exported_symbol(f_name, f.start_ea)

            # Move to next function
            f = ida_funcs.get_next_func(f.start_ea)

        # Move to next segment
        seg = ida_segment.get_next_seg(seg.start_ea)

    # Build and return the final ELF
    return elf.build()
