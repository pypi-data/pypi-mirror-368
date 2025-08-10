# helical_sweep_rsolid

## API定义

```python
def helical_sweep_rsolid(profile: Wire, pitch: float, height: float, radius: float, center: Tuple[float, float, float] = (0, 0, 0), dir: Tuple[float, float, float] = (0, 0, 1)) -> Solid
```

*来源文件: operations.py*

## API作用

沿螺旋路径扫掠二维轮廓创建三维实体，常用于创建螺纹、弹簧、
螺旋管道等具有螺旋特征的几何体。轮廓必须是封闭的。
函数会自动矫正profile的朝向和位置：
- 确保profile的法向量朝向X轴正方向或负方向
- 将profile移动到距离旋转中心指定半径的位置

## API参数说明

### profile

- **类型**: `Wire`
- **说明**: 要扫掠的轮廓线，必须是封闭的线轮廓

### pitch

- **类型**: `float`
- **说明**: 螺距，每转一圈在轴向上的距离，必须为正数

### height

- **类型**: `float`
- **说明**: 螺旋的总高度，必须为正数

### radius

- **类型**: `float`
- **说明**: 螺旋的半径，必须为正数

### center

- **类型**: `Tuple[float, float, float], optional`
- **说明**: 螺旋中心点坐标 (x, y, z)， 默认为 (0, 0, 0)

### dir

- **类型**: `Tuple[float, float, float], optional`
- **说明**: 螺旋轴方向向量 (x, y, z)， 默认为 (0, 0, 1) 表示沿Z轴方向

## 返回值说明

Solid: 螺旋扫掠后的实体对象

## 异常

- **ValueError**: 当轮廓不封闭、螺距/高度/半径无效或扫掠失败时抛出异常

## API使用例子

```python
# 创建螺旋弹簧
circle_profile = make_circle_rwire((0, 0, 0), 0.2)
spring = helical_sweep_rsolid(circle_profile, 1.0, 10.0, 2.0)
# 创建方形截面的螺旋管
square_profile = make_rectangle_rwire(0.5, 0.5)
square_helix = helical_sweep_rsolid(square_profile, 2.0, 8.0, 1.5)
# 创建紧密螺旋结构
small_circle = make_circle_rwire((0, 0, 0), 0.1)
tight_helix = helical_sweep_rsolid(small_circle, 0.5, 5.0, 1.0)
```
