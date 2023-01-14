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

### Traffic collection

Once all software is installed, it is time to collect decrypted traffic using *mitmweb* that will be used to classify encrypted traffic to, afterwards, train the model.
This script can be adapted to different services by changing the keywords of desired traffic. By default, application classifies between Netflix service and others, therefore, Netflix keywords are used.
```bash
mitmweb -s mitmpcap.py
```

When the data is collected and exported to `.pcap` files, we need to parse it to `.csv` files, which will be loaded in a simpler way to the python script to train the model.
```
tshark -r othersmobil.pcap -T fields -E header=y -E separator=, -E quote=d -E occurrence=f -e ip.version -e ip.hdr_len  -e ip.id -e ip.flags -e ip.flags.rb -e ip.flags.df -e ip.flags.mf -e ip.frag_offset -e ip.ttl -e ip.proto -e ip.checksum -e ip.len -e ip.dsfield -e tcp.srcport -e tcp.dstport -e tcp.seq -e tcp.ack -e tcp.len -e tcp.hdr_len -e tcp.flags -e tcp.flags.fin -e tcp.flags.syn -e tcp.flags.reset -e tcp.flags.push -e tcp.flags.ack -e tcp.flags.urg -e tcp.flags.cwr -e tcp.window_size -e tcp.checksum -e tcp.urgent_pointer > traffic.csv"
```

### Model training



