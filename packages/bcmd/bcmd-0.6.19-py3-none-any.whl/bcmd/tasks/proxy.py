import platform
from typing import Final

import psutil
import pyperclip
import typer
from beni import bcolor, btask
from beni.bfunc import syncCall, textToAry

app: Final = btask.app


@app.command()
@syncCall
async def proxy(
    port: int = typer.Argument(15236, help="代理服务器端口"),
):
    '生成终端设置代理服务器的命令'
    processNameAry: list[str] = []
    process = psutil.Process().parent()
    while process:
        processNameAry.append(process.name())
        process = process.parent()
    template = ''

    # 针对不同的终端使用不同的模板
    match platform.system():
        case 'Windows':
            if 'cmd.exe' in processNameAry:
                template = cmdTemplate
            elif set(['powershell.exe', 'pwsh.exe']) & set(processNameAry):
                template = powerShellTemplate
        case 'Linux':
            template = linuxShellTemplate

    btask.assertTrue(template, f'不支持当前终端（{processNameAry}）')
    lineAry = textToAry(template.format(port))
    lineAry.append('curl https://google.com.hk')
    msg = '\n'.join(lineAry)
    bcolor.printMagenta('\r\n' + msg)
    msg += '\n'  # 多增加一个换行，直接粘贴的时候相当于最后一行也执行完
    pyperclip.copy(msg)
    bcolor.printYellow('已复制，可直接粘贴使用')


# ------------------------------------------------------------------------------------


cmdTemplate = '''
    set http_proxy=http://localhost:{0}
    set https_proxy=http://localhost:{0}
    set all_proxy=http://localhost:{0}
'''

powerShellTemplate = '''
    $env:http_proxy="http://localhost:{0}"
    $env:https_proxy="http://localhost:{0}"
    $env:all_proxy="http://localhost:{0}"
'''

linuxShellTemplate = '''
    export http_proxy="http://localhost:{0}"
    export https_proxy="http://localhost:{0}"
    export all_proxy="http://localhost:{0}"
'''
