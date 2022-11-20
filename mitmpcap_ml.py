import functools
import json
import os
import shlex
from time import time
from math import modf
from struct import pack
from subprocess import Popen, PIPE

from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
import joblib

class Exporter:

    def __init__(self):
        self.sessions = {}

    def write(self, data):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def header(self):
        data = pack('<IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 0x040000, 1)
        self.write(data)

    def packet(self, src_host, src_port, dst_host, dst_port, payload):
        # Fer CSV
        key = '%s:%d-%s:%d' % (src_host, src_port, dst_host, dst_port)
        session = self.sessions.get(key)
        if session is None:
            session = {'seq': 1}
            self.sessions[key] = session
        seq = session['seq']

        data = {
            #"ip.version": "4", # Fixed
            #"ip.hdr_len": "20", # Fixed
            "ip.id": "0x00",
            "ip.flags": "0x00",
            "ip.flags.rb": "0",
            "ip.flags.df": "0",
            "ip.flags.mf": "0",
            "ip.frag_offset": "0",
            "ip.ttl": "64", # Fixed
            "ip.proto": "6",
            "ip.checksum": "0x00",
            "ip.src": src_host,
            "ip.dst": dst_host,
            "ip.len": str(len(payload) + 20 + 20),
            "ip.dsfield": "0x00",
            "tcp.srcport": str(src_port),
            "tcp.dstport": str(dst_port),
            "tcp.seq": str(seq), # Fixed
            "tcp.ack": "0", # Fixed
            "tcp.len": str(len(payload)),
            "tcp.hdr_len": "20", # Fixed
            "tcp.flags": "0x0018", # Fixed, above fixed
            "tcp.flags.fin": "0",
            "tcp.flags.syn": "0",
            "tcp.flags.reset": "0",
            "tcp.flags.push": "1",
            "tcp.flags.ack": "1",
            "tcp.flags.urg": "0",
            "tcp.flags.cwr": "0",
            "tcp.window_size": "512", # Fixed
            "tcp.checksum": "0x00", # Fixed
            "tcp.urgent_pointer": "0" # Fixed
        }

        for k in data.keys():
            item = data[k]
            if item.isdigit():
                data[k] = int(item)
            elif type(item) == str and item.startswith('0x'):
                data[k] = int(item, 16)
            elif '.' in item: # IPs
                data[k] = functools.reduce(lambda a, b: a << 8 | b, map(int, item.split(".")))


        loaded_model = joblib.load("finalized_RFC_model.sav")
        result = loaded_model.predict([list(data.values())])
        print(result)

        """with open('jsons.json') as f:
            pak_list = json.load(f)
        pak_list.append(data)
        with open('jsons.json', 'w') as f:
            f.write(json.dumps(pak_list, indent=4))
        print(data)"""

        tcp_args = [src_port, dst_port, seq, 0, 0x50, 0x18, 0x0200, 0, 0]
        tcp = pack('>HHIIBBHHH', *tcp_args)
        ipv4_args = [0x45, 0, int(data["ip.len"]), 0, 0, 0x40, 6, 0]

        ipv4_args.extend(map(int, src_host.split('.')))
        ipv4_args.extend(map(int, dst_host.split('.')))
        ipv4 = pack('>BBHHHBBHBBBBBBBB', *ipv4_args)
        link = b'\x00' * 12 + b'\x08\x00'

        usec, sec = modf(time())
        usec = int(usec * 1000 * 1000)
        sec = int(sec)
        size = len(link) + len(ipv4) + len(tcp) + len(payload)
        head = pack('<IIII', sec, usec, size, size)

        self.write(head)
        self.write(link)
        self.write(ipv4)
        self.write(tcp)
        self.write(payload)
        session['seq'] = seq + len(payload)

    def packets(self, src_host, src_port, dst_host, dst_port, payload):
        limit = 40960
        if src_host == "::1":
            src_host = "127.0.0.1"
        if dst_host == "::1":
            dst_host = "127.0.0.1"
        for i in range(0, len(payload), limit):
            self.packet(src_host, src_port,
                        dst_host, dst_port,
                        payload[i:i + limit])

class File(Exporter):

    def __init__(self, path):
        super().__init__()
        self.path = path
        if os.path.exists(path):
            self.file = open(path, 'ab')
        else:
            self.file = open(path, 'wb')
            self.header()

    def write(self, data):
        # Comparar data amb ML
        self.file.write(data)

    def flush(self):
        self.file.flush()

    def close(self):
        self.file.close()

class Pipe(Exporter):

    def __init__(self, cmd):
        super().__init__()
        self.proc = Popen(shlex.split(cmd), stdin=PIPE)
        self.header()

    def write(self, data):
        self.proc.stdin.write(data)

    def flush(self):
        self.proc.stdin.flush()

    def close(self):
        self.proc.terminate()
        self.proc.poll()

class Addon:

    def __init__(self, createf):
        self.createf = createf
        self.exporter = None

    def load(self, entry): # pylint: disable = unused-argument
        self.exporter = self.createf()

    def done(self):
        self.exporter.close()
        self.exporter = None

    def is_netflix(self, flow):
        key_words = ['netflix', 'nflx']
        for key in key_words:
            if key in flow.request.url or key in str(flow.response.headers):
                return True
        return False

    def response(self, flow):
        client_addr = list(flow.client_conn.peername[:2])
        server_addr = list(flow.server_conn.peername[:2])
        client_addr[0] = client_addr[0].replace('::ffff:', '')
        server_addr[0] = server_addr[0].replace('::ffff:', '')
        #if self.is_netflix(flow):
        #    self.exporter = self.exporter_net
        #else:
        #    self.exporter = self.exporter_oth
        self.export_request(client_addr, server_addr, flow.request)
        self.export_response(client_addr, server_addr, flow.response)
        self.exporter.flush()

    def export_request(self, client_addr, server_addr, r):
        proto = '%s %s %s\r\n' % (r.method, r.path, r.http_version)
        payload = bytearray()
        payload.extend(proto.encode('ascii'))
        payload.extend(bytes(r.headers))
        payload.extend(b'\r\n')
        payload.extend(r.raw_content)
        self.exporter.packets(*client_addr, *server_addr, payload)

    def export_response(self, client_addr, server_addr, r):
        headers = r.headers.copy()
        if r.http_version.startswith('HTTP/2'):
            headers.setdefault('content-length', str(len(r.raw_content)))
            proto = '%s %s\r\n' % (r.http_version, r.status_code)
        else:
            headers.setdefault('Content-Length', str(len(r.raw_content)))
            proto = '%s %s %s\r\n' % (r.http_version, r.status_code, r.reason)

        payload = bytearray()
        payload.extend(proto.encode('ascii'))
        payload.extend(bytes(headers))
        payload.extend(b'\r\n')
        payload.extend(r.raw_content)
        self.exporter.packets(*server_addr, *client_addr, payload)

addons = [Addon(lambda: File('out.pcap'))]
#addons = [Addon(lambda: Pipe('weer -'))]
