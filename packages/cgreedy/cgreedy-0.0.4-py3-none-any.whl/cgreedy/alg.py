import os
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
        LIB_DIR += "x86"
    else:
        raise Exception("ERROR: Only arm64 and x86_64 supported")

    if LIB_DIR not in {"linux_arm64", "linux_x86", "mac_arm64", "mac_x86", "windows_x86"}:
        raise Exception("ERROR: Your operating system / CPU configuration is not supported.")

    return LIB_DIR


def _get_shared_lib_name():
    lib_name = "libcgreedy"
    if sys.platform.startswith("darwin"):
        return lib_name + ".dylib"
    elif sys.platform.startswith("linux"):
        return lib_name + ".so"
    elif sys.platform.startswith("win"):
        return lib_name + ".dll"
    else:
        raise Exception("ERROR: Unsupported operating system!")


_absolute_path_cgreedy = os.path.dirname(os.path.abspath(__file__))
_shared_lib_dir = _get_lib_dir()
_lib_psr_name = os.path.join(_absolute_path_cgreedy, _shared_lib_dir, _get_shared_lib_name())
_clibrary = ctypes.CDLL(_lib_psr_name)

_clibrary.compute_path_with_greedy.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_double, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int32),
    ctypes.c_uint64, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_uint64)
]

try:
    import opt_einsum as oe

    _BaseClassOpt = oe.paths.PathOptimizer
except ImportError:
    _BaseClassOpt = object


class CGreedy(_BaseClassOpt):
    def __init__(self, seed=0, minimize="size", max_repeats=8, max_time=0.0, progbar=False, is_outer_optimal=False,
                 threshold_optimal=12, threads=0, is_linear=True):
        """
         Initialize the CGreedy optimizer.

         Parameters:
         ----------
         seed : int, optional
             Random seed for reproducibility. Default is 0.

         minimize : str, optional
             Criterion to minimize. Either 'size' or 'flops'. Default is 'size'.

         max_repeats : int, optional
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

         Raises:
         ------
         Exception:
             If the 'minimize' parameter is not either 'size' or 'flops'.

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

        if threshold_optimal < 3 or threshold_optimal > 64:
            raise Exception("ERROR: valid input for 'threshold_optimal' is a number between 3 and 64.")
        self.threshold_optimal = threshold_optimal
        self.is_outer_optimal = is_outer_optimal
        self.minimize = minimize
        self.threads = threads
        self.is_linear = is_linear
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
            _clibrary.compute_path_with_greedy(
                self.seed,
                self.max_repeats,
                self.max_time,
                1 if self.progbar else 0,
                1 if self.minimize == "size" else 0,
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
            )

        thread = threading.Thread(target=call_external_library)
        thread.start()
        thread.join()

        self.flops_log10 = out_flops_log10.value
        self.size_log2 = out_size_log2.value
        self.path_time = time.time() - tic

        if len(inputs) == 1:
            return 0,

        _path = []
        for i in range(len(out_path) // 2):
            _path.append((int(out_path[i * 2]), int(out_path[i * 2 + 1])))

        return _path


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


def compute_path(format_string, *arguments, seed=0, minimize="size", max_repeats=8, max_time=0.0, progbar=False,
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

    minimize : str, optional
        Criterion to minimize during contraction. Either 'size' or 'flops'. Default is 'size'.

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

    threads: uint, optional
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
        raise Exception("ERROR: number of tensors in the format string does not match the number of tensors specified.")
    cg = CGreedy(seed=seed, minimize=minimize, max_repeats=max_repeats, max_time=max_time, progbar=progbar,
                 is_outer_optimal=is_outer_optimal, threshold_optimal=threshold_optimal, threads=threads,
                 is_linear=is_linear)
    path = cg.__call__(inputs, output, sizes)
    if not isinstance(path, list):
        path = [path]
    return path, cg.flops_log10, cg.size_log2
