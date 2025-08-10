# translate_shape

## API定义

```python
def translate_shape(shape: AnyShape, vector: Tuple[float, float, float]) -> AnyShape
```

*来源文件: operations.py*

## API作用

将几何体从当前位置平移到新位置，不改变几何体的形状和大小。
平移操作支持当前坐标系变换，适用于所有类型的几何对象。

## API参数说明

### shape

- **类型**: `AnyShape`
- **说明**: 要平移的几何体，可以是点、边、线、面、实体等任意几何对象

### vector

- **类型**: `Tuple[float, float, float]`
- **说明**: 平移向量 (dx, dy, dz)， 定义在X、Y、Z方向上的平移距离

## 返回值说明

AnyShape: 平移后的几何体，类型与输入相同

## 异常

- **ValueError**: 当几何体或平移向量无效时抛出异常

## API使用例子

```python
# 平移立方体
box = make_box_rsolid(2, 2, 2)
moved_box = translate_shape(box, (5, 0, 0))  # 沿X轴移动5个单位
# 平移圆形面
circle = make_circle_rface((0, 0, 0), 1.0)
moved_circle = translate_shape(circle, (1, 1, 2))
# 平移线段
line = make_line_redge((0, 0, 0), (1, 0, 0))
moved_line = translate_shape(line, (0, 3, 0))
```
