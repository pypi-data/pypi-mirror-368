import os

def ensure_java_ready():
    try:
        import jpype
        from jpype.types import JArray, JByte
    except ImportError as e:
        raise ImportError(
            "ZaffalonBounds requires the optional 'jpype1' package.\n"
            "Install it with:\n\n"
            "    pip install causalboundingengine[java]"
        ) from e

    # Start JVM if not already running
    if not jpype.isJVMStarted():
        this_dir = os.path.abspath(os.path.dirname(__file__))
        jar_zaffalon = os.path.join(this_dir, "zaffalon", "zaffalon.jar")
        jar_credici = os.path.join(this_dir, "credici.jar")

        try:
            jpype.startJVM(classpath=[jar_zaffalon, jar_credici])
        except RuntimeError as e:
            raise RuntimeError(
                "Could not start the JVM. Make sure Java is installed and JAVA_HOME is set correctly."
            ) from e
