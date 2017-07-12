Debugging a Lambda
------------------

To debug real events in real time, you should have at least:

* A queue (to store the events)
* A proxy (to forward the events to the queue)
* A lambda project (to process the events)

Creating a queue
----------------

To create a queue, you can use the command ``lt project queue create``::

    $ lt queue create -q myQueue
    Initializing lambda-toolkit CLI (v0.2.11) - Region: eu-west-1 - Auth: file
    [INFO] The queue 'myQueue.fifo' has been created.

.. hint::

   In any moment, you can use ``lt list`` to see all resources in your lambda-toolkit environment.


Deploying a proxy
-----------------

To deploy a proxy, you can use the command ``lt project proxy deploy``::

    $ lt proxy deploy -p myProxy -q myQueue
    Initializing lambda-toolkit CLI (v0.2.11) - Region: eu-west-1 - Auth: file
    [INFO] Lambda proxy myProxy created proxying requests to myQueue.fifo


Verifying requisites
--------------------

Let's list our environment, to check if we already have the **queue**, the **proxy** and the **lambda project**. ::

   $ lt list
   Initializing lambda-toolkit CLI (v0.2.11) - Region: eu-west-1 - Auth: file
   [INFO]
   [INFO] User Projects (Lambda Functions):
   [INFO] - Project:     s3_resources             Deployed: True                     Runtime:  python2.7
   [INFO] - Project:     myLambdaProject          Deployed: True                     Runtime:  python2.7
   [INFO] - Project:     lambda-list-buckets      Deployed: True                     Runtime:  python2.7
   [INFO]
   [INFO] SQS (Queues):
   [INFO] - Queue name:  myQueue.fifo             Used by:  myProxy
   [INFO]
   [INFO] Proxies (Lambda proxies):
   [INFO] - Proxy name:  myProxy                  Queue:    myQueue.fifo             Runtime:  python2.7

.. note::

   Note that now we have the proxy ``myProxy`` forwarding the event to ``myQueue``.

Debugging
---------

Now that you already have the all requisites to run a ``receiver``, we can execute it to start to collect our real data in real time::

    $ lt receiver collect --projectname myLambdaProject --sqsname myQueue
    Initializing lambda-toolkit CLI (v0.2.11) - Region: eu-west-1 - Auth: file
    [INFO] Importing project myLambdaProject
    [INFO] Starting the receiver using the queue myQueue.fifo
    .........


.. attention::

    You can run this command inside your IDE in Debug Mode. By this way you will be able to set break points and debug all data. If you want to just see the logs in real time, you can use the ``lt tail`` instead the ``lt receiver``.