import boto3
import os
import datetime
from botocore.exceptions import ClientError
from git import Repo
from time import strftime, sleep
from tools.utils import print_title


class AWSManager():

    def upload_to_s3(self, artifact):
        """
        Uploads an artifact to Amazon S3
        """
        self.version_label = strftime("%Y%m%d%H%M%S")
        self.last_commit = 'New build from Bitbucket'
        try:
            current_dir = os.getcwd()
            repo = Repo(current_dir)
            last_version = repo.tags[-1].name
            if last_version:
                self.version_label = "{}-{}".format(
                    last_version,
                    self.version_label
                )
            self.last_commit = repo.head.commit.message
        except:
            print('erro ao tentar encontrar a ultima tag')

        self.bucket_key = '{}/{}-bitbucket_builds.zip'.format(
            os.getenv('APPLICATION_NAME'),
            self.version_label
        )
        try:
            client = boto3.client('s3')
        except ClientError as err:
            print("Failed to create boto3 client.\n" + str(err))
            return False

        try:
            client.put_object(
                Body=open(artifact, 'rb'),
                Bucket=os.getenv('S3_BUCKET'),
                Key=self.bucket_key
            )
        except ClientError as err:
            print("Failed to upload artifact to S3.\n" + str(err))
            return False
        except IOError as err:
            print("Failed to access artifact.zip in this directory.\n" + str(err))
            return False

        return True

    def create_new_version(self):
        """
        Creates a new application version in AWS Elastic Beanstalk
        """
        try:
            client = boto3.client('elasticbeanstalk')
        except ClientError as err:
            print("Failed to create boto3 client.\n" + str(err))
            return False

        try:
            response = client.create_application_version(
                ApplicationName=os.getenv('APPLICATION_NAME'),
                VersionLabel=self.version_label,
                Description=self.last_commit,
                SourceBundle={
                    'S3Bucket': os.getenv('S3_BUCKET'),
                    'S3Key': self.bucket_key
                },
                Process=True
            )
        except ClientError as err:
            print("Failed to create application version.\n" + str(err))
            return False

        try:
            if response['ResponseMetadata']['HTTPStatusCode'] is 200:
                return True
            else:
                print(response)
                return False
        except (KeyError, TypeError) as err:
            print(str(err))
            return False

    def deploy_new_version(self):
        """
        Deploy a new version to AWS Elastic Beanstalk
        """
        try:
            client = boto3.client('elasticbeanstalk')
        except ClientError as err:
            print("Failed to create boto3 client.\n" + str(err))
            return False

        try:
            response = client.update_environment(
                ApplicationName=os.getenv('APPLICATION_NAME'),
                EnvironmentName=os.getenv('APPLICATION_ENVIRONMENT'),
                VersionLabel=self.version_label,
            )
        except ClientError as err:
            print("Failed to update environment.\n" + str(err))
            return False

        print(response)
        return True

    def check_deployment(self):
        finished = False
        result = 'pending'
        checks = 0
        first = True
        date_start = datetime.datetime.now()
        print_title("Checking Deployment")
        while not finished and checks < 10:
            check_api = False
            if first:
                check_api = True
                first = False
            else:
                date_now = datetime.datetime.now()
                elapsed_time = date_now - date_start
                period = int(elapsed_time.total_seconds() / 60)
                if period > checks:
                    check_api = True
                    checks = period
            if check_api:
                try:
                    client = boto3.client('elasticbeanstalk')
                    response = client.describe_environment_health(
                        EnvironmentName=os.getenv('APPLICATION_ENVIRONMENT'),
                        AttributeNames=['Status', 'Causes']
                    )
                    print("Check n. {}: Status: {} Reason: {}".format(
                        period + 1, response['Status'], response["Causes"][0]
                    ))
                    if response['Status'] == "Ready":
                        finished = True
                        result = 'finished'
                except ClientError as err:
                    print(
                        "Failed to check environment deployment.\n" +
                        str(err))
                    return 'pending'

        return result

    def deploy(self):
        " Your favorite wrapper's favorite wrapper "
        if not self.upload_to_s3('/tmp/artifact.zip'):
            return False
        if not self.create_new_version():
            return False
        # Wait for the new version to be consistent before deploying
        sleep(5)
        if not self.deploy_new_version():
            return False

        status = self.check_deployment()
        return status
