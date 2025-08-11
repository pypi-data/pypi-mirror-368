import setuptools

PACKAGE_NAME = "contact-group-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.70',  # https://pypi.org/project/contact-group-local
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles contact-group-local Python",
    long_description="PyPI Package for Circles contact-group-local Python",
    long_description_content_type='text/markdown',
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    # packages=setuptools.find_packages(),
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'logger-local>=0.0.135',
        'database-mysql-local>=0.0.300',
        'python-sdk-remote>=0.0.93',
        'group-remote>=0.0.111',
        'group-local>=0.0.24',
        'language-remote>=0.0.20',
        'contact-local>=0.0.42'
    ],
)
