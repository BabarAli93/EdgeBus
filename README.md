# EdgeBus

Kubernetes has revolutionised traditional monolithic Internet of Things (IoT) applications into lightweight, decentralized, and
independent microservices, thus becoming the de facto standard in the realm of container orchestration. Intelligent and efficient
container placement in Mobile Edge Computing (MEC) is challenging subjected to user mobility, and surplus but heterogeneous
computing resources. One solution to constantly altering user location is to relocate containers closer to the user; however, this leads
to additional underutilized active nodes and increases migration’s computational overhead. On the contrary, few to no migrations are
attributed to higher latency, thus degrading the Quality of Service (QoS). To tackle these challenges, we created a framework named
EdgeBus, which enables the co-simulation of container resource management in heterogeneous MEC environments based on
Kubernetes. It enables the assessment of the impact of container migrations on resource management, energy, and latency. Further,
we propose a mobility and migration cost-aware (MANGO) lightweight scheduler for efficient container management by incorporating
migration cost, CPU cores, and memory usage for container scheduling. For user mobility, the Cabspotting dataset is employed, which
contains real-world traces of taxi mobility in San Francisco. In the EdgeBus framework, we have created a simulated environment aided
with a real-world testbed using Google Kubernetes Engine (GKE) to measure the performance of the MANGO scheduler in comparison
to baseline schedulers such as IMPALA-based Mobile-Kube, Latency Greedy, and Bin-Packing. Finally, extensive experiments have
been conducted, which demonstrate the effectiveness of the MANGO in terms of latency and number of migrations
Co-Simulator for Resource Management in Mobile Edge Computing Enviornment.


![Screenshot from 2024-05-21 11-06-10](https://github.com/BabarAli93/EdgeBus/assets/50677432/e37e057f-3b2f-45cd-8760-78960d8248e6)

# Setup
1. Download code by executing following command in the terminal
```
git clone https://github.com/BabarAli93/EdgeBus.git
```
2. Install [miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) or use Python for virtual environment creation.
3. You can create a virtual environment using either conda or Python's built-in venv module.
   
   Using conda:
   ```
   conda create --name Env_Name python=3.9.16
   ```
   Or
   Using Python's venv:
   ```
   python3 -m venv Env_Name
   ```
4. Activate the virtual environment. For conda:
```
conda activate Env_Name
```
5. Install following packages
```
 sudo apt install cmake libz-dev
```
6. Install all the required packages from the requirements file
```
conda install --file requirements.txt
```

# [Optional] Google Kubernetes Engine
EdgeBus supports experimentation both at the simulation level and the real world Kubernetes level. If you have chosen to go for Kubernetes based experiments, you will need to configure a cluster in Google Kubernetes Engine (GKE). 
Follow [GKE Cluster](https://github.com/saeid93/mobile-kube/blob/main/docs/kubernetes/installation-gcp.md) creation guide for this purpose. 
After successful creation of cluster, we need to connect to it using the CONNECT button (shown at cluster page) and execute the given command in the terminal, it will give us access to the cluster from our local machine.
![image (26)](https://github.com/BabarAli93/EdgeBus/assets/50677432/f21b1bc6-0a50-4449-bbea-d2e4c8b1b5c2)

# Project Structure
1. data:
This folder contains configuration files required in this project realated to edge server nodes CPU and Memory configurations, DRP model parameters, training and testing results. Configuration files in this folder are used later stages.
2. experiment: It has files related to training the DRL model, their testing, and the evaluation of Heusistic algorithms. 
3. mobile-kube: It has custom gymnasium environment employed in these settings and the simulation of chosen scheduler
4. mobility-preprocessing: This folder is responsible to generate user mobility traces based on simulation or Cabspotting and California Tower datasets

## mobile-kube
First of all, install this package. Navigate to mobile-kube folder and execute this line of code in the terminal
```
pip install -e .
```
## data
Update the path to data folder so that the configurations are picked and respected cluster is created. Go to experiments folder and modify ```constants.py``` in the utils directory which can be found at here [experiments/utils/constants.py](https://github.com/BabarAli93/EdgeBus/blob/main/experiments/utils/constants.py)
```
DATA_PATH = "/home/babarali/mobilekube-v2/data"
```
## mobility-preprocessing
In here, you will generate user mobolity patterns to be used by the simulator and GKE cluster. Navigate to 'EdgeBus/mobility-preprocssing'

```
pip install -r requirements.txt
```
