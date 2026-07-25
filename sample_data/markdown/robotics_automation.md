# Robotics & Automation

## 1. Robotics Fundamentals

### Robot Components
- **Actuators**: Motors, servos, pneumatics
- **Sensors**: Vision, force, proximity, IMU
- **Controller**: Microcontroller, PLC, computer
- **Power Supply**: Batteries, mains power

### Robot Types
| Type | Application |
|------|-------------|
| Industrial | Manufacturing, assembly |
| Collaborative (Cobot) | Human-robot work |
| Mobile | Logistics, exploration |
| Humanoid | Research, service |
| Surgical | Medical procedures |
| Swarm | Collective behavior |

## 2. Kinematics

### Forward Kinematics
```
Given joint angles → Calculate end-effector position

DH Parameters:
- θ: Joint angle
- d: Link offset
- a: Link length
- α: Link twist
```

### Inverse Kinematics
```
Given end-effector position → Calculate joint angles

Methods:
- Analytical (closed-form)
- Numerical (iterative)
- Geometric
```

### Motion Planning
- **A***: Pathfinding algorithm
- **RRT**: Rapidly-exploring Random Trees
- **PRM**: Probabilistic Roadmaps
- **Potential Fields**: Attraction/repulsion

## 3. Control Systems

### PID Controller
```
u(t) = Kp × e(t) + Ki × ∫e(t)dt + Kd × de(t)/dt

Kp: Proportional gain
Ki: Integral gain
Kd: Derivative gain
```

### State-Space Control
```
ẋ = Ax + Bu (state equation)
y = Cx + Du (output equation)
```

### Stability
- **BIBO**: Bounded Input, Bounded Output
- **Routh-Hurwitz**: Polynomial stability criterion
- **Nyquist**: Frequency domain stability

## 4. Sensors & Perception

### Vision Sensors
- **RGB Camera**: Standard imaging
- **Depth Camera**: RGB-D (Kinect, RealSense)
- **LiDAR**: Laser scanning
- **Stereo Camera**: Depth from disparity

### Tactile Sensors
- Force/torque sensors
- Pressure sensors
- Tactile arrays

### Other Sensors
- **IMU**: Accelerometer + Gyroscope
- **GPS**: Global positioning
- **Ultrasonic**: Distance measurement
- **IR**: Infrared proximity

## 5. Computer Vision for Robotics

### Object Detection
- **YOLO**: Real-time detection
- **R-CNN**: Region-based detection
- **SSD**: Single Shot Detector

### Visual Odometry
- Estimate motion from camera images
- SLAM (Simultaneous Localization and Mapping)

### 3D Perception
- Point cloud processing
- Surface reconstruction
- Object pose estimation

## 6. Robot Operating System (ROS)

### Architecture
```
Nodes: Individual processes
Topics: Named buses for communication
Services: Request-response communication
Actions: Long-running tasks
```

### Key Packages
- **rospy/roscpp**: Language interfaces
- **navigation**: Path planning
- **moveit**: Motion planning
- **gazebo**: Simulation
- **rviz**: Visualization

## 7. Industrial Automation

### PLC (Programmable Logic Controller)
- Ladder logic
- Structured text
- Function block diagram

### SCADA (Supervisory Control and Data Acquisition)
- HMI (Human-Machine Interface)
- Data logging
- Remote monitoring

### Communication Protocols
- **Modbus**: Serial/Ethernet
- **OPC UA**: Unified Architecture
- **EtherCAT**: Real-time Ethernet
- **PROFINET**: Industrial Ethernet

## 8. AI in Robotics

### Reinforcement Learning
- Robot learns through trial and error
- Reward-based learning
- Policy gradient methods

### Imitation Learning
- Learn from human demonstrations
- Behavior cloning
- Inverse reinforcement learning

### Sim-to-Real Transfer
- Train in simulation
- Deploy in real world
- Domain randomization

## 9. Human-Robot Interaction

### Safety Standards
- **ISO 10218**: Industrial robots
- **ISO/TS 15066**: Collaborative robots

### Safety Features
- Force limiting
- Speed monitoring
- Safety-rated monitored stop
- Hand guiding

## 10. Applications

### Manufacturing
- Assembly lines
- Welding
- Painting
- Quality inspection

### Healthcare
- Surgical robots (da Vinci)
- Rehabilitation robots
- Assistive robots

### Logistics
- Warehouse automation
- Autonomous vehicles
- Last-mile delivery

### Exploration
- Space robots (rovers)
- Underwater robots (AUVs)
- Search and rescue
