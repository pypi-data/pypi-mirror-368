import os
import sys
import shutil
import subprocess
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the extensions")

        for ext in self.extensions:
            self.build_extension(ext)

        super().run()

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cfg = 'Debug' if self.debug else 'Release'
        build_temp = os.path.abspath(self.build_temp)
        os.makedirs(build_temp, exist_ok=True)

        if sys.platform == "win32":
            binary_name = "decom_h.pyd"
        elif sys.platform == "linux":
            binary_name = "libdecom_h.so"
        elif sys.platform == "darwin":
            binary_name = "libdecom_h.dylib"
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")

        prebuilt_path = os.path.join(extdir, "Release", binary_name)

        if os.path.exists(prebuilt_path):
            print(f"Found prebuilt binary at {prebuilt_path}, skipping build.")
            target_path = self.get_ext_fullpath(ext.name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copyfile(prebuilt_path, target_path)
        else:
            print(f"No prebuilt binary found for {sys.platform}, building from source.")
            this_dir = os.path.dirname(os.path.abspath(__file__))
            source_dir = os.path.join(this_dir, 'src')

            cmake_args = [
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={os.path.join(extdir, "Release")}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'-DCMAKE_BUILD_TYPE={cfg}',
            ]

            igraph_dir = os.getenv('IGRAPH_DIR')
            if igraph_dir:
                cmake_args.append(f'-DIGRAPH_DIR={igraph_dir}')

            subprocess.check_call(['cmake', source_dir] + cmake_args, cwd=build_temp)
            subprocess.check_call(['cmake', '--build', '.', '--config', cfg], cwd=build_temp)


setup(
    name='netdecom',
    version='0.0.5.5',
    description='Dimensionality Reduction and Decomposition of Undirected Graph Models and Bayesian Networks',
    author='Hugh',
    packages=find_packages(include=['netdecom', 'netdecom.*']),
    ext_modules=[CMakeExtension('netdecom.decom_h')],
    cmdclass={'build_ext': CMakeBuild},
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    package_data={
        'netdecom': ['Release/*.*'],  # 包含 Release 文件夹内所有文件，如 *.pyd, *.dll, *.so 等
        'netdecom.examples': ['*.txt'],
    },
    zip_safe=False,
)
