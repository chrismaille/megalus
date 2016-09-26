from slimit import minify
from rcssmin import cssmin

baseDirStatic = "./static/loja/estrutura/v1/"
jsDestPath = "{}js/all.js".format(baseDirStatic)
jsMinPath = "{}js/all.min.js".format(baseDirStatic)

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

cssDestPath = "{}css/all.css".format(baseDirStatic)
cssMinPath = "{}css/all.min.css".format(baseDirStatic)

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
    return minify(text, mangle=True, mangle_toplevel=True)


def saveFile(function, sourcePaths, destPath, minPath, header=None):
    print "Gerando arquivos %s e %s" % (destPath, minPath)
    f = open(destPath, 'w')
    mf = None
    try:
        mf = open(minPath, 'w')
        if header:
            mf.write(header)
        for srcFile in sourcePaths:
            print(srcFile)
            with open("{}{}".format(baseDirStatic, srcFile)) as inputFile:
                srcText = inputFile.read()
                minText = function(srcText)
            f.write(srcText)
            mf.write(minText)
    except:
        print("Ocorreu um erro ao gerar o Minify")
        return False
    finally:
        f.close()
        if mf and not mf.closed:
            mf.close()
        return True


def minifyJS():
    return saveFile(_minifyJS, jsSources, jsDestPath, jsMinPath)


def minifyCSS():
    return saveFile(_minifyCSS, cssSources, cssDestPath, cssMinPath)
