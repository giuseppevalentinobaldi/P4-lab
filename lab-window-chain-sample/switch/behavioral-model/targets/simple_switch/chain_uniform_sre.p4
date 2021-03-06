/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** G L O B A L  *************************************
*************************************************************************/

#define delta ( p - t )
#define lower_cool ( N + t )
#define lower ( t + 1)
#define upper ( W + t )
#define front (tw + delta)
#define behind (tw + delta - W)

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_TCP = 6;
const bit<32> N = 2;
const bit<32> W = 4;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> value_t;
typedef bit<8> value_opt_t;
typedef bit<32> index_t;
typedef bit<1>  boolean_t;
typedef bit<8>  tos_t;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

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
    ethernet_t ethernet;
    ipv4_t     ipv4;
    tcp_t      tcp;
}

/*************************************************************************
*********************** P A R S E R  *************************************
*************************************************************************/

parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

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
************   C H E C K S U M    V E R I F I C A T I O N   **************
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
**************  I N G R E S S   P R O C E S S I N G   ********************
*************************************************************************/
 
control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    // register
    register<value_t>((index_t) 3) reg;
    register<value_opt_t>((index_t) W) reg_se;
    
    value_t t; // reg index 0
    value_t emergency; // reg index 1
    value_t tw; // reg index 2
    
    boolean_t flag_clone = 0;
    boolean_t flag_emergency = 0;
    value_opt_t se;
    value_opt_t current_se;
    value_t p;
    
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
                // chain sample algorithm
                reg.read(t, 32w0); // read t
                t = t + 1;
                reg.write(32w0, t); // write t
                
                // initial sampling
                if(t <= N){
                    // clone
                    clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w100, { standard_metadata, meta });
                    
                    reg.read(tw, 32w2); // read tw
                    meta.tos = 1; // sample
                    
                    // calculate probability
                    random(p, lower_cool, upper);
                    
                    // write successor in the registers
                    if(tw + delta < W){
                        reg_se.read(se, front);
                        reg_se.write(front, se + 1); 
                    }
                    else{
                        reg_se.read(se, behind);
                        reg_se.write(behind, se + 1);
                    }
                    
                    // write expiry in the registers
                    reg_se.read(se, tw);
                    reg_se.write(tw, (se + 100)); // write packet expiry
                    
                }
                else{
                    reg.read(tw, 32w2); // read tw
                    reg.read(emergency, 32w1); // read emergency
                    reg_se.read(current_se, tw); // read expired
                    // expiry
                    if(current_se >= 100){
                        if(current_se == 100){
                            current_se = 0;
                            reg_se.write(tw, current_se); // reset reg expiry in position tw;
                        }
                        else{
                            current_se = current_se - 100;
                        }
                        flag_clone = 1; // write flag_clone true
                        meta.tos = 2; // expired
                    }
                    
                    // sampling
                    if(current_se > 0 || emergency >0){
                        if (meta.tos == 2){
                            meta.tos = 3; // sample & expired
                        }
                        else{
                            meta.tos = 1; // sample
                        }
                        flag_clone = 0; // write flag_clone false
                        
                        if(emergency > 0){
                            flag_emergency = 1;
                            // clone
                            clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w100, { standard_metadata, meta });
                            
                            // calculate probability
                            random(p, lower, upper);
                            
                            // write successor in the registers
                            if(tw + delta < W){
                                reg_se.read(se, front);
                                reg_se.write(front, se + 1); 
                            }
                            else{
                                reg_se.read(se, behind);
                                reg_se.write(behind, se + 1);
                            }
                            
                            // write expiry in the registers
                            reg_se.read(se, tw);
                            reg_se.write(tw, (se + 100)); // write packet expiry
                            
                            // decremente emergency
                            emergency = emergency - 1;
                            reg.write(32w1, emergency);
                            
                        }
                        if(flag_emergency == 1 && current_se > 0){
                            emergency = emergency + (bit<32>)current_se;
                            if(behind != tw){
                                reg.write(32w1, emergency);
                                reg_se.write(tw , 100); //reset successor
                            }
                            else{
                                reg.write(32w1, emergency);
                                reg_se.write(tw , 101); //reset successor
                            }
                        }
                        else if(current_se > 0){
                            // clone
                            clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w100, { standard_metadata, meta });
                            
                            //reset successor
                            current_se = current_se - 1;
                            if (current_se > 0){
                                reg.write(32w1, (bit<32>)current_se); // new emergency
                            }
                            reg_se.write(tw , 0);
                            
                            // calculate probability
                            random(p, lower, upper);
                            
                            // write successor in the registers
                            if(tw + delta < W){
                                reg_se.read(se, front);
                                reg_se.write(front, se + 1); 
                            }
                            else{
                                reg_se.read(se, behind);
                                reg_se.write(behind, se + 1);
                            }
                            
                            // write expiry in the registers
                            reg_se.read(se, tw);
                            reg_se.write(tw, (se + 100)); // write packet expiry
                        }
                    }
                    
                    // control flag_clone
                    if(flag_clone == 1){
                        // clone
                        clone3<tuple<standard_metadata_t, metadata >>(CloneType.I2E, 32w100, { standard_metadata, meta });
                        flag_clone = 0; // write flag_clone false
                    }
                }
                reg.read(tw, 32w2); // read tw
                tw = tw+1;
                if(tw == W){
                    tw = 0;
                }
                reg.write(32w2, tw);
            }// tcp condidiotn end
        }
        ipv4_lpm.apply();
    }// apply end
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {  

    action clone_assignments(){
        hdr.ipv4.diffserv = meta.tos;
    }

    table packet_clone {
        key = {
            standard_metadata.instance_type: exact;
        }
        actions = {
            clone_assignments;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        packet_clone.apply();
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   ***************
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
***********************  D E P A R S E R  ********************************
*************************************************************************/

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  ************************************
*************************************************************************/

V1Switch(
ParserImpl(),
verifyChecksum(),
ingress(),
egress(),
computeChecksum(),
DeparserImpl()
) main;

