# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
from deploy.utils import run_command

baseDirStatic = ["static", "loja", "estrutura", "v1"]
minify_command = "java -jar ./yuicompressor-2.4.8.jar {all} -o {min} --charset utf-8"

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


def saveFile(sourcePaths, destPath, minPath, baseDir, header=None):
    print("Gerando arquivos {} e {}".format(destPath, minPath))
    try:
        with open(destPath, 'w') as f:
            for dirc, srcFile in sourcePaths:
                print(srcFile)
                with open(os.path.join(baseDir, dirc, srcFile)) as inputFile:
                    srcText = inputFile.read()
                f.write(srcText)

        ret = run_command(
            title=None,
            command_list=[
                {
                    'command': minify_command.format(
                        all=destPath,
                        min=minPath
                    ),
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


def minifyJS(current_dir, baseDir=baseDirStatic, source=jsSources):
    workdir = os.path.join(current_dir, *baseDir)
    jsDestPath = os.path.join(workdir, "js", "all.js")
    jsMinPath = os.path.join(workdir, "js", "all.min.js")
    return saveFile(source, jsDestPath, jsMinPath, workdir)


def minifyCSS(current_dir, baseDir=baseDirStatic, source=cssSources):
    workdir = os.path.join(current_dir, *baseDir)
    cssDestPath = os.path.join(workdir, "css", "all.css")
    cssMinPath = os.path.join(workdir, "css", "all.min.css")
    return saveFile(source, cssDestPath, cssMinPath, workdir)
