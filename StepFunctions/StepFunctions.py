from aws_cdk import(
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
      aws_iam as iam,
)


from constructs import Construct

class SetpFunctionsConstruct(Construct):
    def __init__(self, scope:Construct, id:str,props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

            # Task 1
        textractts = tasks.CallAwsService(self,'textract-analyze',
        input_path="$.detail",
        service="textract",
        action="analyzeDocument",
        parameters={
            "Document": {
                "S3Object":{
                "Bucket.$": "$.bucket.name",
                "Name.$": "$.object.key"
                } 
            },
            "FeatureTypes": ["FORMS", "TABLES"]
        },
        additional_iam_statements=[iam.PolicyStatement(
            actions=["s3:*"],
            resources=["*"]
        )],
        iam_resources=["*"],
        result_path="$.textract"
        )

        #Step function definition
        defintion = textractts.next(
          tasks.LambdaInvoke(self, 'parsedocument',
          lambda_function=props['lambdas']._documentparser,
          payload=sfn.TaskInput.from_json_path_at("$.textract"),
          output_path="$.Payload"
          ).next(
          sfn.Choice(self, 'order matched?').when(
            sfn.Condition.string_equals("$.orderfound", "TRUE"),
             tasks.LambdaInvoke(self, 'writedatatos3',
             lambda_function=props['lambdas']._writetos3,
             output_path="$.Payload").next(
              tasks.CallAwsService(
                self, 'writetosap',
                service="Appflow",
                action="startFlow",
                parameters={
                  "FlowName": props["flowname"]
                },
                iam_resources=["*"]
              )
             )
          ).when(
            sfn.Condition.string_equals("$.orderfound", "FALSE"),
            tasks.SnsPublish( self,'Missing order notification',
            topic=props['snstopic'],
            message=sfn.TaskInput.from_json_path_at(
            "States.Format('Order {} extracted from the doucment could not be matched',$.order)"
            ),
            subject="ENT225 Missing order notification"
            )
          )
          )
        )
    
        # Step function state machine
        self._sfnstate = sfn.StateMachine(self,'textract-workflow',
        state_machine_name='ent225-textract-workflow',
        definition=defintion
        )

        
