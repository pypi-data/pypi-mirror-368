#%% init project env
import esypro
local_sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

from .main import sfs

import dash
from dash import html, dcc
import os
from flask import Flask, send_file

def show_multiple_html_with_dash(port=8051):
    server = Flask(__name__)
    html_dir = sfs.path_of('').ensure()

    def get_html_files():
        # 返回 [(path, mtime)]
        return [(str(p), os.path.getmtime(p)) for p in html_dir.get_files(".html", list_r=True)]

    # 初始文件列表
    html_files = get_html_files()

    # 注册所有路由
    for idx, (html_path, _) in enumerate(html_files):
        route = f"/show_html_{idx}"
        server.add_url_rule(route, route, lambda html_path=html_path: send_file(html_path))

    app = dash.Dash(__name__, server=server)
    app.layout = html.Div([
        html.H3(f"{html_dir} 下所有 HTML 文件动态显示（智能刷新）"),
        dcc.Interval(id="interval_main", interval=1000, n_intervals=0),
        html.Div([
            html.Iframe(
                id=f"iframe_{idx}",
                src=f"/show_html_{idx}",
                style={"width": "100%", "height": "600px", "border": "none"}
            )
            for idx in range(len(html_files))
        ], id="all_iframes")
    ])

    from dash.dependencies import Input, Output, State

    # 状态缓存
    last_files = html_files.copy()

    @app.callback(
        Output("all_iframes", "children"),
        Input("interval_main", "n_intervals"),
        State("all_iframes", "children"),
    )
    def update_iframes(n, children):
        nonlocal last_files
        new_files = get_html_files()
        new_paths = [p for p, _ in new_files]
        last_paths = [p for p, _ in last_files]

        # 检查新增/删除
        if set(new_paths) != set(last_paths):
            last_files = new_files.copy()
            # 注册新路由
            for idx, (html_path, _) in enumerate(new_files):
                route = f"/show_html_{idx}"
                if route not in server.view_functions:
                    server.add_url_rule(route, route, lambda html_path=html_path: send_file(html_path))
            return [
                html.Iframe(
                    id=f"iframe_{idx}",
                    src=f"/show_html_{idx}",
                    style={"width": "100%", "height": "600px", "border": "none"}
                )
                for idx in range(len(new_files))
            ]
        # 检查内容变化（mtime变化）
        elif any(m1 != m2 for (_, m1), (_, m2) in zip(new_files, last_files)):
            updated_children = children.copy()
            for idx, ((path, m_new), (_, m_old)) in enumerate(zip(new_files, last_files)):
                if m_new != m_old and idx < len(children):
                    updated_children[idx]['props']['src'] = f"/show_html_{idx}?t={n}"
            last_files = new_files.copy()
            return updated_children
        else:
            # 无变化
            return children

    app.run(debug=True, port=port)

if __name__ == '__main__':
    show_multiple_html_with_dash()
