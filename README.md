# pyjvm

Yet another Java virtual machine implementation, written in pure python. Heavily inspired by Rava.

This repository is intended mainly for study purposes. It is not meant as a production-ready JVM.

# Usage

1. Download jdk
2. unjar `jdk/jre/lib/rt.jar`
3. Place `java/lang/*` in working directory
4. Compile your program with `javac`
5. Finally, `pyjvm [java class name] [arg 1] [arg 2] …`

# References

* http://www.namikilab.tuat.ac.jp/~sasada/prog/rava.html
* http://www.namikilab.tuat.ac.jp/~sasada/prog/rava2.html
* http://www.namikilab.tuat.ac.jp/~sasada/prog/rava_jp.html
* https://github.com/koichiro/rava