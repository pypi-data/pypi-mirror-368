"""
Unit tests for the ELF builder module
"""

import struct
from pathlib import Path
from gaudit.elfbuilder import (
    EI_CLASS32,
    EI_CLASS64,
    EM_AMD64,
    EM_ARM,
    EM_MIPS,
    EM_PPC,
    EM_PPC64,
    EM_X86,
    ET_DYN,
    ET_EXEC,
    ET_NONE,
    ET_REL,
    Elf,
    SHF_ALLOC,
    SHF_EXECINSTR,
    SHF_GROUP,
    SHF_INFO_LINK,
    SHF_LINK_ORDER,
    SHF_MERGE,
    SHF_OS_NONCONFORMING,
    SHF_STRINGS,
    SHF_TLS,
    SHF_WRITE,
    SHT_DYNAMIC,
    SHT_DYNSYM,
    SHT_HASH,
    SHT_NOBITS,
    SHT_NOTE,
    SHT_NULL,
    SHT_PROGBITS,
    SHT_REL,
    SHT_RELA,
    SHT_SHLIB,
    SHT_STRTAB,
    SHT_SYMTAB,
    elf32Header,
    elf32Section,
    elf32Sym,
    elf64Header,
    elf64Section,
    elf64Sym,
)


class TestElfBuilder:
    """Test the Elf class and its methods"""

    def test_init_64bit(self):
        """Test 64-bit ELF initialization"""
        elf = Elf(e_entry=0x400000, e_machine=EM_AMD64)

        assert elf.e_entry == 0x400000
        assert elf.e_machine == EM_AMD64
        assert elf.ei_class == EI_CLASS64
        assert elf.elf_header_size == elf64Header.sizeof()
        assert len(elf.sections) == 1  # null section
        assert elf.sections[0]["sh_type"] == SHT_NULL

    def test_init_32bit(self):
        """Test 32-bit ELF initialization"""
        elf = Elf(e_entry=0x08048000, e_machine=EM_X86)

        assert elf.e_entry == 0x08048000
        assert elf.e_machine == EM_X86
        assert elf.ei_class == EI_CLASS32
        assert elf.elf_header_size == elf32Header.sizeof()
        assert len(elf.sections) == 1  # null section

    def test_add_section_name(self):
        """Test adding section names to string table"""
        elf = Elf(e_entry=0x400000)

        offset1 = elf.add_section_name(".text")
        offset2 = elf.add_section_name(".data")
        offset3 = elf.add_section_name(".bss")

        assert offset1 == 1
        assert offset2 == 7  # ".text\0" = 6 bytes
        assert offset3 == 13  # ".text\0.data\0" = 12 bytes
        assert b".text\0.data\0.bss\0" in elf.shstrtab_content

    def test_add_progbits_section(self):
        """Test adding a PROGBITS section"""
        elf = Elf(e_entry=0x400000)

        code = b"\x90\x90\x90\x90"  # NOP instructions
        elf.add_progbits_section(".text", code, 0x400000)

        assert len(elf.sections) == 2  # null + .text
        text_section = elf.sections[1]
        assert text_section["sh_type"] == SHT_PROGBITS
        assert text_section["sh_flags"] == (SHF_ALLOC | SHF_EXECINSTR)
        assert text_section["sh_addr"] == 0x400000
        assert text_section["sh_size"] == len(code)

    def test_add_data_section(self):
        """Test adding a data section"""
        elf = Elf(e_entry=0x400000)

        data = b"Hello, World!\0"
        elf.add_data_section(".data", data, 0x600000)

        assert len(elf.sections) == 2  # null + .data
        data_section = elf.sections[1]
        assert data_section["sh_type"] == SHT_PROGBITS
        assert data_section["sh_flags"] == SHF_ALLOC
        assert data_section["sh_addr"] == 0x600000
        assert data_section["sh_size"] == len(data)

    def test_add_exported_symbol(self):
        """Test adding exported symbols"""
        elf = Elf(e_entry=0x400000)

        # Add a code section first
        code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        elf.add_progbits_section(".text", code, 0x400000)

        # Add symbol within the section
        elf.add_exported_symbol("my_function", 0x400000)

        # Symbol should be added to dynsym
        assert len(elf.dynsym_content) > 0
        assert b"my_function\0" in elf.dynstrtab_content

    def test_add_exported_symbol_outside_section(self):
        """Test that symbols outside sections are not added"""
        elf = Elf(e_entry=0x400000)

        # Add a code section
        code = b"\x90\x90\x90\x90"
        elf.add_progbits_section(".text", code, 0x400000)

        # Try to add symbol outside the section range
        elf.add_exported_symbol("bad_symbol", 0x500000)

        # Symbol should not be added
        assert len(elf.dynsym_content) == 0
        assert b"bad_symbol" not in elf.dynstrtab_content

    def test_build_64bit_elf(self):
        """Test building a complete 64-bit ELF"""
        elf = Elf(e_entry=0x401000, e_machine=EM_AMD64)

        # Add some sections
        code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        data = b"Hello\0"

        elf.add_progbits_section(".text", code, 0x401000)
        elf.add_data_section(".data", data, 0x402000)
        elf.add_exported_symbol("main", 0x401000)

        # Build the ELF
        elf_bytes = elf.build()

        # Verify ELF magic
        assert elf_bytes[:4] == b"\x7fELF"

        # Verify it's 64-bit
        assert elf_bytes[4] == EI_CLASS64

        # Verify machine type
        assert struct.unpack_from("<H", elf_bytes, 0x12)[0] == EM_AMD64

        # Verify entry point
        assert struct.unpack_from("<Q", elf_bytes, 0x18)[0] == 0x401000

    def test_build_32bit_elf(self):
        """Test building a complete 32-bit ELF"""
        elf = Elf(e_entry=0x08048000, e_machine=EM_X86)

        # Add some sections
        code = b"\x31\xc0\xc3"  # xor eax, eax; ret
        data = b"Test\0"

        elf.add_progbits_section(".text", code, 0x08048000)
        elf.add_data_section(".data", data, 0x08049000)

        # Build the ELF
        elf_bytes = elf.build()

        # Verify ELF magic
        assert elf_bytes[:4] == b"\x7fELF"

        # Verify it's 32-bit
        assert elf_bytes[4] == EI_CLASS32

        # Verify machine type
        assert struct.unpack_from("<H", elf_bytes, 0x12)[0] == EM_X86

        # Verify entry point
        assert struct.unpack_from("<I", elf_bytes, 0x18)[0] == 0x08048000

    def test_multiple_sections(self):
        """Test adding multiple sections"""
        elf = Elf(e_entry=0x400000)

        elf.add_progbits_section(".text", b"\x90" * 100, 0x400000)
        elf.add_data_section(".data", b"A" * 50, 0x600000)
        elf.add_data_section(".rodata", b"B" * 25, 0x700000)

        # Build and verify
        elf_bytes = elf.build()

        # Should have null + 3 user sections + dynsym + dynstr + shstrtab = 7 sections
        assert elf.sections[0]["sh_type"] == SHT_NULL

        # Verify section count in header (after building)
        # For 64-bit ELF, e_shnum is at offset 0x3C
        section_count = struct.unpack_from("<H", elf_bytes, 0x3C)[0]
        assert section_count == 7

    def test_multiple_exported_symbols(self):
        """Test adding multiple exported symbols"""
        elf = Elf(e_entry=0x400000)

        # Add a larger code section
        code = b"\x90" * 100
        elf.add_progbits_section(".text", code, 0x400000)

        # Add multiple symbols at different offsets
        elf.add_exported_symbol("func1", 0x400000)
        elf.add_exported_symbol("func2", 0x400010)
        elf.add_exported_symbol("func3", 0x400020)

        # Build the ELF
        elf.build()

        # Verify all symbols are in the string table
        assert b"func1\0" in elf.dynstrtab_content
        assert b"func2\0" in elf.dynstrtab_content
        assert b"func3\0" in elf.dynstrtab_content

        # Verify dynsym has entries (3 symbols * symbol size)
        if elf.ei_class == EI_CLASS64:
            assert len(elf.dynsym_content) == 3 * elf64Sym.sizeof()
        else:
            assert len(elf.dynsym_content) == 3 * elf32Sym.sizeof()

    def test_section_alignment_padding(self):
        """Test that sections are properly padded for alignment"""
        elf = Elf(e_entry=0x400000)

        # Add sections with various sizes to test padding
        elf.add_data_section(".data1", b"A", 0x400000)  # 1 byte
        elf.add_data_section(".data2", b"BB", 0x401000)  # 2 bytes
        elf.add_data_section(".data3", b"CCC", 0x402000)  # 3 bytes
        elf.add_data_section(".data4", b"DDDD", 0x403000)  # 4 bytes

        # All sections should have proper padding info
        for i in range(1, 5):
            section = elf.sections[i]
            original_size = i  # Original data size
            total_size = section["sh_size"]
            padding = section["padding"]

            # Verify padding calculation
            if original_size % 1 == 0:  # SECTION_ALIGNMENT = 1
                assert padding == 0
            assert total_size == original_size + padding

    def test_different_architectures(self):
        """Test creating ELFs for different architectures"""
        architectures = [
            (EM_AMD64, EI_CLASS64, 0x400000),
            (EM_X86, EI_CLASS32, 0x08048000),
            (EM_ARM, EI_CLASS32, 0x00010000),
            (EM_PPC, EI_CLASS32, 0x10000000),
            (EM_PPC64, EI_CLASS64, 0x10000000),
            (EM_MIPS, EI_CLASS32, 0x00400000),
        ]

        for machine, expected_class, entry in architectures:
            elf = Elf(e_entry=entry, e_machine=machine)

            assert elf.e_machine == machine
            assert elf.ei_class == expected_class

            # Add a simple section
            elf.add_progbits_section(".text", b"\x00\x00\x00\x00", entry)

            # Build and verify
            elf_bytes = elf.build()
            assert elf_bytes[:4] == b"\x7fELF"
            assert elf_bytes[4] == expected_class

    def test_empty_sections(self):
        """Test handling of empty sections"""
        elf = Elf(e_entry=0x400000)

        # Add an empty section
        elf.add_progbits_section(".empty", b"", 0x400000)

        # Section should still be added
        assert len(elf.sections) == 2
        empty_section = elf.sections[1]
        assert empty_section["sh_size"] == 0
        assert empty_section["padding"] == 0

    def test_build_shstrtab_section(self):
        """Test that shstrtab section is properly built"""
        elf = Elf(e_entry=0x400000)

        # Add sections with names
        elf.add_progbits_section(".text", b"\x90", 0x400000)
        elf.add_data_section(".data", b"test", 0x600000)

        # Build the ELF
        elf.build()

        # Verify shstrtab contains all section names
        assert b".text\0" in elf.shstrtab_content
        assert b".data\0" in elf.shstrtab_content
        assert b".shstrtab\0" in elf.shstrtab_content
        assert b".dynsym\0" in elf.shstrtab_content
        assert b".dynstr\0" in elf.shstrtab_content

    def test_elf_file_output(self, tmp_path):
        """Test writing ELF to file and basic validation"""
        elf = Elf(e_entry=0x401000, e_machine=EM_AMD64)

        # Create a simple executable
        # mov eax, 60  ; sys_exit
        # xor edi, edi ; exit code 0
        # syscall
        code = b"\xb8\x3c\x00\x00\x00\x31\xff\x0f\x05"

        elf.add_progbits_section(".text", code, 0x401000)
        elf.add_exported_symbol("_start", 0x401000)

        # Build and save
        elf_bytes = elf.build()

        output_file = tmp_path / "test.elf"
        output_file.write_bytes(elf_bytes)

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size == len(elf_bytes)

        # Read back and verify
        read_bytes = output_file.read_bytes()
        assert read_bytes == elf_bytes
        assert read_bytes[:4] == b"\x7fELF"

    def test_elf_type_setting(self):
        """Test that ELF type is correctly set"""
        elf = Elf(e_entry=0x400000)

        # Build and check type
        elf_bytes = elf.build()

        # e_type is at offset 0x10 (16)
        e_type = struct.unpack_from("<H", elf_bytes, 0x10)[0]
        assert e_type == ET_DYN  # Default is ET_DYN

    def test_section_ranges_tracking(self):
        """Test that section ranges are properly tracked"""
        elf = Elf(e_entry=0x400000)

        # Add sections at different addresses
        elf.add_progbits_section(".text", b"\x90" * 100, 0x400000)
        elf.add_data_section(".data", b"A" * 50, 0x600000)

        # Check ranges
        assert (0x400000, 0x400064) in elf.sections_ranges  # 100 bytes
        assert (0x600000, 0x600032) in elf.sections_ranges  # 50 bytes

        # Check index mapping
        assert elf.sections_ranges[(0x400000, 0x400064)] == 1  # .text is section 1
        assert elf.sections_ranges[(0x600000, 0x600032)] == 2  # .data is section 2

    def test_complex_elf_structure(self):
        """Test building a more complex ELF with multiple sections and symbols"""
        elf = Elf(e_entry=0x401000, e_machine=EM_AMD64)

        # Add multiple sections
        text_code = b"\x55\x48\x89\xe5"  # push rbp; mov rbp, rsp
        init_code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        fini_code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        rodata = b"Hello, World!\0Version 1.0\0"
        data = b"\x00" * 16  # 16 bytes of zeros
        bss_placeholder = b""  # BSS is typically empty in file

        elf.add_progbits_section(".text", text_code, 0x401000)
        elf.add_progbits_section(".init", init_code, 0x400000)
        elf.add_progbits_section(".fini", fini_code, 0x402000)
        elf.add_data_section(".rodata", rodata, 0x403000)
        elf.add_data_section(".data", data, 0x604000)
        elf.add_section(
            ".bss", elf.add_section_name(".bss"), bss_placeholder, 0x605000, SHT_NOBITS, SHF_ALLOC | SHF_WRITE
        )

        # Add multiple symbols
        elf.add_exported_symbol("_start", 0x401000)
        elf.add_exported_symbol("_init", 0x400000)
        elf.add_exported_symbol("_fini", 0x402000)

        # Build the complex ELF
        elf_bytes = elf.build()

        # Verify basic structure
        assert elf_bytes[:4] == b"\x7fELF"
        assert len(elf_bytes) > 200  # Should be reasonably sized

        # Verify all section names are in shstrtab
        for section_name in [".text", ".init", ".fini", ".rodata", ".data", ".bss"]:
            assert section_name.encode() + b"\0" in elf.shstrtab_content

        # Verify all symbols are in dynstr
        for symbol_name in ["_start", "_init", "_fini"]:
            assert symbol_name.encode() + b"\0" in elf.dynstrtab_content

    def test_simple_elf(self):
        elf = Elf(e_entry=0x401000, e_machine=EM_AMD64)

        # Add multiple sections
        text_code = b"\x55\x48\x89\xe5"  # push rbp; mov rbp, rsp
        init_code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        fini_code = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret
        rodata = b"Hello, World!\0Version 1.0\0"
        data = b"\x00" * 16  # 16 bytes of zeros
        bss_placeholder = b""  # BSS is typically empty in file

        elf.add_progbits_section(".text", text_code, 0x401000)
        elf.add_progbits_section(".init", init_code, 0x400000)
        elf.add_progbits_section(".fini", fini_code, 0x402000)
        elf.add_data_section(".rodata", rodata, 0x403000)
        elf.add_data_section(".data", data, 0x604000)
        elf.add_section(
            ".bss", elf.add_section_name(".bss"), bss_placeholder, 0x605000, SHT_NOBITS, SHF_ALLOC | SHF_WRITE
        )

        # Add multiple symbols
        elf.add_exported_symbol("_start", 0x401000)
        elf.add_exported_symbol("_init", 0x400000)
        elf.add_exported_symbol("_fini", 0x402000)

        # Build the complex ELF
        elf_bytes = elf.build()

        # Verify build

        p = Path(__file__).with_name("simple.elf")
        with p.open("rb") as f:
            expected = f.read()
            assert elf_bytes == expected


class TestElfHeaders:
    """Test the construct-based header structures"""

    def test_elf64_header_size(self):
        """Test that 64-bit header has correct size"""
        assert elf64Header.sizeof() == 64

    def test_elf32_header_size(self):
        """Test that 32-bit header has correct size"""
        assert elf32Header.sizeof() == 52

    def test_elf64_section_size(self):
        """Test that 64-bit section header has correct size"""
        assert elf64Section.sizeof() == 64

    def test_elf32_section_size(self):
        """Test that 32-bit section header has correct size"""
        assert elf32Section.sizeof() == 40

    def test_elf64_sym_size(self):
        """Test that 64-bit symbol has correct size"""
        assert elf64Sym.sizeof() == 24

    def test_elf32_sym_size(self):
        """Test that 32-bit symbol has correct size"""
        assert elf32Sym.sizeof() == 16

    def test_build_parse_elf64_header(self):
        """Test building and parsing 64-bit ELF header"""
        header_data = {
            "ei_mag": b"\x7fELF",
            "ei_class": EI_CLASS64,
            "ei_data": 1,
            "ei_version": 1,
            "ei_osabi": 0,
            "ei_abiversion": 0,
            "e_type": ET_EXEC,
            "e_machine": EM_AMD64,
            "e_version": 1,
            "e_entry": 0x400000,
            "e_phoff": 0x40,
            "e_shoff": 0x1000,
            "e_flags": 0,
            "e_ehsize": 64,
            "e_phentsize": 56,
            "e_phnum": 2,
            "e_shentsize": 64,
            "e_shnum": 10,
            "e_shstrndx": 9,
        }

        # Build the header
        built = elf64Header.build(header_data)
        assert len(built) == 64
        assert built[:4] == b"\x7fELF"

        # Parse it back
        parsed = elf64Header.parse(built)
        assert parsed.ei_mag == b"\x7fELF"
        assert parsed.e_entry == 0x400000
        assert parsed.e_machine == EM_AMD64

    def test_build_parse_elf32_header(self):
        """Test building and parsing 32-bit ELF header"""
        header_data = {
            "ei_mag": b"\x7fELF",
            "ei_class": EI_CLASS32,
            "ei_data": 1,
            "ei_version": 1,
            "ei_osabi": 0,
            "ei_abiversion": 0,
            "e_type": ET_EXEC,
            "e_machine": EM_X86,
            "e_version": 1,
            "e_entry": 0x08048000,
            "e_phoff": 0x34,
            "e_shoff": 0x1000,
            "e_flags": 0,
            "e_ehsize": 52,
            "e_phentsize": 32,
            "e_phnum": 2,
            "e_shentsize": 40,
            "e_shnum": 10,
            "e_shstrndx": 9,
        }

        # Build the header
        built = elf32Header.build(header_data)
        assert len(built) == 52
        assert built[:4] == b"\x7fELF"

        # Parse it back
        parsed = elf32Header.parse(built)
        assert parsed.ei_mag == b"\x7fELF"
        assert parsed.e_entry == 0x08048000
        assert parsed.e_machine == EM_X86


class TestConstants:
    """Test that ELF constants are properly defined"""

    def test_ei_class_constants(self):
        """Test EI_CLASS constants"""
        assert EI_CLASS32 == 1
        assert EI_CLASS64 == 2

    def test_elf_type_constants(self):
        """Test ELF type constants"""
        assert ET_NONE == 0
        assert ET_REL == 1
        assert ET_EXEC == 2
        assert ET_DYN == 3

    def test_machine_constants(self):
        """Test machine type constants"""
        assert EM_X86 == 0x03
        assert EM_MIPS == 0x08
        assert EM_PPC == 0x14
        assert EM_PPC64 == 0x15
        assert EM_ARM == 0x28
        assert EM_AMD64 == 0x3E

    def test_section_type_constants(self):
        """Test section type constants"""
        assert SHT_NULL == 0x0
        assert SHT_PROGBITS == 0x1
        assert SHT_SYMTAB == 0x2
        assert SHT_STRTAB == 0x3
        assert SHT_RELA == 0x4
        assert SHT_HASH == 0x5
        assert SHT_DYNAMIC == 0x6
        assert SHT_NOTE == 0x7
        assert SHT_NOBITS == 0x8
        assert SHT_REL == 0x9
        assert SHT_SHLIB == 0x0A
        assert SHT_DYNSYM == 0x0B

    def test_section_flag_constants(self):
        """Test section flag constants"""
        assert SHF_WRITE == 0x1
        assert SHF_ALLOC == 0x2
        assert SHF_EXECINSTR == 0x4
        assert SHF_MERGE == 0x10
        assert SHF_STRINGS == 0x20
        assert SHF_INFO_LINK == 0x40
        assert SHF_LINK_ORDER == 0x80
        assert SHF_OS_NONCONFORMING == 0x100
        assert SHF_GROUP == 0x200
        assert SHF_TLS == 0x400
