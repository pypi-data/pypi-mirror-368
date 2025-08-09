from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("canoaicli")
    __author__ = "carellihoula"
except PackageNotFoundError:
    pass
    # print("Package not found")