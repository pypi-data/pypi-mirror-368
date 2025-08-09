import os
os.environ.setdefault("MAX_NUM_THREADS_SESUM", "64")
import ctypes
import numpy as np
import time
import sys
import platform
import signal
import threading


def _windows_handler(dwCtrlType):
    if dwCtrlType == 0:  # CTRL_C_EVENT
        print("\nYou pressed Ctrl+C! Terminating...")
        os._exit(1)
    return 1  # don't call other handlers


def _unix_signal_handler(sig, frame):
    print("\nYou pressed Ctrl+C! Terminating...")
    os._exit(1)


if sys.platform.startswith("win"):
    _HandlerRoutine = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)
    _callback = _HandlerRoutine(_windows_handler)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_callback, 1)
else:  # unix-like systems
    signal.signal(signal.SIGINT, _unix_signal_handler)


# functionality copied from py-cpuinfo
def _get_arch_and_bits():
    arch_string_raw = platform.machine()
    import re

    arch, bits = None, None
    arch_string_raw = arch_string_raw.lower()

    # X86
    if re.match(r'^i\d86$|^x86$|^x86_32$|^i86pc$|^ia32$|^ia-32$|^bepc$', arch_string_raw):
        arch = 'X86_32'
        bits = 32
    elif re.match(r'^x64$|^x86_64$|^x86_64t$|^i686-64$|^amd64$|^ia64$|^ia-64$', arch_string_raw):
        arch = 'X86_64'
        bits = 64
    # ARM
    elif re.match(r'^armv8-a|aarch64|arm64$', arch_string_raw):
        arch = 'ARM_8'
        bits = 64
    elif re.match(r'^armv7$|^armv7[a-z]$|^armv7-[a-z]$|^armv6[a-z]$', arch_string_raw):
        arch = 'ARM_7'
        bits = 32
    elif re.match(r'^armv8$|^armv8[a-z]$|^armv8-[a-z]$', arch_string_raw):
        arch = 'ARM_8'
        bits = 32
    # PPC
    elif re.match(r'^ppc32$|^prep$|^pmac$|^powermac$', arch_string_raw):
        arch = 'PPC_32'
        bits = 32
    elif re.match(r'^powerpc$|^ppc64$|^ppc64le$', arch_string_raw):
        arch = 'PPC_64'
        bits = 64
    # SPARC
    elif re.match(r'^sparc32$|^sparc$', arch_string_raw):
        arch = 'SPARC_32'
        bits = 32
    elif re.match(r'^sparc64$|^sun4u$|^sun4v$', arch_string_raw):
        arch = 'SPARC_64'
        bits = 64
    # S390X
    elif re.match(r'^s390x$', arch_string_raw):
        arch = 'S390X'
        bits = 64
    # MIPS
    elif re.match(r'^mips$', arch_string_raw):
        arch = 'MIPS_32'
        bits = 32
    elif re.match(r'^mips64$', arch_string_raw):
        arch = 'MIPS_64'
        bits = 64
    # RISCV
    elif re.match(r'^riscv$|^riscv32$|^riscv32be$', arch_string_raw):
        arch = 'RISCV_32'
        bits = 32
    elif re.match(r'^riscv64$|^riscv64be$', arch_string_raw):
        arch = 'RISCV_64'
        bits = 64
    # LoongArch
    elif re.match(r'^loongarch32$', arch_string_raw):
        arch = 'LOONG_32'
        bits = 32
    elif re.match(r'^loongarch64$', arch_string_raw):
        arch = 'LOONG_64'
        bits = 64

    return arch, bits


# functionality copied from py-cpuinfo
def _get_flags():
    def _is_bit_set(reg, bit):
        mask = 1 << bit
        is_set = reg & mask > 0
        return is_set

    class DataSource:
        is_windows = platform.system().lower() == 'windows'

    class ASM:
        def __init__(self, restype=None, argtypes=(), machine_code=[]):
            self.restype = restype
            self.argtypes = argtypes
            self.machine_code = machine_code
            self.prochandle = None
            self.mm = None
            self.func = None
            self.address = None
            self.size = 0

        def compile(self):
            machine_code = bytes.join(b'', self.machine_code)
            self.size = ctypes.c_size_t(len(machine_code))

            if DataSource.is_windows:
                # Allocate a memory segment the size of the machine code, and make it executable
                size = len(machine_code)
                # Alloc at least 1 page to ensure we own all pages that we want to change protection on
                if size < 0x1000: size = 0x1000
                MEM_COMMIT = ctypes.c_ulong(0x1000)
                PAGE_READWRITE = ctypes.c_ulong(0x4)
                pfnVirtualAlloc = ctypes.windll.kernel32.VirtualAlloc
                pfnVirtualAlloc.restype = ctypes.c_void_p
                self.address = pfnVirtualAlloc(None, ctypes.c_size_t(size), MEM_COMMIT, PAGE_READWRITE)
                if not self.address:
                    raise Exception("Failed to VirtualAlloc")

                # Copy the machine code into the memory segment
                memmove = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)(
                    ctypes._memmove_addr)
                if memmove(self.address, machine_code, size) < 0:
                    raise Exception("Failed to memmove")

                # Enable execute permissions
                PAGE_EXECUTE = ctypes.c_ulong(0x10)
                old_protect = ctypes.c_ulong(0)
                pfnVirtualProtect = ctypes.windll.kernel32.VirtualProtect
                res = pfnVirtualProtect(ctypes.c_void_p(self.address), ctypes.c_size_t(size), PAGE_EXECUTE,
                                        ctypes.byref(old_protect))
                if not res:
                    raise Exception("Failed VirtualProtect")

                # Flush Instruction Cache
                # First, get process Handle
                if not self.prochandle:
                    pfnGetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
                    pfnGetCurrentProcess.restype = ctypes.c_void_p
                    self.prochandle = ctypes.c_void_p(pfnGetCurrentProcess())
                # Actually flush cache
                res = ctypes.windll.kernel32.FlushInstructionCache(self.prochandle, ctypes.c_void_p(self.address),
                                                                   ctypes.c_size_t(size))
                if not res:
                    raise Exception("Failed FlushInstructionCache")
            else:
                from mmap import mmap, MAP_PRIVATE, MAP_ANONYMOUS, PROT_WRITE, PROT_READ, PROT_EXEC

                # Allocate a private and executable memory segment the size of the machine code
                machine_code = bytes.join(b'', self.machine_code)
                self.size = len(machine_code)
                self.mm = mmap(-1, self.size, flags=MAP_PRIVATE | MAP_ANONYMOUS,
                               prot=PROT_WRITE | PROT_READ | PROT_EXEC)

                # Copy the machine code into the memory segment
                self.mm.write(machine_code)
                self.address = ctypes.addressof(ctypes.c_int.from_buffer(self.mm))

            # Cast the memory segment into a function
            functype = ctypes.CFUNCTYPE(self.restype, *self.argtypes)
            self.func = functype(self.address)

        def run(self):
            # Call the machine code like a function
            retval = self.func()

            return retval

        def free(self):
            # Free the function memory segment
            if DataSource.is_windows:
                MEM_RELEASE = ctypes.c_ulong(0x8000)
                ctypes.windll.kernel32.VirtualFree(ctypes.c_void_p(self.address), ctypes.c_size_t(0), MEM_RELEASE)
            else:
                self.mm.close()

            self.prochandle = None
            self.mm = None
            self.func = None
            self.address = None
            self.size = 0

    def _run_asm(*machine_code):
        asm = ASM(ctypes.c_uint32, (), machine_code)
        asm.compile()
        retval = asm.run()
        asm.free()
        return retval

    max_extension_support = _run_asm(
        b"\xB8\x00\x00\x00\x80"  # mov ax,0x80000000
        b"\x0f\xa2"  # cpuid
        b"\xC3"  # ret
    )

    flags = []

    # http://en.wikipedia.org/wiki/CPUID#EAX.3D7.2C_ECX.3D0:_Extended_Features
    if max_extension_support >= 7:
        # EBX
        ebx = _run_asm(
            b"\x31\xC9",  # xor ecx,ecx
            b"\xB8\x07\x00\x00\x00"  # mov eax,7
            b"\x0f\xa2"  # cpuid
            b"\x89\xD8"  # mov ax,bx
            b"\xC3"  # ret
        )

        # Get the extended CPU flags
        extended_flags = {
            'avx2': _is_bit_set(ebx, 5),
            'avx512f': _is_bit_set(ebx, 16)
        }

        # Get a list of only the flags that are true
        extended_flags = [k for k, v in extended_flags.items() if v]
        flags += extended_flags

    flags.sort()
    return flags


def _get_lib_dir():
    if sys.platform.startswith("darwin"):
        LIB_DIR = "mac_"
    elif sys.platform.startswith("linux"):
        LIB_DIR = "linux_"
    elif sys.platform.startswith("win"):
        LIB_DIR = "windows_"
    else:
        raise Exception("ERROR: Unsupported operating system!")

    # Check architecture and AVX capabilities
    architecture, bits = _get_arch_and_bits()

    if bits != 64:
        raise Exception("ERROR: 32-bit systems are not supported!")

    if architecture == "ARM_8":
        LIB_DIR += "arm64"
    elif architecture == "X86_64":
        flags = _get_flags()

        # Check for AVX512 and AVX support using the CPU flags
        has_avx512 = "avx512f" in flags
        has_avx = "avx2" in flags

        if has_avx512:
            LIB_DIR += "avx512"
        elif has_avx:
            LIB_DIR += "avx2"
        else:
            raise Exception("ERROR: On X86_64 only AVX2 or AVX512 are supported!")
    else:
        raise Exception("ERROR: Only arm64 and x86_64 supported")

    if LIB_DIR == "mac_avx512":
        LIB_DIR = "mac_avx2"

    if LIB_DIR not in {"linux_arm64", "linux_avx2", "linux_avx512", "mac_arm64", "mac_avx2", "windows_avx2",
                       "windows_avx512", "windows_arm64"}:
        raise Exception("ERROR: Your operating system / CPU configuration is not supported.")

    return LIB_DIR


def _get_shared_lib_name():
    lib_name = "libsr"
    if sys.platform.startswith("darwin"):
        return lib_name + ".dylib"
    elif sys.platform.startswith("linux"):
        return lib_name + ".so"
    elif sys.platform.startswith("win"):
        return lib_name + ".dll"
    else:
        raise Exception("ERROR: Unsupported operating system!")


_absolute_path_sesum = os.path.dirname(os.path.abspath(__file__))
_shared_lib_dir = _get_lib_dir()
_lib_psr_name = os.path.join(_absolute_path_sesum, _shared_lib_dir, _get_shared_lib_name())
_clibrary = ctypes.CDLL(_lib_psr_name, mode=ctypes.RTLD_LOCAL)

_clibrary.compute_path_with_greedy_sesum.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_double, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int32),
    ctypes.c_uint64, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_uint64), ctypes.c_double, ctypes.c_int
]

_clibrary.execute_sesum.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),  # inputs_outputs_flat
    ctypes.POINTER(ctypes.c_int32),  # inputs_outputs_sizes
    ctypes.c_uint64,  # n_tensors
    ctypes.c_uint64,  # n_map_items
    ctypes.POINTER(ctypes.c_uint32),  # keys_sizes
    ctypes.POINTER(ctypes.c_uint64),  # values_sizes
    ctypes.c_int,  # sring
    ctypes.c_int,  # dt
    ctypes.c_int,  # be
    ctypes.c_int,  # debug
    ctypes.POINTER(ctypes.c_int64),  # path_ptr
    ctypes.c_void_p  # data
]

# Set the argument types for the function
_clibrary.execute_bigint_sesum.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),  # const uint32_t* inputs_outputs_flat
    ctypes.POINTER(ctypes.c_int32),  # const int32_t* inputs_outputs_sizes
    ctypes.c_uint64,  # uint64_t n_tensors
    ctypes.c_uint64,  # uint64_t n_map_items
    ctypes.POINTER(ctypes.c_uint32),  # const uint32_t* keys_sizes
    ctypes.POINTER(ctypes.c_uint64),  # const uint64_t* values_sizes
    ctypes.c_int,  # int sring
    ctypes.c_int,  # int dt
    ctypes.c_int,  # int be
    ctypes.c_int,  # int debug
    ctypes.POINTER(ctypes.c_int64),  # const int64_t* path_ptr
    ctypes.c_void_p,  # void* data
    ctypes.c_int  # int out data type
]
_clibrary.execute_bigint_sesum.restype = ctypes.c_void_p

_clibrary.get_string_of_num_sesum.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint64,
    ctypes.c_int
]
_clibrary.get_string_of_num_sesum.restype = ctypes.c_void_p

_clibrary.free_string_sesum.argtypes = [ctypes.c_void_p]

_clibrary.free_bigint_data_sesum.argtypes = [ctypes.c_void_p, ctypes.c_int]

try:
    import opt_einsum as oe

    _BaseClassOpt = oe.paths.PathOptimizer
except ImportError:
    _BaseClassOpt = object


class CGreedy(_BaseClassOpt):
    def __init__(self, seed=0, is_deterministic=False, minimize="size", algorithm="greedy", skops_alpha=0, max_repeats=8, max_time=0.0, progbar=False, is_outer_optimal=False,
                 threshold_optimal=12, threads=0, is_linear=True):
        """
         Initialize the CGreedy optimizer.

         Parameters:
         ----------
         seed : int, optional
             Random seed for reproducibility. Default is 0.

         is_deterministic : bool, optional
             Whether a random seed generates always the same path. Default is False.

         minimize : str, optional
             Criterion to minimize. Either "size" or "flops". Default is "size".

         algorithm : str, optional
             Algorithm for computing the contraction path. Either "greedy" or "kahypar". Default is "greedy".

         skops_alpha : float, optional
             Adjusts pairwise flops computations in tensor contractions by adding
             skops_alpha * abs(sizeA - sizeB) * log10(flops). Aims to emphasize tensor size disparities' impact,
             with higher values penalizing size mismatches more. Default is 0.0.

         max_repeats : int, optional
             Maximum number of times the optimization can be repeated. Default is 8.

         max_time : float, optional
             Maximum time (in seconds) the optimizer is allowed to run. If set to 0.0 or less,
             there's no time limit. Default is 0.0.

         progbar : bool, optional
             Whether to display a progress bar during optimization. Default is False.

         is_outer_optimal: bool, optional
             Whether to consider outer products in the optimal search. Default is False.

         threshold_optimal: uint, optional
             Maximum number of input tensors to perform an expensive optimal search instead
             of a greedy search. Default is 12.

         threads : uint, optional
             Number of threads to be used for the greedy algorithm. Default is 0.
             (Setting the value to 0 uses all available threads.)

         is_linear : bool, optional
            Whether to compute a path in linear format or SSA format. Default is True.

         Raises:
         ------
         Exception:
             If the 'minimize' parameter is not either "size" or "flops".

         Attributes:
         -----------
         flops_log10 : float
             Log base 10 of the number of flops (floating-point operations). Initialized to negative infinity.
             This value is updated after the algorithm is executed.

         size_log2 : float
             Log base 2 of the biggest intermediate tensor size. Initialized to negative infinity.
             This value is updated after the algorithm is executed.

         path_time : float
             Time (in seconds) used internally to compute the contraction path. Initialized to negative infinity.
             This value is updated after the algorithm is executed.

         """
        self.seed = seed
        self.max_repeats = max_repeats
        self.max_time = max_time
        self.progbar = progbar
        if minimize in {"size", "flops"}:
            self.minimize = minimize
        else:
            raise Exception("ERROR: minimize parameter can only be 'size' or 'flops'.")

        if algorithm in {"greedy", "kahypar"}:
            self.algorithm = algorithm
        else:
            raise Exception("ERROR: algorithm parameter can only be 'greedy' or 'kahypar'.")

        if threshold_optimal < 3 or threshold_optimal > 64:
            raise Exception("ERROR: valid input for 'threshold_optimal' is a number between 3 and 64.")

        if skops_alpha < 0:
            raise Exception("ERROR: valid input for 'skops_alpha' is a floating-point number >= 0.")

        self.threshold_optimal = threshold_optimal
        self.is_outer_optimal = is_outer_optimal
        self.minimize = minimize
        self.threads = threads
        self.is_linear = is_linear
        self.is_deterministic = is_deterministic
        self.skops_alpha = float(skops_alpha)
        self.flops_log10 = float("-inf")
        self.size_log2 = float("-inf")
        self.path_time = float("-inf")

    def __call__(self, inputs, output, sizes, memory_limit=None):
        tic = time.time()
        l_flat = [ord(char) for s in inputs for char in s]

        for s in output:
            l_flat.append(ord(s))
        l_sizes = [len(s) for s in inputs]
        l_sizes.append(len(output))

        inputs_outputs_flat = np.array(l_flat, dtype=np.uint32)
        inputs_outputs_sizes = np.array(l_sizes, dtype=np.int32)
        n_tensors = len(inputs_outputs_sizes)
        n_map_items = len(sizes)
        keys_sizes = (ctypes.c_uint32 * n_map_items)(*[ord(k) for k in sizes.keys()])
        values_sizes = (ctypes.c_uint64 * n_map_items)(*sizes.values())

        out_flops_log10 = ctypes.c_double(float("-inf"))
        out_size_log2 = ctypes.c_double(float("-inf"))
        out_path = np.empty((n_tensors - 2) * 2, dtype=np.uint64)

        def call_external_library():
            _clibrary.compute_path_with_greedy_sesum(
                self.seed,
                self.max_repeats,
                self.max_time,
                1 if self.progbar else 0,
                1 if self.minimize == "size" else 0,
                1 if self.algorithm == "kahypar" else 0,
                1 if self.is_outer_optimal else 0,
                self.threshold_optimal,
                self.threads,
                1 if self.is_linear else 0,
                inputs_outputs_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                inputs_outputs_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                n_tensors,
                n_map_items,
                keys_sizes,
                values_sizes,
                ctypes.byref(out_flops_log10),
                ctypes.byref(out_size_log2),
                out_path.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
                self.skops_alpha,
                1 if self.is_deterministic else 0
            )

        thread = threading.Thread(target=call_external_library)
        thread.start()
        thread.join()

        self.flops_log10 = out_flops_log10.value
        self.size_log2 = out_size_log2.value
        self.path_time = time.time() - tic

        if len(inputs) == 1:
            return 0,

        linear_path = []
        for i in range(len(out_path) // 2):
            linear_path.append((int(out_path[i * 2]), int(out_path[i * 2 + 1])))

        return linear_path


def _get_sizes(einsum_notation, shapes):
    index_sizes = {}
    for einsum_index, shape in zip(einsum_notation.split("->")[0].split(","), shapes):
        if not hasattr(shape, '__iter__'):
            shape = list(shape)
        for index, dimension in zip(einsum_index, shape):
            if not index in index_sizes:
                index_sizes[index] = dimension
            else:
                if index_sizes[index] != dimension:
                    raise Exception(f"Dimension error for index '{index}'.")
    return index_sizes


def compute_path(format_string, *arguments, seed=0, is_deterministic=False, minimize="size", algorithm="greedy", skops_alpha=0, max_repeats=8, max_time=0.0, progbar=False,
                 is_outer_optimal=False, threshold_optimal=12, threads=0, is_linear=True):
    """
    Compute the contraction path for a given format string and tensor shapes.

    Parameters:
    ----------
    format_string : str
        The format string specifying the contraction. For example, "ij,jk->ik".

    *arguments : numpy.ndarray or list or tuple
        Shapes of tensors involved in the contraction. They can be provided as numpy arrays, lists, or tuples.

    seed : int, optional
        Random seed for reproducibility. Default is 0.

    is_deterministic : bool, optional
       Whether a random seed generates always the same path. Default is False.

    minimize : str, optional
        Criterion to minimize during contraction. Either "size" or "flops". Default is "size".

    algorithm : str, optional
        Algorithm for computing the contraction path. Either "greedy" or "kahypar". Default is "greedy".

    skops_alpha : float, optional
        Adjusts pairwise flops computations in tensor contractions by adding
        skops_alpha * abs(sizeA - sizeB) * log10(flops). Aims to emphasize tensor size disparities' impact,
        with higher values penalizing size mismatches more. Default is 0.0.

    max_repeats : uint, optional
        Maximum number of times the optimization can be repeated. Default is 8.

    max_time : float, optional
        Maximum time (in seconds) the optimizer is allowed to run. If set to 0.0 or less,
        there's no time limit. Default is 0.0.

    progbar : bool, optional
        Whether to display a progress bar during optimization. Default is False.

    is_outer_optimal : bool, optional
        Whether to consider outer products in the optimal search. Default is False.

    threshold_optimal : uint, optional
        Maximum number of input tensors to perform an expensive optimal search instead
        of a greedy search. Default is 12.

    threads : uint, optional
       Number of threads to be used for the greedy algorithm. Default is 0.
       (Setting the value to 0 uses all available threads.)

    is_linear : bool, optional
       Whether to compute a path in linear format or SSA format. Default is True.

    Returns:
    -------
    tuple
        A tuple containing:
        - contraction path as a list of pairwise contraction.
        - Log base 10 of the number of flops (floating-point operations).
        - Log base 2 of the biggest intermediate tensor size.

    Notes:
    -----
    The format string should be in the form "input->output", where 'input' is a comma-separated list of tensor indices,
    and 'output' is the desired contraction output tensor indices.

    The input tensor shapes can be provided in multiple ways, including numpy arrays, lists, or tuples.

    Example:
    -------
    >>> compute_path("ij,jk->ik", (2,3), (3,4))
    """
    format_string = format_string.replace(" ", "")
    shapes = []
    for arg in arguments:
        if isinstance(arg, np.ndarray):
            shapes.append(arg.shape)
        elif isinstance(arg, list):
            shapes.append(arg)
        elif isinstance(arg, tuple):
            shapes.append(arg)
        elif np.isscalar(arg):
            shapes.append([])
        else:
            try:
                shapes.append(arg.shape)
            except Exception as e:
                print(f"An error occurred: {e}")
    sizes = _get_sizes(format_string, shapes)
    str_in, str_out = format_string.split("->")
    inputs = list(map(set, str_in.split(",")))
    output = set(str_out)
    if len(shapes) != len(inputs):
        raise Exception(
            "ERROR: number of tensors in the format string does not match the number of tensors in arguments.")
    cg = CGreedy(seed=seed, minimize=minimize, algorithm=algorithm, skops_alpha=skops_alpha, max_repeats=max_repeats, max_time=max_time, progbar=progbar,
                 is_outer_optimal=is_outer_optimal, threshold_optimal=threshold_optimal, threads=threads, is_linear=is_linear, is_deterministic=is_deterministic)
    path = cg.__call__(inputs, output, sizes)
    if not isinstance(path, list):
        path = [path]
    return path, cg.flops_log10, cg.size_log2


class _Tag:
    """A simple class to represent a type tag."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


bigint = _Tag("bigint")
int128 = _Tag("int128")
uint128 = _Tag("uint128")
standard = _Tag("standard")
max_plus = _Tag("max_plus")


def _safe_convert(tensor, final_dtype):
    if np.shape(tensor) == ():
        tensor = np.array(tensor, order='C')
    # Check if the dtype is a valid integer or floating point type.
    # Other dtypes like complex numbers, strings, etc. won't have clear bounds using iinfo/finfo.
    if np.issubdtype(final_dtype, np.integer):
        max_val = np.iinfo(final_dtype).max
        min_val = np.iinfo(final_dtype).min
    elif np.issubdtype(final_dtype, np.floating):
        max_val = np.finfo(final_dtype).max
        min_val = np.finfo(final_dtype).min
    else:
        # If not integer or floating point, don't do bound checking.
        return np.array(tensor, order='C', dtype=final_dtype)
    if tensor.max() > max_val or tensor.min() < min_val:
        raise Exception(f"ERROR: Overflow or underflow detected when converting input arrays to {final_dtype}")
    return np.array(tensor, order='C', dtype=final_dtype)


def _calculate_final_dtype_safely(*arguments):
    try:
        final_dtype = np.result_type(*arguments)
        return final_dtype
    except Exception as e:
        return None

def sesum(format_string, *arguments, path=None, dtype=None, debug=False, safe_convert=False, backend="dense",
          semiring=standard):
    """
    This function contracts tensors according to the given format string.

    Parameters:
    ----------
    format_string : str
        The format string specifying the contraction. For example, "ij,jk->ik".

    *arguments : numpy.ndarray(s)
        Input tensors involved in the contraction.

    path : list of tuples, optional
        Sequence of pairwise tensor contractions, where each tuple defines which tensors to contract.
        If not provided, it will be computed automatically. Default is None.

    dtype : numpy dtype or property method, optional
        Data type of the result tensor. Supported data types include:
        - Floating Point: np.float64, np.float32
        - Complex Numbers: np.csingle, np.cdouble
        - Integers: np.int8, np.int16, np.int32, np.int64
        - Unsigned Integers: np.uint8, np.uint16, np.uint32, np.uint64
        - Special Types: bigint, int128, uint128
        Default is None, in which case it is inferred.

    debug : bool, optional
        If set to True, additional debugging information will be printed while executing. Default is False.

    safe_convert : bool, optional
        If True, ensures input data conversion to the final data type is overflow-free. Default is False.
        Note: This does not check for overflow during computation.

    backend : str, optional
        Backend used for tensor contractions. Valid values are "dense" and "sparse". Default is "dense".

    semiring : enum, optional
        Specifies the semiring to be used. Valid values are 'standard' and 'max_plus'. Default is 'standard'.

    Returns:
    -------
    numpy.ndarray
        Resulting tensor from the contraction.

    Raises:
    ------
    ValueError:
        If there's any inconsistency in the format string or input tensors.

    Exception:
        For unsupported data types or backends.

    Notes:
    -----
    The format string should be in the form "input->output", where 'input' is a comma-separated list of tensor indices,
    and 'output' is the desired contraction output tensor indices.

    Example:
    -------
    >>> a = np.array([[1,2],[3,4]])
    >>> b = np.array([[1,1],[1,1]])
    >>> sesum("ij,jk->ik", a, b)
    array([[3., 3.],
           [7., 7.]])
    """

    if format_string.count(",") + 1 != len(arguments):
        raise Exception(
            "ERROR: number of tensors in the format string does not match the number of tensors in arguments.")

    l = []
    bigIntTypes = {int128, uint128, bigint}
    if dtype in bigIntTypes:
        final_dtype = np.int64
    elif dtype is None:
        final_dtype = _calculate_final_dtype_safely(*arguments)
        if final_dtype is None:
            error_message = ("ERROR: Automatic type deduction failed. Specify the numpy dtype using the 'dtype' "
                             "parameter in 'sesum' function.")
            raise Exception(error_message)
    else:
        final_dtype = dtype

    dt = 999  # undefined
    if final_dtype == np.float64:
        dt = 12
    elif final_dtype == np.float32:
        dt = 11
    elif final_dtype == np.csingle:
        dt = 13
    elif final_dtype == np.cdouble:
        dt = 14
    elif final_dtype == np.int8 or final_dtype == np.bool_:
        dt = 1
    elif final_dtype == np.uint8:
        dt = 2
    elif final_dtype == np.int16:
        dt = 3
    elif final_dtype == np.uint16:
        dt = 4
    elif final_dtype == np.int32:
        dt = 5
    elif final_dtype == np.uint32:
        dt = 6
    elif final_dtype == np.int64:
        dt = 7
    elif final_dtype == np.uint64:
        dt = 8
    else:
        raise Exception("ERROR: Data type " + str(final_dtype) + " not supported.")

    be = 999
    if backend == "dense":
        be = 0
    elif backend == "sparse":
        be = 1
    else:
        raise Exception("ERROR: Backend " + backend + " not supported. (valid backends: dense, sparse)")

    for tensor in arguments:
        if isinstance(tensor, np.ndarray) and tensor.flags["C_CONTIGUOUS"] and tensor.dtype == final_dtype:
            l.append(tensor)
        else:
            if safe_convert and tensor.dtype != final_dtype:
                tensor_array = _safe_convert(tensor, final_dtype)
            else:
                tensor_array = np.array(tensor, order='C', dtype=final_dtype)
            l.append(tensor_array)

    sring = 999
    if semiring == standard:
        sring = 0
    elif semiring == max_plus:
        sring = 1
    else:
        raise Exception("ERROR: Undefined semiring!")

    format_string = format_string.replace(" ", "")
    shapes = [arr.shape for arr in l]
    sizes = _get_sizes(format_string, shapes)
    str_in, str_out = format_string.split("->")
    tensors = str_in.split(",")
    tensors.append(str_out)
    out_shape = [sizes[c] for c in str_out]
    l.append(np.empty(shape=out_shape, dtype=final_dtype, order='C'))

    l_flat = [ord(char) for s in tensors for char in s]
    l_sizes = [len(s) for s in tensors]
    inputs_outputs_flat = np.array(l_flat, dtype=np.uint32)
    inputs_outputs_sizes = np.array(l_sizes, dtype=np.int32)
    n_tensors = len(inputs_outputs_sizes)
    n_map_items = len(sizes)
    keys_sizes = (ctypes.c_uint32 * n_map_items)(*[ord(k) for k in sizes.keys()])
    _sizes_values = sizes.values()
    values_sizes = (ctypes.c_uint64 * n_map_items)(*_sizes_values)

    if backend == "sparse":
        for value in _sizes_values:
            if value not in [1, 2]:
                raise Exception(
                    f"ERROR: Invalid dimension size {value} found. Backend sparse requires all sizes of dimensions to be either 1 or 2.")

    pointer_array = (ctypes.c_void_p * n_tensors)()  # array of void pointers
    for i, arr in enumerate(l):
        pointer_array[i] = arr.ctypes.data_as(ctypes.c_void_p)
    data = ctypes.cast(pointer_array, ctypes.c_void_p)

    if n_tensors == 2:
        path = [(0, 0)]
    elif n_tensors == 3:
        path = [(0, 1)]
    elif path is None:
        out_flops_log10 = ctypes.c_double(float("-inf"))
        out_size_log2 = ctypes.c_double(float("-inf"))
        out_path = np.empty((n_tensors - 2) * 2, dtype=np.uint64)

        def call_external_library():
            _clibrary.compute_path_with_greedy_sesum(0, 8, 1.0, 0, 1, 0, 0, 12, 0, 1,
                                               inputs_outputs_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                                               inputs_outputs_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                                               n_tensors,
                                               n_map_items,
                                               keys_sizes,
                                               values_sizes,
                                               ctypes.byref(out_flops_log10),
                                               ctypes.byref(out_size_log2),
                                               out_path.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
                                               0.0,
                                               1
                                               )

        thread = threading.Thread(target=call_external_library)
        thread.start()
        thread.join()

        path = []
        for i in range(len(out_path) // 2):
            path.append((out_path[i * 2], out_path[i * 2 + 1]))

    if n_tensors > 2 and len(path) != n_tensors - 2:
        raise Exception(
            f"ERROR: Expected path length of {n_tensors - 2}, but got {len(path)}. "
            f"Ensure the path length is consistent with the number of tensors.")

    flattened_path = np.array([item for sublist in path for item in sublist], dtype=np.int64)
    path_ptr = flattened_path.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))

    if dtype in bigIntTypes:

        if dtype == int128:
            out_dt = 9
        elif dtype == uint128:
            out_dt = 10
        else:
            out_dt = 16

        n_items = 1
        for d in out_shape:
            n_items *= d
        out = np.empty(shape=n_items, dtype=object, order='C')

        def call_external_library():
            void_ptr = _clibrary.execute_bigint_sesum(
                inputs_outputs_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                inputs_outputs_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                n_tensors,
                n_map_items,
                keys_sizes,
                values_sizes,
                sring,
                dt,
                be,
                int(debug),  # Convert Python bool to int
                path_ptr,
                data,
                out_dt
            )
            c_string_ptr = ctypes.c_void_p(None)
            try:
                for i in range(n_items):
                    c_string_ptr = _clibrary.get_string_of_num_sesum(void_ptr, i, out_dt)
                    out[i] = int(ctypes.cast(c_string_ptr, ctypes.c_char_p).value)
                    _clibrary.free_string_sesum(c_string_ptr)
                    c_string_ptr = ctypes.c_void_p(None)
            finally:
                _clibrary.free_string_sesum(c_string_ptr)
                _clibrary.free_bigint_data_sesum(void_ptr, out_dt)

        thread = threading.Thread(target=call_external_library)
        thread.start()
        thread.join()
        del l
        return out.reshape(out_shape)
    else:
        def call_external_library():
            _clibrary.execute_sesum(
                inputs_outputs_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                inputs_outputs_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                n_tensors,
                n_map_items,
                keys_sizes,
                values_sizes,
                sring,
                dt,
                be,
                int(debug),  # Convert Python bool to int
                path_ptr,
                data
            )

        thread = threading.Thread(target=call_external_library)
        thread.start()
        thread.join()

    return l[-1]
