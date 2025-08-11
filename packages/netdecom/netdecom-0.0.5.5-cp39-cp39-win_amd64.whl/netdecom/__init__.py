import os
import sys
import importlib.machinery
import importlib.util

# 当前包目录
current_dir = os.path.dirname(__file__)
release_dir = os.path.join(current_dir, "Release")

# 根据平台确定扩展模块文件名
if sys.platform == "win32":
    ext_path = os.path.join(release_dir, "decom_h.pyd")
elif sys.platform.startswith("linux") or sys.platform == "darwin":
    ext_path = os.path.join(release_dir, "libdecom_h.so")
else:
    raise ImportError(f"Unsupported platform: {sys.platform}")

# 检查扩展模块文件是否存在
if not os.path.exists(ext_path):
    raise ImportError(f"Could not find the decom_h extension module at {ext_path}")

# Windows 下将 Release 目录加入 PATH，方便查找依赖 DLL
if sys.platform == "win32":
    os.environ['PATH'] = release_dir + os.pathsep + os.environ.get('PATH', '')

# 使用 ExtensionFileLoader 加载扩展模块，捕获异常方便调试
try:
    loader = importlib.machinery.ExtensionFileLoader('netdecom.decom_h', ext_path)
    spec = importlib.util.spec_from_loader('netdecom.decom_h', loader)
    decom_h = importlib.util.module_from_spec(spec)
    loader.exec_module(decom_h)
except Exception as e:
    raise ImportError(f"Failed to load decom_h extension module from {ext_path}") from e

# 绑定扩展模块到包命名空间
import netdecom
sys.modules['netdecom.decom_h'] = decom_h
netdecom.decom_h = decom_h

from .Convex_hull_DAG import Convex_hull_DAG
from .Graph_gererators import generator_connected_ug, generate_connected_dag, random_connected_dag
from .examples import get_example

# 从扩展模块导入接口
from .decom_h import recursive_decom, find_convex_hull, components_forbidden, close_separator

__all__ = [
    'recursive_decom',
    'find_convex_hull',
    'components_forbidden',
    'close_separator',
    'get_example',
    'generator_connected_ug',
    'generate_connected_dag',
    'random_connected_dag',
]

def CMDSA(graph, r):
    """
    Perform Convex Hull Decomposition for Directed Acyclic Graph (CMDSA).

    :param graph: The NetworkX graph to perform CMDSA on
    :param r: The set of nodes to perform CMDSA on
    :return: The result of the CMDSA decomposition
    """
    convex_hull_dag = Convex_hull_DAG(graph)
    return convex_hull_dag.CMDSA(r)
