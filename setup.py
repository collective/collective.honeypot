from setuptools import setup

setup(
    name="collective.honeypot",
    version="5.0.1.dev0",
    description="Anti-spam honeypot for Plone",
    long_description=(open("README.rst").read() + "\n" + open("CHANGES.rst").read()),
    # Get more strings from https://pypi.org/classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="honeypot antispam form protection plone",
    author="Maurits van Rees",
    author_email="maurits@vanrees.org",
    url="https://github.com/collective/collective.honeypot",
    license="GPL",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=[
        "Products.CMFCore",
        "Zope",
        "lxml",
        "plone.protect",
        "plone.transformchain",
        "plone.z3cform",
        "repoze.xmliter",
        "z3c.form",
        "z3c.jbot",
    ],
    extras_require={
        "test": [
            "plone.app.discussion",
            "Products.CMFPlone",
            "plone.app.testing",
            "plone.base",
            "plone.restapi[test]",
            "plone.testing",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
