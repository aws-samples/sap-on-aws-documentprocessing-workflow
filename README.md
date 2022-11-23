
## Intelligently process your documents and automate your SAP business processes using Amazon AppFlow and AWS native services

Manual document processing is time-consuming and error-prone. Intelligent Document Processing techniques have grown tremendously, allowing us to extract, classify, identify, and process unstructured data. With ML powered services such as Amazon Textract building an IDP solution has become much easier and doesn’t require specialized ML skills.  

You can quickly automate document processing and act on the information extracted, whether you’re automating order processing or extracting information from invoices and receipts. You can also further automate your SAP business processes by feeding back the enriched data into SAP application using Amazon Appflow.

This post focuses on how you can use Amazon AI services in combination with Amazon AppFlow to analyze content stored in documents, automatically extract order information, and ultimately feed this information back into the SAP  system.

## Architecture
![architecture](/aws-idp-sap-integration.png)

This project is intended to be sample code only. Not for use in production.

This project will create the following in your AWS cloud environment specified:
* S3 Buckets
* Appflow Data flows 
* Appflow connector profile 
* AWS Step Functions
* SNS Topic
* Event Bridge Rule
* Lambda

## Deploying the CDK Project

This project is set up like a standard Python project.  For an integrated development environment (IDE), use `AWS Cloud9 environment` to create python virtual environment for the project with required dependencies.  

1. Launch your AWS Cloud9 environment.

2.  Clone the github repository and navigate to the directory.

```
$ git clone https://github.com/aws-samples/sap-on-aws-documentprocessing-workflow

$ cd sap-on-aws-documentprocessing-workflow
```
To manually create a virtualenv 

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Bootstrap your AWS account for CDK. Please check [here](https://docs.aws.amazon.com/cdk/latest/guide/tools.html) for more details on bootstraping for CDK. Bootstraping deploys a CDK toolkit stack to your account and creates a S3 bucket for storing various artifacts. You incur any charges for what the AWS CDK stores in the bucket. Because the AWS CDK does not remove any objects from the bucket, the bucket can accumulate objects as you use the AWS CDK. You can get rid of the bucket by deleting the CDKToolkit stack from your account.

```
$ cdk bootstrap -c account=<YOUR ACCOUNT ID> -c region=<YOUR AWS REGION>
```

Deploy the stack to your account. Make sure your CLI is setup for account ID and region provided in the appConfig.json file.

```
$ cdk deploy \
--parameters email=<YOUR E-MAIL ID> \
--parameters sapuser=<YOUR SAP USER> \
--parameters sappassword=<YOUR SAP PASSWORD>
```

## Cleanup

In order to delete all resources created by this CDK app, run the following command

```
cdk destroy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!