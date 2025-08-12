"""
./deploy.ps1
"""
import setuptools

setuptools.setup(
    name='expressmoney',
    packages=setuptools.find_packages(),
    version='14.1.116',
    description='SDK ExpressMoney',
    author='Development team',
    author_email='dev@expressmoney.com',
    install_requires=('requests', 'python-json-logger==2.0.4', 'django-phonenumber-field[phonenumberslite]==5.2.0',
                      'django-jsonstore==0.5.0', 'packaging==23.1.0', 'boto3==1.35.99', 'cryptography==41.0.7',
                      ),
    python_requires='>=3.7',
    include_package_data=True,
)
