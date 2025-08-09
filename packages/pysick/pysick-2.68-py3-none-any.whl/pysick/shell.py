import code
import pysick

def main():
    print(f"----------------------------")
    print(f"  PySick on Shell  ")
    print(f"  pysick v{pysick.SickVersion}")
    print(f"----------------------------")

    # All symbols from pysick.__init__ will be available
    namespace = dict(vars(pysick))

    console = code.InteractiveConsole(locals=namespace)
    console.interact("This is pysick, on your Shell ")
