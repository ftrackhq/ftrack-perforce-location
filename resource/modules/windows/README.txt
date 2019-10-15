This document describes how the VC11 and VC14 versions of the p4py package were 
built for the Windows platform. The VC9 version is the standard version and can 
be retrieved using pip.

VC11
========================================================
Microsoft Visual Studio Express 2012 for Windows Desktop
Version 11.0.50727.42 VSLRSTAGE
Microsoft .NET Framework
Version 4.7.03190

Installed Version: Desktop Express

1. Install and tweak OpenSSL v1.0.2s
    https://slproweb.com/download/Win64OpenSSL-1_0_2s.exe
    a) Copy and rename /lib/libeay32.lib → /lib/libeay64.lib
       Copy and rename /lib/ssleay32.lib → /lib/ssleay64.lib

2. Download p4 base libraries for VC14 here: http://ftp.perforce.com/perforce/r18.2/bin.ntx64/
    a) Pick p4api_vs2012_dyn.zip
    b) Extract it

3. Download and extract p4python
    ftp://ftp.perforce.com/perforce/r18.2/bin.tools/p4python.tgz

4. Open command prompt in p4python extracted directory (i.e. in the "p4python-2018.2.1743033" directory)

5. In the cmd prompt, setup environment:
    "C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat"

6. Establish the right Python interpreter. 
    a) Locate your installation of Maya 2016. 
    b) Make sure you downloaded and installed the devkit in the right locations
        https://www.autodesk.com/developer-network/platform-technologies/maya?_ga=2.105896448.207679052.1568130020-1501833846.1525785207
        scroll down to the Maya 2016 devkit Downloads section and pick the right one
    c) Copy <maya>/bin/mayapy.exe to <maya>/bin/python.exe 
    c) Copy <maya>/include/python2.7/*.* to <maya>/Python/include
    d) Copy <maya>/lib/python27.lib to <maya>Python/libs/python27.lib

    e) Make sure this python interpreter comes first in your PATH:
        set PATH="D:\Program Files\Autodesk\Maya2016\bin";%PATH%
    f) Type "python" in the command prompt and confirm the compiler version (MSC v.1700 64 bit (AMD64))

7. build:
   a) delete the build folder
   python setup.py build --apidir "D:\projects\ftrack-perforce-location\resource\p4python\VC11\p4api-2018.2.1832527-vs2012_dyn" --ssl "C:\OpenSSL-Win64\lib"

The resulting P4.py and P4API.pyd files are located under build\lib.win-amd64-2.7


VC14
======================================
Microsoft Visual Studio Community 2015
Version 14.0.25431.01 Update 3
Microsoft .NET Framework
Version 4.7.03190

Installed Version: Community

1. Install and tweak OpenSSL v1.0.2s
    https://slproweb.com/download/Win64OpenSSL-1_0_2s.exe
    a) Copy and rename /lib/libeay32.lib → /lib/libeay64.lib
       Copy and rename /lib/ssleay32.lib → /lib/ssleay64.lib

2. Download p4 base libraries for VC14 here: http://ftp.perforce.com/perforce/r18.2/bin.ntx64/
    a) Pick p4api_vs2015_dyn.zip
    b) Extract it

3. Download and extract p4python
    ftp://ftp.perforce.com/perforce/r18.2/bin.tools/p4python.tgz

4. Open command prompt in p4python extracted directory (i.e. in the "p4python-2018.2.1743033" directory)

5. In the cmd prompt, setup environment:
    "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\vcvars64.bat"

6. Establish the right Python interpreter. 
    a) Locate your installation of Maya 2018. 
    b) Copy <maya>/bin/mayapy.exe to <maya>/bin/python.exe 
    c) Copy <maya>/include/python2.7/*.* to <maya>/Python/include
    d) Copy <maya>/lib/python27.lib to <maya>Python/libs/python27.lib

    e) Make sure this python interpreter comes first in your PATH:
        set PATH="D:\Program Files\Autodesk\Maya2018\bin";%PATH%
    f) Type "python" in the command prompt and confirm the compiler version (MSC v.1900 64 bit (AMD64))

7. build:
    a) delete the build folder
    python setup.py build --apidir "D:\projects\ftrack-perforce-location\resource\p4python\VC14\p4api-2018.2.1832527-vs2015_dyn" --ssl "C:\OpenSSL-Win64\lib"

The resulting P4.py and P4API.pyd files are located under build\lib.win-amd64-2.7

