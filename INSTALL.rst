Currently, HaaS is only tested on Centos 6.  These instructions may implicitly
assume that you are running on Centos 6.


**Dependencies**
================

Many packages that HaaS depends on are only available in EPEL.  You can enable
the EPEL repos by running::

  yum install epel-release

HaaS has several Python dependencies, listed in ``requirements.txt``.  Note
particularly that HaaS depends on a helper library that we wrote, which can be
found at https://github.com/CCI-MOC/moc-rest .  ``moc-rest`` has additional
Python dependencies as well.  The Python dependencies can be installed with
``pip``, from the Centos package ``python-pip``, by running::

  pip install -r requirements.txt

In addition, HaaS requires the following packages:

- ``gcc``, for compiling some Python dependencies
- ``libvirt`` and ``qemu-kvm``, for running "headnode" VMs
- ``bridge-utils`` and ``vconfig``, for networking to VMs
- ``ipmitool``, for power cycling and monitoring physical nodes
- ``telnet``, for communicating with some switches
- ``sqlite``.  In future releases, other SQL databases will be supported, but
  right now this is your only option.
- ``httpd`` (Apache), and ``mod_wsgi``.  This is currently the only tested
  webserver setup.


**Installation**
================

First install the applications and Python packages, as well as the HaaS
package.  This can be done system-wide or in a Python virtual
environment---for details see the **Getting Started** section of
``README.rst``


**Configuration**
=================

HaaS is configured with the file ``haas.cfg``.  This file contains
configuration for both the CLI client and the server.  The provided file
``haas.cfg.example`` describes the relevant options in detail.


**Setup**
=========

All network traffic to headnodes in HaaS is routed through the ``trunk_port``
NIC chosen in ``haas.cfg``, on a tagged VLAN.  So, the corresponding port on
the switch must have all of HaaS's VLANS trunked to it.  This network
configuration must currently be done manually.

HaaS uses ``bridge-utils`` to route the traffic from the trunk port to the
headnode.  Currently the bridges and taps for this must be created ahead of
time.  The provided script ``create_bridges`` will create bridges for all
VLANS in the allocation pool.  This pre-allocation is easier to reason about
than on-demand creation, but also causes some limitations.  For instance,
headnodes can only be connected to networks with allocated VLANs.  Note also
that this script must be re-run on reboot.

Now we must make a clonable base headnode.  (One is required, and more are
allowed.)  First create a storage pool.  Any kind can be used, but we will
only document creating a directory-backed storage pool::

  virsh pool-create pool.xml

where ``pool.xml`` contains a description of the pool::

  <pool type="dir">
    <name>haas_headnodes</name>
    <target>
      <path>/path/to/storage/pool/directory</path>
    </target>
  </pool>

(Make sure that the HaaS user can read and write to that folder.)  Then make
the pool autostart with::

  virsh pool-autostart haas_headnodes

Then put your base image in the storage pool directory::

  mv base.img /path/to/storage/pool/directory/

Finally, create the base headnode with::

  virsh define base.xml

where ``base.xml`` contains a description of the headnode::

  <domain type='kvm'>
    <name>base</name>
    <currentMemory>524288</currentMemory>
    <memory>524288</memory>
    <uuid>30d18a08-d6d8-d5d4-f675-8c42c11d6c62</uuid>
    <os>
      <type arch='x86_64'>hvm</type>
      <boot dev='hd'/>
    </os>
    <features>
      <acpi/><apic/><pae/>
    </features>
    <clock offset="utc"/>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>restart</on_crash>
    <vcpu>1</vcpu>
    <devices>
      <emulator>/usr/libexec/qemu-kvm</emulator>
      <disk type='file' device='disk'>
        <driver name='qemu' type='raw'/>
        <source file='/path/to/storage/pool/directory/base.img'/>
        <target dev='vda' bus='virtio'/>
      </disk>
      <interface type='network'>
        <source network='default'/>
        <mac address='52:54:00:9c:94:3b'/>
        <model type='virtio'/>
      </interface>
      <input type='tablet' bus='usb'/>
      <graphics type='vnc' port='-1'/>
      <console type='pty'/>
      <sound model='ac97'/>
      <video>
        <model type='cirrus'/>
      </video>
    </devices>
  </domain>

Many of these fields are probably not needed, but we have not tested this
thoroughly.  Further, this set of XML duplicates the path to storage
directory---this seems unnecessary.

Finally, initialize an empty database with::

  haas init_db


**Running**
===========

HaaS consists of two services: an API server, and a networking server.  The
former is a WSGI application, ``haas.wsgi``, which we recommend running with
Apache's ``mod_wsgi``.  Start the latter with::

  haas serve_networks

The API WSGI application currently requires root privileges, for VM
operations.  The networking server does not.  Both require read **and** write
access to the SQL database.

HaaS is configured with the file ``haas.cfg`` .  When running the ``haas``
executable, ``haas.cfg`` must be in your working directory.  (Note that ``haas
serve_networks`` runs the ``haas`` executable.)  When running the API server
as a WSGI application, ``haas.cfg`` must be at ``/etc/haas.cfg``.  (This is an
inconsistency that will be fixed in later versions of HaaS.  For now, we
recommend using symlinks to ensure consistency.)


**Further setup**
=================

For HaaS to do anything useful, you must now use the HaaS API to add nodes to
be allocated.  This is done with the following API calls:

- ``node_register``
- ``node_delete``
- ``node_register_nic``
- ``node_delete_nic``
- ``port_register``
- ``port_delete``
- ``port_connect_nic``
- ``port_detach_nic``
