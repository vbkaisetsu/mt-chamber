Available commands
=======================================================

The following commands are included in the program.


System command launcher
-------------------------------------------------------

* ``System``: Launch system command.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``command``|A command line to run.                   |
  |          |``showerr``|``True`` shows standard error.           |
  |Input     |1          |Texts given to a command line as standard input.|
  |Output    |1          |A variable to save standard output.      |


File I/O
-------------------------------------------------------

* ``Read``: Read lines from a file.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``file``   |A location of read file.                 |
  |Input     |None       |                                         |
  |Output    |1          |A variable to save each line.            |

* ``Write``: Write contents to a file.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``file``   |A location of output file.               |
  |          |``buff``   |Buffering type.                          |
  |Input     |1          |Contents to write.                       |
  |Output    |None       |                                         |


Generator
-------------------------------------------------------

* ``Echo``: Repeatedly output a specified string.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``count``  |Number of output times.                  |
  |          |``text``   |Output string.                           |
  |Input     |1          |Output until end of input.               |
  |Output    |1          |A variable to save output data.          |

* ``Seq``: Output a sequence of numbers from 0 to a specified value.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``stop``   |Upper limit.                             |
  |Input     |1          |Output until end of input.               |
  |Output    |1          |A variable to save output data.          |

* ``Random``: Repeatedly output random numbers.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``count``  |Number of output times.                  |
  |Input     |1          |Output until end of input.               |
  |Output    |1          |A variable to save output data.          |


Barkeley socket
-------------------------------------------------------

* ``ListeningSocket``: Listen on a specified ip address and port, and output socket objects when connection is arriving.（IPv4）

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``host``   |Host name.                               |
  |          |``port``   |Port number.                             |
  |          |``backlog``|A length of the connection queue.        |
  |Input     |None       |                                         |
  |Output    |1          |A socket object for a new connection.    |

* ``ShutdownSocketConnection``: Shutdown read or write direction of a socket.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``how``    |Read (``r``), write (``w``)  or both (``rw``). |
  |Input     |1          |Socket object.                           |
  |Output    |1          |Socket object.                           |

* ``CloseSocketConnection``: Close a socket.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |None       |                                         |
  |Input     |1          |Socket object.                           |
  |Output    |None       |                                         |

* ``SocketReceiveData``: Receives data using a socket.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``size``   |Maximum length of receiving data.        |
  |          |``decode`` |If you want to decode data to string, it is an encoding.|
  |Input     |1          |Socket object.                           |
  |Output    |1          |Socket object.                           |
  |          |2          |Received data.                           |

* ``SocketSendData``: Sends data using a socket.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``encode`` |If you want to encode string to data, it is an encoding.|
  |Input     |1          |Socket object.                           |
  |          |2          |Data to send.                            |
  |Output    |1          |Socket object.                           |

Example:

    ListeningSocket:ipaddr="localhost":port=1234:backlog=5 > conn
    SocketReceiveData:size=65536:decode="utf-8" < conn > conn data
    MyCommand < data > result
    SocketSendData:encode="utf-8" < conn result > conn
    CloseSocketConnection < conn


Distributed computing over SSH
-------------------------------------------------------

* ``SSHParallelWrapper``: Run some threads on other computers using SSH.

  |Field     |Name/#         |Description                              |
  |:---------|:--------------|:----------------------------------------|
  |Options   |``basecmd``    |Command name to run.                     |
  |          |``nodes``      |Semi-colon sepalated list of nodes.      |
  |          |``ssh_user``   |User name of node computers.             |
  |          |``ssh_pass``   |User's password. (Optional)              |
  |          |``rsa_keyfile``|RSA secret key file. (Optional)          |
  |          |``rsa_keypass``|Password of the specified key. (Optional)|
  |          |``node_exec``  |Node executable path. (Optional)         |
  |          |``(options)``  |Options of the specified command.        |
  |Input     |*              |(Depends on ``basecmd``)                 |
  |Output    |*              |(Depends on ``basecmd``)                 |

``nodes`` is a list of computers separated by ``;``. Each item is formatted as follows:

    hostname:port/threads

where ``port`` is omittable.

If ``ssh_pass`` or ``rsa_keypass`` is not specified and the password is required,
you will input the password in the initialization phase.
``node_exec`` is the path of ``ssh-parallel-node.py`` on nodes. If it is omitted,
it is the same path of the local executable.

Example:

    Alias SSHParallelSettings nodes="node01.example.com/10;node02.example.com/10" \
                    :ssh_user="user":rsa_keyfile="/home/user/.ssh/id_rsa"
    Alias PKyTea basecmd="System":command="kytea -notags -wsconst D"
    SSHParallelWrapper:SSHParallelSettings:PKyTea * 30 < raw > tok

In this case, 30 threads total of ``System`` commands are run.
However, 20 threads are run on other computers, and 10 threads are run on the local computer.


Debug
-------------------------------------------------------

* ``Watch``: Defines watches for ``watch`` command in the prompt mode.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``name``   |Watch's name.                            |
  |Input     |1 ...      |Data to watch.                           |
  |Output    |None       |                                         |

* ``Log``: Exports a log file.

  |Field     |Name/#     |Description                              |
  |:---------|:----------|:----------------------------------------|
  |Options   |``file``   |A location of log file.                  |
  |          |``tags``   |Names list of data separated by ``;``.   |
  |Input     |1 ...      |Data to write.                           |
  |Output    |None       |                                         |

Example:

    MyCommand < data > result
    Seq < data > counter
    Watch:name="new_watch" < counter data result
    Log:file="log.txt":tags="Data;Result" < data result
