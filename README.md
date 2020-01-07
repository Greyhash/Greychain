# Greychain
A complete blockchain in python in little over 1000 lines of code

# Dependencies
* python3
* python3-pynacl
          
# What is this
Greychain is a blockchain written by Greyhash AB.
Its purpose is to demonstrate blockchain technology. 
<br>
We would like to hear from you if you are planning on using part of this code in production.

* The blockchain is made up of blocks. Each block has the hash of the previous block, hence it's a chain.
* Each block contains transactions as well as a reward of 13 Greycoins to the miner(creator) of the block.
* Each transaction has:
  * Time
  * Amount
  * Senders public key
  * Receivers public key
  * Comment (For example "Payment for the sheep"
  * Signature

Each transaction is signed by the senders [Curve25519](https://en.wikipedia.org/wiki/Curve25519 "Curve25519") private key.

Greychain run as a node which then becomes a part of the Greychain network.
Basically it's a http rest api server communicating using json objects.

# How to run
```bash
 python3 ./Server.py
```

# To create a transaction, run test_add_transaction.py
```bash
python3 ./test/test_add_transactions.py
```

# Operations security
Greyhash focuses heavily on opsec.
As such we have provided a systemd service file and a SELinux policy module for Greychain.
<br>
To compile and install the SELinux policy is needed.

```bash
sudo yum install policycoreutils-devel # Install SELinux dependecies 
make -f /usr/share/selinux/devel/Makefile greychain.pp # Compile the SELinux policy
sudo semodule -i greychain.pp # Load the policy
sudo cp -r ./ /opt/greychain # Install Greychain to /opt/greychain
sudo chown -R nobody /opt/greychain
sudo restorecon -r /opt/greychain/ # Set the correct SELinux filecontexts
```

The systemd service file assume Greychain is installed under /opt/greychain
<br>
```bash
sudo cp greychain.service /usr/lib/systemd/system/greychain.service
sudo systemctl daemon-reload
sudo systemctl start greychain.service
sudo systemctl enable greychain.service
sudo systemctl status greychain.service # Show the log
```

