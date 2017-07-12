Creating a lambda project
=========================

The first step to start to use the lambda-toolkit is creating or importing a lambda project. Lambda-toolkit provides a command called ``project``, that you can invoke to create a lambda project running the command ``lt project create``::

   $ lt project create -p myLambdaProject
   Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
   [INFO] Creating the project lambda-toolkit folder '/Users/glucio/lambda-toolkit/lambdas/myLambdaProject_eu-west-1'
   [INFO] Project 'myLambdaProject' [python2.7] has been created.

Now I have my project pre-configured in ``lambdas/myLambdaProject_eu-west-1``::

   $ ls /Users/glucio/lambda-toolkit/lambdas/myLambdaProject_eu-west-1
   __init__.py index.py

.. note::
    Lambda-toolkit created also the file ``__init__.py``. Lambda-toolkit creates this file to make sure that it will be possible to load this project as module.

Now, if we list our environment, we already can see this project::

    $ lt list
    Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
    [INFO]
    [INFO] User Projects (Lambda Functions):
    [INFO] - Project:     lambda-list-buckets      Deployed: True                     Runtime:  python2.7
    [INFO] - Project:     myLambdaProject          Deployed: False                    Runtime:  python2.7

To see the project command help, just type ``lt project --help``:

   .. literalinclude:: ../lambda_toolkit/data/helps/project.txt

.. hint::

   For all the commands, you can use ``--help``. For example: ``lt invoke --help`` or ``lt queue --help``.

Listing AWS lambda projects
====================================

To list all existing AWS lambda projects in your AWS environment, you can use the command ``lt project list-aws``::

   $ lt project list-aws
   Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
   [INFO] AWS Projects (Lambda Functions):
   [INFO] - Project:     abcd                     Imported: False                    Runtime:  python2.7
   [INFO] - Project:     s3_resources             Imported: False                    Runtime:  python2.7
   [INFO] - Project:     lambda-list-buckets      Imported: True                     Runtime:  python2.7

Importing an existing AWS lambda project
========================================

To import an existing lambda project in your AWS environment, you can use the command ``lt project import``::

   $ lt project import -p s3_resources
   Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
   [INFO] Creating the project lambda-toolkit folder '/Users/glucio/lambda-toolkit/lambdas/s3_resources_eu-west-1'
   [INFO] Project s3_resources imported.


.. warning::

    Note that if you import an proxy that you already have inside lambda-toolkit, it will overwrite your local project. It can be very useful if you wish to update your local project from the lambda in the AWS, but it also can make you lose data.

Deploying a project in AWS
==========================

To deploy a project to your AWS environment, you can use the command ``lt project deploy``::

    $ lt project deploy -p myLambdaProject
    Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
    [INFO] Lambda project myLambdaProject was created and deployed.

.. note::

   Note that I didn't provide the option ``--rolename`` that is required. It happened due I previously had configured a default role using the command ``lt role --set-default``.

.. warning::

   If you already have a lambda project with this name in your AWS environment, it will be overwritten.

Setting a default role
=======================

To set a default role to be used always that you do not provide a rolename to deploy a proxy or a lambda project, you can use the command ``lt role``::

   $ lt role set-default --rolename arn:aws:iam::432811670411:role/service-role/myRoleLambda
   Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
   [INFO] Role 'arn:aws:iam::123456789000:role/service-role/myRoleLambda' is set as default now.

.. hint::

   If you define a default role, but you use the ``--rolename`` to deploy a lambda project, the rolename that you specify will preponderate.

Invoking a local lambda
========================

To invoke a lambda project locally in your machine, you can use the command ``lt project invoke``::

    $ lt invoke local --projectname myLambdaProject --event-file helloworld.json
    Initializing lambda-toolkit CLI (v0.2.10) - Region: eu-west-1 - Auth: file
    [INFO] Importing project myLambdaProject
    Hi, I'm here. Lambda-proxy is working. =)
    AWS Event ID: 11111111-1111-1111-1111-111111111111
    Event Body: {"key3": "value3", "key2": "value2", "key1": "value1"}

.. hint::

   You can customize or add new events file in the folder ``~/lambda-toolkit/invoke/events/``

Invoking a remote lambda
========================

To invoke a lambda project remotely, you can use the command ``lt project invoke remote``::

    $ lt invoke remote --event-file helloworld.json --projectname myLambdaProject
    Initializing lambda-toolkit CLI (v0.2.11) - Region: eu-west-1 - Auth: file
    [INFO] Invoking the project myLambdaProject
    START RequestId: 5a380d00-66c6-11e7-8119-9b430b7e8688 Version: $LATEST
    Hi, I'm here. Lambda-proxy is working. =)
    AWS Event ID: 5a380d00-66c6-11e7-8119-9b430b7e8688
    Event Body: {"key3": "value3", "key2": "value2", "key1": "value1"}
    END RequestId: 5a380d00-66c6-11e7-8119-9b430b7e8688
    REPORT RequestId: 5a380d00-66c6-11e7-8119-9b430b7e8688	Duration: 0.57 ms	Billed Duration: 100 ms 	Memory Size: 128 MB	Max     Memory Used: 29 MB

.. hint::

   You can invoke remotely your lambda-toolkit proxy, providing the argument ``--proxyname`` instead ``--projectname``.

Tailing a remote lambda
=======================

To tail a remote lambda project, you can use the command ``lt tail cloudwatch``::

   $ lt tail cloudwatch --loggroupname "/aws/lambda/myLambdaProject"
   Initializing tail-toolkit CLI (v0.0.5) - Region: eu-west-1
   Collecting logs in real time, starting from 5 minutes ago
   START RequestId: 8b690d74-66de-11e7-b54e-2d48a73dcaf9 Version: $LATEST
   Hi, I'm here. Lambda-proxy is working. =)
   AWS Event ID: 8b690d74-66de-11e7-b54e-2d48a73dcaf9
   Event Body: {"account": "123456789000", "region": "eu-west-1", "detail": {"state": "running", "instance-id": "i-03169cf0533d7d000"}, "detail-type": "EC2 Instance State-change Notification", "source": "aws.ec2", "version": "0", "time": "2017-07-12T08:46:05Z", "id": "812d642c-5f46-4588-9dde-bfa4478a4e78", "resources": ["arn:aws:ec2:eu-west-1:123456789000:instance/i-03169cf0533d7d000"]}
   END RequestId: 8b690d74-66de-11e7-b54e-2d48a73dcaf9
   REPORT RequestId: 8b690d74-66de-11e7-b54e-2d48a73dcaf9	Duration: 0.69 ms	Billed Duration: 100 ms 	Memory Size: 128 MB	Max Memory Used: 29 MB
   *************

.. important::

   Please note that tail can be used to any log group name in your cloudwatch environment. To tail your lambda functions you should append the lambda log group prefix ``/aws/lambda/<your lambda function name>``

.. note::

   If you want to debug your remote lambda function, you should use the ``receiver`` command instead the ``tail``.