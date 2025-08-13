![Header-Image](docs/header.png)

> Infrastructure as Code or IaC is the process of provisioning and managing infrastructure defined through code, instead of doing so with a manual process.
>
> Infrastructure as code brings a lot of advantages into the network operation:
> + Reducing shadow IT within organizations and allowing timely and efficient infrastructure changes
> + Integrating directly with CI/CD platforms
> + Enabling version-controlled infrastructure and configuration changes leading to trackable configurations
> + Standardizing infrastructure with reproducible configurations
> + Effectively managing configurating drift and keeping infrastructure and configurations in their desired state
> + Having the ability to easily scale up infrastructure as automation eliminates the need for manual configurations

# Nornir-Collection Python-Package
----
</br>

This repository builds a python package and is a complete solution to manage the network configuration from code.
The Nornir-Collection package modules are a collection of network automation functions and complete workflows
with Nornir and other python tools. All scripts can be executed manually from a central server, workstation or integrated into a CI/CD pipeline. The folder azure_pipelines provides bash functions to facilitate the writing
of Azure DevOps pipelines.

# Python Development and Testing
----
</br>

The Python scripts were developed with static code analysis, ruff auto-formatting and functional testing with Azure
DevOps pipelines executed by a pipeline agent installed within the Kyndryl labor network. The `Makefile` is used to
run the black auto-formatter, yamllint, pylint and prospector linting, bandit for security and vulnerability verification
as well as vulture for dead code verification. All pylint warnings that should be ignored are part of the script with a
pylint control message e.g `# pylint: disable=import-error`. Pylint and prospector uses a custom configuration profile.
The other tools use the default configuration.

The `Makefile` contains the tasks `all`, `fmt` and `lint`

To execute the `Makefile` with all tasks (black auto-formatting, yamllint, pylint, bandit and vulture):
```bash
make
```

To execute only the black auto-formatting:
```bash
make fmt
```

To execute only the linting with yamllint, pylint, bandit and vulture:
```bash
make lint
```

# Languages and Tools
----
</br>

<p align="center">
  <img width="7.8%" src="https://user-images.githubusercontent.com/70367776/177972422-da6933d5-310e-4cdb-9433-89f2dc6ebb7a.png" alt="Python" />
  <img width="9.5%" src="https://user-images.githubusercontent.com/70367776/177969859-476bd542-2c0e-41a9-82f2-3e4919a61d4e.png" alt="YAML" />
  <img width="10%" src="https://user-images.githubusercontent.com/70367776/177966199-e8476a0d-f972-4409-8b9a-d493d339bf38.png" alt="Nornir" />
  <img width="8.9%" src="https://user-images.githubusercontent.com/70367776/177970540-b59a294f-82fd-4647-b8e2-9305c399c900.png" alt="Scrapli" />
  <img width="19.5%" src="https://user-images.githubusercontent.com/70367776/229153411-6e5d10c3-634e-47b9-8920-0ed5e2311f9b.png" alt="Netmiko" />
  <img width="10.5%" src="https://user-images.githubusercontent.com/70367776/183677690-fd956308-fda9-4583-863e-3a39d3ecc7f7.png" alt="NETCONF" />
  <img width="9%" src="https://user-images.githubusercontent.com/70367776/183678136-4fbf50a8-adbb-468e-91b6-988d4c1ccd72.png" alt="RESTCONF" />
  <img width="9.5%" src="https://user-images.githubusercontent.com/70367776/177966474-e66d8a59-e26e-4a3d-ac59-ded7cc005e4b.png" alt="Jinja2" />
  <img width="10%" src="https://user-images.githubusercontent.com/70367776/177971288-e32552cd-1529-470a-8881-30c22d2df8ac.png" alt="pyATS" />
  <img width="10%" src="https://user-images.githubusercontent.com/70367776/222764714-1ff86034-76f9-49d0-9e24-68798d779f56.png" alt="Batfish" />
  <img width="10.2%" src="https://user-images.githubusercontent.com/70367776/183678800-403cf0ea-3c8a-47bb-b52a-2caa0cedc195.png" alt="Makefile" />
  <img width="10.5%" src="https://user-images.githubusercontent.com/70367776/183679432-2b89f00c-f5b1-4d47-9c68-ad7fa332de01.png" alt="Prospector" />
  <img width="9%" src="https://user-images.githubusercontent.com/70367776/183680151-62d5c625-0430-4c90-adfc-1ebb47fce4a9.png" alt="Bandit" />
  <img width="9.4%" src="https://user-images.githubusercontent.com/70367776/177972703-3be3c4c3-aa9a-4468-97a6-e7760d536b89.png" alt="Git" />
  <img width="9.4%" src="https://user-images.githubusercontent.com/70367776/177972925-1780012f-64a6-4b93-a215-fd47e3222b8f.png" alt="GitHub" />
  <img width="11.5%" src="https://user-images.githubusercontent.com/70367776/232078456-8aee2fda-1289-4cd9-b7f3-9b34fcb4d7c7.png" alt="Docker" />
  <img width="9.4%" src="https://user-images.githubusercontent.com/70367776/231501139-a449202e-6a81-4364-a4ea-1e42906e846e.png" alt="Azure Pipeline" />
  <img width="33.2%" src="https://user-images.githubusercontent.com/70367776/231500048-77eeff9a-166b-4bd7-a0cc-3c5fc58be368.png" alt="NetBox" />
</p>

<br>

<h3 align="center">APIs can also be amusing to provide a programming joke ...</h3>
<p align="center"><img src="https://readme-jokes.vercel.app/api?hideBorder&theme=calm" /></p>
<h3 align="center">... or an interesting quote.</h3>
<p align="center"><img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=dracula" /></p>