import os

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from mtmtool.extensions.matplotlib import get_scientific_style_context, savefig_with_fixed_edgesize

from .indicator import envelope_of_expected_error, pearsonr_scipy, r2_score, root_mean_square_error

example_config = {
    # 绘图开关，设置为False则不绘制对应图层
    "draw.ee_envelopes_lines": True,
    "draw.ee_equal_line": True,
    "draw.legend": True,
    "draw.indicator_text": True,
    # 一些参数
    "dpi": 300,
    "figsize": (3.6, 9),  # 宽度最重要，当aspect固定时，高度会自动调整
    "xlabel": "Measured AOD",
    "ylabel": "Retrieved AOD",
    "title": None,
    "aspect": "equal",
    # 部分细节参数
    "EE.absolute_error": 0.05,
    "EE.relative_error": 0.15,
    "indicator.text": ["EE", "RMSE", "R", "N"],
}


class AODComparisonChart:
    @staticmethod
    def add_envelope_layer(ax: Axes, ee=None, label="EE envelopes", **kwargs):
        # 生成包络线图层, default EE envelopes: ±(0.05+15%)
        # 设置默认参数
        ee = ee if ee is not None else (0.05, 0.15)
        kwargs["linestyle"] = kwargs.get("linestyle", "--")
        kwargs["color"] = kwargs.get("color", "black")
        kwargs["linewidth"] = kwargs.get("linewidth", 1)
        # 计算EE包络线的斜率和截距
        absolute_error, relative_error = ee
        slope_positive = 1 + relative_error
        point_positive = (0, absolute_error)
        slope_negative = 1 - relative_error
        point_negative = (0, -absolute_error)
        ax.axline(point_positive, slope=slope_positive, label=label, **kwargs)
        ax.axline(point_negative, slope=slope_negative, **kwargs)

    @staticmethod
    def add_equal_line_layer(ax: Axes, label="y=x line", **kwargs):
        # 设置默认参数
        kwargs["linestyle"] = kwargs.get("linestyle", "-")
        kwargs["color"] = kwargs.get("color", "black")
        kwargs["linewidth"] = kwargs.get("linewidth", 1)
        ax.axline((0, 0), slope=1, label=label, **kwargs)

    @staticmethod
    def add_kernel_density_layer(ax: Axes, x, y, point_size, cmap="jet", label=None, Normalize=False):
        # 计算数据的高斯核密度分布
        from scipy.stats import gaussian_kde

        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)

        # 归一化
        if Normalize:
            z = z / z.max()

        # 生成散点图图层
        p = ax.scatter(x, y, marker="o", c=z, s=point_size, cmap=cmap, vmin=0, label=label)
        return p

    @staticmethod
    def add_indicator_text_layer(
        ax: Axes, xdata, ydata, px=None, py=None, indicators=None, ee=None, mathuse=True, **kwargs
    ):
        # 设置默认参数
        ee = ee if ee is not None else (0.05, 0.15)
        indicators = indicators if indicators is not None else ["EE", "N"]
        kwargs["verticalalignment"] = kwargs.get("verticalalignment", "top")
        kwargs["horizontalalignment"] = kwargs.get("horizontalalignment", "left")
        kwargs["transform"] = kwargs.get("transform", ax.transAxes)
        # 计算指标
        absolute_error, relative_error = ee
        text_list = []
        for indicator in indicators:
            if indicator not in ["EE", "RMSE", "R2", "R", "N"]:
                raise ValueError(f"指标{indicator}不在支持的指标列表中")
            if indicator == "EE":
                above_percent, below_percent, within_percent = envelope_of_expected_error(
                    xdata, ydata, absolute_error=absolute_error, relative_error=relative_error
                )
                texts = [
                    f"EE envelopes: ±({absolute_error}+{int(relative_error*100)}%)",
                    f"     {format(within_percent, '.1f')}% within EE",
                    f"     {format(above_percent, '.1f')}% above EE",
                    f"     {format(below_percent, '.1f')}% below EE",
                ]
                texts = [text.replace("EE", "$EE$") if mathuse else text for text in texts]
                text_list += texts
            if indicator == "RMSE":
                rmse = root_mean_square_error(xdata, ydata)
                text = f"RMSE = {format(rmse, '.3f')}"
                text = text.replace("RMSE", "$RMSE$") if mathuse else text
                text_list.append(text)
            if indicator == "R2":
                r2 = r2_score(xdata, ydata)
                text = f"R^2 = {format(r2, '.3f')}"
                text = text.replace("R^2", "$R^2$") if mathuse else text
                text_list.append(text)
            if indicator == "R":
                r = pearsonr_scipy(xdata, ydata) if len(xdata) > 1 else 0
                text = f"R = {format(r, '.3f')}"
                text = text.replace("R", "$R$") if mathuse else text
                text_list.append(text)
            if indicator == "N":
                text = f"N = {len(xdata)}"
                text = text.replace("N", "$N$") if mathuse else text
                text_list.append(text)
        _text = "\n".join(text_list)

        if px is None or py is None:
            px, py = 0.03, 1 - 0.03  # 默认在左上角绘制
        p = ax.text(px, py, _text, **kwargs)
        return p

    @staticmethod
    def add_legend(ax: Axes, **kwargs):
        # 设置默认参数
        kwargs["alignment"] = kwargs.get("alignment", "right")
        kwargs["labelspacing"] = kwargs.get("labelspacing", 0.2)
        kwargs["borderpad"] = kwargs.get("borderpad", 0.2)
        kwargs["handletextpad"] = kwargs.get("handletextpad", 0.2)
        kwargs["handlelength"] = kwargs.get("handlelength", 1)
        kwargs["loc"] = kwargs.get("loc", "lower right")
        lg = ax.legend(**kwargs)
        lg.get_frame().set(linewidth=0.5, edgecolor="k", alpha=0.5)


def plot_default_density_kernel_chart(x, y, xy_max_edge=2, save_path=None, **kwargs):
    config = example_config.copy()
    config.update(kwargs)
    kwargs = config
    with mpl.rc_context(get_scientific_style_context(fontname="Times New Roman")):
        # 设置画布
        fig, axes = plt.subplots(1, 1, figsize=kwargs["figsize"], layout="compressed")

        # 设置其它参数
        axes.set_title(kwargs.get("title", None))  # 设置标题
        # 设置坐标轴参数
        axes.set_xlabel(kwargs.get("xlabel", None), labelpad=2)
        axes.set_ylabel(kwargs.get("ylabel", None), labelpad=2)
        axes.set_xlim(-0.05, xy_max_edge + 0.05)
        axes.set_ylim(-0.05, xy_max_edge + 0.05)
        axes.set_aspect(kwargs.get("aspect", "auto"))

        # 设置刻度, 保证刻度不会超过xy_max_edge, 且刻度间隔为0.5
        if 1.5 < xy_max_edge <= 5:
            xyticks = [i / 2 for i in range(int(xy_max_edge // 0.5) + 1)]
            xyticks = [i for i in xyticks if i <= xy_max_edge]
            xytickslables = [f"{format(i, '.1f')}" for i in xyticks]
            axes.set_xticks(xyticks)
            axes.set_yticks(xyticks)
            axes.set_xticklabels(xytickslables)
            axes.set_yticklabels(xytickslables)

        # 绘制包络线图层
        ee_errors = (kwargs["EE.absolute_error"], kwargs["EE.relative_error"])
        if kwargs["draw.ee_envelopes_lines"]:
            AODComparisonChart.add_envelope_layer(axes, label="EE envelopes", ee=ee_errors)
        if kwargs["draw.ee_equal_line"]:
            AODComparisonChart.add_equal_line_layer(axes, label="1:1 line")
        # 将数据转为numpy数组
        x, y = np.array(x).reshape(-1), np.array(y).reshape(-1)  # x means label, y means predict
        mask = (x <= xy_max_edge) & (y <= xy_max_edge)
        print(f"数据总数: {len(x)}, 有效数据总数: {mask.sum()}, 越界数据总数: {(~mask).sum()}")

        # 计算scatter散点的大小
        point_size = kwargs.get("dpi", 300) / 100
        # 生成散点图图层
        p = AODComparisonChart.add_kernel_density_layer(
            axes, x, y, point_size, cmap="jet", label="AOD points", Normalize=True
        )

        # 生成colorbar
        cb = fig.colorbar(p, ax=fig.axes, pad=0.02)
        cb.ax.set_title(label="Density", pad=7)

        # 生成文本图层
        if kwargs["draw.indicator_text"]:
            AODComparisonChart.add_indicator_text_layer(axes, x, y, indicators=kwargs["indicator.text"], ee=ee_errors)

        # 生成图例
        if kwargs["draw.legend"]:
            AODComparisonChart.add_legend(axes)

        # 画图
        if save_path is not None:
            # 检查保存路径父文件夹是否存在, 不存在则创建上级目录
            pic_dirpath = os.path.dirname(os.path.abspath(save_path))
            if not os.path.exists(pic_dirpath):
                os.makedirs(pic_dirpath)
            # 保存图片
            dpi = kwargs.get("dpi", None)
            savefig_with_fixed_edgesize(fig, save_path, fixed="width", dpi=dpi)  # 固定图片大小，基于宽度调整高度
            plt.close(fig)
            return
        else:
            return fig, axes
