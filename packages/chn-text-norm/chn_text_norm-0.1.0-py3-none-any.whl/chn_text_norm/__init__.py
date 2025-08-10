"""chn_text_norm 包

提供 `Text` 类用于将中文文本中的数字、日期、金额、百分比、分数、电话等进行规范化。
"""

from .text import Text

__all__ = ["Text", "__version__"]
__version__ = "0.1.0"


