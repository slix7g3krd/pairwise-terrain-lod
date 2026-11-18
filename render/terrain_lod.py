"""第 52 批：大世界跨区块飞行时地表裂开、法线接缝、脚下悬空：...

本模块提供地形 LOD 的纯函数修复：
- conservative_height: 高度图 LOD 采样做保守（取覆盖范围内最大高度），
  避免低模采样漏掉高峰导致地表裂开/脚下悬空。
- stitch_edge: 跨 LOD 裙边缝合，裙边以较低一侧为基准再下探一个 step，
  而不是按各自网格高度，避免相邻块接缝。
- splat_weights: splatmap 权重归一化，零权重退化为均匀分布。
- normal_from_slope: 由高度梯度计算归一化法线（高模法线），
  避免三平面法线使用低模法线造成法线接缝。
- cave_layer_height: 多层洞穴高度，按层号在基准高度上叠加层间距。
- collision_lod_sync: 视觉与物理 LOD 是否同步，碰撞需随 LOD 同步。
- clamp_layer: 纹理数组层索引钳制到 [0, max_layer]，避免越界。
- displacement_continuous: 判断位移贴图在 LOD 边界是否连续。
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple


def conservative_height(samples: Iterable[float]) -> float:
    """返回一组高度采样中的保守高度。

    保守采样要求结果不低于覆盖范围内任意采样点，因此取最大值，
    这样低 LOD 块不会把高峰削掉而在跨块飞行时露出裂缝或悬空。
    """
    values = list(samples)
    if not values:
        return 0.0
    return max(values)


def stitch_edge(edge: float, neighbor: float, step: float) -> float:
    """返回跨 LOD 裙边缝合后的边缘高度。

    相邻块 LOD 不同时，两侧边缘高度可能不一致。裙边应以较低的一侧
    为基准，再向下延伸一个 ``step``（LOD 步长）来盖住裂缝，
    而不是各自按本块网格高度生成裙边。
    """
    return min(edge, neighbor) - step


def splat_weights(weights: Sequence[float]) -> List[float]:
    """把 splatmap 权重归一化。

    块边界处各层权重之和可能不为 1，直接插值会变暗/变亮。
    全零权重退化为均匀权重，避免除零。
    """
    values = [float(w) for w in weights]
    if not values:
        return []
    total = sum(values)
    if total == 0.0:
        share = 1.0 / len(values)
        return [share] * len(values)
    return [w / total for w in values]


def normal_from_slope(dx: float, dz: float, scale: float = 1.0) -> Tuple[float, float, float]:
    """按高度梯度返回归一化法线。

    高度场 h(x, z) 的梯度为 (dx, dz)，表面法线方向为
    ``(-dx * scale, 1, -dz * scale)``，归一化后返回。
    ``scale`` 用于在视觉 LOD 与物理/高模之间统一斜率强度。
    """
    nx = -dx * scale
    ny = 1.0
    nz = -dz * scale
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0.0:  # 理论上不可能（ny 恒为 1），保守处理
        return (0.0, 1.0, 0.0)
    return (nx / length, ny / length, nz / length)


def cave_layer_height(base: float, layer: int, spacing: float) -> float:
    """返回多层洞穴指定层的高度。

    洞穴/地形洞不是单层高度图，第 ``layer`` 层（0 为地表）位于
    ``base + layer * spacing``，避免把高度图当单层导致洞内碰撞错误。
    """
    if layer < 0:
        raise ValueError("layer must be non-negative")
    return base + layer * spacing


def collision_lod_sync(visual_lod: int, physics_lod: int) -> bool:
    """判断视觉与物理 LOD 是否同步。

    远处块淡出/切换 LOD 时，物理高度采样必须与视觉 LOD 一致，
    否则会出现脚下悬空或穿模。
    """
    return visual_lod == physics_lod


def clamp_layer(layer: int, max_layer: int) -> int:
    """把纹理数组层索引钳制到有效范围。

    纹理数组层索引越界会读到错误层或触发采样失败，需钳制到
    ``[0, max_layer]``。
    """
    hi = max(int(max_layer), 0)
    return min(max(int(layer), 0), hi)


def displacement_continuous(a: float, b: float, tol: float) -> bool:
    """判断位移贴图在边界是否连续。

    相邻块/相邻 LOD 的位移值之差在容差内视为连续，
    避免 LOD 切换时位移贴图跳变。
    """
    return abs(float(a) - float(b)) <= abs(float(tol))
