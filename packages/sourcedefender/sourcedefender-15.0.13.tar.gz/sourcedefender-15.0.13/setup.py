from struct import calcsize
from setuptools import setup
from os import path, chdir, getcwd, remove
from platform import machine, system
from sys import version_info, executable

chdir(path.abspath(path.dirname(__file__)))


def read(filename):
    try:
        with open(filename, 'rb') as fp:
            data = fp.read().decode('utf-8')
    except UnicodeDecodeError:
        with open(filename, 'r') as fp:
            data = fp.read()
    return data


def find_version(file_paths):
    version_file = read(file_paths)
    import re
    version_match = re.search(
        r"^##\s(.*)$",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


def get_package_data_list():

    # from platform import machine, system, architecture
    # from sys import version_info
    # from struct import calcsize
    # from os import path
    # if architecture()[0].lower() == "64bit":
    #     bit_size = 64
    # else:
    #     bit_size = 32

    # PLATFORM = path.join(system().lower()+str(bit_size), machine().lower(), str(
    #     version_info.major)+str(version_info.minor))

    # _find_all_files = ['__init__.py', '__main__.py']
    # from os import walk, path, remove
    # from shutil import copyfile, SameFileError
    # path_to_check = path.join('src', 'ext', PLATFORM)
    # print("Checking:", path_to_check)
    # if path.isdir(path_to_check):
    machine_name = machine().lower()
    arch_bit = int(calcsize("P")*8)
    if system().lower() == "linux":

        if machine().lower() == "x86_64":
            pass
            # ends_with = "linux-gnu.so"

        elif machine().lower() == "aarch64":
            pass

        # elif machine().lower().startswith("arm"):
        #     pass
            # machine_name = "armv6l"
            # ends_with = "arm-linux-gnueabihf.so"

    elif system().lower() == "windows":

        if machine().lower() == "amd64":
            pass
            # ends_with = "win_amd64.pyd"

    elif system().lower() == "darwin":

        if machine().lower() == "amd64":
            pass
            # ends_with = "darwin.so"

        elif machine().lower() == "arm64":
            pass
            # ends_with = "darwin.so"

    _find_all_files = ['__init__.py', '__main__.py']
    from os import walk, path, remove
    from shutil import copyfile, SameFileError
    path_to_check = path.join('src', 'ext', system().lower(
    ), machine_name, str(arch_bit), str(version_info.major) + str(version_info.minor))
    if path.isdir(path_to_check):
        for root, subfiles, files in walk(path_to_check):
            del subfiles
            for file in files:
                try:
                    copyfile(path.join(root, file), path.join('src', file))
                    _find_all_files.append(file)
                except SameFileError:
                    pass

        changelog = "CHANGELOG.md"
        if path.exists(changelog):
            try:
                copyfile(changelog, path.join('src', changelog))
                _find_all_files.append(changelog)
            except SameFileError:
                pass

    else:
        raise RuntimeError(
            "\n\n\n\n\nPlease contact hello@sourcedefender.co.uk for assistance\nPath: "+path_to_check+"\n\n\n\n")

    return _find_all_files


def get_requirements():
    requirements = []
    requirements.append("setuptools")
    for P in open("requirements.txt").readlines():
        # if P.lower().startswith("pyinstaller") and system().lower() == "darwin" and machine().lower() == "arm64":
        #    pass
        # else:
        requirements.append(P)
    return requirements


setup(
    name="sourcedefender",
    version=find_version('CHANGELOG.md'),
    python_requires="!=2.*,>=3.9",
    description='Advanced encryption protecting your python codebase.',
    long_description=read(path.join(getcwd(), 'README.md')) + '\n',
    long_description_content_type="text/markdown",
    author='SOURCEdefender',
    author_email="hello@sourcedefender.co.uk",
    keywords="encryption source aes",
    packages=['sourcedefender'],
    package_dir={'sourcedefender': 'src'},
    package_data={'sourcedefender': get_package_data_list()},
    install_requires=list(get_requirements()),
    url="https://sourcedefender.co.uk/?src=pypi-url",
    setup_requires=['setuptools', 'wheel'],
    project_urls={
        'Dashboard': 'https://dashboard.sourcedefender.co.uk/login?src=pypi-navbar',
    },
    license='Proprietary',
    entry_points={
        'console_scripts': [
            'sourcedefender = sourcedefender.encrypt:main',
        ]
    },
    options={
        'build_scripts': {
            'executable': executable,
        },
    },
    zip_safe=False,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',

        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',

        'Programming Language :: Python :: Implementation :: CPython'
    ],
)

for file in get_package_data_list():
    if not file.endswith(".py"):
        full_path_file = path.join('src', file)
        if path.exists(full_path_file):
            remove(path.join('src', file))
