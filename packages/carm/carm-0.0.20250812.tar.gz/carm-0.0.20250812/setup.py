from setuptools import setup, find_packages

setup(
    name="carm",
    version="0.0.20250812",
    packages=find_packages(),
    package_data={
        "carm": [
            "__init__.py",
            "carm.py",
        ],  
    },
    scripts=['scripts/carm','scripts/carm_ros2'],
    include_package_data=True,
    install_requires=["websocket-client"],
    zip_safe=True,
    author='Yong Zhao',
    author_email='zhaoyong11933@cvte.com',
    description="Python interface for cvte arm.",
    long_description='Python interface for cvte arm.',
)
