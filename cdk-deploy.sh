# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#====================================================================================
#!/bin/bash
#set -x

# Set the variables
EMAIL=$1
SAPUSER=$2
SAPPASS=$3
ACCOUNTID=`aws sts get-caller-identity|jq -r .Account`
DEPLOY_FILE="SaponawsTextractWorkflowCDK.zip"

if [ $# -ne 3 && $# -gt 4 ]
then
        echo "Synopsis: provide <your_email> <sap-user> <sap-passwd>" >&2
        echo "" >&2
        exit 1
fi

## Check if the file has been downloaded
#cd ~
#if [ ! -e $DEPLOY_FILE ]; then echo "Missing $DEPLOY_FILE"; exit 1; fi


#cd ~
#git clone https://github.com/sap-on-aws/workshop-asset.git
#if [ $? -ne 0 ]
#    then
#	echo "ERROR: Repo clone failed, aborting!"
#    exit 1
#fi

# Unzip the file 
#echo "Unziping the deployment file"
#cd sap-on-aws-documentprocessing-workflow
#unzip -o $DEPLOY_FILE
#if [ $? -ne 0 ]
#    then
#	echo "ERROR: Unzip failed, aborting!"
#    exit 1
#fi

# Change directory to SaponawsTextractWorkflowCDK
cd ~/sap-on-aws-documentprocessing-workflow

# Install latest CDK

echo "Installing latest CDK"
sudo npm install -g aws-cdk@latest
if [ $? -ne 0 ]
    then
	echo "ERROR: CDK binaries installation failed, aborting!"
    exit 1
fi

# Create the python virtual environment 

echo "Setting Python environment"
python3 -m venv .venv
if [ $? -ne 0 ]
    then
	echo "ERROR: Python environment setup failed, aborting!"
    exit 1
fi

# Activate the virtualenv
echo "Activating Python environment"
source .venv/bin/activate
if [ $? -ne 0 ]
    then
	echo "ERROR: Python environment activation failed, aborting!"
    exit 1
fi


# Install the required dependencies
echo "Installing pip"
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]
    then
	echo "ERROR: PIP upgrade failed, aborting!"
    exit 1
fi

echo "Installing requirement packages"
pip install -r requirements.txt 
if [ $? -ne 0 ]
    then
	echo "ERROR: PIP installation failed, aborting!"
    exit 1
fi

# Provision resources for the AWS CDK 
cdk bootstrap -c account=$ACCOUNTID --require-approval never
if [ $? -ne 0 ]
    then
	echo "ERROR: Bootstrap failed, aborting!"
    exit 1
fi

# Synthesize the CloudFormation template for this code
cdk synth
if [ $? -ne 0 ]
    then
	echo "ERROR: Synth failed, aborting!"
    exit 1
fi

# Deploy the infrastructure and configuration

cdk deploy --require-approval never \
        --parameters email=$EMAIL \
        --parameters sapuser=$SAPUSER \
        --parameters sappassword=$SAPPASS
if [ $? -ne 0 ]
    then
	echo "ERROR: CDK deployment failed, aborting!"
    exit 1
fi

echo "########################################################"
echo "#### Deployment successfull continue to next step ######"
echo "########################################################"

## END