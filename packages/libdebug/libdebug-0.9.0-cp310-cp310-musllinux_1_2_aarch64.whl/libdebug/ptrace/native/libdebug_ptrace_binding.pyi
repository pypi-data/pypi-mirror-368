from collections.abc import Sequence


class PtraceRegsStruct:
    @property
    def x0(self) -> int: ...

    @x0.setter
    def x0(self, arg: int, /) -> None: ...

    @property
    def x1(self) -> int: ...

    @x1.setter
    def x1(self, arg: int, /) -> None: ...

    @property
    def x2(self) -> int: ...

    @x2.setter
    def x2(self, arg: int, /) -> None: ...

    @property
    def x3(self) -> int: ...

    @x3.setter
    def x3(self, arg: int, /) -> None: ...

    @property
    def x4(self) -> int: ...

    @x4.setter
    def x4(self, arg: int, /) -> None: ...

    @property
    def x5(self) -> int: ...

    @x5.setter
    def x5(self, arg: int, /) -> None: ...

    @property
    def x6(self) -> int: ...

    @x6.setter
    def x6(self, arg: int, /) -> None: ...

    @property
    def x7(self) -> int: ...

    @x7.setter
    def x7(self, arg: int, /) -> None: ...

    @property
    def x8(self) -> int: ...

    @x8.setter
    def x8(self, arg: int, /) -> None: ...

    @property
    def x9(self) -> int: ...

    @x9.setter
    def x9(self, arg: int, /) -> None: ...

    @property
    def x10(self) -> int: ...

    @x10.setter
    def x10(self, arg: int, /) -> None: ...

    @property
    def x11(self) -> int: ...

    @x11.setter
    def x11(self, arg: int, /) -> None: ...

    @property
    def x12(self) -> int: ...

    @x12.setter
    def x12(self, arg: int, /) -> None: ...

    @property
    def x13(self) -> int: ...

    @x13.setter
    def x13(self, arg: int, /) -> None: ...

    @property
    def x14(self) -> int: ...

    @x14.setter
    def x14(self, arg: int, /) -> None: ...

    @property
    def x15(self) -> int: ...

    @x15.setter
    def x15(self, arg: int, /) -> None: ...

    @property
    def x16(self) -> int: ...

    @x16.setter
    def x16(self, arg: int, /) -> None: ...

    @property
    def x17(self) -> int: ...

    @x17.setter
    def x17(self, arg: int, /) -> None: ...

    @property
    def x18(self) -> int: ...

    @x18.setter
    def x18(self, arg: int, /) -> None: ...

    @property
    def x19(self) -> int: ...

    @x19.setter
    def x19(self, arg: int, /) -> None: ...

    @property
    def x20(self) -> int: ...

    @x20.setter
    def x20(self, arg: int, /) -> None: ...

    @property
    def x21(self) -> int: ...

    @x21.setter
    def x21(self, arg: int, /) -> None: ...

    @property
    def x22(self) -> int: ...

    @x22.setter
    def x22(self, arg: int, /) -> None: ...

    @property
    def x23(self) -> int: ...

    @x23.setter
    def x23(self, arg: int, /) -> None: ...

    @property
    def x24(self) -> int: ...

    @x24.setter
    def x24(self, arg: int, /) -> None: ...

    @property
    def x25(self) -> int: ...

    @x25.setter
    def x25(self, arg: int, /) -> None: ...

    @property
    def x26(self) -> int: ...

    @x26.setter
    def x26(self, arg: int, /) -> None: ...

    @property
    def x27(self) -> int: ...

    @x27.setter
    def x27(self, arg: int, /) -> None: ...

    @property
    def x28(self) -> int: ...

    @x28.setter
    def x28(self, arg: int, /) -> None: ...

    @property
    def x29(self) -> int: ...

    @x29.setter
    def x29(self, arg: int, /) -> None: ...

    @property
    def x30(self) -> int: ...

    @x30.setter
    def x30(self, arg: int, /) -> None: ...

    @property
    def sp(self) -> int: ...

    @sp.setter
    def sp(self, arg: int, /) -> None: ...

    @property
    def pc(self) -> int: ...

    @pc.setter
    def pc(self, arg: int, /) -> None: ...

    @property
    def pstate(self) -> int: ...

    @pstate.setter
    def pstate(self, arg: int, /) -> None: ...

    @property
    def override_syscall_number(self) -> bool: ...

    @override_syscall_number.setter
    def override_syscall_number(self, arg: bool, /) -> None: ...

class PtraceFPRegsStruct:
    @property
    def dirty(self) -> bool: ...

    @dirty.setter
    def dirty(self, arg: bool, /) -> None: ...

    @property
    def fresh(self) -> bool: ...

    @fresh.setter
    def fresh(self, arg: bool, /) -> None: ...

    @property
    def vregs(self) -> list[Reg128]: ...

    @property
    def fpsr(self) -> int: ...

    @fpsr.setter
    def fpsr(self, arg: int, /) -> None: ...

    @property
    def fpcr(self) -> int: ...

    @fpcr.setter
    def fpcr(self, arg: int, /) -> None: ...

class Reg80:
    """An 80-bit register."""

    @property
    def data(self) -> list[int]:
        """The data of the register, as a byte array."""

    @data.setter
    def data(self, arg: Sequence[int], /) -> None: ...

class Reg128:
    """A 128-bit register."""

    @property
    def data(self) -> list[int]:
        """The data of the register, as a byte array."""

    @data.setter
    def data(self, arg: Sequence[int], /) -> None: ...

class Reg256:
    """A 256-bit register."""

    @property
    def data(self) -> list[int]:
        """The data of the register, as a byte array."""

    @data.setter
    def data(self, arg: Sequence[int], /) -> None: ...

class Reg512:
    """A 512-bit register."""

    @property
    def data(self) -> list[int]:
        """The data of the register, as a byte array."""

    @data.setter
    def data(self, arg: Sequence[int], /) -> None: ...

class ThreadStatus:
    """The waitpid result of a specific thread."""

    @property
    def tid(self) -> int:
        """The thread id."""

    @property
    def status(self) -> int:
        """The waitpid result."""

class LibdebugPtraceInterface:
    """The native binding for ptrace on Linux."""

    def __init__(self, fpregs_definition: PtraceFPRegsStructDefinition) -> None:
        """Initializes a new ptrace interface for debugging."""

    def cleanup(self) -> None:
        """Cleans up the instance from any previous state."""

    def register_thread(self, tid: int) -> tuple[PtraceRegsStruct, PtraceFPRegsStruct]:
        """
        Registers a new thread that must be debugged.

        Args:
            tid (int): The thread id to be registered.

        Returns:
            tuple: A tuple containing a reference to the registers, integer and floating point.
        """

    def unregister_thread(self, tid: int) -> None:
        """
        Unregisters a thread that was previously registered.

        Args:
            tid (int): The thread id to be unregistered.
        """

    def attach(self, tid: int) -> int:
        """
        Attaches to a process for debugging.

        Args:
            tid (int): The thread id to be attached to.

        Returns:
            int: The error code of the operation, if any.
        """

    def detach_for_migration(self) -> None:
        """Detaches from the process for migration to another debugger."""

    def reattach_from_migration(self) -> None:
        """Reattaches to the process after migration from another debugger."""

    def detach_and_cont(self) -> None:
        """Detaches from the process and continues its execution."""

    def detach_from_child(self, pid: int, follow_child: bool) -> None:
        """
        Detaches from a specific child process.

        Args:
            pid (int): The process id to detach from.    follow_child (bool): A flag to indicate if the child should be followed.
        """

    def set_ptrace_options(self) -> None:
        """Sets the ptrace options for the process."""

    def get_event_msg(self, tid: int) -> int:
        """
        Gets an event message for a thread.

        Args:
            tid (int): The thread id to get the event message for.

        Returns:
            int: The event message.
        """

    def wait_all_and_update_regs(self, all_zombies: bool) -> list[tuple[int, int]]:
        """
        Waits for any thread to stop, interrupts all the others and updates the registers.

        Args:
            all_zombies (bool): A flag to indicate if all the threads are zombies.

        Returns:
            list: A list of tuples containing the thread id and the corresponding waitpid result.
        """

    def cont_all_and_set_bps(self, handle_syscalls: bool) -> None:
        """
        Sets the breakpoints and continues all the threads.

        Args:
            handle_syscalls (bool): A flag to indicate if the debuggee should stop on syscalls.
        """

    def step(self, tid: int) -> None:
        """
        Steps a thread by one instruction.

        Args:
            tid (int): The thread id to step.
        """

    def step_until(self, tid: int, addr: int, max_steps: int) -> None:
        """
        Steps a thread until a specific address is reached, or for a maximum amount of steps.

        Args:
            tid (int): The thread id to step.
            addr (int): The address to step until.
            max_steps (int): The maximum amount of steps to take, or -1 if unlimited.
        """

    def stepping_finish(self, tid: int, use_trampoline_heuristic: bool) -> None:
        """
        Runs a thread until the end of the current function call, by single-stepping it.

        Args:
            tid (int): The thread id to step.
            use_trampoline_heuristic (bool): A flag to indicate if the trampoline heuristic for i386 should be used.
        """

    def forward_signals(self, signals: Sequence[tuple[int, int]]) -> None:
        """
        Forwards signals to the threads.

        Args:
            signals (list): A list of tuples containing the thread id and the signal to forward.
        """

    def get_remaining_hw_breakpoint_count(self, tid: int) -> int:
        """
        Gets the remaining hardware breakpoint count for a thread.

        Args:
            tid (int): The thread id to get the remaining hardware breakpoint count for.
        """

    def get_remaining_hw_watchpoint_count(self, tid: int) -> int:
        """
        Gets the remaining hardware watchpoint count for a thread.

        Args:
            tid (int): The thread id to get the remaining hardware watchpoint count for.
        """

    def register_hw_breakpoint(self, tid: int, address: int, type: int, len: int) -> None:
        """
        Registers a hardware breakpoint for a thread.

        Args:
            tid (int): The thread id to register the hardware breakpoint for.
            address (int): The address to set the hardware breakpoint at.
            type (int): The type of the hardware breakpoint.
            len (int): The length of the hardware breakpoint.
        """

    def unregister_hw_breakpoint(self, tid: int, address: int) -> None:
        """
        Unregisters a hardware breakpoint for a thread.

        Args:
            tid (int): The thread id to unregister the hardware breakpoint for.
            address (int): The address to remove the hardware breakpoint from.
        """

    def get_hit_hw_breakpoint(self, tid: int) -> int:
        """
        Gets the address of the hardware breakpoint hit by a specific thread, if any.

        Args:
            tid (int): The thread id to get the hit hardware breakpoint for.

        Returns:
            int: The address of the hit hardware breakpoint.
        """

    def register_breakpoint(self, address: int) -> None:
        """
        Registers a software breakpoint at a specific address.

        Args:
            address (int): The address to set the software breakpoint at.
        """

    def unregister_breakpoint(self, address: int) -> None:
        """
        Unregisters a software breakpoint at a specific address.

        Args:
            address (int): The address to remove the software breakpoint from.
        """

    def enable_breakpoint(self, address: int) -> None:
        """
        Enables a previously registered software breakpoint at a specific address.

        Args:
            address (int): The address to enable the software breakpoint at.
        """

    def disable_breakpoint(self, address: int) -> None:
        """
        Disables a previously registered software breakpoint at a specific address.

        Args:
            address (int): The address to disable the software breakpoint at.
        """

    def detach_for_kill(self) -> None:
        """Detaches from the process and kills it."""

    def get_fp_regs(self, tid: int) -> None:
        """
        Refreshes the floating point registers for a thread.

        Args:
            tid (int): The thread id to refresh the floating point registers for.
        """

    def peek_data(self, addr: int) -> int:
        """
        Peeks memory from a specific address.

        Args:
            addr (int): The address to peek memory from.

        Returns:
            int: The memory value at the address.
        """

    def poke_data(self, addr: int, data: int) -> None:
        """
        Pokes memory at a specific address.

        Args:
            addr (int): The address to poke memory at.
            data (int): The data to poke at the address.
        """

class PtraceFPRegsStructDefinition:
    def __init__(self, struct_size: int, avx_ymm0_offset: int, avx512_zmm0_offset: int, avx512_zmm1_offset: int, type: int, has_xsave: bool) -> None:
        """Constructor for PtraceFPRegsStructDefinition."""

    @property
    def struct_size(self) -> int:
        """The size of the fpregs struct."""

    @property
    def avx_ymm0_offset(self) -> int:
        """The offset of the first ymm0 register in the fpregs struct."""

    @property
    def avx512_zmm0_offset(self) -> int:
        """The offset of the first zmm0 register in the fpregs struct."""

    @property
    def avx512_zmm1_offset(self) -> int:
        """The offset of the first zmm1 register in the fpregs struct."""

    @property
    def type(self) -> int:
        """The type of the fpregs struct."""

    @property
    def has_xsave(self) -> bool:
        """Whether the current CPU supports XSAVE."""
