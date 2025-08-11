# math_build02
math_build02提供了两种方法：
|方法|描述|
|:--:|:--:|
|math_tool|用于计算两个数的减法|
|math_tool2|用于计算三个数的运算|

## 使用讲解
### 通过pip安装
`pip install math_build02`
#### 1.使用方法(直接在代码中引用)
<pre>
math_build02 import math_tool
from math_build02 import math_tool02

print(math_tool.new_numpy(1, 2))
print(math_tool02.new_numpy02(1, 2, 3))
</pre>
#### 2.使用方法（通过命令行调用）
<pre>
PS C:\Users\14976\Desktop\app_build\math_build02> uv run math-build-two --a 1 --b 2        
a + b = 12
PS C:\Users\14976\Desktop\app_build\math_build02> uv run math-build-three --a 1 --b 2 --c 4
a - b + c = 3
</pre>