  # WTF - Wi-Fi Test Framework
  
  WTF is a Python CLI tool for automating Wi-Fi throughput tests with different Wi-Fi radio settings.
  
  At the current stage, WTF is designed for OpenWrt-based access points and uses UCI and SSH.
  
  
  ## Why?
  Manually changing Wi-Fi channel/bandwidth settings, running a test, recording the result, and repeating this 30+ times is tedious and error-prone. WTF automates this loop.

  ## Prerequisites
  - **Access Point**: OpenWrt
  - **Client machine**: Linux
  - **Software**: iperf3, Python 3.11+
  - **Setup**: AP and client machine must be connected through:
    - a control network for SSH/UCI access;
    - a Wi-Fi test network for throughput measurements.
  ## Installation
  1. First download the package sources(not published to pip yet): 

  ```git clone https://github.com/KOROBYAKA/WTF```

  2. Enter the project directory: 

  ```cd WTF```

  3. Create a Python3 virtual environment(``pipenv run`` or ```python3 -m venv .venv```) and activate it

  4. Install the package: 

  ```pip install .```
  
  ## Usage
  
  ### Check the configuration
  wtf check-config allows user to check if the configuration in given path is valid, the basic file for configuration to check is the conf.toml (conf example can be found from the conf.toml.example).

  ```wtf check-config --config conf.toml```
  ### Run
  wtf run executes the test.
  

  ```wtf run --config conf.toml```


  ## Roadmap
  - [ ] Results saving
  - [ ] Automated tests
  - [ ] CI/CD pipeline
  - [ ] pip publish
