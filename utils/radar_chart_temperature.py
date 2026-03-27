import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as pe
from matplotlib import rcParams

# 字体回退，支持中文
rcParams["font.sans-serif"] = [
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans",
]
rcParams["axes.unicode_minus"] = False


def repel_texts_safe(ax, texts, rmin=0.03, rmax=1.0, max_iter=200):
    """简单径向排斥，减小重叠"""
    try:
        fig = ax.figure
        _ = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else None
    except Exception:
        pass
    for _ in range(max_iter):
        moved = False
        for i in range(len(texts)):
            ti = texts[i]
            theta_i, r_i = ti.get_position()
            for j in range(i + 1, len(texts)):
                tj = texts[j]
                theta_j, r_j = tj.get_position()
                dtheta = abs((theta_i - theta_j + np.pi) % (2 * np.pi) - np.pi)
                dr = abs(r_i - r_j)
                if dtheta < np.deg2rad(15) and dr < 0.04:
                    step = 0.01
                    if r_i >= r_j:
                        r_i = min(r_i + step, rmax - 0.01)
                        r_j = max(r_j - step, rmin)
                    else:
                        r_j = min(r_j + step, rmax - 0.01)
                        r_i = max(r_i - step, rmin)
                    ti.set_position((theta_i, r_i))
                    tj.set_position((theta_j, r_j))
                    moved = True
        if not moved:
            break


def stack_texts_by_angle(texts_info, rmin=0.03, rmax=1.0, min_sep=0.045):
    """按角度分组后沿径向堆叠修正（备用）"""
    from collections import defaultdict

    groups = defaultdict(list)
    for angle_idx, txt in texts_info:
        theta, r = txt.get_position()
        groups[angle_idx].append((r, txt))
    for angle_idx, items in groups.items():
        items.sort(key=lambda x: -x[0])
        prev_r = None
        for r, txt in items:
            target_r = max(min(r, rmax - 0.01), rmin)
            if prev_r is not None and target_r > prev_r - min_sep:
                target_r = max(prev_r - min_sep, rmin)
            theta, _ = txt.get_position()
            txt.set_position((theta, target_r))
            prev_r = target_r


def create_combined_radar_chart(
    baseline=0.0,
    mode="truncate",
    tick_step=0.20,
    label_arrange="even",  # 左图标签方式: 'even' | 'stack'
    label_arrange_right="even",  # 右图标签方式: 'point' | 'even' | 'stack'
    label_span=0.55,
    rlabel_anchor="top",  # 'top' 或 'bottom'
    title_fontsize=18,  # 标题字号
):
    """生成双雷达：左图可选堆叠/均匀分布标签，右图同策略。

    参数
    -----
    baseline : float (默认 0.0) 径向轴最小值。
    mode : 'truncate' | 'rescale' 控制是否裁剪或映射。
    tick_step : float (默认 0.20) 径向刻度间隔 (0.20=20%)。
    label_arrange : 左图标签布局 'even' | 'stack'
    label_arrange_right : 右图标签布局 'point' | 'even' | 'stack'; 'point' 表示值贴在数据点上。
    label_span : float 在 even 模式下使用的径向跨度比例。
    rlabel_anchor : 'top' 或 'bottom' 径向刻度整体放置在正上方或正下方，自动考虑 theta 偏移。
    title_fontsize : 子图标题字号（默认 18）。
    """
    # 读取数据与预处理
    df = pd.read_csv("data/temperature_processed.csv")
    metrics = ["CovL", "CovB", "CSR", "PR"]
    df_original = df.copy()
    for m in metrics:
        df_original[m] = df_original[m].str.rstrip("%").astype(float) / 100.0
    df_normalized = df.copy()
    for m in metrics:
        vals_tmp = df[m].str.rstrip("%").astype(float)
        df_normalized[m] = (vals_tmp - vals_tmp.min()) / (
            vals_tmp.max() - vals_tmp.min() + 1e-9
        )

    categories = metrics
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(16, 7), subplot_kw=dict(projection="polar")
    )
    angle_offset = np.pi / 4
    for ax in (ax1, ax2):
        ax.set_theta_offset(angle_offset)
    # 计算径向刻度放置角度（修正 offset 后仍保持视觉正上/正下）
    angle_offset_deg = np.degrees(angle_offset)
    if rlabel_anchor == "bottom":
        target_deg = 270
    else:
        target_deg = 90
    rlabel_angle_effective = (target_deg - angle_offset_deg) % 360
    fig.subplots_adjust(left=0.035, right=0.965, bottom=0.12, wspace=0.0)
    pos1 = ax1.get_position()
    pos2 = ax2.get_position()
    y0 = min(pos1.y0, pos2.y0)
    height = min(pos1.height, pos2.height)
    ax1.set_position([0.05, y0, 0.46, height])
    ax2.set_position([0.49, y0, 0.46, height])

    colors = ["#CC6666", "#66A37A", "#5F8EC1", "#8E79B8", "#A87C5A", "#E59545"]

    # 参数：左图堆叠
    STACK_MIN_SEP = 0.075
    STACK_TOP_EXTRA = 0.06
    STACK_ANGLE_JITTER = 0.02
    # 数值标签字体（可调）
    FONT_SIZE_LABEL = 12  # 放大以提升可读性
    # 根据 baseline / mode 设置绘图使用的 r 变换
    baseline = float(baseline)
    if not (0 <= baseline < 1):
        raise ValueError("baseline 必须在 [0,1) 之间，例如 0, 0.5, 0.55")

    def transform(v):
        if mode == "rescale":
            return baseline + (1 - baseline) * v  # 保留所有数据并抬高中心
        else:  # truncate
            return v

    # 径向范围上下界
    rmin, rmax = baseline, 1.0

    # 左图绘制
    texts_left = []
    texts_left_info = []
    curves_left = []
    for i, (_, row) in enumerate(df_original.iterrows()):
        raw_vals = [row[c] for c in categories]
        # 可能截断
        if mode == "truncate":
            vals = [v for v in raw_vals]
        else:  # rescale
            vals = [transform(v) for v in raw_vals]
        vals_plot = vals + [vals[0]]
        color = colors[i % len(colors)]
        ax1.plot(
            angles,
            vals_plot,
            linewidth=2.2,
            label=f"T = {row['Temperature']}",
            color=color,
            marker="o",
            markersize=4.5,
            markerfacecolor="white",
            markeredgewidth=1.0,
        )
        ax1.fill(
            angles, vals_plot, alpha=0.06, color=color, edgecolor=color, linewidth=0.8
        )
        curves_left.append((color, vals))

    # 堆叠标签逻辑（左图）
    for j in range(len(categories)):
        angle = angles[j]
        vals_here = [(vals[j], color) for color, vals in curves_left]
        if not vals_here:
            continue
        if label_arrange == "even":
            vals_here.sort(key=lambda x: -x[0])  # 保留大小顺序
            top_r_full = rmax - 0.03
            bottom_r_full = max(rmin + 0.04, baseline + 0.02)
            # 按 label_span 缩小范围
            span_full = top_r_full - bottom_r_full
            span_use = max(0.05, span_full * label_span)
            center = bottom_r_full + span_full / 2
            top_r = center + span_use / 2
            bottom_r = center - span_use / 2
            n = len(vals_here)
            if n == 1:
                r_positions = [min(top_r, max(vals_here[0][0], bottom_r))]
            else:
                r_positions = np.linspace(top_r, bottom_r, n)
            for (val, color), r_pos in zip(vals_here, r_positions):
                txt = ax1.text(
                    angle,
                    r_pos,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=FONT_SIZE_LABEL,
                    color=color,
                    fontweight="bold",
                    clip_on=False,
                    zorder=10,
                    path_effects=[pe.withStroke(linewidth=1.6, foreground="white")],
                )
                texts_left.append(txt)
                texts_left_info.append((j, txt))
        else:  # stack 模式
            vals_here.sort(key=lambda x: -x[0])
            max_val = vals_here[0][0]
            top_r = min(max_val + STACK_TOP_EXTRA, rmax - 0.02)
            available = top_r - rmin
            needed = (len(vals_here) - 1) * STACK_MIN_SEP
            sep = (
                STACK_MIN_SEP
                if needed <= available or len(vals_here) <= 1
                else available / (len(vals_here) - 1)
            )
            r_cur = top_r
            for idx_label, (val, color) in enumerate(vals_here):
                jitter_dir = (idx_label % 2) * 2 - 1
                angle_j = (
                    angle + jitter_dir * STACK_ANGLE_JITTER * (idx_label // 2 + 1) * 0.5
                )
                txt = ax1.text(
                    angle_j,
                    r_cur,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=FONT_SIZE_LABEL,
                    color=color,
                    fontweight="bold",
                    clip_on=False,
                    zorder=10,
                    path_effects=[pe.withStroke(linewidth=1.6, foreground="white")],
                )
                texts_left.append(txt)
                texts_left_info.append((j, txt))
                r_cur = max(r_cur - sep, rmin)

    if texts_left and label_arrange == "stack":
        stack_texts_by_angle(
            texts_left_info, rmin=rmin, rmax=rmax, min_sep=STACK_MIN_SEP * 0.75
        )
        repel_texts_safe(ax1, texts_left, rmin=rmin, rmax=rmax)

    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(categories, fontsize=18, fontweight="bold")
    # 径向范围
    if mode == "truncate":
        ax1.set_ylim(baseline, 1.0)
        yticks = np.arange(baseline, 1.0001, tick_step)
    else:  # rescale (显示也从 baseline 到 1，但刻度含义是映射后的真实百分比)
        ax1.set_ylim(baseline, 1.0)
        yticks = np.arange(baseline, 1.0001, tick_step)
    ax1.set_yticks(yticks)
    if mode == "rescale":
        # 逆映射到原始百分比
        labels = [f"{( (y - baseline)/(1-baseline) )*100:.0f}%" for y in yticks]
    else:
        labels = [f"{y*100:.0f}%" for y in yticks]
    ax1.set_yticklabels(labels, fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_rlabel_position(rlabel_angle_effective)
    # 左图标题（使用可调字号）
    ax1.set_title(
        "(a) Original Performance Metrics",
        fontsize=title_fontsize,
        fontweight="bold",
        pad=-40,
        y=-0.1,
    )

    # 右图：顶点标签
    texts_right = []
    curves_right = []
    for i, (_, row) in enumerate(df_normalized.iterrows()):
        raw_vals = [row[c] for c in categories]  # 0~1
        if mode == "rescale":
            vals = [transform(v) for v in raw_vals]
        else:  # truncate 直接使用原始 0~1，但会被 ylim 裁剪
            vals = raw_vals
        vals_plot = vals + [vals[0]]
        color = colors[i % len(colors)]
        ax2.plot(
            angles,
            vals_plot,
            linewidth=2.2,
            label=f"T = {row['Temperature']}",
            color=color,
            marker="o",
            markersize=4.5,
            markerfacecolor="white",
            markeredgewidth=1.0,
        )
        ax2.fill(
            angles, vals_plot, alpha=0.06, color=color, edgecolor=color, linewidth=0.8
        )
        curves_right.append((color, vals))

    # 右图：标签策略（可与左不同）
    angle_value_map = {j: [] for j in range(len(categories))}
    for color, vals in curves_right:
        for j, v in enumerate(vals):
            angle_value_map[j].append((v, color))
    if label_arrange_right == "point":
        # 每条曲线每个点，直接贴点（稍微径向外移避免压住 marker）
        delta = 0.015
        for color, vals in curves_right:
            for j, val in enumerate(vals):
                angle = angles[j]
                if mode == "rescale":
                    original_val = (val - baseline) / (1 - baseline)
                    display_text = f"{original_val:.2f}"
                else:
                    display_text = f"{val:.2f}"
                r_pos = min(val + delta, 1.0)
                txt = ax2.text(
                    angle,
                    r_pos,
                    display_text,
                    ha="center",
                    va="center",
                    fontsize=FONT_SIZE_LABEL,
                    color=color,
                    fontweight="bold",
                    clip_on=False,
                    zorder=12,
                    path_effects=[pe.withStroke(linewidth=1.6, foreground="white")],
                )
                texts_right.append(txt)
    elif label_arrange_right == "even":
        for j in range(len(categories)):
            angle = angles[j]
            arr = angle_value_map[j]
            if not arr:
                continue
            arr.sort(key=lambda x: -x[0])
            top_r_full = rmax - 0.03
            bottom_r_full = max(rmin + 0.04, baseline + 0.02)
            span_full = top_r_full - bottom_r_full
            span_use = max(0.05, span_full * label_span)
            center = bottom_r_full + span_full / 2
            top_r = center + span_use / 2
            bottom_r = center - span_use / 2
            n = len(arr)
            if n == 1:
                r_positions = [min(top_r, max(arr[0][0], bottom_r))]
            else:
                r_positions = np.linspace(top_r, bottom_r, n)
            for (val, color), r_pos in zip(arr, r_positions):
                if mode == "rescale":
                    original_val = (val - baseline) / (1 - baseline)
                    display_text = f"{original_val:.2f}"
                else:
                    display_text = f"{val:.2f}"
                txt = ax2.text(
                    angle,
                    r_pos,
                    display_text,
                    ha="center",
                    va="center",
                    fontsize=FONT_SIZE_LABEL,
                    color=color,
                    fontweight="bold",
                    clip_on=False,
                    zorder=11,
                    path_effects=[pe.withStroke(linewidth=1.6, foreground="white")],
                )
                texts_right.append(txt)
    else:  # stack
        for j in range(len(categories)):
            angle = angles[j]
            arr = angle_value_map[j]
            if not arr:
                continue
            arr.sort(key=lambda x: -x[0])
            sep = 0.06
            base_top = rmax - 0.03
            r_cur = base_top
            for idx, (val, color) in enumerate(arr):
                if mode == "rescale":
                    original_val = (val - baseline) / (1 - baseline)
                    display_text = f"{original_val:.2f}"
                else:
                    display_text = f"{val:.2f}"
                txt = ax2.text(
                    angle,
                    r_cur,
                    display_text,
                    ha="center",
                    va="center",
                    fontsize=FONT_SIZE_LABEL,
                    color=color,
                    fontweight="bold",
                    clip_on=False,
                    zorder=11,
                    path_effects=[pe.withStroke(linewidth=1.6, foreground="white")],
                )
                texts_right.append(txt)
                r_cur = max(r_cur - sep, rmin + 0.02)

    if texts_right and label_arrange_right == "stack":
        repel_texts_safe(ax2, texts_right, rmin=rmin, rmax=rmax)

    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, fontsize=18, fontweight="bold")
    if mode == "truncate":
        ax2.set_ylim(baseline, 1.0)
        yticks2 = np.arange(baseline, 1.0001, tick_step)
        labels2 = [f"{y*100:.0f}%" for y in yticks2]
    else:
        ax2.set_ylim(baseline, 1.0)
        yticks2 = np.arange(baseline, 1.0001, tick_step)
        labels2 = [f"{( (y - baseline)/(1-baseline) )*100:.0f}%" for y in yticks2]
    ax2.set_yticks(yticks2)
    ax2.set_yticklabels(labels2, fontsize=13)
    ax2.grid(True, alpha=0.3)
    ax2.set_rlabel_position(rlabel_angle_effective)
    ax2.set_title(
        "(b) Normalized Performance Metrics",
        fontsize=title_fontsize,
        fontweight="bold",
        pad=-40,
        y=-0.1,
    )

    handles, labels = ax2.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=min(3, max(1, len(labels) // 2 + len(labels) % 2)),
            fontsize=16,
            title="Temperature",
            title_fontsize=18,
        )

    plt.savefig(
        "pictures/temperature_radar.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.show()
    mode_cn = "截断" if mode == "truncate" else "重新映射"
    print(
        f"✅ Combined radar chart (baseline={baseline:.2f}, mode={mode_cn}, left={label_arrange}, right={label_arrange_right}, tick={tick_step}, span={label_span}, rlabel={rlabel_anchor}, title_fs={title_fontsize}) saved successfully!"
    )


if __name__ == "__main__":
    print(
        "Creating enhanced combined radar chart (20% ticks, top labels, compact even labels)..."
    )
    create_combined_radar_chart(
        baseline=0.0,
        mode="truncate",
        tick_step=0.20,
        label_arrange="even",
        label_arrange_right="even",
        label_span=0.55,
        rlabel_anchor="top",
        title_fontsize=18,
    )
