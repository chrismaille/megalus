import datadog
from slacker import Slacker


class Message():
    def __init__(self, config, branch, commit, *args, **kwargs):
        self.config = config
        self.branch = branch
        self.commit = commit

    def send_datadog(self, alert_type="info"):

        options = {
            'api_key': self.config['datadog_api_key'],
            'app_key': self.config['datadog_app_key']
        }

        datadog.initialize(**options)

        title = "DEPLOY INICIADO: {}/{}".format("XXX", self.branch.name)
        text = self.commit
        tags = ["deploy"]

        datadog.api.Event.create(
            title=title,
            text=text,
            tags=tags,
            alert_type=alert_type
        )

    def send_slacker(self, channel="teste_automacao"):
        slack = Slacker(self.config['slack_api_key'])

        text = "DEPLOY INICIADO: {}/{}\n{}".format(
            "XXX",
            self.branch.name,
            self.commit
        )

        slack.chat.post_message('#{}'.format(channel), text)
