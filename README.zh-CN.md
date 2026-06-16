> **免责声明**
> 本项目为粉丝自制作品，与 Atlus Co., Ltd. 或 SEGA Corporation 无关，未经其认可或赞助。
> 本仓库中的所有视觉素材均为作者原创。视觉风格受游戏《Persona 5》启发，但不包含任何
> 来自游戏的受版权保护的素材、商标或专有材料。
>
> *Persona 5* 及 *Persona* 系列为 Atlus Co., Ltd. 的商标。

# P5 Phantom — Persona 5 风格 fcitx5 输入法皮肤

受《Persona 5》UI 风格启发的 fcitx5 输入法皮肤。

- 黑色标签形面板 + 厚实白色外框 + 右侧钝角箭头
- 选中候选为红色矩形 + 白色文字
- 所有 SVG 素材由 `scripts/generate_assets.py` 参数化生成
- 可安全开源分发（不包含任何官方游戏素材）

## 预览

![P5 Phantom fcitx5 皮肤预览](./docs/preview.png)

## 安装

```bash
# 1. 克隆或下载本仓库

# 2. 生成素材（可选 —— dist/ 下已有预生成文件）
python scripts/generate_assets.py

# 3. 复制皮肤到 fcitx5 主题目录
mkdir -p ~/.local/share/fcitx5/themes/
cp -r dist/p5-phantom-skin ~/.local/share/fcitx5/themes/

# 4. 设置主题
# 方式 A：使用 fcitx5-configtool
fcitx5-configtool
#    → 附加组件 → 经典用户界面 → 主题 → 选择 "P5 Phantom"

# 方式 B：直接编辑配置文件
# ~/.config/fcitx5/conf/classicui.conf
# Theme=P5 Phantom
# DarkTheme=P5 Phantom

# 5. 重启 fcitx5
fcitx5 -r
```

## 推荐字体

皮肤本身不捆绑字体。要获得最佳效果，推荐使用粗体无衬线字体：

```ini
# ~/.config/fcitx5/conf/classicui.conf
Font="Noto Sans CJK SC Bold 13"
```

如需更装饰性的 P5 风格，可自行安装 **P5 Hatty** 字体（仅限个人使用）并设置为字体。
**请勿将 P5 Hatty 字体文件与本项目一起分发。**

## 开发

编辑 `scripts/generate_assets.py` 可调整颜色、边框粗细、箭头形状等参数：

```bash
python scripts/generate_assets.py
cp -r dist/p5-phantom-skin ~/.local/share/fcitx5/themes/
fcitx5 -r
```

## 项目结构

```text
p5-skin/
├── scripts/
│   └── generate_assets.py      # 参数化 SVG 生成器
├── dist/
│   └── p5-phantom-skin/        # 可直接安装的 fcitx5 主题
│       ├── theme.conf
│       ├── panel.svg
│       ├── highlight.svg
│       ├── menu-panel.svg
│       ├── menu-highlight.svg
│       ├── arrow.svg
│       └── checkbox.svg
├── docs/
│   ├── IMPLEMENTATION.md       # 实现方案
│   └── preview.png             # 截图预览
└── README.md
```

## 许可证

MIT 许可证。详见 [LICENSE](./LICENSE)。
