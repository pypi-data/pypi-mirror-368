"""
ELF (Executable and Linkable Format) Builder Module

This module provides functionality to programmatically build ELF binaries
for various architectures. It supports both 32-bit and 64-bit ELF formats
and can create sections, add symbols, and generate complete ELF files.

The module uses the `construct` library for binary structure definitions
and provides a high-level interface through the `Elf` class.

Example:
    >>> elf = Elf(e_entry=0x400000, e_machine=EM_AMD64)
    >>> elf.add_progbits_section(".text", b"\\x90\\x90", 0x400000)
    >>> elf.add_exported_symbol("main", 0x400000)
    >>> elf_bytes = elf.build()
"""

from typing import Dict, List
from typing import Tuple, Union
import construct as cs

# ELF Header Structures
elf64Header = cs.Struct(
    "ei_mag" / cs.Bytes(4),  # 0x0 - ELF magic number
    "ei_class" / cs.Int8ub,  # 0x4 - File class (32/64 bit)
    "ei_data" / cs.Int8ub,  # 0x5 - Data encoding
    "ei_version" / cs.Int8ul,  # 0x6 - File version
    "ei_osabi" / cs.Int8ul,  # 0x7 - OS/ABI identification
    "ei_abiversion" / cs.Int8ul,  # 0x8 - ABI version
    "ei_pad" / cs.Padding(7),  # 0x9 - Padding bytes
    "e_type" / cs.Int16ul,  # 0x10 - Object file type
    "e_machine" / cs.Int16ul,  # 0x12 - Machine type
    "e_version" / cs.Int32ul,  # 0x14 - Object file version
    "e_entry" / cs.Int64ul,  # 0x18 - Entry point address
    "e_phoff" / cs.Int64ul,  # 0x20 - Program header offset
    "e_shoff" / cs.Int64ul,  # 0x28 - Section header offset
    "e_flags" / cs.Int32ul,  # 0x30 - Processor-specific flags
    "e_ehsize" / cs.Int16ul,  # 0x34 - ELF header size
    "e_phentsize" / cs.Int16ul,  # 0x36 - Program header entry size
    "e_phnum" / cs.Int16ul,  # 0x38 - Number of program header entries
    "e_shentsize" / cs.Int16ul,  # 0x3A - Section header entry size
    "e_shnum" / cs.Int16ul,  # 0x3C - Number of section header entries
    "e_shstrndx" / cs.Int16ul,  # 0x3E - Section name string table index
)

elf32Header = cs.Struct(
    "ei_mag" / cs.Bytes(4),  # 0x0 - ELF magic number
    "ei_class" / cs.Int8ub,  # 0x4 - File class (32/64 bit)
    "ei_data" / cs.Int8ub,  # 0x5 - Data encoding
    "ei_version" / cs.Int8ul,  # 0x6 - File version
    "ei_osabi" / cs.Int8ul,  # 0x7 - OS/ABI identification
    "ei_abiversion" / cs.Int8ul,  # 0x8 - ABI version
    "ei_pad" / cs.Padding(7),  # 0x9 - Padding bytes
    "e_type" / cs.Int16ul,  # 0x10 - Object file type
    "e_machine" / cs.Int16ul,  # 0x12 - Machine type
    "e_version" / cs.Int32ul,  # 0x14 - Object file version
    "e_entry" / cs.Int32ul,  # 0x18 - Entry point address
    "e_phoff" / cs.Int32ul,  # 0x1C - Program header offset
    "e_shoff" / cs.Int32ul,  # 0x20 - Section header offset
    "e_flags" / cs.Int32ul,  # 0x24 - Processor-specific flags
    "e_ehsize" / cs.Int16ul,  # 0x28 - ELF header size
    "e_phentsize" / cs.Int16ul,  # 0x2A - Program header entry size
    "e_phnum" / cs.Int16ul,  # 0x2C - Number of program header entries
    "e_shentsize" / cs.Int16ul,  # 0x2E - Section header entry size
    "e_shnum" / cs.Int16ul,  # 0x30 - Number of section header entries
    "e_shstrndx" / cs.Int16ul,  # 0x32 - Section name string table index
)

# Section Header Structures
elf64Section = cs.Struct(
    "sh_name" / cs.Int32ul,  # Section name (string table index)
    "sh_type" / cs.Int32ul,  # Section type
    "sh_flags" / cs.Int64ul,  # Section flags
    "sh_addr" / cs.Int64ul,  # Virtual address in memory
    "sh_offset" / cs.Int64ul,  # Offset in file
    "sh_size" / cs.Int64ul,  # Size of section
    "sh_link" / cs.Int32ul,  # Link to another section
    "sh_info" / cs.Int32ul,  # Additional section information
    "sh_addralign" / cs.Int64ul,  # Section alignment
    "sh_entsize" / cs.Int64ul,  # Entry size if section holds table
)

elf32Section = cs.Struct(
    "sh_name" / cs.Int32ul,  # Section name (string table index)
    "sh_type" / cs.Int32ul,  # Section type
    "sh_flags" / cs.Int32ul,  # Section flags
    "sh_addr" / cs.Int32ul,  # Virtual address in memory
    "sh_offset" / cs.Int32ul,  # Offset in file
    "sh_size" / cs.Int32ul,  # Size of section
    "sh_link" / cs.Int32ul,  # Link to another section
    "sh_info" / cs.Int32ul,  # Additional section information
    "sh_addralign" / cs.Int32ul,  # Section alignment
    "sh_entsize" / cs.Int32ul,  # Entry size if section holds table
)

# Symbol Table Structures
elf64Sym = cs.Struct(
    "name" / cs.Int32ul,  # Symbol name (string table index)
    "info" / cs.Int8ul,  # Symbol type and binding
    "other" / cs.Int8ul,  # Symbol visibility
    "shndx" / cs.Int16ul,  # Section index
    "value" / cs.Int64ul,  # Symbol value
    "size" / cs.Int64ul,  # Symbol size
)

elf32Sym = cs.Struct(
    "name" / cs.Int32ul,  # Symbol name (string table index)
    "value" / cs.Int32ul,  # Symbol value
    "size" / cs.Int32ul,  # Symbol size
    "info" / cs.Int8ul,  # Symbol type and binding
    "other" / cs.Int8ul,  # Symbol visibility
    "shndx" / cs.Int16ul,  # Section index
)

# ELF Class Constants
EI_CLASS32: int = 1  # 32-bit objects
EI_CLASS64: int = 2  # 64-bit objects

# ELF Type Constants
ET_NONE: int = 0  # No file type
ET_REL: int = 1  # Relocatable file
ET_EXEC: int = 2  # Executable file
ET_DYN: int = 3  # Shared object file

# Machine Type Constants
EM_X86: int = 0x03  # Intel 80386
EM_MIPS: int = 0x08  # MIPS
EM_PPC: int = 0x14  # PowerPC
EM_PPC64: int = 0x15  # PowerPC 64-bit
EM_ARM: int = 0x28  # ARM
EM_AMD64: int = 0x3E  # AMD x86-64

# Section Type Constants
SHT_NULL: int = 0x0  # Section header table entry unused
SHT_PROGBITS: int = 0x1  # Program data
SHT_SYMTAB: int = 0x2  # Symbol table
SHT_STRTAB: int = 0x3  # String table
SHT_RELA: int = 0x4  # Relocation entries with addends
SHT_HASH: int = 0x5  # Symbol hash table
SHT_DYNAMIC: int = 0x6  # Dynamic linking information
SHT_NOTE: int = 0x7  # Notes
SHT_NOBITS: int = 0x8  # Program space with no data (bss)
SHT_REL: int = 0x9  # Relocation entries, no addends
SHT_SHLIB: int = 0x0A  # Reserved
SHT_DYNSYM: int = 0x0B  # Dynamic linker symbol table

# Section Flag Constants
SHF_WRITE: int = 0x1  # Writable
SHF_ALLOC: int = 0x2  # Occupies memory during execution
SHF_EXECINSTR: int = 0x4  # Executable
SHF_MERGE: int = 0x10  # Might be merged
SHF_STRINGS: int = 0x20  # Contains null-terminated strings
SHF_INFO_LINK: int = 0x40  # 'sh_info' contains SHT index
SHF_LINK_ORDER: int = 0x80  # Preserve order after combining
SHF_OS_NONCONFORMING: int = 0x100  # Non-standard OS specific handling
SHF_GROUP: int = 0x200  # Section is member of a group
SHF_TLS: int = 0x400  # Section hold thread-local data
SHF_MASKOS: int = 0x0FF00000  # OS-specific
SHF_MASKPROC: int = 0xF0000000  # Processor-specific
SHF_ORDERED: int = 0x4000000  # Special ordering requirement
SHF_EXCLUDE: int = 0x8000000  # Section is excluded

# Section alignment constant
SECTION_ALIGNMENT: int = 1


class Elf:
    """
    ELF binary builder class.

    This class provides a high-level interface for constructing ELF binaries.
    It supports both 32-bit and 64-bit formats and various architectures.

    Attributes:
        e_entry: Entry point address of the ELF binary
        e_machine: Target machine architecture
        ei_class: ELF class (32-bit or 64-bit)
        sections: List of section information dictionaries
        sections_ranges: Mapping of address ranges to section indices
    """

    def __init__(self, e_entry: int, e_machine: int = EM_AMD64) -> None:
        """
        Initialize an ELF builder instance.

        Args:
            e_entry: Entry point address for the ELF binary
            e_machine: Machine architecture constant (default: EM_AMD64)
        """
        self.e_entry: int = e_entry
        self.e_machine: int = e_machine
        self.sections: List[Dict[str, Union[int, bytes]]] = []
        self.sections_ranges: Dict[Tuple[int, int], int] = {}

        # Determine ELF class based on architecture
        if self.e_machine in [EM_AMD64, EM_PPC64]:
            self.ei_class: int = EI_CLASS64
            self.elf_header_size: int = elf64Header.sizeof()
        else:
            self.ei_class: int = EI_CLASS32
            self.elf_header_size: int = elf32Header.sizeof()

        self.current_file_offset: int = self.elf_header_size

        # Section content buffers
        self.section_header_content: bytes = b""
        self.sections_content: bytes = b""

        # String table for section names
        self.shstrtab_content: bytes = b""

        # Dynamic string table
        self.dynstrtab_content: bytes = b""

        # Dynamic symbol table
        self.dynsym_content: bytes = b""

        # Add null section (required as first section)
        self.add_section("null", self.add_section_name(""), b"", 0x0, SHT_NULL, 0)

    def add_section_name(self, name: str) -> int:
        """
        Add a section name to the section header string table.

        Args:
            name: Name of the section

        Returns:
            Offset of the name in the string table
        """
        nameFormat = cs.CString("utf8")

        # Add name to shstrtab and get offset
        offset: int = len(self.shstrtab_content)
        self.shstrtab_content += nameFormat.build(name)

        return offset

    def add_section(
        self,
        name: str,
        name_offset: int,
        data: bytes,
        addr: int,
        sh_type: int,
        sh_flags: int,
        sh_link: int = 0,
        sh_entsize: int = 0,
    ) -> None:
        """
        Add a section to the ELF binary.

        Args:
            name: Section name (for internal tracking)
            name_offset: Offset of the name in the string table
            data: Section data content
            addr: Virtual address where section should be loaded
            sh_type: Section type constant (SHT_*)
            sh_flags: Section flags (SHF_*)
            sh_link: Link to another section (default: 0)
            sh_entsize: Entry size if section holds a table (default: 0)
        """
        sectionInfo: Dict[str, Union[int, bytes]] = {}

        # Calculate padding for alignment
        if len(data) == 0:
            sectionInfo["padding"] = 0
        else:
            if len(data) % SECTION_ALIGNMENT == 0:
                sectionInfo["padding"] = 0
            else:
                sectionInfo["padding"] = SECTION_ALIGNMENT - len(data) % SECTION_ALIGNMENT

        # Build section header information
        sectionInfo["sh_name"] = name_offset
        sectionInfo["sh_type"] = sh_type
        sectionInfo["sh_flags"] = sh_flags
        sectionInfo["sh_addr"] = addr
        sectionInfo["sh_offset"] = self.current_file_offset
        sectionInfo["sh_size"] = len(data) + sectionInfo["padding"]
        sectionInfo["sh_link"] = sh_link
        sectionInfo["sh_info"] = 0
        sectionInfo["sh_addralign"] = SECTION_ALIGNMENT
        sectionInfo["sh_entsize"] = sh_entsize

        # Track section address range
        self.sections_ranges[(addr, addr + len(data))] = len(self.sections)
        self.sections.append(sectionInfo)

        # Add section content with padding
        self.sections_content += data
        self.sections_content += b"\0" * sectionInfo["padding"]
        self.current_file_offset += len(data) + sectionInfo["padding"]

        # Build section header
        if self.ei_class == EI_CLASS64:
            self.section_header_content += elf64Section.build(sectionInfo)
        else:
            self.section_header_content += elf32Section.build(sectionInfo)

    def add_progbits_section(self, name: str, data: bytes, addr: int) -> None:
        """
        Add a PROGBITS section (typically for executable code).

        Args:
            name: Section name
            data: Section content (machine code)
            addr: Virtual address where section should be loaded
        """
        self.add_section(name, self.add_section_name(name), data, addr, SHT_PROGBITS, SHF_ALLOC | SHF_EXECINSTR)

    def add_data_section(self, name: str, data: bytes, addr: int) -> None:
        """
        Add a data section (for initialized data).

        Args:
            name: Section name
            data: Section content
            addr: Virtual address where section should be loaded
        """
        self.add_section(name, self.add_section_name(name), data, addr, SHT_PROGBITS, SHF_ALLOC)

    def add_shstrtab_section(self) -> None:
        """
        Add the section header string table section.

        This section contains the names of all sections in the ELF file.
        """
        name_offset: int = self.add_section_name(".shstrtab")
        self.add_section(".shstrtab", name_offset, self.shstrtab_content, 0, SHT_STRTAB, 0)

    def add_dynsym_section(self) -> None:
        """
        Add the dynamic symbol table section.

        This section contains information about exported symbols.
        """
        if self.ei_class == EI_CLASS64:
            entsize: int = elf64Sym.sizeof()
        else:
            entsize: int = elf32Sym.sizeof()

        self.add_section(
            ".dynsym",
            self.add_section_name(".dynsym"),
            self.dynsym_content,
            0,
            SHT_DYNSYM,
            0,
            sh_link=len(self.sections) + 1,
            sh_entsize=entsize,
        )

    def add_dynstr_section(self) -> None:
        """
        Add the dynamic string table section.

        This section contains the names of exported symbols.
        """
        self.add_section(".dynstr", self.add_section_name(".dynstr"), self.dynstrtab_content, 0, SHT_STRTAB, 0)

    def build_sections_header(self) -> None:
        """
        Build all required section headers.

        This includes dynamic symbol table, dynamic string table,
        and section header string table.
        """
        self.add_dynsym_section()
        self.add_dynstr_section()
        self.add_shstrtab_section()

    def add_exported_name(self, name: str) -> int:
        """
        Add an exported symbol name to the dynamic string table.

        Args:
            name: Symbol name to export

        Returns:
            Offset of the name in the dynamic string table
        """
        nameFormat = cs.CString("utf8")

        # Add name to dynstrtab
        offset: int = len(self.dynstrtab_content)
        self.dynstrtab_content += nameFormat.build(name)

        return offset

    def add_exported_symbol(self, name: str, addr: int) -> None:
        """
        Add an exported symbol to the ELF binary.

        The symbol must be located within an existing section.

        Args:
            name: Name of the symbol to export
            addr: Address of the symbol
        """
        # Find which section contains this address
        shndx: int = -1
        for (start_addr, end_addr), index in self.sections_ranges.items():
            if start_addr <= addr < end_addr:
                shndx = index
                break

        if shndx == -1:
            # Address not in any section, skip
            return

        # Build symbol information
        symbol: Dict[str, int] = {}
        symbol["name"] = self.add_exported_name(name)
        symbol["info"] = 0x12  # STT_FUNC / GLOBAL
        symbol["other"] = 0
        symbol["shndx"] = shndx
        symbol["value"] = addr
        symbol["size"] = 0

        # Add symbol to dynamic symbol table
        if self.ei_class == EI_CLASS64:
            self.dynsym_content += elf64Sym.build(symbol)
        else:
            self.dynsym_content += elf32Sym.build(symbol)

    def build(self) -> bytes:
        """
        Build the complete ELF binary.

        This method assembles all sections and headers into a complete
        ELF file that can be written to disk or loaded into memory.

        Returns:
            Complete ELF binary as bytes
        """
        # Build all section headers
        self.build_sections_header()

        # Prepare ELF header information
        elfHeaderInfo: Dict[str, Union[bytes, int]] = {
            "ei_mag": b"\x7fELF",
            "ei_class": self.ei_class,
            "ei_data": 1,  # Little-endian
            "ei_version": 1,
            "ei_osabi": 0,
            "ei_abiversion": 0,
            "e_type": ET_DYN,
            "e_version": 1,
            "e_ehsize": self.elf_header_size,
            "e_phentsize": 0,  # No program headers
            "e_phnum": 0,  # No program headers
            "e_entry": self.e_entry,
            "e_machine": self.e_machine,
            "e_flags": 0,
            "e_phoff": 0x0,  # No program headers
            "e_shoff": self.elf_header_size + len(self.sections_content),
            "e_shnum": len(self.sections),
            "e_shstrndx": len(self.sections) - 1,  # Last section is shstrtab
        }

        # Set section header entry size based on ELF class
        if self.ei_class == EI_CLASS64:
            elfHeaderInfo["e_shentsize"] = elf64Section.sizeof()
            elf_header: bytes = elf64Header.build(elfHeaderInfo)
        else:
            elfHeaderInfo["e_shentsize"] = elf32Section.sizeof()
            elf_header: bytes = elf32Header.build(elfHeaderInfo)

        # Assemble complete ELF file
        elf: bytes = elf_header + self.sections_content + self.section_header_content
        return elf
