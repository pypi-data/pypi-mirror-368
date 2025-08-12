from setuptools import  setup,find_packages

setup(
    name='siem_hkm_ai_smartcore',
    packages=find_packages(),
    install_requires=[
        "pandas" , "BAC0","opcua"
    ],
    version='0.1.0',
    description="lanzco's team",
    author="lanzco's team",
    license='MIT',
)
