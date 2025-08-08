#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

import dash
from dash import html
import os
from flask import Flask, send_file
import threading
import time

# 示例用法
if __name__ == '__main__':
    import plotly.graph_objs as go
    from main import server_sfs

    html_dir = server_sfs.path_of("").ensure()
    figs = [
        go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers')),
        go.Figure(data=go.Bar(x=["A", "B", "C"], y=[7, 8, 9]))
    ]
    for i, fig in enumerate(figs):
        fig.update_layout(title=f"Plotly 图表 {i+1}")
        html_path = html_dir / f"my_custom_plotly_chart_{i}.html"
        fig.write_html(str(html_path))

    # 主线程动态更新数据
    t = 0
    while True:
        figs[0].data[0].y = [4+t, 5*t, 6+t]
        figs[0].update_layout(title=f"Plotly 图表 1 动态 {t}")
        html_path = html_dir / "my_custom_plotly_chart_0.html"
        figs[0].write_html(str(html_path))
        time.sleep(3)
        t += 1

# %%
