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

![image](https://github.com/BabarAli93/Commando/assets/50677432/3bd666f1-fb09-4a5a-a37a-553e34664f94)

