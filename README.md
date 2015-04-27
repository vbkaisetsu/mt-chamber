# Multi-thread chamber

A framework for multi-thread pipeline process


Introduction
=======================================================

This software supports performing multi-thread pipeline processing for sequences of texts or objects by using "ChamberLang."
First of all, let's look at the following simple example.

    Read:file="./input" > inputdata
    Write:file="./output" < inputdata

Please save this code as ``./example-code``, and prepare a text file named ``./input`` with several lines.
To run this script:

    $ mt-chamber.py --threads 2 ./example-code

Then, a file named ``./output`` that has same contents with ``./input`` will be generated.

You can interpret this script as follows:

1. ``Read`` command reads lines of ``./input`` one by one, and outputs them to a variable ``inputdata``.
2. ``Write`` command writes contents of ``inputdata`` to ``./output`` one by one.

The point we should notice is that ``Write`` will begin before ``Read`` is finished.
``Read`` passes data immediately after it reads each line.

You can specify the following arguments to ``mt-chamber.py``:

* ``--threads``: Number of jobs.
* ``--unsrt-limit``: This value affects the size of queues used to transfer data between processes. It should be large enough to ``--threads``.
* ``--prompt``: Prompt mode. Displays an interactive screen during running to show progress and to debug a script.
* ``FILE``: A script file to run. If not set, standard input is read. If the prompt mode is enabled, standard input will be used for the prompt mode, so ``FILE`` has to be specified.


ChamberLang
=======================================================

ChamberLang basics
-------------------------------------------------------

A line of ChamberLang script generally consists of a command name, options, input and output variables.
If a backslash ``\`` is contained at end of line, that line will be concatenated with a next line.
If ``#`` is contained, after that symbol will be interpreted as comments.

    Command:option:option... < input variables > output variables

Input and output does not have to one variable like UNIX shell commands.
Some commands receive and export multiple data.
Available characters for I/O variables are alphanumerics and underscore, and must not start from the numbers.

Options are specified using ``OptionName=value`` forms, and multiple options are separated with ``:``.
If values are omitted, values are automatically interpreted to ``True``.
If you specify string values, they are quoted by ``" "`` or ``' '``.

Here is an example of using ``LengthCleaner`` command contained in ``plugins``:

    # Read files
    Read:file="./en.tok" > en_tok
    Read:file="./ja.tok" > ja_tok
    # Clean lines by number of words
    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok ja_tok > en_clean ja_clean
    # Write files
    Write:file="./en.clean" < en_clean
    Write:file="./ja.clean" < ja_clean

In this example, it reads two files ``./en.tok`` and ``./ja.tok`` which are corresponding to each line, and if one of both lines are longer than 80 words, these pairs are removed.

Using ``*``, you can specify the number of threads for each command individually.

    # Next command will be run on three threads regardless of --threads argument
    LengthCleaner *3 < en_tok ja_tok > en_clean ja_clean


Alias
-------------------------------------------------------

If you want to specify many options and write them in the script, its readability becomes low.
To avoid that problem, you can use ``Alias`` statement.
Alias can name long statement by using a short string.

    Alias MyCleaner LengthCleaner:maxlen1=80,maxlen2=80
    MyCleaner < en_tok ja_tok > en_clean ja_clean

``Alias`` replaces any names before interpreting scripts.


Available commands
=======================================================

Please refer [Command reference](CommandReference.md).


Command definition using Python
=======================================================

Next, let's take a look at the method to define commands using python.

To define the new command, place a python file on ``plugins/CommandName.py``.
In this file, you will define a ``Command`` class as follows:

```python
class Command:

    # Settings variable
    InputSize = 1
    OutputSize = 1
    MultiThreadable = True
    ShareResources = False

    def __init__(self, options...):
        ::::

    def routine(self, instream):
        ::::

    def hook_prompt(self, statement):
        ::::

    def kill(self):
        ::::

    def __del__(self):
        ::::
```

* **InputSize:** The size of input tuple.
* **OutputSize:** The size of output tuple.
* **MultiThreadable:** If ``True``, this command is run on multi-threads. If it is difficult to run on multi-threads like file reader/writer, please set to ``False``.
* **ShareResources:** If ``True``, resources are shared by all threads. If you want to create instance for each thread, please set to ``False``.

In ``Command`` class, you have to define at least ``routine`` function. In addition, you will define other functions.

* ``__init__``: Called when an instance of ``Command`` class is created. Instances are created specified numbers by ``MultiThreadable`` and ``ShareResources``. If ``MultiThreadable`` is ``False`` or ``ShareResources`` is ``True``, it will be generated once. Otherwise, it will be generated for each thread. In ``options...``, you can define options as normal arguments.
* ``routine``: Called when the command received data. ``instream`` is a tuple of input data, and this function will return output data as a tuple. If it returns ``None`` instead of a tuple, this command will be finished and notify it to other commands.
* ``hook_prompt``: Called when a command is input in the prompt mode. ``statement`` is a list of a command and arguments.
* ``kill``: Called when ``kill`` command is input in the prompt mode.
* ``__del__``: Called when the script is finished and an instance is discarded.

``InputSize`` and ``OutputSize`` can be defined as a function.

```python
class Command:

    def InputSize(self, size):
        ::::
            raise Exception(...)
        ::::

    ::::
```

If it is defined as a function, it will get actual number of given variables as ``size`` argument.
If ``size`` is incorrect, it raises an exception.

``example/example-script`` is a large example, and there are many example plugins in ``plugins`` directory. Please refer them.


Prompt mode
=======================================================

If ``mt-chamber.py`` is run with ``--prompt``, it shows interactive interface.

In this mode, you can input commands following to ``>>> ``.
You can run the following commands by default.

* ``watch``: Shows variables specified in ``Watch`` in script.
  ```
  watch [name...]
  ```
  |Arguments    |Description                                                                  |
  |:------------|:----------------------------------------------------------------------------|
  |``name...``  |Watch's name you want to show. If it is empty, all watches are shown.        |

* ``pause``: Pauses script.
  ```
  pause
  ```

* ``start``: Restarts paused script.
  ```
  start
  ```

* ``exit``: If the script is finished, closes the prompt. You can also do it by <kbd>CTRL</kbd>+<kbd>D</kbd>.
  ```
  exit
  ```

* ``kill``: Stops script forcely.
  ```
  kill
  ```
