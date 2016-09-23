import datadog
import slackweb


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
        print("\n>> Enviando mensagens")
        print("*********************")

    def send_datadog(self, alert_type="info"):

        options = {
            'api_key': self.config['datadog_api_key'],
            'app_key': self.config['datadog_app_key']
        }

        datadog.initialize(**options)

        if self.test:
            title = "Teste. Por favor ignorar."
            text = title
            tags = ""
        else:
            title = "DEPLOY {}: {}/{}".format(
                self.action, self.repo, self.branch.name)
            text = self.commit
            tags = ["deploy"]

        datadog.api.Event.create(
            title=title,
            text=text,
            tags=tags,
            alert_type=alert_type if not self.test else "info"
        )
        print("Datadog OK")

    def send_slack(self):

        slack = slackweb.Slack(
            url=self.config['slack_url']
        )

        if self.test:
            text = "Teste. Por favor ignorar."
        else:
            text = "DEPLOY {}: {}/{}\n{}".format(
                self.action,
                self.repo,
                self.branch.name,
                self.commit
            )

        slack.notify(
            text=text,
            channel="#{}".format(
                self.config['slack_channel']) if not self.test else "#teste_automacao",
            username=self.config['slack_user'],
            icon_emoji=":{}:".format(
                self.config['slack_icon']))
        print("Slack OK")
