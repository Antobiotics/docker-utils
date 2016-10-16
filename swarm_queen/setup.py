try:
    from setuptools import setup
except:
    from distutils.core import setup

try:
    import multiprocessing
except ImportError:
    pass

setup(
    name="swarm-queen",
    version='1.0.0',
    description="Bootstrap Swarm Cluster",
    author_email="albclus@gmail.com",
    url="https://github.com/Antobiotics/docker-utils",
    platforms="Posix; MacOS X; Windows",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
    ],
    packages=[
        "swarm_queen"
    ],
    install_requires=[
        "click",
        "coloredlogs",
        "executor"
    ]
)

