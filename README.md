#Udacity Item Catalog project

This project creates an adaptable data driven app for categorizing items.  With only minor alterations it can be made to serve the user's individual purposes.  The project includes two JSON endpoints.  You can find the repository for this project [here](https://github.com/YouKnowBagu/item-catalog)

## Software Used

-Python 2.7, specifically, [Anaconda](https://www.continuum.io/downloads)
- Vagrant, a command line utility to control a virtual machine's lifecycle.  A preconfigured Vagrant file is included in the repo.
- Virtual Box, a free open source virtual machine provider.
- SQLAlchemy, the Python SQL toolkit and object relational mapper.
- Flask, a microframework for Python based on [Werkzeug] and [Jinja2].  [License information for Flask]
- Responsive navigation code from viljamis be found at [Responsive Nav](http://responsive-nav.com).  It is a small and user friendly Javascript plugin that doesn't require any external libraries.

## Quick Start
To begin, download and install Vagrant [here](https://www.vagrantup.com/downloads.html).  Installation and usage guides can be found [here](https://www.vagrantup.com/docs/).  Ensure your installation was successful and you have the most recent version by opening your terminal and typing

```
$ vagrant -v
```

Once Vagrant is installed, download and install VirtualBox [here](https://www.virtualbox.org).
Documentation for VirtualBox can be found [here](https://www.virtualbox.org/wiki/Documentation).

Download and unzip the repository.  Using the command line, navigate to the Catalog/ directory.  To create the Virtual Machine, enter

```
$ vagrant up
```

in the terminal.  This process could take several minutes.
Once the virtual machine is running, enter

```
$ vagrant ssh
```

to connect.  Once connected, enter

```
cd /vagrant
```

The leading forward slash is required.  This will take you to the virtual machine's shared folder, which will contain all of the Catalog/ files.

To launch the app, simply execute

```
$ python run.py
```

from the /Catalog/ directory.  This will launch a version of the app with a generic database structure.  To view the application, open a web browser and navigate to localhost:8080

## Contact

I am happy to share any insights or answer any questions about this code. You can e-mail me at youknowbagu@gmail.com

