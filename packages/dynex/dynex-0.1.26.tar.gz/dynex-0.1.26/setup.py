from setuptools import setup

setup(
    name='dynex',
    version='0.1.26',    
    description='Dynex SDK Neuromorphic Computing',
    url='https://github.com/dynexcoin/DynexSDK',
    author='Dynex Developers',
    author_email='office@dynexcoin.org',
    license='GPLv3',
    packages=['dynex'],
    install_requires=['pycryptodome>=3.18.0',
                      'dimod>=0.12.10',
                      'tabulate>=0.9.0',
                      'tqdm>=4.65.0',
                      'ipywidgets>=8.0.7',
                      'numpy'
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: POSIX :: Linux',     
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
        'Topic :: System :: Distributed Computing',
    ],

    long_description = 'The Dynex SDK is a collection of open-source Python tools designed to tackle difficult problems using n.quantum computing. It helps adapt your applications challenges for resolution on the Dynex platform and manages the communication between your application code and the n.quantum system seamlessly. Programmers who are familiar with quantum gate circuit languages such as Qiskit, Cirq, Pennylane, OpenQASM, or quantum annealing tools like the Dimod framework, PyQUBO, and other QUBO frameworks, will find it easy to run computations on the Dynex neuromorphic computing platform. The Dynex SDK supports both quantum circuits and quantum annealing, but without the typical constraints associated with conventional quantum machines.',
)


