# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
import platform
from deploy.utils import run_command

baseDirStatic = ["static", "loja", "estrutura", "v1"]
minify_command = "java -jar yuicompressor-2.4.8.jar {all} -o {min} --charset utf-8"
minify_command_windows = "java -jar yuicompressor-2.4.8.jar {all} --charset utf-8 > {min}"

jsSources = [
    ("js", "jquery-1.10.1.min.js"),
    ("js", "jquery-ui.js"),
    ("js", "bootstrap.min.js"),
    ("js", "css3-mediaqueries.js"),
    ("js", "jquery.flexslider-min.js"),
    ("js", "jquery.mask.min.js"),
    ("js", "modernizr.custom.17475.js"),
    ("js", "jquery.cookie.min.js"),
    ("js", "jquery.rwdImageMaps.min.js"),
    ("js", "main.js")
]

cssSources = [
    ("css", "bootstrap.css"),
    ("css", "font-awesome.css"),
    ("css", "font-awesome-ie7.css"),
    ("css", "font-awesome-v4.css"),
    ("css", "flexslider.css"),
    ("css", "prettify.css"),
    ("css", "es-cus.css"),
    ("css", "style.css"),
    ("css", "cores.css")
]

jsAlone = [
    ("js", "produto.js"),
    ("js", "carrinho.js"),
    ("js", "checkout.js")
]

cssAlone = [
    ("css", "tema-escuro.css"),
    ("css", "ie-fix.css")
]


def saveFile(sourcePaths, destPath, minPath, baseDir, header=None):
    print("Gerando arquivos {} e {}".format(destPath, minPath))
    try:
        with open(destPath, 'w') as f:
            for dirc, srcFile in sourcePaths:
                print(srcFile)
                with open(os.path.join(baseDir, dirc, srcFile)) as inputFile:
                    if destPath[-2:] == "js":
                        srcText = "{};\n".format(
                            inputFile.read().decode("utf-8"))
                    else:
                        srcText = inputFile.read().decode("utf-8")
                    f.write(srcText.encode("utf-8"))

        if platform.system() == "Windows":
            command = minify_command_windows
        else:
            command = minify_command

        compress_cmd = command.format(
            all=destPath,
            min=minPath
        )

        ret = run_command(
            title=None,
            command_list=[
                {
                    'command': compress_cmd,
                    'run_stdout': False
                }
            ]
        )
        if not ret:
            print("Ocorreu um erro ao gerar o Minify")
            return False
        else:
            return True
    except:
        raise
        print("Ocorreu um erro ao gerar o Minify")
        return False


def saveAlone(workdir, alone_list):
    for dirc, file in alone_list:
        destPath = os.path.join(workdir, dirc, file)
        minPath = os.path.join(workdir, dirc, "{}.min.{}".format(
            file.split(".")[0],
            file.split(".")[-1]
        ))
        print("Minificando arquivo {} para {}.".format(file, minPath))

        if platform.system() == "Windows":
            command = minify_command_windows
        else:
            command = minify_command

        compress_cmd = command.format(
            all=destPath,
            min=minPath
        )

        ret = run_command(
            title=None,
            command_list=[
                {
                    'command': compress_cmd,
                    'run_stdout': False
                }
            ]
        )
        if not ret:
            print("Ocorreu um erro ao gerar o Minify")
            return False

    return True


def minifyJS(current_dir, baseDir=baseDirStatic, source=jsSources):
    workdir = os.path.join(current_dir, *baseDir)
    jsDestPath = os.path.join(workdir, "js", "all.js")
    jsMinPath = os.path.join(workdir, "js", "all.min.js")
    ret = saveFile(source, jsDestPath, jsMinPath, workdir)
    if ret:
        return saveAlone(workdir, jsAlone)
    else:
        return ret


def minifyCSS(current_dir, baseDir=baseDirStatic, source=cssSources):
    workdir = os.path.join(current_dir, *baseDir)
    cssDestPath = os.path.join(workdir, "css", "all.css")
    cssMinPath = os.path.join(workdir, "css", "all.min.css")
    ret = saveFile(source, cssDestPath, cssMinPath, workdir)
    if ret:
        return saveAlone(workdir, cssAlone)
    else:
        return ret
