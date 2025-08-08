import os
from pathlib import Path
from typing import Final

from beni import btask, bpath
from beni.bfunc import syncCall
from typer import Argument, Option

app: Final = btask.newSubApp('项目相关')


@app.command()
@syncCall
async def init(
    path: Path = Argument(Path.cwd(), help='workspace 路径'),
    deep: int = Option(3, '--deep', '-d', help='探索深度'),
):
    '找出项目执行初始化 pnpm install 和 uv sync --all-extras'

    initSubFolder(path, deep)


def initSubFolder(path: Path, deep: int):
    uvLockFile = path / 'uv.lock'
    pnpmLockFile = path / 'pnpm-lock.yaml'
    if uvLockFile.exists():
        with bpath.changePath(path):
            os.system('uv sync --all-extras')
    elif pnpmLockFile.exists():
        with bpath.changePath(path):
            os.system('pnpm install')
    elif deep > 1:
        for subPath in bpath.listDir(path):
            initSubFolder(subPath, deep - 1)
