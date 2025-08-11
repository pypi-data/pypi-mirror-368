from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='kozhindev_data_labeler',
  version='0.0.1',
  author='YVoskanyan',
  author_email='yuvoskanyan@team.kozhin.dev',
  description='Пакет, содержащий пайплайн для разметки данных, используя большие языковые модели',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['pandas>=2.3.1', 'pydantic>=2.11.7', 'litellm>=1.75.4'],
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='kozhindev datalaber classification llm',
  python_requires='>=3.12'
)