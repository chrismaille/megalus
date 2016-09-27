from rjsmin import jsmin
from rcssmin import cssmin

baseDirStatic = "./static/loja/estrutura/v1/"

jsSources = [
    "js/jquery-1.10.1.min.js",
    "js/jquery-ui.js",
    "js/bootstrap.min.js",
    "js/css3-mediaqueries.js",
    "js/jquery.flexslider-min.js",
    "js/jquery.mask.min.js",
    "js/modernizr.custom.17475.js",
    "js/jquery.cookie.min.js",
    "js/jquery.rwdImageMaps.min.js",
    "js/main.js"
]

cssSources = [
    "css/bootstrap.css",
    "css/font-awesome.css",
    "css/font-awesome-ie7.css",
    "css/font-awesome-v4.css",
    "css/flexslider.css",
    "css/prettify.css",
    "css/es-cus.css",
    "css/style.css",
    "css/cores.css"
]


def _minifyCSS(text):
    return cssmin(text, keep_bang_comments=True)


def _minifyJS(text):
    return jsmin(text)


def saveFile(function, sourcePaths, destPath, minPath, baseDir, header=None):
    print("Gerando arquivos {} e {}".format(destPath, minPath))
    f = open(destPath, 'w')
    mf = None
    fullminText = ""
    try:
        mf = open(minPath, 'w')
        if header:
            mf.write(header)
        for srcFile in sourcePaths:
            print(srcFile)
            with open("{}{}".format(baseDir, srcFile)) as inputFile:
                srcText = inputFile.read()
                minText = function(srcText)
                if function.__name__ == "_minifyJS":
                    if not minText[-1] == ";":
                        minText += ";"
                    minText = minText.replace("\n", ";")
            f.write(srcText)
            mf.write(minText)
            fullminText += minText
    except:
        print("Ocorreu um erro ao gerar o Minify")
        return False
    finally:
        f.close()
        if mf and not mf.closed:
            mf.close()
        return True


def minifyJS(baseDir=baseDirStatic, source=jsSources):
    jsDestPath = "{}js/all.js".format(baseDir)
    jsMinPath = "{}js/all.min.js".format(baseDir)
    return saveFile(_minifyJS, source, jsDestPath, jsMinPath, baseDir)


def minifyCSS(baseDir=baseDirStatic, source=cssSources):
    cssDestPath = "{}css/all.css".format(baseDir)
    cssMinPath = "{}css/all.min.css".format(baseDir)
    return saveFile(_minifyCSS, source, cssDestPath, cssMinPath, baseDir)
