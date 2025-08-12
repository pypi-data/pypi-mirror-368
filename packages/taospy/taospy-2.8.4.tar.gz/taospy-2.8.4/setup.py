# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taos', 'taosrest']

package_data = \
{'': ['*']}

install_requires = \
['iso8601==1.0.2', 'pytz', 'requests>=2.27.1']

extras_require = \
{'ws:python_version >= "3.7" and python_version < "4.0"': ['taos-ws-py>=0.3.0']}

entry_points = \
{'sqlalchemy.dialects': ['taos = taos.sqlalchemy:TaosDialect',
                         'taosrest = taosrest.sqlalchemy:TaosRestDialect',
                         'taosws = taos.sqlalchemy:TaosWsDialect']}

setup_kwargs = {
    'name': 'taospy',
    'version': '2.8.4',
    'description': 'The official TDengine Python connector',
    'long_description': '<!-- omit in toc -->\n# TDengine Python Connector\n\n\n[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/taosdata/taos-connector-python/build.yml)](https://github.com/taosdata/taos-connector-python/actions/workflows/build.yml)\n[![codecov](https://codecov.io/gh/taosdata/taos-connector-python/branch/main/graph/badge.svg?token=BDANN3DBXS)](https://codecov.io/gh/taosdata/taos-connector-python)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/taosdata/taos-connector-python)\n![PyPI](https://img.shields.io/pypi/dm/taospy)\n![GitHub License](https://img.shields.io/github/license/taosdata/taos-connector-python)\n[![PyPI](https://img.shields.io/pypi/v/taospy)](https://pypi.org/project/taospy/)\n<br />\n[![Twitter Follow](https://img.shields.io/twitter/follow/tdenginedb?label=TDengine&style=social)](https://twitter.com/tdenginedb)\n[![YouTube Channel](https://img.shields.io/badge/Subscribe_@tdengine--white?logo=youtube&style=social)](https://www.youtube.com/@tdengine)\n[![Discord Community](https://img.shields.io/badge/Join_Discord--white?logo=discord&style=social)](https://discord.com/invite/VZdSuUg4pS)\n[![LinkedIn](https://img.shields.io/badge/Follow_LinkedIn--white?logo=linkedin&style=social)](https://www.linkedin.com/company/tdengine)\n[![StackOverflow](https://img.shields.io/badge/Ask_StackOverflow--white?logo=stackoverflow&style=social&logoColor=orange)](https://stackoverflow.com/questions/tagged/tdengine)\n\nEnglish | [简体中文](./README-CN.md)\n\n<!-- omit in toc -->\n## Table of Contents\n\n- [1. Introduction](#1-introduction)\n- [2. Documentation](#2-documentation)\n- [3. Prerequisites](#3-prerequisites)\n- [4. Build](#4-build)\n- [5. Testing](#5-testing)\n  - [5.1 Test Execution](#51-test-execution)\n  - [5.2 Test Case Addition](#52-test-case-addition)\n  - [5.3 Performance Testing](#53-performance-testing)\n- [6. CI/CD](#6-cicd)\n- [7. Submitting Issues](#7-submitting-issues)\n- [8. Submitting PRs](#8-submitting-prs)\n- [9. References](#9-references)\n- [10. License](#10-license)\n\n## 1. Introduction\n\n`taospy` is the official Python Connector for TDengine, allowing Python developers to develop applications that access the TDengine database. It supports functions such as data writing, querying, subscription, schemaless writing, and parameter binding.\n\nThe API for `taospy` is compliant with the Python DB API 2.0 (PEP-249). It contains two modules:\n\n1. The `taos` module. It uses TDengine C client library for client server communications.\n2. The `taosrest` module. It wraps TDengine RESTful API to Python DB API 2.0 (PEP-249). With this module, you do not need to install the TDengine C client library.\n\n## 2. Documentation\n\n- To use Python Connector, please check [Developer Guide](https://docs.tdengine.com/developer-guide/), which includes how an application can introduce the Python Connector , as well as examples of data writing, querying, schemaless writing, parameter binding, and data subscription.\n- For other reference information, please check [Reference Manual](https://docs.taosdata.com/reference/connector/python/), which includes version history, data types, example programs, API descriptions, and FAQs.\n- This quick guide is mainly for developers who like to contribute/build/test the Python Connector by themselves. To learn about TDengine, you can visit the [official documentation](https://docs.tdengine.com).\n\n## 3. Prerequisites\n\n- Python runtime environment (taospy: Python >= 3.6.2, taos-ws-py: Python >= 3.7)\n- TDengine has been deployed locally. For specific steps, please refer to [Deploy TDengine](https://docs.tdengine.com/get-started/deploy-from-package/), and taosd and taosAdapter have been started.\n\n## 4. Build\n\nDownload the repository code and execute the following in root directory to build develop environment:\n``` bash\npip3 install -e ./ \n```\n\n## 5. Testing\n### 5.1 Test Execution\nThe Python Connector testing framework is `pytest`  \nThe testing directory for `taospy` is located in the root directory: tests/  \nThe testing directory for `taos-ws-py` is located in the root directory: taos-ws-py/tests/  \nThe test code has been written into one bash file. You can open and view the detailed testing process   \nThe following command runs all test cases on Linux platform:\n``` bash\n# for taospy\nbash ./test_taospy.sh\n```\n\n``` bash\n# for taos-ws-py\nbash ./test_taos-ws-py.sh\n```\n\n### 5.2 Test Case Addition\nYou can add new test files or add test cases in existing test files that comply with `pytest` standards\n\n### 5.3 Performance Testing\nPerformance testing is in progress.\n\n## 6. CI/CD\n- [Build Workflow](https://github.com/taosdata/taos-connector-python/actions/workflows/build.yml)\n- [Code Coverage](https://app.codecov.io/gh/taosdata/taos-connector-python)\n\n## 7. Submitting Issues\nWe welcome the submission of [GitHub Issue](https://github.com/taosdata/taos-connector-python/issues/new?template=Blank+issue). When submitting, please provide the following information:\n\n- Problem description, whether it always occurs, and it\'s best to include a detailed call stack.\n- Python Connector version.\n- Python Connection parameters (username and password not required).\n- TDengine server version.\n\n## 8. Submitting PRs\nWe welcome developers to contribute to this project. When submitting PRs, please follow these steps:\n\n1. Fork this project, refer to ([how to fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)).\n2. Create a new branch from the main branch with a meaningful branch name (`git checkout -b my_branch`). Do not modify the main branch directly.\n3. Modify the code, ensure all unit tests pass, and add new unit tests to verify the changes.\n4. Push the changes to the remote branch (`git push origin my_branch`).\n5. Create a Pull Request on GitHub ([how to create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)).\n6. After submitting the PR, you can find your PR through the [Pull Request](https://github.com/taosdata/taos-connector-python/pulls). Click on the corresponding link to see if the CI for your PR has passed. If it has passed, it will display "All checks have passed". Regardless of whether the CI passes or not, you can click "Show all checks" -> "Details" to view the detailed test case logs.\n7. After submitting the PR, if CI passes, you can find your PR on the [codecov](https://app.codecov.io/gh/taosdata/taos-connector-python/pulls) page to check the test coverage.\n\n## 9. References\n- [TDengine Official Website](https://www.tdengine.com/) \n- [TDengine GitHub](https://github.com/taosdata/TDengine) \n\n## 10. License\n[MIT License](./LICENSE)',
    'author': 'Taosdata Inc.',
    'author_email': 'support@taosdata.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
