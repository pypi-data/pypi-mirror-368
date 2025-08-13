from setuptools import setup, find_packages
# Configuration
NAME = "CATEGORIT"
VERSION = "0.0.0.3"

INSTALL_REQUIRES = [

]

AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = ""
LICENSE = ""
KEYWORDS = ["orange3 add-on",]

PACKAGES = find_packages()
PACKAGES = [pack for pack in PACKAGES if "orangecontrib" in pack and "ALGORITHM" in pack]
PACKAGES.append("orangecontrib")
print("####", PACKAGES)

PACKAGE_DATA = {
    "orangecontrib.ALGORITHM.widgets": ["icons/*", "designer/*"],
    "orangecontrib.API.widgets": ["icons/*", "designer/*"],
    "orangecontrib.LLM_INTEGRATION.widgets": ["icons/*", "designer/*"],
    "orangecontrib.LLM_MODELS.widgets": ["icons/*", "designer/*"],
    "orangecontrib.TOOLBOX.widgets": ["icons/*", "designer/*"],
}

ENTRY_POINTS = {
    "orange.widgets": (
        "AAIT - ALGORITHM = orangecontrib.ALGORITHM.widgets",
        "AAIT - API = orangecontrib.API.widgets",
        "AAIT - LLM INTEGRATION = orangecontrib.LLM_INTEGRATION.widgets",
        "AAIT - Models = orangecontrib.LLM_MODELS.widgets",
        "AAIT - Toolbox = orangecontrib.TOOLBOX.widgets",
    )
}

NAMESPACE_PACKAGES = ["orangecontrib"]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    keywords=KEYWORDS,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    namespace_packages=NAMESPACE_PACKAGES,
)
