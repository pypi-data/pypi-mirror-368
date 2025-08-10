# make_polyline_rwire

## API定义

```python
def make_polyline_rwire(points: List[Tuple[float, float, float]], closed: bool = False) -> Wire
```

*来源文件: operations.py*

## API作用

创建由多个直线段连接的多段线，用于构建折线、多边形轮廓等。
相邻点之间用直线连接，可以创建开放或闭合的多段线。

## API参数说明

### points

- **类型**: `List[Tuple[float, float, float]]`
- **说明**: 顶点坐标列表 [(x, y, z), ...]， 至少需要2个点，相邻点之间用直线连接

### closed

- **类型**: `bool, optional`
- **说明**: 是否创建闭合的多段线，默认为False。 如果为True，会自动连接最后一个点和第一个点

## 返回值说明

Wire: 创建的线对象，由多个直线段组成的多段线

## 异常

- **ValueError**: 当顶点少于2个时抛出异常

## API使用例子

```python
# 创建L形多段线
points = [(0, 0, 0), (3, 0, 0), (3, 2, 0)]
l_shape = make_polyline_rwire(points)
# 创建三角形轮廓
triangle_points = [(0, 0, 0), (2, 0, 0), (1, 2, 0)]
triangle = make_polyline_rwire(triangle_points, closed=True)
# 创建复杂的多边形
polygon_points = [(0, 0, 0), (2, 0, 0), (3, 1, 0), (2, 2, 0), (0, 2, 0)]
polygon = make_polyline_rwire(polygon_points, closed=True)
```
