from setuptools import find_packages
from setuptools import setup


setup(
    name="collective.honeypot",
    version="2.0",
    description="Anti-spam honeypot for Plone",
    long_description=(open("README.rst").read() + "\n" + open("CHANGES.rst").read()),
    # Get more strings from https://pypi.org/classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="honeypot antispam form protection plone",
    author="Maurits van Rees",
    author_email="maurits@vanrees.org",
    url="https://github.com/collective/collective.honeypot",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "z3c.jbot",],
    extras_require={"test": ["plone.app.testing",],},
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
