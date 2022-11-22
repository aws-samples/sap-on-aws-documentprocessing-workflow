from aws_cdk import(
 aws_lambda as _lambda,
 Duration,
 aws_s3 as s3,
 aws_s3_notifications as s3_notifications,
)
import os
from   os import path

from constructs import Construct

class LambdaConstruct(Construct):
    def __init__(self, scope:Construct, id:str,props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        __dirname = (os.path.dirname(__file__))
        appflowparams = dict(self.node.try_get_context('appflow'))
        
        targetbucketname = props['targetbucket'].bucket_name
        self._documentparser = _lambda.Function(
            self, 'documentparser',
            description='Lambda to parse document and lookup',
            function_name='ent225-sfn-documentparser',
            architecture=_lambda.Architecture.X86_64,
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset(path.join(__dirname, './documentparser')),
            handler='parsedocument.handler',
            environment={
            'DATA_BUCKET': props['databucket']
            },
            memory_size=2048,
            timeout=Duration.seconds(900),
            role=props['role']
        )

        self._writetos3 = _lambda.Function(
            self, 'createjsonlines',
            description='Lambda to analyze document and parse using texract',
            function_name='ent225-write-jsonln-to-s3',
            architecture=_lambda.Architecture.X86_64,
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset(path.join(__dirname, './writetos3')),
            handler='createjsonln.handler',
            environment={
                'APPFLOW_TARGET_BUCKET': targetbucketname,
                'APPFLOW_TARGET_BUCKET_PREFIX': appflowparams.get('prefix')
            },
            memory_size=2048,
            timeout=Duration.seconds(900),
            role=props['role']
        )

        """
        #All functions are embeeded to this lambda
        #TextAnalysis, lookup, SNS notification, write to S3 target 
        self._textractparser = _lambda.Function(
            self, 'textractparser',
            description='Lambda to analyze document and parse using texract',
            function_name='textractparaser',
            architecture=_lambda.Architecture.X86_64,
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset(path.join(__dirname, './textract')),
            handler='textract.handler',
            environment={
                'APPFLOW_TARGET_BUCKET': targetbucketname,
                'APPFLOW_TARGET_BUCKET_PREFIX': appflowparams.get('prefix'),
                'SNSTOPICARN': props['snstopicarn'],
                'DATA_BUCKET': props['databucket']
            },
            memory_size=2048,
            timeout=Duration.seconds(900),
            role=props['role']
        )

        bucket =props['sourcebucket']
        notification = s3_notifications.LambdaDestination(self._textractparser)
        notification.bind(self, bucket)
        bucket.add_object_created_notification(notification, s3.NotificationKeyFilter(suffix='.pdf'))
        """






