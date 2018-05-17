from setuptools import setup

# vim: expandtab tabstop=4 shiftwidth=4

setup(
    version='0.10.2',
    name='pypki2',
    description='More user-friendly way to access PKI-enabled services',
    url='https://github.com/nbgallery/pypki2',
    author="Bill Allen",
    author_email="photo.allen@gmail.com",
    scripts=[],
    packages=['pypki2', 'pypki2config', 'pypki2pip'],
    package_data={},
    python_requires='>=2.7.9, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=['pyOpenSSL'],
    keywords=['pki','ssl','pem','pkcs12','p12','mypki','pip']
)
