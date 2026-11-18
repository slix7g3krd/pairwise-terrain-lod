# pairwise-terrain-lod

大世界跨区块飞行时地表裂开、法线接缝、脚下悬空：高度图 LOD 采样没做 conservative；相邻块 LOD 级别不同但裙边高度按各自网格；splatmap 在块边界权重不归一；三平面法线用低模法线；物理高度采样用视觉 LOD；地形洞和洞穴把高度图当单层；远处块淡出时碰撞没同步；位移贴图在 LOD 切换跳变；纹理数组层索引越界；流式加载块和地形查询竞争。render/terrain_lod.py 是核心，tests/test_terrain_lod.py 15个红。要修的是：保守高度采样；裙边缝合；splatmap 权重归一；法线取高模；物理与视觉分离；多层洞穴高度；碰撞随 LOD 同步；位移连续；层索引钳制；加载屏障。

## 运行

```bash
python -m pytest tests -q
```

初始状态：15 个用例失败。修复实现使全部用例通过，不要修改 `tests/` 下的测试。

子方向：图形渲染；任务类型：Bugfix；语言/框架：Python 3, pytest；环境可复现等级：无外部依赖。
