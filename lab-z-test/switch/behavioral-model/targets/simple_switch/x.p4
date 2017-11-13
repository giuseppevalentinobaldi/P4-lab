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
    bit<1>  resubmit_flag;
    bit<48> ingress_global_tstamp;
    bit<16> mcast_grp;
    bit<1>  deflection_flag;
    bit<1>  deflect_on_drop;
    bit<19> enq_qdepth;
    bit<32> enq_tstamp;
    bit<2>  enq_congest_stat;
    bit<19> deq_qdepth;
    bit<2>  deq_congest_stat;
    bit<32> deq_timedelta;
    bit<13> mcast_hash;
    bit<16> egress_rid;
    bit<32> lf_field_list;
	bit<3> priority;
}

struct custom_metadata_t {
	boolean_t srcCorrect;
	bit<32> random_m;
	bit<32> random_v;
	bit<16> index_n;
    bit<16> value_n;
    bit<16> index_s;
    bit<16> value_s;
    bit<16> index_num;
    bit<16> value_num;
    bit<8> f1;
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
    register<value_t>((index_t) 3) reg; 
    
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
    
    apply {
    	check_src.apply();
    	if(hdr.ipv4.totalLen >= 16w400 && meta.custom_metadata.srcCorrect == 1 && meta.custom_metadata.f1 != 8w1){
        	meta.custom_metadata.index_n = 16w0;
        	reg.read(meta.custom_metadata.value_n, (bit<32>)meta.custom_metadata.index_n);
        	if(meta.custom_metadata.value_n < N){
        		meta.custom_metadata.value_n = meta.custom_metadata.value_n + 16w1;
        		reg.write((bit<32>)meta.custom_metadata.index_n, meta.custom_metadata.value_n);
				clone3<tuple<standard_metadata_t, custom_metadata_t>>(CloneType.I2E, 32w50,{ standard_metadata, meta.custom_metadata });
				if(meta.custom_metadata.value_n == N){
					meta.custom_metadata.index_s = 16w1;
        			meta.custom_metadata.index_num = 16w2;
        			reg.write((bit<32>)meta.custom_metadata.index_n, meta.custom_metadata.value_n + 16w1);
        			reg.write((bit<32>)meta.custom_metadata.index_s, 16w0);
        			reg.write((bit<32>)meta.custom_metadata.index_num, 16w0);
				}
        	}
        	else{
        		meta.custom_metadata.index_n = 16w0;
        		meta.custom_metadata.index_s = 16w1;
        		meta.custom_metadata.index_num = 16w2;
        		reg.read(meta.custom_metadata.value_n, (bit<32>)meta.custom_metadata.index_n);
        		reg.read(meta.custom_metadata.value_s, (bit<32>)meta.custom_metadata.index_s);
        		reg.read(meta.custom_metadata.value_num, (bit<32>)meta.custom_metadata.index_num);
        		random(meta.custom_metadata.random_v, 32w0, 32w1);
        		if( (meta.custom_metadata.value_num/meta.custom_metadata.value_t) > meta.custom_metadata.random_v
        		   && meta.custom_metadata.value_t == 16w0){
        		   clone3<tuple<standard_metadata_t, custom_metadata_t>>(CloneType.I2E, 32w50,{ standard_metadata, meta.custom_metadata });
        		}
        		//random(meta.custom_metadata.random, (bit<32>)32w0, (bit<32>)meta.custom_metadata.value);
        		meta.custom_metadata.value = meta.custom_metadata.value + 16w1;
        		reg.write((bit<32>)meta.custom_metadata.index, (bit<16>)meta.custom_metadata.value);
        		if(meta.custom_metadata.random < (bit<32>)N){
					clone3<tuple<standard_metadata_t, custom_metadata_t>>(CloneType.I2E, 32w50,{ standard_metadata, meta.custom_metadata });
        		}
        	}
        }
        ipv4_lpm.apply();
    }
}

/*alg x in python
*def calculateS(V):
*    global t, s, num
*    quot = num / t 
*    while quot > V:
*        s = s + 1
*        t = t + 1
*        num = num + 1
*        quot = quot * num / t 
*    
*def x(packet):
*    global N, n, t, resevoir, s, num
*    if n < N:
*        resevoir[n] = packet
*        n = n + 1
*        if n == N:
*            t = n
*    else:
*        if s == 0:
*            t = t + 1
*            num = num + 1
*            V = random.uniform(0, 1)
*            M = random.randint(0, n - 1)
*            if num > 1:
*                resevoir[M] = packet
*                calculateS(V)
*            else:
*                calculateS(V)
*                if s == 0:
*                    resevoir[M] = packet
*                else:
*                    s = s - 1                
*        else:
*            s = s - 1
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