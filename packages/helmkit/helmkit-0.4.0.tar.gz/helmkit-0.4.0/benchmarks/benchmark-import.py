import sys
import time


def benchmark_imports(import_code: str, repeats: int = 100):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        exec(import_code)
        end = time.perf_counter()
        times.append(end - start)
        # Remove imported modules to force fresh import next run
        for mod in list(sys.modules):
            if mod.startswith("pyPept") or mod.startswith("helmkit"):
                del sys.modules[mod]
    avg_time = sum(times) / repeats
    print(f"Average import time for:\n{import_code}\n= {avg_time:.6f} seconds\n")


pyPept_imports = """from pyPept.converter import Converter
from pyPept.molecule import Molecule
from pyPept.sequence import Sequence
"""

helmkit_imports = """from helmkit import load_monomer_library
from helmkit import Molecule
"""


def main():
    benchmark_imports(pyPept_imports)
    benchmark_imports(helmkit_imports)


if __name__ == "__main__":
    main()
