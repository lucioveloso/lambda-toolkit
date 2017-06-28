# lambda-toolkit

Welcome to lambda-toolkit. 

The lambda-toolkit is a command line tool that helps the developers in: 

* Creating 
* Developing
* Debug (In real time with real events using Lambda-toolkit proxy)
* Testing
* Deploying

Basically lambda-toolkit proxy make you able to run and debug your lambda functions in your own machine, even inside your IDE.

After you get your lambda function tested and ready to use, you can easily deploy the final version to AWS.

## Getting Started

#### Prerequisites

* Python 2.7
* Git client
* AWS account configured in your user profile

#### Installing

```
[~/] $ git clone https://github.com/lucioveloso/lambda-toolkit.git
[~/] $ cd Lambda-toolkit
[~/Lambda-toolkit/] $ ./lt
```

## How the Lambda-toolkit proxy works

![Alt text](https://s3-eu-west-1.amazonaws.com/lucio-public-bucket/lambda-proxy-diagram.png "How it works")
* You can see the image in https://s3-eu-west-1.amazonaws.com/lucio-public-bucket/lambda-proxy-diagram.png if it's not available here.

## Usage

Lambda-toolkit offers a lot of resources around your lambda environment. You can see the available commands in lambda toolkit just running the binary without arguments.

```
[~/Lambda-toolkit/] $ ./lt
```

## Using lambda-toolkit proxy

You can create your resources manually (Queue, Lambda Proxy and your Lambda Project) or use the "create-star" to create using only one command.

#### - Creating manually:

Create a default lambda role to be used in lambdas
```
[~/Lambda-toolkit/] $ ./lt set-default-role -r arn:aws:iam::123456789012:role/service-role/myLambdaRole 
```
Create a queue to store the events
```
[~/Lambda-toolkit/] $ ./lt create-sqs testQueue 
```
Deploy a lambda-proxy to forward the events to the queue
```
[~/Lambda-toolkit/] $ ./lt deploy-lambda-proxy -l testLambdaProxy -q testQueue
```
Create a project to start to code your lambda function
```
[~/Lambda-toolkit/] $ ./lt create-project -p myLambdaProject
```
Run a receiver making your lambda project process the events in the queue
```
[~/Lambda-toolkit/] $ ./lt receiver -p myLambdaProject -q testQueue
```

#### - Creating using "create-star" (One-step)

Create a default lambda role to be used in lambdas
```
[~/Lambda-toolkit/] $ ./lt set-default-role -r arn:aws:iam::123456789012:role/service-role/myLambdaRole 
```
Create the queue, deploy the lambda-proxy and create a project in one command
```
[~/Lambda-toolkit/] $ ./lt create-star -p myProject
```

## Availables commands

###### list

List all configuration in your lambda-toolkit environment.

###### create-sqs

Create a SQS in your AWS environment.

Required argument(s):

* sqsname: SQS Queue name to be created.

###### delete-sqs

Create a SQS in your AWS environment.

Required argument:

* sqsname: SQS Queue name to be removed.

###### deploy-lambda-proxy

Deploy a Lambda-tookit Lambda function with lambda-proxy content.

Required arguments:

* lambdaname: The lambda name to be created in your AWS environment.
* sqsname: SQS Queue name to be redirected the requests.

###### undeploy-lambda-proxy

Remove the Lambda-tookit Lambda function with lambda-proxy content.

Required argument:

* lambdaname: The lambda name to be removed in your AWS environment.

###### create-project

Create a Lambda Project in your Lambda-toolkit environment.

Required argument:

* projectname: The lambda name to be created in your Lambda-toolkit environment.

###### delete-project

Delete a Lambda Project in your Lambda-toolkit environment.

Required argument:

* projectname: The lambda name to be removed in your Lambda-toolkit environment.

###### deploy-project

Deploy in your AWS environment your Lambda Project.

Required argument:

* projectname: The lambda name to be created in your AWS environment.

###### undeploy-project

Undeploy from your AWS environment your Lambda Project.

Required argument:

* projectname: The lambda name to be removed in your AWS environment.

###### import-project

Import to Lambda-tookit an existing lambda project from your AWS environment.

Required argument:

* projectname: The lambda name to be imported in from your AWS environment.

###### create-star

Create in one command the Queue, the Lambda Proxy and a Lambda Project to you.

Required argument:

* projectname: This projectname will be used to create the 3 resources.

###### delete-all-configuration

Clean up all queues and lambda-proxy from AWS Lambda toolkit and AWS environment.

* No argument required.

###### receiver

Run an existing project receiving information from an existing queue. (Better to run inside any IDE, to get a rich debug experience)

Required arguments:

* projectname: The name of project that will be invoked to process an event collected in the queue.
* queuename: The queue to get the events.

## Default help
```
 * List projects:                 ./lt list
 * Add SQS:                       ./lt create-sqs [-q] --sqsname <queuename>
 * Delete SQS:                    ./lt delete-sqs [-q] --sqsname <queuename>
 * Deploy Lambda Proxy:           ./lt deploy-lambda-proxy [-l] --lambdaname <lambdaname> [-q] --sqsname <queuename> [-r] --rolename <rolename>
 * Undeploy Lambda proxy:         ./lt undeploy-lambda-proxy [-l] --lambdaname <lambdaname>
 * Create a new lambda project:   ./lt create-project [-p] --projectname <projectname>
 * Delete a lambda project:       ./lt delete-project [-p] --projectname <projectname>
 * Deploy a lambda project:       ./lt deploy-project [-p] --projectname <projectname>[-r] --rolename <rolename>
 * Undeploy a lambda project:     ./lt undeploy-project [-p] --projectname <projectname>
 * Import a lambda project:       ./lt import-project [-p] --projectname <projectname>
 * Set a default role to lambdas: ./lt set-default-role [-r] --rolename <rolename> 
 * Create star (All)              ./lt create-star [-p] --projectname <projectname> [-r] --rolename <rolename>
 * Remove all proxies and queues  ./lt delete-all-configuration
 * Receive and Process queue:     ./lt receiver [-p] --projectname <projectname> [-q]--sqsname <queuename>
```
## To do list

* Create the receiver in others languages (NodeJS, Java...) - Maybe put even the python receiver in a different file.
* Create response events templates to several services, and make it available as module to the lambda-toolkit projects.

## Authors

* **Lucio Veloso Guimaraes** - *Initial work*
