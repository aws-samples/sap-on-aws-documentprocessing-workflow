from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_sns_subscriptions as subs,
    aws_sns as _sns,
    RemovalPolicy,
    aws_appflow as appflow,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    CfnParameter,
)

from constructs            import Construct
from Lambda.Lambda         import LambdaConstruct
from Roles.roles           import RolesConstruct
from CustomResource.custom import customResourceConstruct
from DataFlows.appflow import AppflowConstruct
from StepFunctions.StepFunctions import SetpFunctionsConstruct

class AwsTextractAutomationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        appflowparams = self.node.try_get_context('appflow')
        textractparams = self.node.try_get_context('textract')
        
        #CfnParameters
        snsemail = CfnParameter(self, "email", 
        type="String", 
        description="E-mail ID for SNS notificaitons")

        appflow_username = CfnParameter(self, "sapuser", 
        type="String", 
        description="SAP user name for Appflow connector")

        appflow_pwd = CfnParameter(self, "sappassword", 
        type="String", 
        no_echo=True,
        description="SAP password for Appflow connector")

        #1.Roles
        lambdarole = RolesConstruct(self, 'lamdbasuperrole')

        #2.S3 Bucket
        bucket_name="".join([textractparams.get('s3bucketname'),
        '-',
         str(self.account)])
        
        sourcebukcet = s3.Bucket(self, 'textractbucket',
        bucket_name=bucket_name,
        removal_policy=RemovalPolicy.DESTROY,
        event_bridge_enabled=True,
        auto_delete_objects=True
        )

        targetbucketname="".join([appflowparams.get('s3bucketname'),
        '-',
        str(self.account)])

        #3.S3 Target Bucket
        targetbucket = s3.Bucket(self, 'targetbucket',
        bucket_name=targetbucketname,
        removal_policy=RemovalPolicy.DESTROY,
        auto_delete_objects=True
        )

        #4.S3 Data Bucket
        databucketname="".join([appflowparams.get('databucket'),
        '-',str(self.account)
        ])

        databucket = s3.Bucket(self, 'databucket', 
        bucket_name=databucketname,
        removal_policy=RemovalPolicy.DESTROY,
        auto_delete_objects=True
        )


        databucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal('appflow.amazonaws.com')],
                actions=["s3:*"],
                resources=[databucket.bucket_arn,databucket.bucket_arn+"/*"],
                sid='Allows3Access'
            )
        )       

        targetbucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal('appflow.amazonaws.com')],
                actions=["s3:*"],
                resources=[targetbucket.bucket_arn,targetbucket.bucket_arn+"/*"],
                sid="Allows3accessforwrite"
            )
        )
        
        #5.Custom Resources
        customResourceConstruct(self, 'bucketfolder', props={
            'role': lambdarole._lambdarole,
            'bucket': targetbucket
        })

        #6.SNS Topic
        snstopic = _sns.Topic(self, 
        'sns-order-notification',
        display_name='missing-order-notification',
        topic_name='ent22-missingorder-notification'
        ) 
        
        # SNS subscription
        email = snsemail.value_as_string
        snstopic.add_subscription(subs.EmailSubscription(email_address=str(email)))

        #7.Lambda
        lambdas = LambdaConstruct(self, 'textractparser', props={
            'role': lambdarole._lambdarole,
            'sourcebucket': sourcebukcet,
            'targetbucket': targetbucket,
            'databucket': databucket.bucket_name,
            'snstopicarn': snstopic.topic_arn
        })

        #8 Appflow
        dataflows = AppflowConstruct(self,'dataflows', props={
            'username':appflow_username.value_as_string,
            'password':appflow_pwd.value_as_string,
            'data_bucket_name': databucket.bucket_name,
            'target_bucket_name': targetbucket.bucket_name,
            'account': str(self.account)
        })
    
        #9 Step functions 
        stepfunctions = SetpFunctionsConstruct(self,'order-automation',
        props={
            "lambdas": lambdas,
            "snstopic": snstopic,
            "flowname": dataflows.cfn_sap_flow.flow_name
        }) 


        # Event bridge rule
        rule = events.Rule(self,'s3-events-stepfunction',
        description="ent225-s3-textract-event",
        event_pattern=events.EventPattern(
            source=["aws.s3"],
            detail_type=["Object Created"],
            detail={ "bucket": {"name": [sourcebukcet.bucket_name]}},
            )
        )
        
        #Event bridge target
        rule.add_target(targets.SfnStateMachine(
            machine=stepfunctions._sfnstate,
            )
        )

        dataflows._cfnconnectorprofile.apply_removal_policy(policy=RemovalPolicy.DESTROY)
        dataflows.cfn_sap_flow.apply_removal_policy(policy=RemovalPolicy.DESTROY)