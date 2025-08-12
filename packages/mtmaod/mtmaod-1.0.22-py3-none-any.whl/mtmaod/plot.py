import os

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt

from .indicator import envelope_of_expected_error, r2_score, root_mean_square_error

font_config = {
    "Default": {},
    "Times New Roman": {
        "family": "serif",
        "serif": ["Times New Roman"],
        "weight": "normal",
    },
}

style_config = {
    "single_normal": {"figsize": (3.538, 3.538), "fontsize": 10.5, "ticksize": 9},
    "single_bold": {"figsize": (5, 4.5), "fontsize": 12, "ticksize": 10.5},
    # "double_normal": {"figsize": (6.7, 5)},
    # "double_bold": {"figsize": (7.48, 6)},
}


def density_chart(
    x,
    y,
    xlabel="AOD Measured",
    ylabel="AOD Retrieved",
    title=None,
    type="kernels",
    bins=25,
    xy_max_edge=2,
    save_path=None,
    dpi=300,
    figsize=(3, 3),
    style=None,
    fontsize=9,
    ticksize=8,
):
    """绘制密度图, 来比较标签和预测值的分布情况, 使用高斯核密度(kernels)来绘制密度图 或 使用直方图(scatter or grid)来统计单位面积内的点的数量

    Parameters
    ----------
    x : list
        label
    y : list
        predict
    xlabel : str, optional
        x轴标签, by default "AOD Measured"
    ylabel : str, optional
        y轴标签, by default "AOD Retrieved"
    title : str, optional
        标题, by default None
    type : str, {"kernels", "scatter", "grid"}, optional
        要绘制的图的类型, by default "kernels"
    bins : int, optional
        直方图统计时, 每1个单位有多少个箱子, 每个箱子单位刻度为(1/bins), by default 25
    xy_max_edge : int, optional
        最大的xy显示边界, by default 2
    save_path : _type_, optional
        保存路径, 如果为None, 则直接显示, by default None
    dpi : int, optional
        分辨率, 每英寸下多少个像元, by default 300
    figsize : tuple, optional
        画布大小, 单位是英寸, by default (3, 3)
    style : _type_, optional
        风格样式, by default None
    fontsize : int, optional
        标题等的字体大小, by default 9
    ticksize : int, optional
        tick等的字体大小, by default 8

    """
    # 设置风格
    style = "single_bold" if style is None else style
    if style in style_config:
        figsize = style_config[style].get("figsize", figsize)
        fontsize = style_config[style].get("fontsize", fontsize)
        ticksize = style_config[style].get("ticksize", ticksize)
        fontname = style_config[style].get("fontname", "Times New Roman")
    # 设置字体, 默认使用Times New Roman, 如果系统中没有该字体, 则使用Matplotlib默认字体
    matplotlib_fontnames = [i.name for i in mpl.font_manager.fontManager.ttflist]
    if (fontname not in ["Default"]) and (fontname not in matplotlib_fontnames):
        print(f"Warning: 系统中没有找到{fontname}字体, 请安装该字体, 本次将使用默认字体")
        fontname = "Default"
    with mpl.rc_context():
        # 设置字体
        mpl.rc("font", **font_config[fontname])
        mpl.rcParams["font.size"] = fontsize
        mpl.rcParams["mathtext.fontset"] = "stix"

        # 设置布局
        mpl.rcParams["savefig.bbox"] = "tight"
        mpl.rcParams["figure.constrained_layout.use"] = True

        # Set x axis
        mpl.rcParams["xtick.direction"] = "in"
        mpl.rcParams["xtick.major.size"] = 3
        mpl.rcParams["xtick.major.width"] = 0.5
        mpl.rcParams["xtick.minor.size"] = 1.5
        mpl.rcParams["xtick.minor.width"] = 0.5
        mpl.rcParams["xtick.minor.visible"] = True
        mpl.rcParams["xtick.top"] = True

        # Set y axis
        mpl.rcParams["ytick.direction"] = "in"
        mpl.rcParams["ytick.major.size"] = 3
        mpl.rcParams["ytick.major.width"] = 0.5
        mpl.rcParams["ytick.minor.size"] = 1.5
        mpl.rcParams["ytick.minor.width"] = 0.5
        mpl.rcParams["ytick.minor.visible"] = True
        mpl.rcParams["ytick.right"] = True

        # 设置分辨率
        mpl.rcParams["figure.dpi"] = dpi  # plt.show显示分辨率
        mpl.rcParams["savefig.dpi"] = dpi  # plt.savefig保存分辨率

        # 设置画布
        fig, axes = plt.subplots(1, 1, figsize=figsize)

        # 设置其它参数
        axes.set_title(title)  # 设置标题
        # 设置坐标轴参数
        axes.set_xlabel(xlabel, labelpad=2)
        axes.set_ylabel(ylabel, labelpad=2)
        axes.set_xlim(-0.05, xy_max_edge + 0.05)
        axes.set_ylim(-0.05, xy_max_edge + 0.05)
        axes.set_aspect("equal")
        axes.grid(linestyle=":", color="r", alpha=0.1)
        # 设置刻度, 保证刻度不会超过xy_max_edge, 且刻度间隔为0.5
        xyticks = [i / 2 for i in range(int(xy_max_edge // 0.5) + 1)]
        xyticks = [i for i in xyticks if i <= xy_max_edge]
        xytickslables = [f"{format(i, '.1f')}" for i in xyticks]
        axes.set_xticks(xyticks)
        axes.set_yticks(xyticks)
        axes.set_xticklabels(xytickslables)
        axes.set_yticklabels(xytickslables)
        # 设置刻度字体大小
        axes.tick_params(labelsize=ticksize)

        # 将数据转为numpy数组
        x, y = np.array(x).reshape(-1), np.array(y).reshape(-1)  # x means label, y means predict
        mask = (x <= xy_max_edge) & (y <= xy_max_edge)
        print(f"数据总数: {len(x)}, 有效数据总数: {mask.sum()}, 越界数据总数: {(~mask).sum()}")

        if type in ["kernels"]:
            # 计算数据的高斯核密度分布
            from scipy.stats import gaussian_kde

            xy = np.vstack([x, y])
            z = gaussian_kde(xy)(xy)
            # 计算scatter散点的大小
            point_size = dpi / 100
            # 生成散点图图层
            ax_data = axes.scatter(x, y, marker="o", c=z, s=point_size, cmap="jet", vmin=0)

        elif type in ["scatter", "grid"]:
            # 计算数据的直方图分布
            xy_max_edge = xy_max_edge
            nbins = xy_max_edge * bins
            x = x[mask]
            y = y[mask]
            H, xedges, yedges = np.histogram2d(x, y, bins=nbins, range=[[0, xy_max_edge], [0, xy_max_edge]])

            if type == "scatter":  # 散点图
                x_index = (x * bins).astype("int")
                y_index = (y * bins).astype("int")
                z = H[x_index, y_index]
                # 获取散点大小
                axis_height = axes.xaxis.clipbox.height  # 获取坐标轴高度
                axis_length = axes.get_xlim()[1] - axes.get_xlim()[0]  # 获取坐标轴长度
                scatter_point_size = int(axis_height / (bins * (axis_length)))
                s = (scatter_point_size**2) / 4
                # 画散点图
                sort_index = np.argsort(z)
                x = x[sort_index]
                y = y[sort_index]
                z = z[sort_index]
                # 生成散点图图层
                ax_data = axes.scatter(x, y, marker=".", c=z, s=s, label="AOD scatter", cmap="jet", linewidths=0)
            elif type == "grid":  # 方格图
                # H needs to be rotated and flipped
                H = np.rot90(H)
                H = np.flipud(H)
                # Mask zeros
                Hmasked = np.ma.masked_where(H == 0, H)  # Mask pixels with a value of zero
                # Plot 2D histogram using pcolor
                ax_data = axes.pcolormesh(xedges, yedges, Hmasked, cmap="jet", vmin=1, linewidth=0)
        else:
            raise ValueError(f"没有type: {type}参数对应的画图模式")

        # 生成包络线图层
        axes.plot(
            [-1 / 3, xy_max_edge + 1],
            [-1 / 3, (xy_max_edge + 1) - (0.05 + 0.15 * (xy_max_edge + 1))],
            linestyle="--",
            color="black",
            label="EE envelopes",
            linewidth=0.5,
        )
        axes.plot(
            [-1 / 3, xy_max_edge],
            [-1 / 3, xy_max_edge + (0.05 + 0.15 * xy_max_edge)],
            linestyle="--",
            color="black",
            linewidth=0.6,
        )
        axes.plot([-1 / 3, xy_max_edge + 1], [-1 / 3, xy_max_edge + 1], linestyle="-", color="black", linewidth=0.5)

        # 生成文本图层
        # # 计算指标
        above_percent, below_percent, within_percent = envelope_of_expected_error(x, y)
        rmse = root_mean_square_error(x, y)
        r2 = r2_score(x, y) if len(x) > 1 else 0
        add_text = "\n".join(
            [
                f"$EE$ envelopes: ±(0.05+15%)",
                f"     {format(within_percent, '.1f')}% within $EE$",
                f"     {format(above_percent, '.1f')}% above $EE$",
                f"     {format(below_percent, '.1f')}% below $EE$",
                f"$RMSE$ = {format(rmse, '.3f')}",
                f"$R^2$ = {format(r2, '.3f')}",
                f"$N$ = {len(x)}",
            ]
        )
        if style in ["single_normal", "single_bold"]:
            alpha_text = 0.7
        else:
            alpha_text = 0
        axes.text(
            x=0,
            y=xy_max_edge,
            s=add_text,
            fontsize=ticksize,
            verticalalignment="top",
            color="black",
            bbox=dict(boxstyle="round", facecolor="white", alpha=alpha_text, linewidth=0.2),
        )

        # 生成图例
        lg = axes.legend(
            loc=4,
            alignment="right",
            fontsize=ticksize,
            labelspacing=0.2,
            borderpad=0.2,
            handletextpad=0.2,
            handlelength=1,
        )
        lg.get_frame().set(linewidth=0.2, edgecolor="k", alpha=0.5)

        # 生成colorbar
        cb = fig.colorbar(ax_data, ax=axes, pad=0.02, fraction=0.05)
        if type in ["scatter", "grid"]:
            cb.ax.set_title(label="Num", loc="center", fontdict={"size": ticksize}, pad=0)  # loc参数
            yticks = list(filter(lambda x: x == int(x), cb.ax.get_yticks()))
            cb.ax.set_yticks(yticks)
        else:
            cb.ax.set_title(label="Density", loc="center", fontdict={"size": ticksize}, pad=0)
        cb.ax.tick_params(labelsize=ticksize)

        # 画图
        if save_path is not None:
            # 检查保存路径父文件夹是否存在, 不存在则创建上级目录
            pic_dirpath = os.path.dirname(os.path.abspath(save_path))
            if not os.path.exists(pic_dirpath):
                os.makedirs(pic_dirpath)
            # 保存图片
            fig.savefig(save_path, dpi=dpi)
            plt.close(fig)
        else:
            # 显示图片
            plt.show()
