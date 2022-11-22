#!/usr/bin/env python3
import os
import aws_cdk as cdk
import uuid

from aws_textract_automation.aws_textract_automation_stack import AwsTextractAutomationStack
app = cdk.App()
env = cdk.Environment(account=app.node.try_get_context('account'),
region=app.node.try_get_context('region'))
stackname = app.node.try_get_context('stackname')
AwsTextractAutomationStack(app,stackname,env=env)
app.synth()
