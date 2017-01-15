import datadog
import platform
import requests
import slackweb
from tools import settings
from tools.utils import run_command, unitext


class Message():
    def __init__(
            self,
            config,
            branch,
            commit,
            repo,
            action,
            test=False,
            *args,
            **kwargs):
        self.config = config
        self.branch = branch
        self.commit = commit
        self.repo = repo
        self.test = test
        self.action = action
        print("\033[1m\033[93m\n>> Enviando mensagens")
        print("*********************\033[0m")

    def send(self, alert_type="info"):
        if settings.USE_DATADOG:
            self.send_datadog(alert_type)
        if settings.USE_SLACK:
            self.send_slack()
        if settings.USE_GRAFANA:
            self.send_grafana()

    def send_datadog(self, alert_type):

        options = {
            'api_key': self.config['datadog_api_key'],
            'app_key': self.config['datadog_app_key']
        }

        title = "DEPLOY {}: {}/{}".format(
            self.action, self.repo, self.branch.name)
        text = self.commit
        tags = ["deploy"]

        if not self.test:
            datadog.initialize(**options)
            datadog.api.Event.create(
                title=title,
                text=text,
                tags=tags,
                alert_type=alert_type if not self.test else "info"
            )
            print("Datadog OK")
        else:
            return "{}\n{}".format(title, text)

    def send_slack(self):

        text = "DEPLOY {}: {}/{}\n{}".format(
            self.action,
            self.repo,
            self.branch.name,
            self.commit
        )

        if not self.test:
            slack = slackweb.Slack(
                url=self.config['slack_url']
            )

            slack.notify(
                text=text,
                channel="#{}".format(
                    self.config['slack_channel'])
                if not self.test else settings.TEST_CHANNEL,
                username=self.config['slack_user'],
                icon_emoji=":{}:".format(
                    self.config['slack_icon']))
            print("Slack OK")
        else:
            return text

    def send_grafana(self):
        if self.action == "INICIADO":
            status = "started"
            value = 1
        else:
            status = "ended"
            value = 0

        post_data = "{},action=deploy,user={},"
        "repo={},status={},env={} value={}".format(
            settings.GRAFANA_APP,
            self.config['slack_user'],
            self.repo,
            status,
            self.branch,
            value
        )
        if not self.test:
            try:
                ret = requests.post(
                    settings.GRAFANA_MSG_URL, data=post_data, headers={
                        "Content-Type":
                        "application/x-www-form-urlencoded"}, timeout=1)
                if ret.status_code == requests.codes.ok:
                    print("Grafana OK")
                else:
                    print("Ocorreu um erro ao "
                          "tentar enviar mensagem ao Grafana")
            except:
                print("Ocorreu um erro ao tentar enviar mensagem ao Grafana")
        else:
            return "Passou pelo Grafana"


def notify(msg, title=None):
    if not title:
        title = "{}-Tools".format(settings.TERMINAL_CMD.upper())
    if platform.system().lower() == 'linux':  # Linux
        run_command(
            command_list=[
                {
                    'command': 'notify-send '
                    '-i gsd-xrandr {title} {msg}'.format(
                        title='"{}"'.format(
                            unitext(title)),
                        msg='"{}"'.format(
                            unitext(msg))),
                    'run_stdout': False}],
            get_stdout=True,
            title=None)
    elif platform.system().lower() != "windows":  # Mac
        run_command(
            command_list=[
                {
                    'command': "osascript -e "
                    "'display notification {msg} "
                    "with title {title}'".format(
                        title='"{}"'.format(
                            unitext(title)),
                        msg='"{}"'.format(
                            unitext(msg))),
                    'run_stdout': False
                }
            ],
            get_stdout=False,
            title=None)
