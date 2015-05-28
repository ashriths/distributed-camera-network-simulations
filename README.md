# Object tracking Using Distributed camera Network

The following module will try to craete a distributed netowrk of devices and track objects.



### Version
1.0.0

### Requirements

Dillinger uses a number of open source projects to work properly:

* [Python] - networking and image processing language used to interaface
* [OpenCV] - The Image porcessing Library
* [Numpy] - Math Library for Python
* [Scipy] - Visualization Tool used
* [matplotlib] - Visualization tool
* [virtualenv] - environment setup for clean run

### Installation on  Mac
1. Install [Homebrew]
```sh
$ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
2. install latest [Python] 2.7 
```sh
$ brew install python
```
3. install [virtualenv] 
```sh
$ pip isnstall virtualenv
```
3. Setup virtual Environment at the path `<workspace>`
```sh
$ virtualenv <workspace>
```
3. Activate virtualenv 
```sh
$ source <workspace>/bin/acitvate
```
3. install [opencv] 
```sh
$ brew install opencv
```
3. install [Numpy] 
```sh
$ brew install numpy
```
3. install [SciPy] 
```sh
$ brew install scipy
```
3. Clone this repository 
```sh
$ git clone https://github.com/ashriths/img-proc
```

### Installation on Debian (Use yum for centOS or other distros )
1. Update apt package manager
```sh
$ sudo apt-get update
```
3. install [virtualenv] 
```sh
$ pip isnstall virtualenv
```
3. Setup virtual Environment at the path `<workspace>`
```sh
$ virtualenv <workspace>
```
3. Activate virtualenv 
```sh
$ source <workspace>/bin/acitvate
```
3. install [opencv] 
```sh
$ sudo apt-get install opencv
```
3. install [Numpy] 
```sh
$ sudo apt-get install numpy
```
3. install [SciPy] 
```sh
$ sudo apt-get install scipy
```
3. Clone this repository 
```sh
$ git clone https://github.com/ashriths/img-proc
```





### How to run ? 


1. All objects to be tracked should be put in `<workspace>/img-proc/img` directory before running. Check out the demo images. The file name will be taken as the name of the object. Eg. `match.jpg` => Name :  `match`
![alt tag](https://raw.githubusercontent.com/ashriths/img-proc/master/img/match.jpg)
1. Connect the devices to a single network and note down their IP addresses
2. Open `<workspace>/img-proc/lib/network_generator.py` and `<workspace>/img-proc/lib/node_generator.py` to modify the IP to your IP network Admin's and node's IP address respectively
```python
IP = '<your IP Address>'
```
3. Run the Netowork Admin on one of the devices to setup the network
```sh
$ <workspace>/img-proc python netowork.py
[1] to start
[2] to exit
```
Press 1 to start the network and you should see this
```sh
Server created on <YOUR IP ADDRESS> listening to port 5000
```
4. Run the Node script in a new terminal or another device
```sh
$ <workspace>/img-proc python node.py
Enter Network IP: <Enter Your Netowork Admin's IP here>
Enter Network PORT: <Enter your Network Admin's Port here, usually 5000>
Enter Location:
x : <X coordinate of the node's geolocation>
y : <Y coordinate of the node's geolocation>
[1] to start
[2] to exit
```
press 1 to start the node tracking and you'll see the tracking like this
![alt tag](https://raw.githubusercontent.com/ashriths/img-proc/master/screenshots/Screen%20Shot%202015-05-02%20at%201.22.17%20am.png)

5. To generate the report of tracking 
```sh
$ <workspace>/img-proc python report.py
Enter File_name: <leave empty to analyze default>
Enter Object Name: <id,match etc>
```
You should see the report like this.
![alt tag](https://raw.githubusercontent.com/ashriths/img-proc/2e76785f1cc5610a3b61d22ff3472ac3364930b0/screenshots/Screen%20Shot%202015-05-28%20at%2012.37.04%20pm.png)



### Todo's

* Write Tests
* Night Mode

License
----
Free

[openCV]:http://opencv.org/
[Numpy]:http://numpy.org/
[Python]:https://www.python.org/
[Homebrew]:http://brew.sh/
[matplotlib]:http://matplotlib.org/
[Scipy]:http://scipy.org/
[virtualenv]:https://virtualenv.pypa.io/
