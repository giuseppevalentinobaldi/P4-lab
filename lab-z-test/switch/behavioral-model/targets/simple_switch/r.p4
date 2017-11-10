/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;
const bit<16> N = 3;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<16> value_t;
typedef bit<32> index_t;
typedef bit<1> boolean_t;

struct intrinsic_metadata_t {
    bit<4>  mcast_grp;
    bit<4>  egress_rid;
    bit<16> mcast_hash;
    bit<32> lf_field_list;
    bit<16> resubmit_flag;
}

struct custom_metadata_t {
	boolean_t srcCorrect;
	bit<32> random;
    bit<16> index;
    bit<16> value;
    bit<8> f1;
}

struct custom_clone_packet_t{
	bit<1024> packet_clone;
}

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct metadata {
	custom_metadata_t custom_metadata;
	intrinsic_metadata_t intrinsic_metadata;
}

struct headers {
    ethernet_t 	ethernet;
    ipv4_t		ipv4;
    tcp_t		tcp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser ParserImpl(packet_in packet,
                  out headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }
    
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_TCP: parse_tcp;
            default: accept;
        }
    }
    
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
    
    state start {
        transition parse_ethernet;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control verifyChecksum(inout headers hdr, inout metadata meta) {   
    apply { 
    verify_checksum(true,
            { hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr
            },
            hdr.ipv4.hdrChecksum, HashAlgorithm.csum16);
     }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
 
control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    register<value_t>((index_t) 1) reg; 
    
    action drop() {
        mark_to_drop();
    }
    
    action set_check(boolean_t check){
    	meta.custom_metadata.srcCorrect = check;
    }
    
    action ipv4_forward(macAddr_t srcAddr, macAddr_t dstAddr, egressSpec_t port) {  	
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = srcAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    
    action set_port(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }
    
    table check_src {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            set_check;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    
    table resubmit_set_port {
        key = {
            meta.custom_metadata.f1: exact;
        }
        actions = {
            set_port;
            NoAction;
        }
        size = 128;
        default_action = NoAction();
    }
    
    apply {
    	check_src.apply();
    	if(hdr.ipv4.totalLen >= 16w400 && meta.custom_metadata.srcCorrect == 1 && meta.custom_metadata.f1 != 8w1){
        	//hash(meta.custom_metadata.hash_val1, HashAlgorithm.csum16, (bit<16>)0, { hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, hdr.ipv4.protocol, hdr.tcp.srcPort, hdr.tcp.dstPort }, (bit<32>)16);       		
        	meta.custom_metadata.index = 16w0;
        	reg.read(meta.custom_metadata.value, (bit<32>)meta.custom_metadata.index);
        	if(meta.custom_metadata.value < N){
        		meta.custom_metadata.value = meta.custom_metadata.value + 16w1;
        		reg.write((bit<32>)meta.custom_metadata.index, (bit<16>)meta.custom_metadata.value);
				meta.custom_metadata.f1 = 8w1;
				resubmit<tuple<standard_metadata_t, custom_metadata_t>>({ standard_metadata, meta.custom_metadata });
        		meta.custom_metadata.f1 = 8w0;
        	}
        	else{
        		random(meta.custom_metadata.random, 32w0, (bit<32>)meta.custom_metadata.value);
        		meta.custom_metadata.value = meta.custom_metadata.value + 16w1;
        		reg.write((bit<32>)meta.custom_metadata.index, (bit<16>)meta.custom_metadata.value);
        		if(meta.custom_metadata.random < (bit<32>)N){
        			meta.custom_metadata.f1 = 8w1;
        			resubmit<tuple<standard_metadata_t, custom_metadata_t>>({ standard_metadata, meta.custom_metadata });
        			meta.custom_metadata.f1 = 8w0;
        		}
        	}
        }
        if(meta.custom_metadata.f1 == 8w1){
        	resubmit_set_port.apply();
        }
        else{
    		ipv4_lpm.apply();
    	}
    }
}

/*alg r in python
*def r(packet):
*    global N, n, t, resevoir
*    if n < N:
*        resevoir[n] = packet
*        n = n + 1
*        if n == N:
*            t = n
*    else:
*        t = t + 1
*        M = random.randint(0, t - 1)
*        if M < n:
*            resevoir[M] = packet
*/

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {   
    apply {
     }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control computeChecksum(
    inout headers  hdr,
    inout metadata meta)
{
    apply {
        update_checksum(true,
            { hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr
            },
            hdr.ipv4.hdrChecksum, HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
ParserImpl(),
verifyChecksum(),
ingress(),
egress(),
computeChecksum(),
DeparserImpl()
) main;