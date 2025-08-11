import sys

try:
    from IPython.core.getipython import get_ipython
    ipython = get_ipython()
    if ipython is not None:
        # 如果处于 Jupyter 环境，禁用回溯信息
        from IPython.core.interactiveshell import InteractiveShell

        def custom_showtraceback(self, *args, **kwargs):
            exc_type, exc_value, _ = sys.exc_info()
            print(f"Error: {exc_type.__name__} {str(exc_value)}")

        InteractiveShell.showtraceback = custom_showtraceback
except ImportError:
    # 如果没有安装 IPython，说明不在 Jupyter 环境
    pass


# 这里可以添加你的包的其他功能代码
def example_function():
    # 触发一个异常用于测试
    result = 1 / 0
    return result