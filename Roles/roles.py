from aws_cdk import(
 aws_iam as iam
)
from constructs import Construct

class RolesConstruct(Construct):
    def __init__(self, scope:Construct, id:str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._lambdarole = iam.Role(self,'textracelambdarole',
        assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))

        self._lambdarole.add_managed_policy(iam.ManagedPolicy.\
            from_managed_policy_arn(self,
            'LambdaInVPC',
            'arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole' ))

        self._lambdarole.add_managed_policy(iam.ManagedPolicy.\
            from_aws_managed_policy_name('AdministratorAccess'))
