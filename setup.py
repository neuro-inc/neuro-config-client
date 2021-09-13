from setuptools import find_packages, setup


install_requires = ("aiohttp>=3.7.4",)

setup(
    name="neuro-config-client",
    use_scm_version=True,
    url="https://github.com/neuro-inc/neuro-config-client",
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=["setuptools_scm"],
    zip_safe=False,
)
