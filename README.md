# Blockchain Enabled File Sharing



For running on Ubuntu Linux:

**** Initial Installs *****
On all machines in terminal:

1) Install python3:

a) $ sudo apt-get update

b) $ sudo apt-get install python3.6

2) Install pip:

a) $ sudo apt install python3-pip

3) Install Necessary Imports:
	
 a) $ pip install tk
	
 b) $ pip install requests
	
 c) $ pip install moralis
	
 d) $ pip install rsa
***************************


*** Running the project ***
On full nodes:

1) Get machine IPs:
	
 a) $ ip a
	
 b) Take note of the IP for each machine.

2) Run the main program on the primary node:
	
 a) Navigate to the project directory.
	
 b) $ python3 [projectname.py]
	
 c) Input the IP of the second machine into the window's IP text box.

3) Run the main program on secondary nodes:
	
 a) Navigate to the project directory.
	
 b) $ python3 [projectname.py]
	
 c) Input the IP of the first machine into the window's IP text box.

For all future machines:
4) Run the main program:
	
 a) Navigate to the project directory.
	
 b) $ python3 [projectname.py]
	
 c) Input the IP of any existing machine running the program into the window's IP text box.
***************************


**** Using the project ****
1) Login using existing credentials on the blockchain:
	
 a) Default username for first admin account: admin
	
 b) Default password for first admin account: admin
	
 c) Default username for first doctor account: doctor
	
 d) Default password for first doctor account: batman
***************************
