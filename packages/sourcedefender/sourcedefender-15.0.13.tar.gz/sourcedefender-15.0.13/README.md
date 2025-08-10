![SOURCEdefender - advanced encryption protecting your Python codebase](https://images.sourcedefender.co.uk/logo.png "SOURCEdefender - advanced encryption protecting your python3 codebase")
- - -
[![python](https://shields.io/pypi/pyversions/sourcedefender)][python-url]
[![downloads](https://pepy.tech/badge/sourcedefender)][pepy-url]
[![downloads](https://pepy.tech/badge/sourcedefender/week)][pepy-url]

SOURCEdefender is the easiest way to obfuscate Python code using AES-256 encryption. AES is a symmetric algorithm which uses the same key for both encryption and decryption (the security of an AES system increases exponentially with key length). There is no impact on the performance of your running application as the decryption process takes place during the import of your module, so encrypted code won't run any slower once loaded from a _.pye_ file compared to loading from a _.py_ or _.pyc_ file.

# Features

- No end-user device license required
- Symmetric AES 256-bit encryption
- Set your own password & salt for encryption
- Enforced an expiration time on encrypted code
- Bundle encrypted files or folders into a single executable binary using PyInstaller

## Supported Environments

We support the following Operating System and architecture combinations and hook directly into the import process, so there are no cross-platform compatibility issues. Encrypted code will run on ___ANY___ other target using the same version of Python. For example, files encrypted in Windows using Python 3.10 will run with Python 3.10 on Linux.

| CPU Architecture | Operating System | Python Architecture | Python Versions |
| ---------------- | ---------------- | ------------------- | --------------- |
| AMD64            | Windows          | 64-bit              | 3.9 - 3.13      |
| x86_64           | Linux            | 64-bit              | 3.9 - 3.13      |
| x86_64           | macOS            | 64-bit              | 3.9 - 3.13      |
| ARM64            | macOS            | 64-bit              | 3.9 - 3.13      |
| AARCH64          | Linux            | 64-bit              | 3.9 - 3.13      |

###### If you do not see your required combination here, please [contact][sourcedefender-hello-email] us so we can help find you a solution

# Trial License

The installation of SOURCEdefender will grant you a trial license to encrypt files. This trial license will only allow your script to work for a maximum of 24 hours; after that, it won't be usable. This is so you can test whether our solution is suitable for your needs. If you get stuck, then please [contact][sourcedefender-hello-email] us so we can help.

# Subscribe

To distribute encrypt code without limitation, you will need to create an [account][sourcedefender-dashboard] and set up your payment method. Once you have set up the account, you will be able to retrieve your activation token and use it to authorise your installation:

    $ sourcedefender activate --token 470a7f2e76ac11eb94390242ac130002
      SOURCEdefender

      Registration:

       - Account Status  : Active
       - Email Address   : hello@sourcedefender.co.uk
       - Account ID      : bfa41ccd-9738-33c0-83e9-cfa649c05288
       - System ID       : 42343554645384
       - Valid Until     : Sun, Apr 9, 2025 10:59 PM

Without activating your SDK, any encrypted code you create will only be usable for a maximum of __24hrs__. Access to our dashboard (via HTTPS) from your system is required so we can validate your account status.

If you want to view your activated license status, you can use the __validate__ option:

    $ sourcedefender validate
      SOURCEdefender

      Registration:

       - Account Status  : Active
       - Email Address   : hello@sourcedefender.co.uk
       - Account ID      : bfa41ccd-9738-33c0-83e9-cfa649c05288
       - System ID       : 42343554645384
       - Valid Until     : Sun, Apr 9, 2025 10:59 PM
    $

If your license is valid, this command will give the Exit Code (EC) of #0 (zero); otherwise, an invalid licence will be indicated by the EC of #1 (one). You should run this command after any automated build tasks to ensure you haven't created code with an unexpected 24-hour limitation.

## Price Plans

Our price plans are detailed on our [Dashboard][sourcedefender-dashboard]. If you do not see a price you like, please [email][sourcedefender-hello-email] us so we can discuss your situation and requirements.

# Usage

We have worked hard to ensure that the encryption/decryption process is as simple as possible. Here are a few examples of how it works and how to use the features provided. If you need advice on how to encrypt or import your code, please [contact][sourcedefender-hello-email] us for assistance.

### How do I protect my Python source code?

First, let's have a look at an example of the encryption process:

    $ cat /home/ubuntu/helloworld.py
    print("Hello World!")
    $

This is a very basic example, but we do not want anyone to get at our source code. We also don't want anyone to run this code after 1 hour so when we encrypt the file we can enforce an expiration time of 1 hour from now with the __--ttl__ option, and we can delete the plaintext .py file after encryption by adding the __--remove__ option.

The command would look like this:

    $ sourcedefender encrypt --remove --ttl=1h /home/ubuntu/helloworld.py
    SOURCEdefender

    Processing:

    /home/ubuntu/helloworld.py

    $

The TTL argument offers the following options: weeks(w), days(d), hours(h), minutes(m), and seconds(s).
Usage is for example: --ttl=10s, or --ttl=24m, or --ttl=1m, or just --ttl=3600. This can't be changed after encryption.

The '--remove' option deletes the original .py file. Make sure you use this so you don't accidentally distribute the plain-text code. Now the file is encrypted, its contents are as follows:

    $ cat /home/ubuntu/helloworld.pye
    -----BEGIN SOURCEDEFENDER FILE-----
    GhP6+FOEA;qsm6NrRnXHnlU5E!(pT(E<#t=
    GhN0L!7UrbN"Am#(8iPPAG;nm-_4d!F9"*7
    T1q4VZdj>uLBghNY)[;Ber^L=*a-I[MA.-4
    ------END SOURCEDEFENDER FILE------
    $

Once a file has been encrypted, its new extension is __.pye__ so our loader can identify encrypted files. All you need to remember is to include __sourcedefender__ as a Python dependency while packaging your project and import the sourcedefender module before you attempt to import and use your encrypted code.

### Importing packages & modules

The usual import system can still be used, and you can import encrypted code from within encrypted code, so you don't need to do anything special with your import statements.

    $ cd /home/ubuntu
    $ ls
    helloworld.pye
    $ python3
    >>>
    >>> import sourcedefender
    >>> import helloworld
    Hello World!
    >>> exit()
    $

### Using your own password or salt for encryption

It's easy to use your own encryption password and salt. If you do not set these, we generate unique ones for each file you encrypt. Should you wish to set your own, these can be set from either
a command option:

    sourcedefender encrypt --password 1234abcd --salt dcba4321 mycode.py

or as an Environment variable:

    export SOURCEDEFENDER_PASSWORD="1234abcd"
    export SOURCEDEFENDER_SALT="dcba4321"
    sourcedefender encrypt mycode.py

To import the code, you can either set an environment variable (as with the encryption process). You can also set these in your code before the import:

    $ python3
    >>> import sourcedefender
    >>> from os import environ
    >>> environ["SOURCEDEFENDER_PASSWORD"] = "1234abcd"
    >>> environ["SOURCEDEFENDER_SALT"] = "dcba4321"
    >>> import mycode

The password and salt set are specific to the next import, so if you want different ones for different files, feel free to encrypt with different values. Remember to set 'sourcedefender.password/salt=something' before your import.

### Can I still run Python from the command line?

Yes, you can still run scripts from the command line, but there are some differences due to the way Python loads command-line scripts. For example, you need to ask Python to load the sourcedefender package and then tell it what to import:

    $ python3 -m sourcedefender /home/ubuntu/helloworld.pye
    Hello World!
    $

However, due to the way Python works - and the fact that we need to run the 'sourcedefender' module first - you won't be able to compare \_\_name\_\_ == "\_\_main\_\_" in the code to see if it is being imported or executed as a script. This means that the usual starting code block will not get executed.

### Dynamic Downloads

You can download individual .pye files from a URI at runtime. As an example, we have encrypted the following script and made it publicly available:

    $ cat hello.py
    def message():
        print("hi!")
    $

To download the file from the Internet, you can use the following code example:

    $ cat download.py
    from sourcedefender.tools import getUrl
    getUrl("https://downloads.sourcedefender.co.uk/hello.pye")
    from hello import message
    message()
    $

> We can only download a single file at a time. Python packages or zip files are not supported.

When executed, this will do the following:

    $ python3 download.py
    hi!
    $

We know this is a simple example, and security can be increased by using your own salt/password.

### Integrating encrypted code with PyInstaller

PyInstaller scans your plain-text code for import statements so it knows what packages to freeze. This scanning is not possible inside encrypted code, so we have created a 'pack' command to help. However, you will need to ask PyInstaller to include any hidden libs by using the '--hidden-import' or '--add-binary' options.

We are unable to guess what parts of your code you want to encrypt. If you encrypt all your code, sometimes that stops Python from working. So, with that in mind, please ensure you encrypt your code before using the pack command.

For this example, we have the following project structure:

    pyexe.py
    lib
    └── helloworld.pye

In our pyexe script, we have the following code:

    $ cat pyexe.py
    import helloworld

To ensure that PyInstaller includes our encrypted files, we need to tell it where they are with the --add-binary option. So, for the above project, we could use this command:

    sourcedefender encrypt pyexe.py --remove
    sourcedefender pack pyexe.pye -- --add-binary $(pwd)/lib:.

There is a strange quirk with PyInstaller that we haven't yet found a workaround for. When you include extra args after '--', you need to provide full paths of the source folders otherwise, you will get a tmp folder not found error such as this:

    Unable to find "/tmp/tmpp9pt6l97/lib" when adding binary and data files.

### Integrating encrypted code with Django

You can encrypt your Django project just the same as you can any other Python code. Don't forget to include "import sourcedefender" in the __init__.py file that is in the same directory as your settings.py file. Only obfuscate your own code and not code generated by the Django commands. There is no point in protecting files such as urls.py as these should not contain much/any of your own code other than things that have been imported.

### requirements.txt

Because we only keep the last available version of a branch online, you can lock your version to a branch by including this in your requirements.txt file:

    sourcedefneder~=15.0

This will install the latest release >= 15.0.0 but less than 16.0.0, so major branch updates will need to be completed manually.


We always endeavour to keep the latest release of a branch on PyPi but there may be some reasons that we need to remove all older versions.
You should alwasys attempt to cache/mirror our SDK, please take a look at the [unearth][pypi-unearth] package which will give you a URL for the tar.gz file.

# Legal

THE SOFTWARE IS PROVIDED "AS IS," AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE. REVERSE ENGINEERING IS STRICTLY PROHIBITED.

##### __Copyright © 2018-2025 SOURCEdefender. All rights reserved.__

<!-- URLs -->
[python-url]: https://www.python.org
[pepy-url]: https://pepy.tech/project/sourcedefender
[pypi-url]: https://pypi.org/project/sourcedefender
[sourcedefender-hello-email]: mailto:hello@sourcedefender.co.uk
[sourcedefender-dashboard]: https://dashboard.sourcedefender.co.uk/signup?src=pypi-readme
[pypi-unearth]: https://pypi.org/project/unearth
