import setuptools

PACKAGE_NAME = "database-infrastructure-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/database-infrastructure-local/
    version='0.1.5',
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="Database Infrastructure Local Python Package",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "mysql-connector-python>=8.5.0",
        "python-sdk-remote>=0.0.93",
        "logger-local>=0.0.170",
    ]
)
