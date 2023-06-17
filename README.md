# tweets-classification-backend

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** Markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="app/assets/images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">tweets-classification-backend</h3>

  <p align="center">
    Backend for Tweets Classification project.
    <br />
    <a href="https://github.com/jpcadena/tweets-classification-backend"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About the project

[![Project][project-screenshot]](https://example.com)

This project is the Python backend for the Tweets Classification Machine
Learning project developed using FastAPI, PostgreSQL and Redis.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built with

- [![Python][Python]][python-url]
- [![FastAPI][FastAPI]][fastapi-url]
- [![Pydantic][Pydantic]][pydantic-url]
- [![Starlette][Starlette]][starlette-url]
- [![Uvicorn][Uvicorn]][uvicorn-url]
- [![Gunicorn][Gunicorn]][gunicorn-url]
- [![PostgreSQL][PostgreSQL]][postgresql-url]
- [![Redis][Redis]][redis-url]
- [![jwt][JWT]][jwt-url]
- [![HTML5][html5]][html5-url]
- [![Pandas][Pandas]][pandas-url]
- [![numpy][NumPy]][numpy-url]
- [![scikit-learn][Scikit-Learn]][scikit-learn-url]
- [![Pytest][Pytest]][pytest-url]
- [![DigitalOcean][DigitalOcean]][DigitalOcean-url]
- [![Nginx][Nginx]][Nginx-url]
- [![Ruff][ruff]][ruff-url]
- [![Black][Black]][Black-url]
- [![MyPy][MyPy]][MyPy-url]
- [![Pycharm][PyCharm]][Pycharm-url]
- [![visual-studio-code][visual-studio-code]][visual-studio-code-url]
- [![Markdown][Markdown]][Markdown-url]
- [![Swagger][Swagger]][Swagger-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting started

### Prerequisites

- [Python 3.10+][Python-docs]

### Installation

1. Clone the **repository**
   ```
   git clone https://github.com/jpcadena/tweets-classification-backend.git
   ```
2. Change the directory to **root project**
   ```
   cd tweets-classification-backend
   ```
3. Create a **virtual environment** _venv_
   ```
   python -m venv venv
   ```
4. Activate **environment** in Windows
   ```
   .\venv\Scripts\activate
   ```
5. Install requirements with PIP
   ```
   pip install -r requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

### Usage

1. If found **sample.env**, rename it to **.env**.
2. Replace your **credentials** into the _.env_ file.
3. Execute with console
   ```
   uvicorn main:app --reload
   ```
4. Visit http://localhost:8000/docs for Swagger UI documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

[![GitHub][GitHub]][GitHub-url]

If you have a suggestion that would make this better, please fork the repo and
create a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Use docstrings with **reStructuredText** format by adding triple double quotes
**"""** after function definition.\
Add a brief function description, also for the parameters including the return
value and its corresponding data type.\
Please use **linting** to check your code quality
following [PEP 8](https://peps.python.org/pep-0008/).\
Check documentation
for [Visual Studio Code](https://code.visualstudio.com/docs/python/linting#_run-linting)
or [Jetbrains Pycharm](https://github.com/leinardi/pylint-pycharm/blob/master/README.md).\
Recommended plugin for
autocompletion: [Tabnine](https://www.tabnine.com/install)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

- [![LinkedIn][LinkedIn]][linkedin-url]

- [![Outlook][Outlook]](mailto:jpcadena@espol.edu.ec?subject=[GitHub]tweets-classification-backend)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[LinkedIn]: https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://linkedin.com/in/juanpablocadenaaguilar
[Outlook]: https://img.shields.io/badge/Microsoft_Outlook-0078D4?style=for-the-badge&logo=microsoft-outlook&logoColor=white
[project-screenshot]: app/assets/images/project.png
[Python-docs]: https://docs.python.org/3.10/
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[FastAPI]: https://img.shields.io/badge/FastAPI-FFFFFF?style=for-the-badge&logo=fastapi
[Pydantic]: https://img.shields.io/badge/Pydantic-FF43A1?style=for-the-badge&logo=pydantic&logoColor=white
[Starlette]: https://img.shields.io/badge/Starlette-392939?style=for-the-badge&logo=starlette&logoColor=white
[Uvicorn]: https://img.shields.io/badge/Uvicorn-2A308B?style=for-the-badge&logo=uvicorn&logoColor=white
[Gunicorn]: https://img.shields.io/badge/Gunicorn-489846?style=for-the-badge&logo=gunicorn&logoColor=white
[Pylint]: https://img.shields.io/badge/linting-pylint-yellowgreen
[Pytest]: https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white
[Redis]: https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white
[PostgreSQL]: https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white
[Pandas]: https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white
[NumPy]: https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white
[Scikit-Learn]: https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white
[html5]: https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white
[JWT]: https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens
[DigitalOcean]: https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white
[PyCharm]: https://img.shields.io/badge/PyCharm-21D789?style=for-the-badge&logo=pycharm&logoColor=white
[Nginx]: https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white
[Markdown]: https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white
[Swagger]: https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white
[visual-studio-code]: https://img.shields.io/badge/Visual_Studio_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white
[python-url]: https://www.python.org/
[fastapi-url]: https://fastapi.tiangolo.com
[pydantic-url]: https://docs.pydantic.dev
[starlette-url]: https://www.starlette.io/
[uvicorn-url]: https://www.uvicorn.org/
[gunicorn-url]: https://gunicorn.org/
[pylint-url]: https://www.pylint.org/
[pytest-url]: https://docs.pytest.org/en/7.2.x/
[redis-url]: https://redis.io/
[postgresql-url]: https://www.postgresql.org/
[pandas-url]: https://pandas.pydata.org/docs/
[numpy-url]: https://numpy.org/
[scikit-learn-url]: https://scikit-learn.org/stable/

[html5-url]: https://developer.mozilla.org/en-US/docs/Glossary/HTML5

[jwt-url]: https://jwt.io/

[DigitalOcean-url]: https://www.digitalocean.com/

[Pycharm-url]: https://www.jetbrains.com/pycharm/

[Nginx-url]: https://www.nginx.com/

[Markdown-url]: https://daringfireball.net/projects/markdown/

[Swagger-url]: https://swagger.io/

[visual-studio-code-url]: https://code.visualstudio.com/

[GitHub]: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white

[GitHub-url]: https://github.com/jpcadena/tweets-classification-backend

[ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json

[ruff-url]: https://beta.ruff.rs/docs/

[Black]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge&logo=appveyor

[Black-url]: https://github.com/psf/black

[MyPy]: https://img.shields.io/badge/mypy-checked-2A6DB2.svg?style=for-the-badge&logo=appveyor

[MyPy-url]: http://mypy-lang.org/
