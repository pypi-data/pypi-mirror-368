'''
Author: yuweipeng
Date: 2023-04-26 20:38:55
LastEditors: yuweipeng
LastEditTime: 2023-05-30 20:02:31
Description: 主要用于性能测试摸高，并生成统一测试报告
'''
from pathlib import *
import re
import time
import csv
import pandas as pd
from json2html import *
from decimal import Decimal
import operator
from .sh_and_os_ext import exec_cmd


run_time_list = []
scene_name_list = []
csvfile_list = []
htmlreport_list = []


def get_jmx_file(dir):
    path = Path(dir)
    jmx_files = [f.name for f in path.rglob("*.jmx")]
    return jmx_files

def get_datetime():
    '''
    获取当前日期时间，格式'20150708085159'
    '''
    return time.strftime(r'%Y%m%d%H%M%S', time.localtime(time.time()))

def combine_cli_cmd(jmx_dir, threads, loops, jmx_files=None, others_args=''):
    parent_path = Path.cwd()
    csvlog_dir = PurePath(parent_path, 'csvlog')
    report_dir = PurePath(parent_path, 'web-report')
    csvlog_path = Path(csvlog_dir)
    report_path = Path(report_dir)
    if not csvlog_path.exists():
        Path.mkdir(csvlog_path)
    if not report_path.exists():
        Path.mkdir(report_path)
    if not jmx_files:
        jmx_files = get_jmx_file(jmx_dir)
        print(jmx_files)
    cmd_list = []
    for jmx in jmx_files:
        now = get_datetime()
        suffix = f"{jmx}t{threads}Xl{loops}at{now}"
        jmx_file = Path.joinpath(jmx_dir, jmx)
        csv_file = Path.joinpath(csvlog_dir, f"{suffix}.csv")
        web_report = Path.joinpath(report_dir, suffix)
        cmd = f'jmeter -Jthreads={threads} -Jloops={loops} {others_args} -n -t {jmx_file} -l {csv_file} -e -o {web_report}'
        print(cmd)
        cmd_list.append(cmd)
    for cmd in cmd_list:
        exec_cmd(cmd)
        time.sleep(30)

def gen_summary_report(data, report_name='SummaryReport'):
    table = json2html.convert(json=data,escape=False)
    style = """
        <style type="text/css">
        html {
            font-family: sans-serif;tan
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }
        
        body {
            margin: 10px;
        }
        table {
            border-collapse: collapse;
            border-spacing: 0;
        }
        
        td,th {
            padding: 5;
        }
        
        .pure-table {
            border-collapse: collapse;
            border-spacing: 0;
            empty-cells: show;
            border: 1px solid #cbcbcb;
        }
        
        .pure-table caption {
            color: #000;
            font: italic 85%/1 arial,sans-serif;
            padding: 1em 0;
            text-align: center;
        }
        
        .pure-table td,.pure-table th {
            border-left: 1px solid #cbcbcb;
            border-width: 0 0 0 1px;
            font-size: inherit;
            margin: 0;
            overflow: visible;
            padding: .5em 1em;
        }
        
        .pure-table thead {
            background-color: #e0e0e0;
            color: #000;
            text-align: left;
            vertical-align: bottom;
        }
        
        .pure-table td {
            background-color: transparent;
        }
        
        .pure-table-bordered td {
            border-bottom: 1px solid #cbcbcb;
        }
        
        .pure-table-bordered tbody>tr:last-child>td {
            border-bottom-width: 0;
        }
        </style>
    """
    html = f"""
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                    <title>{report_name}</title>
                    {style}
                </head>
                <body><center>{table} </center></body> </html>
            """
    with open(f'{report_name}.html', 'w', encoding='utf-8') as file:
        file.writelines(html)

def filter_error(data):
    error_data = []
    for d in data:
        val = d["error%"].replace('%','')
        if Decimal(val) > 0:
            error_data.append(d)
    return error_data

def collect_jmx_csv_reports(jmx_dir, csv_dir, report_dir):
    jmx_csv_report = []
    jmx_files = get_jmx_file(jmx_dir)
    csv_files = [f.name for f in Path(csv_dir).rglob("*.csv")]
    for jmx in jmx_files:
        jmx_csv_list = [f.name for f in Path(csv_dir).rglob(f"{jmx}*.csv")]
        jmx_report_list = [f.name for f in Path(report_dir).rglob(f"{jmx}*")]
        tmp = {'jmx_file': jmx, 'csv_files': jmx_csv_list, 'report_dirs': jmx_report_list}
        jmx_csv_report.append(tmp)
    return jmx_csv_report


def deal_pt_data(jmx_dir, csv_dir, report_dir, jmx_scene=None):
    if not jmx_scene:
        jmx_scene = {}
    data = []
    jmx_csv_report = collect_jmx_csv_reports(jmx_dir, csv_dir, report_dir)
    for rows in jmx_csv_report:
        run_time = '无'
        txl = '无'
        jmx_name = rows['jmx_file']
        td_jmx = f'<a href="file:///./jmx/{jmx_name}" target="_blank">{jmx_name}</a>'
        if not rows['csv_files']:
            data.append({"执行时间": run_time,
                         "场景名": jmx_scene.get(jmx_name, ''),
                         "并发用户数(T)X循环数(L)": txl,
                         "jmx文件": td_jmx,
                         "csvLog": "无",
                         "报告详情": "无",
                         "平均响应时间（ms）": "0",
                         "99th pct": "0",
                         "tps（t/s）": "0",
                         "接收": "0",
                         "发送": "0",
                         "error%": "0"})
        else:
            for i in rows['csv_files']:
                run_time = i.split('at')[-1].split('.csv')[0]
                txl = i.split('jmx')[-1].split('at')[0]
                jmx_name = rows['jmx_file']
                td_jmx = f'<a href="./jmx/{jmx_name}" target="_blank">{jmx_name}</a>'
                td_csv = f'<a href="./csvlog/{i}" target="_blank">{i}</a>'
                td_report = "无"
                may_be_report_name = i[:-4]
                if may_be_report_name in rows['report_dirs']:
                    report = f"./web-report/{may_be_report_name}/index.html"
                    td_report = f'<a href="{report}" target="_blank">查看</a>'
                    js = f"./web-report/{may_be_report_name}/content/js/dashboard.js"
                    text = ''
                    with open(js, encoding='utf-8') as f:
                        text = f.read()
                    pat = re.compile(r'''statisticsTable.+\["Total",(.+)\], "isController": false}, "titles":''')
                    detail = re.findall(pat, text)[0].split(',')
                    error = Decimal(detail[2]).quantize(Decimal('0.00'))
                    error_pct = f'{error}%'
                    avg_time = Decimal(detail[3]).quantize(Decimal('0.00'))
                    pct_99th = Decimal(detail[-4]).quantize(Decimal('0.00'))
                    throughput = Decimal(detail[-3]).quantize(Decimal('0.00'))
                    rec = Decimal(detail[-2]).quantize(Decimal('0.00'))
                    sent = Decimal(detail[-1]).quantize(Decimal('0.00'))
                try:
                    data.append({"执行时间": run_time,
                                 "场景名": jmx_scene.get(jmx_name, ''),
                                 "并发用户数(T)X循环数(L)": txl,
                                 "jmx文件": td_jmx,
                                 "csvLog": td_csv,
                                 "报告详情": td_report,
                                 "平均响应时间（ms）": avg_time,
                                 "99th pct": pct_99th,
                                 "tps（t/s）": throughput,
                                 "接收": rec,
                                 "发送": sent,
                                 "error%": error_pct})
                except Exception as err:
                    print(err)
    sort_data = sorted(data, key=operator.itemgetter('执行时间'), reverse=False)
    return sort_data


def export_excel(data, title):
    if data:
        csv_file = f'{title}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ('执行时间', '场景名', "并发用户数(T)X循环数(L)", 'jmx文件', 'csvLog', '报告详情', '平均响应时间（ms）', '99th pct', 'tps（t/s）', '接收', '发送', "error%")
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        csv_file = pd.read_csv(csv_file)
        csv_file.to_excel(f'{title}.xlsx', sheet_name='data')


if __name__ == '__main__':
    pass
