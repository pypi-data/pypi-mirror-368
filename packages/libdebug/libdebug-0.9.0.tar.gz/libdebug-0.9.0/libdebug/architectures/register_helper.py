#
# This file is part of libdebug Python library (https://github.com/libdebug/libdebug).
# Copyright (c) 2023-2024 Roberto Alessandro Bertolini. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for details.
#

from libdebug.architectures.aarch64.aarch64_ptrace_register_holder import (
    Aarch64PtraceRegisterHolder,
)
from libdebug.architectures.amd64.amd64_ptrace_register_holder import (
    Amd64PtraceRegisterHolder,
)
from libdebug.architectures.amd64.compat.i386_over_amd64_ptrace_register_holder import (
    I386OverAMD64PtraceRegisterHolder,
)
from libdebug.architectures.i386.i386_ptrace_register_holder import (
    I386PtraceRegisterHolder,
)
from libdebug.data.register_holder import RegisterHolder
from libdebug.utils.libcontext import libcontext


def register_holder_provider(
    architecture: str,
    register_file: object,
    fp_register_file: object,
) -> RegisterHolder:
    """Returns an instance of the register holder to be used by the `_InternalDebugger` class."""
    match architecture:
        case "amd64":
            return Amd64PtraceRegisterHolder(register_file, fp_register_file)
        case "aarch64":
            return Aarch64PtraceRegisterHolder(register_file, fp_register_file)
        case "i386":
            if libcontext.platform == "amd64":
                return I386OverAMD64PtraceRegisterHolder(register_file, fp_register_file)
            else:
                return I386PtraceRegisterHolder(register_file, fp_register_file)
        case _:
            raise NotImplementedError(f"Architecture {architecture} not available.")
