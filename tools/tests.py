# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import unittest
import os
from tools.config import get_config_data
from tools.compress import minifyJS, minifyCSS
from tools.messages import Message
from tools.utils import run_command
from os.path import expanduser
from unittest.mock import Mock


class TestDeploy(unittest.TestCase):

    maxDiff = None

    def test_ler_arquivo_config(self):
        self.assertIsInstance(
            get_config_data(filename="test_tool"),
            dict
        )
        filepath_test = "{}/.test_tool".format(expanduser("~"))
        self.assertTrue(
            os.path.isfile(filepath_test)
        )

    def teste_compress_JS(self):
        response = 'console.log("Olá Mundo");function teste(){var a=1;if(a>0){console.log("número positivo")}else{console.log("número menor ou igual a zero");a=a-1}};teste();console.log("fim");'
        source = [
            'js/javascript_file01.js',
            'js/javascript_file02.js'
        ]

        minifyJS(
            baseDir="./test_files/",
            source=source
        )

        with open("./test_files/js/all.min.js") as test_file:
            line = test_file.read()

        self.assertEqual(
            line,
            response
        )

    def teste_compress_CSS(self):
        response = '.teste,#id01{display:flex;justify-content:flex-start}p{font-family:"Times New Roman",Georgia,Serif;color:rgba(255,255,128,10)}@media screen and (min-width:480px){body{background-color:lightgreen}}'
        source = [
            'css/css_file01.css',
            'css/css_file02.css'
        ]

        minifyCSS(
            baseDir="./test_files/",
            source=source
        )

        with open("./test_files/css/all.min.css") as test_file:
            line = test_file.read()

        self.assertEqual(
            line,
            response
        )

    def test_send_message_datadog(self):
        result = "DEPLOY TESTE: repositorio_teste/teste\nteste de envio"

        fake_branch = Mock()
        fake_branch.name = "teste"

        config = get_config_data()
        message = Message(
            config=config,
            branch=fake_branch,
            commit="teste de envio",
            repo="repositorio_teste",
            action="TESTE",
            test=True)

        self.assertEqual(
            message.send_datadog(),
            result
        )

    def test_send_message_slack(self):
        result = "DEPLOY TESTE: repositorio_teste/teste\nteste de envio"

        fake_branch = Mock()
        fake_branch.name = "teste"

        config = get_config_data()
        message = Message(
            config=config,
            branch=fake_branch,
            commit="teste de envio",
            repo="repositorio_teste",
            action="TESTE",
            test=True)

        self.assertEqual(
            message.send_slack(),
            result
        )

    def test_run_command(self):
        self.assertTrue(
            run_command(
                title="TESTE",
                command_list=[
                    {
                        'command': "ls",
                        'run_stdout': False
                    }
                ]
            )
        )
