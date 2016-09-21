Performance Testing
===================

This describes only performance tests of the desired API endpoint. The goal is to run a load test and benchmark how many concurrent requests this code can handle reliably without starting to return errors. Ideally, this should be at least 1000 concurrent requests.


Preparation
-----------

For these tests a popular tool named ``siege`` is used, see https://www.joedog.org/siege-home/ for installation procedure. On Mac OS X it can be conveniently installed using ``brew install siege``.

Siege comes with its own configuration settings in the directory ``~/.siege/``. It runs load tests by sending requests (concurrently and/or repeatedly) to a website, and has a default limit of 255 concurrent users. So, for these tests you must change in ``~/.siege/siege.conf`` the variable ``limit`` to something around 1000, like 1023. (For even higher numbers you might have to change process-related parameters of the operating system, too.)

A sample run of ``siege`` for GET requests on google.com would look like below. Notice, that if you do this with high numbers of concurrent users (``-c``) and/or repetitions (``-r``) you might find you IP blocked by Google, very soon! 

.. code-block:: bash

    $ siege -c5 -r2 "http://www.google.com/"
    ** SIEGE 4.0.2
    ** Preparing 5 concurrent users for battle.
    The server is now under siege...
    HTTP/1.1 302     0.06 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.06 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.07 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.07 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.07 secs:     258 bytes ==> GET  /
    HTTP/1.1 200     0.15 secs:   45040 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV6WrIKuK8Qe6y6K4Bw
    HTTP/1.1 200     0.17 secs:   45038 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV-ejIKyK8QfU_LLwDQ
    HTTP/1.1 200     0.17 secs:   45074 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV4GlIKmK8Qe0z6nwCA
    HTTP/1.1 200     0.17 secs:   45088 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV5OpIKaK8QelrYCwBQ
    HTTP/1.1 200     0.19 secs:   45047 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV_qoIKuK8Qe6y6K4Bw
    HTTP/1.1 302     0.06 secs:     258 bytes ==> GET  /
    HTTP/1.1 200     0.16 secs:   45040 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV-rOLamK8Qe0z6nwCA
    HTTP/1.1 302     0.06 secs:     258 bytes ==> GET  /
    HTTP/1.1 200     0.16 secs:   45074 bytes ==> GET  /?gfe_rd=cr&ei=QTDNV7XpN6yK8QfU_LLwDQ
    HTTP/1.1 302     0.05 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.06 secs:     258 bytes ==> GET  /
    HTTP/1.1 302     0.08 secs:     258 bytes ==> GET  /
    HTTP/1.1 200     0.15 secs:   45035 bytes ==> GET  /?gfe_rd=cr&ei=QjDNV8f7B6uK8Qe6y6K4Bw
    HTTP/1.1 200     0.17 secs:   45085 bytes ==> GET  /?gfe_rd=cr&ei=QjDNV8-7DKyK8QfU_LLwDQ
    HTTP/1.1 200     0.17 secs:   45046 bytes ==> GET  /?gfe_rd=cr&ei=QjDNV46OD6OK8Qfrz4eoDg

    Transactions:                 20 hits
    Availability:             100.00 %
    Elapsed time:               1.27 secs
    Data transferred:               0.43 MB
    Response time:              0.12 secs
    Transaction rate:              15.75 trans/sec
    Throughput:                 0.34 MB/sec
    Concurrency:                1.81
    Successful transactions:          20
    Failed transactions:               0
    Longest transaction:            0.19
    Shortest transaction:           0.05

Appologies for the non-aligned values in the second column of the results... For brevity, all further invocations of ``siege`` in the Snowdonia context will not list any single requests made.

Since providing URLs on the command-line can be laborious and error-prone, ``siege`` also accepts them from a separate file, so the above example could be also executed like this (with single requests removed from the output): 

.. code-block:: bash

    $ cat urls.txt
    http://www.google.com/

    $ siege -c5 -r2 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 5 concurrent users for battle.
    The server is now under siege...

    Transactions:                 20 hits
    Availability:             100.00 %
    Elapsed time:               1.23 secs
    Data transferred:               0.43 MB
    Response time:              0.13 secs
    Transaction rate:              16.26 trans/sec
    Throughput:                 0.35 MB/sec
    Concurrency:                2.07
    Successful transactions:          20
    Failed transactions:               0
    Longest transaction:            0.20
    Shortest transaction:           0.05


Local Test Results
------------------

In this section the implemented microservice is tested while running locally on a development machine (in this case a MacBook Pro running Mac OS X). Before you reproduce these tests, please make sure, you have a database and the service is running locally (see the other document named Manual)! Also, the debug value in ``config.ini`` is set to ``False``.

Without loss of generality, and because only the performance needs to be tested, all further test runs use the same location data to be posted, including a vehicle UID, ``11111111-1111-1111-1111-111111111111``, easy to spot in the database if needed.

Since the vehicles send data only once every 20 seconds the tests can vary the number of concurrent requests, and let the number of repetitions at one.

.. code-block:: bash

    $ cat urls.txt
    http://localhost:5000/data POST uid=00000000-0000-0000-0000-000000000000&type=bus&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=42

    $ siege -c100 -r1 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 100 concurrent users for battle.
    The server is now under siege...

    Transactions:                100 hits
    Availability:             100.00 %
    Elapsed time:               0.67 secs
    Data transferred:               0.00 MB
    Response time:              0.10 secs
    Transaction rate:             149.25 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               15.13
    Successful transactions:         100
    Failed transactions:               0
    Longest transaction:            0.19
    Shortest transaction:           0.01

    $ siege -c500 -r1 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 500 concurrent users for battle.
    The server is now under siege...

    Transactions:                500 hits
    Availability:             100.00 %
    Elapsed time:               2.21 secs
    Data transferred:               0.00 MB
    Response time:              0.01 secs
    Transaction rate:             226.24 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                1.18
    Successful transactions:         500
    Failed transactions:               0
    Longest transaction:            0.03
    Shortest transaction:           0.00

    $ siege -c1000 -r1 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               1000 hits
    Availability:             100.00 %
    Elapsed time:              12.79 secs
    Data transferred:               0.00 MB
    Response time:              0.00 secs
    Transaction rate:              78.19 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                0.24
    Successful transactions:        1000
    Failed transactions:               0
    Longest transaction:            0.04
    Shortest transaction:           0.00

When increasing the number of repetitions, errors start appearing at five repeated requests per 1000 concurrent users:

.. code-block:: bash

    $ cat urls.txt
    http://localhost:5000/data POST uid=00000000-0000-0000-0000-000000000000&type=bus&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=42

    $ siege -c1000 -r4 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               4000 hits
    Availability:             100.00 %
    Elapsed time:              13.79 secs
    Data transferred:               0.02 MB
    Response time:              0.07 secs
    Transaction rate:             290.07 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               20.62
    Successful transactions:        4000
    Failed transactions:               0
    Longest transaction:            0.24
    Shortest transaction:           0.00

    $ siege -c1000 -r5 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...
    [error] unable to write to socket sock.c:637: Broken pipe
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] unable to write to socket sock.c:637: Broken pipe

    Transactions:               4997 hits
    Availability:              99.94 %
    Elapsed time:              14.33 secs
    Data transferred:               0.02 MB
    Response time:              0.13 secs
    Transaction rate:             348.71 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               45.09
    Successful transactions:        4997
    Failed transactions:               3
    Longest transaction:            0.43
    Shortest transaction:           0.00

For comparison, these are a few tests with a GET endpoint, returning the string ``done`` and doing nothing else. Here errors start appearing at 10 repetitions:

.. code-block:: bash

    $ siege -c1000 -r10 "http://localhost:5000/simple" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:              10000 hits
    Availability:             100.00 %
    Elapsed time:              14.69 secs
    Data transferred:               0.04 MB
    Response time:              0.03 secs
    Transaction rate:             680.74 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               18.67
    Successful transactions:       10000
    Failed transactions:               0
    Longest transaction:            0.13
    Shortest transaction:           0.00

    $ siege -c1000 -r10 "http://localhost:5000/simple" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    ...
    [error] unable to write to socket sock.c:637: Broken pipe
    [error] unable to write to socket sock.c:637: Broken pipe
    [error] unable to write to socket sock.c:637: Broken pipe
    [error] unable to write to socket sock.c:637: Broken pipe

    Transactions:               9966 hits
    Availability:              99.66 %
    Elapsed time:              14.21 secs
    Data transferred:               0.04 MB
    Response time:              0.03 secs
    Transaction rate:             701.34 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               24.53
    Successful transactions:        9966
    Failed transactions:              34
    Longest transaction:            4.10
    Shortest transaction:           0.00


Remote Test Results
-------------------

In this section the same tests are performed on a remote AWS EC2 instance, run from a local ``siege``, which is the most expected use case (running ``siege`` on the remote instance, too, would rather not be the normal use case).

So, to reproduce these tests, you need to have a remote instance created and all software fully deployed to it, and the service itself started (see the other document named Manual). Note that the IP address for the remote server in the ``urls.txt`` file will most likely be different for your instance!

.. code-block:: bash

    $ cat urls.txt
    http://52.57.59.147:5000/data POST uid=00000000-0000-0000-0000-000000000000&type=bus&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=42

    $ siege -c1000 -r1 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               1000 hits
    Availability:             100.00 %
    Elapsed time:              12.65 secs
    Data transferred:               0.00 MB
    Response time:              0.07 secs
    Transaction rate:              79.05 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                5.88
    Successful transactions:        1000
    Failed transactions:               0
    Longest transaction:            0.11
    Shortest transaction:           0.06

    $ siege -c1000 -r2 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               2000 hits
    Availability:             100.00 %
    Elapsed time:              13.12 secs
    Data transferred:               0.01 MB
    Response time:              0.43 secs
    Transaction rate:             152.44 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               65.78
    Successful transactions:        2000
    Failed transactions:               0
    Longest transaction:            1.24
    Shortest transaction:           0.07

Significant errors start appearing at three repeated requests per 1000 concurrent users:

.. code-block:: bash

    $ siege -c1000 -r3 -f urls.txt > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    ...
    [error] socket: 138964992 connection timed out.: Operation timed out

    Transactions:               2587 hits
    Availability:              86.23 %
    Elapsed time:              41.78 secs
    Data transferred:               0.01 MB
    Response time:              3.66 secs
    Transaction rate:              61.92 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:              226.75
    Successful transactions:        2587
    Failed transactions:             413
    Longest transaction:           35.21
    Shortest transaction:           0.07


Tests With Alternative Servers
------------------------------

This section contains two additional tests to compare the performance for the simplest GET request of the Snowdonia implementation (using Flask, a minimalist synchronous web application framework) in this archive with an equally simple GET request using other web frameworks.

The first other framework is an pure Python asynchronous web server, ``aiohttp``, see http://aiohttp.readthedocs.io/en/stable/web.html. The file ``serve_aiohttp.py`` is basically a copy of this code, which you can run like this:

.. code-block:: bash

    $ ~/mc3/bin/python3 serve_aiohttp.py
    ======== Running on http://0.0.0.0:8080/ ========
    (Press CTRL+C to quit)

    $ siege -c1000 -r10 "http://0.0.0.0:8080/" > out.txt

Running the same GET test with ``siege`` on it like at the end of the section *Local Test Results* above, shows a very similar performance:

.. code-block:: bash

    $ siege -c1000 -r1 "http://0.0.0.0:8080/" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               1000 hits
    Availability:             100.00 %
    Elapsed time:              12.60 secs
    Data transferred:               0.01 MB
    Response time:              0.00 secs
    Transaction rate:              79.37 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                0.14
    Successful transactions:        1000
    Failed transactions:               0
    Longest transaction:            0.11
    Shortest transaction:           0.00

    $ siege -c1000 -r10 "http://0.0.0.0:8080/" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:              10000 hits
    Availability:             100.00 %
    Elapsed time:              12.89 secs
    Data transferred:               0.11 MB
    Response time:              0.02 secs
    Transaction rate:             775.80 trans/sec
    Throughput:                 0.01 MB/sec
    Concurrency:               14.76
    Successful transactions:       10000
    Failed transactions:               0
    Longest transaction:            0.16
    Shortest transaction:           0.00

A final comparison was conducted against an equally simple GET example running on ``node.js``, which on Mac OS X can be conveniently installed using ``brew install node``. 

.. code-block:: bash

    $ node serve_mini.js
    Server listening on: http://localhost:8080

    $ siege -c1000 -r1 "http://0.0.0.0:8080/" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:               1000 hits
    Availability:             100.00 %
    Elapsed time:              12.80 secs
    Data transferred:               0.02 MB
    Response time:              0.00 secs
    Transaction rate:              78.12 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                0.04
    Successful transactions:        1000
    Failed transactions:               0
    Longest transaction:            0.02
    Shortest transaction:           0.00

    $ siege -c1000 -r10 "http://0.0.0.0:8080/" > out.txt
    ** SIEGE 4.0.2
    ** Preparing 1000 concurrent users for battle.
    The server is now under siege...

    Transactions:              10000 hits
    Availability:             100.00 %
    Elapsed time:              13.11 secs
    Data transferred:               0.21 MB
    Response time:              0.00 secs
    Transaction rate:             762.78 trans/sec
    Throughput:                 0.02 MB/sec
    Concurrency:                0.60
    Successful transactions:       10000
    Failed transactions:               0
    Longest transaction:            0.02
    Shortest transaction:           0.00

Increasing the number of repeated requests beyond 10 leads to a growing number of failed requests also in this case (results are skipped from this report).


Summary
-------

The above findings suggest that the API endpoint implemented in this code can handle a load of 1000 concurrent requests without problems as desired, even repeated up to four times. When comparing the POST request with a simple GET request, the latter shows higher performance which is to be expected since there are no POST parameters to handle or save into a database. 

A remote instance of type ``t2.micro`` starts showing errors at three repeated requests compared to five repeated requests on the local development machine. This might be largely due to the added network latency. For the remote tests on an AWS instance type ``t2.micro`` the results were as satisfactory as those obtained on the local machine.

It could be expected that choosing increasingly more powerful machines in the same series like ``t2.small``, ``t2.medium``,  ``t2.large`` or even those of other series (``x...``) will result in even better performance. Only one more such test using the more performant instance type ``t2.medium`` was conducted, but didn't improve the results significantly.

Finally, a comparisson between the web application framework (Flask) selected for the Snowdonia code in this archive (although only the simplest possible GET request) with an asynchronous Python webserver as well as with Node.js (often recommended for asynchronous web servers) shows very similar performance results. It can be argued that this is because the example used for making these comparissons was "too simple" and lacking any possibility for asynchronous code to show any benefits. This could be verified only with more complex example code implemented multiple times for the respective framework, which is, of course, a more laborious task and, sadly, outside the reach of such a code challenge.
