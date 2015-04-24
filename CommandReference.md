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
  |Options   |``ipaddr`` |Listening ip addres.                     |
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
