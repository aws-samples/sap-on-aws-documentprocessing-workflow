from aws_cdk import(
aws_lambda as _lambda,
aws_logs as _logs,
Duration,
CustomResource,
custom_resources as cr
)
import os
from   os import path

from constructs import Construct

class customResourceConstruct(Construct):
    def __init__(self, scope:Construct, id:str,props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        __dirname = (os.path.dirname(__file__))

        appflowparams = dict(self.node.try_get_context('appflow'))
        textractparams = dict(self.node.try_get_context('textract'))
        self._lambdaevent = _lambda.Function(self,'lambdabackeds3',
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.from_asset(path.join(__dirname, './customResource')),
        handler='s3CustomResource.handler',
        environment={
            'APPFLOW_BUCKET_NAME': props['bucket'].bucket_name,
            'BUCKET_PREFIX': appflowparams.get("prefix"),
        },
        memory_size=2048,
        timeout=Duration.seconds(900),
        role=props['role']
        )

        self.s3CustomResourceProvider = cr.Provider(self, 's3CustomResourceProvider',
        on_event_handler=self._lambdaevent,
        log_retention=_logs.RetentionDays.ONE_DAY)


        self.s3CustomResource = CustomResource(self, 's3CustomResource',
        service_token=self.s3CustomResourceProvider.service_token
        )



