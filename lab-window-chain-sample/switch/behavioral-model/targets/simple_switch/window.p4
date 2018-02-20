/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#define c (W / N)
#define wj (t - W)

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;
const int<32> N = 90;
const int<32> W = 900;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef int<32> value_t;
typedef bit<32> index_t;
typedef bit<1>  boolean_t;
typedef bit<8>  tos_t;

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
    bit<3>  priority;
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
    intrinsic_metadata_t intrinsic_metadata;
    boolean_t            srcCorrect;
    tos_t                tos;
}

struct headers {
    ethernet_t	ethernet;
    ipv4_t	ipv4;
    tcp_t 	tcp;
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
    register<value_t>((index_t) 8) reg;
    int<32> tn; //reg[0] 
    int<32> ntot; //reg[1]
    int<32> V; //reg[2]
    int<32> t; //reg[3]
    int<32> wcount; //reg[4]
    int<32> ls; //reg[5]
    int<32> tw; //reg[6]
    int<32> Y; //reg[7]

    bit<32> caster;
    
    action drop() {
        mark_to_drop();
    }
    
    action set_check(boolean_t check){
    	meta.srcCorrect = check;
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
        if(hdr.ethernet.etherType == 0x800){
            if(hdr.ipv4.totalLen >= 16w256 && meta.srcCorrect == 1 && hdr.ipv4.protocol == 6){
                reg.read(ntot, 32w1);
                reg.read(tw, 32w6);
                if(ntot < N){ //cold start!!
        	        ntot = ntot + 32s1;
                    reg.write(32w1, ntot); //ntot = ntot + 1
                    reg.write(32w6, tw + 32s1); //tw = tw + 1
                    clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w50, { standard_metadata, meta });

                    if(ntot == N){
                        random(caster, 32w0, (bit<32>)N);
                        reg.write(32w2, (int<32>)caster); //P = random(0,N)
                        reg.write(32w3, ntot); //t = N
                    }
                }
                else{
                    reg.read(tn, 32w0);
                    reg.read(V, 32w2);
                    reg.read(t, 32w3);
                    reg.read(wcount, 32w4);
                    reg.read(ls, 32w5);
                    if(tw == W){
                        reg.write(32w6, 32s0); //tw = 0
                        reg.write(32w4, wcount + 32s1); //wcount = wcount +1
                        reg.read(tw, 32w6); //update tw
                        reg.read(wcount, 32w4); //update wcount
                    }
                    if(tn == N){
                        reg.write(32w0, 32s0); //tn = 0
                        reg.read(tn, 32w0); //update tn
                    }
                    tn = tn + 32s1;
                    tw = tw + 32s1;
                    t = t + 32s1;
                    reg.write(32w0, tn); //tn = tn + 1
                    reg.write(32w6, tw); //tw = tw + 1
                    reg.write(32w3, t); //t = t + 1
        	        if((wj + t - ntot) > W * wcount && wj > 0){
                        reg.read(Y, 32w7);
                        Y = Y + ls;
                        reg.write(32w7, Y);
                        if( (V - tn - Y) < 32s0 ){
                            reg.write(32w5, 32s0); //ls = 0
                            reg.write(32w7, 32s0); //Y = 0
                            random(caster, 32w0, (bit<32>)N -1);
                            reg.write(32w2,(int<32>)caster); //P = random(0,N)
                            reg.write(32w1, ntot + 32s1); //ntot = ntot + 1
                            clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w50, { standard_metadata, meta });

                        }
                        else{
                            reg.write(32w5, ls + 32s1); //ls= ls + 1
                            //skip
                        }
                    }
                    else{
                        if( (V - tn) < 32s0 ){
                            reg.write(32w5, 32s0); //ls = 0
                            reg.write(32w7, 32s0); //Y = 0
                            random(caster, 32w0, (bit<32>)N -1);
                            reg.write(32w2,(int<32>)caster); //P = random(0,N)
                            reg.write(32w1, ntot + 32s1); //ntot = ntot + 1
                            clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w50, { standard_metadata, meta });

                        }
                        else{
                            reg.write(32w5, ls + 32s1); //ls= ls + 1
                            //skip
                        }
                    }
                }
            }
        }
        ipv4_lpm.apply();
    }
}

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
