<div align="center">
  <img src="https://github.com/ShimaSama/Netflix-QoS/blob/9cebf301ba711d2cd47a570dbc23d9e0cd24e3e8/netclass-logo.png" width="300px" />
</div>

# NETCLASS

## Introduction

<p>Network classifier application for internet services from multiple different devices usign Machine Learning.</p>

## Project Info

- Project name: NetClass
- Subject: Network traffic monitoring and analysis (TMA)
- University: Escola Tècnica Superior d'Enginyeria de Telecomunicació de Barcelona (ETSETB - UPC)
- Course: 2022/23 Q1
- Group members:
> - [Casas Saez, Arnau](mailto:arnau.casas@estudiantat.upc.edu)
> - [Cuesta Arcos, Pau](mailto:pau.cuesta.arcos@estudiantat.upc.edu)
> - [Dumitrasc, Valentina](mailto:valentina.dumitrasc@estudiantat.upc.edu)
> - [Font Gironés, Paula](mailto:paula.font@estudiantat.upc.edu)
> - [López Valero, Raúl](mailto:raul.lopez.valero@estudiantat.upc.edu)
> - [Reig Callis, Jordi](mailto:jordi.reig.callis@estudiantat.upc.edu)

## User Guide

### Setup

For the complete execution of the NetClass application, the following software is needed:

- [Python 2.7.0](https://www.python.org/download/releases/2.7/)
- [mitmproxy](https://mitmproxy.org/)

In order to download the necessary files, clone this repository with:

```
git clone https://github.com/ShimaSama/Netflix-QoS.git
```

After it, get into `Netflix-QoS` directory and install project dependencies:
```
pip install -r requirements.txt
```

### Computer traffic collection

Once all software is installed, it is time to collect decrypted traffic using *mitmweb* that will be used to classify encrypted traffic to, afterwards, train the model.
This script can be adapted to different services by changing the keywords of desired traffic. By default, application classifies between Netflix service and others, therefore, Netflix keywords are used.
```bash
mitmweb -s mitmpcap.py
```

When the data is collected and exported to `.pcap` files, we need to parse it to `.csv` files, which will be loaded in a simpler way to the python script to train the model.
```
tshark -r othersmobil.pcap -T fields -E header=y -E separator=, -E quote=d -E occurrence=f -e ip.version -e ip.hdr_len  -e ip.id -e ip.flags -e ip.flags.rb -e ip.flags.df -e ip.flags.mf -e ip.frag_offset -e ip.ttl -e ip.proto -e ip.checksum -e ip.len -e ip.dsfield -e tcp.srcport -e tcp.dstport -e tcp.seq -e tcp.ack -e tcp.len -e tcp.hdr_len -e tcp.flags -e tcp.flags.fin -e tcp.flags.syn -e tcp.flags.reset -e tcp.flags.push -e tcp.flags.ack -e tcp.flags.urg -e tcp.flags.cwr -e tcp.window_size -e tcp.checksum -e tcp.urgent_pointer > traffic.csv"
```

### Mobile traffic collection

To capture traffic from an Adnroid device we need to perform some specific steps. Android devices with a version higher or equal than 7 do not trust users certificates, so to simplify the process we need to install it as a system certificate to be able to capture https traffic from any application. This requires root access.
```
# Rename the certificate for the phone to accept it
hashed_name=`openssl x509 -inform PEM -subject_hash_old -in mitmproxy-ca-cert.cer | head -1`
cp mitmproxy-ca-cert.cer $hashed_name.0

# Push certificate to the phone
adb push $hashed_name.0 /sdcard
adb shell
  scorpio:/ $ su
  scorpio:/ # mount -o rw,remount /system /system
  scorpio:/ # cp /sdcard/<old_hash>.0 /system/etc/security/cacerts/<old_hash>.0
  scorpio:/ # chmod 644 /system/etc/security/cacerts/<old_hash>.0
  scorpio:/ # chown root:root /system/etc/security/cacerts/<old_hash>.0
  scorpio:/ # reboot

# Configure IP tables and run MITM proxy
sudo iptables -t nat -A POSTROUTING -s 10.10.10.0/24 -o wlan0 -j MASQUERADE
sudo iptables -t nat -A PREROUTING -i wlan0 -s 10.10.10.1/24 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i wlan0 -s 10.10.10.1/24 -p tcp --dport 443 -j REDIRECT --to-port 8080
mitmproxy --mode transparent -s mitmpcap.py
```
Change Android proxy settings to redirect to this device at port 8080.

### Model training

We have collected the data from the network and parsed it to csv file. Now it is time to create the model using the data generated with different algorithms. Following command generate three outputs:
- Most influence features plot
- Better algorithms plot
- Generated model with Random Forest Classifier algorithm, which has better performance (finalized_RFC_model.sav)
```
python2 classify.py traffic.csv
```

### Traffic classifying

Model is trained, so it is time to classify existing traffic. To do this, we need to execute the following command, specifying the file to classify:
```
python2 test.py <dataset>.csv
```

### Live traffic classifying

Previous solution is used to classify traffic with an already collected data, but we can also classify network traffic with live data, taking profit of mitmweb and loading the model on it with the command:
```
mitmweb -s mitmpcap_ml.py
```
