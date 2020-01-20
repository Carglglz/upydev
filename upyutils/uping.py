# µPing (MicroPing) for MicroPython
# copyright (c) 2018 Shawwwn <shawwwn1@gmail.com>
# License: MIT

# Internet Checksum Algorithm
# Author: Olav Morken
# https://github.com/olavmrk/python-ping/blob/master/ping.py
# @data: bytes

# ping statistics, loop mode and KeyboardInterrupt handler, + esp8266 compatible
# copyright (c) 2020 Carglglz
# License: MIT


def checksum(data):
    if len(data) & 0x1:  # Odd number of bytes
        data += b'\0'
    cs = 0
    for pos in range(0, len(data), 2):
        b1 = data[pos]
        b2 = data[pos + 1]
        cs += (b1 << 8) + b2
    while cs >= 0x10000:
        cs = (cs & 0xffff) + (cs >> 16)
    cs = ~cs & 0xffff
    return cs


def stddev(data):
    N = len(data)
    avg = sum(data)/N
    num = sum([(x-avg)**2 for x in data])
    den = N - 1
    stddev = (num/den)**0.5
    return stddev


def ping(host, count=4, timeout=5000, interval=10, quiet=False, size=64,
         rtn=True, loop=False, int_loop=800):
    import utime
    import uselect
    import uctypes
    import usocket
    import ustruct
    import urandom
    from sys import platform
    import gc
    from array import array

    # prepare packet
    assert size >= 16, "pkt size too small"
    pkt = b'Q'*size
    pkt_desc = {
        "type": uctypes.UINT8 | 0,
        "code": uctypes.UINT8 | 1,
        "checksum": uctypes.UINT16 | 2,
        "id": uctypes.UINT16 | 4,
        "seq": uctypes.INT16 | 6,
        "timestamp": uctypes.UINT64 | 8,
    }  # packet header descriptor
    h = uctypes.struct(uctypes.addressof(pkt), pkt_desc, uctypes.BIG_ENDIAN)
    h.type = 8  # ICMP_ECHO_REQUEST
    h.code = 0
    h.checksum = 0
    if platform == 'esp8266':
        h.id = urandom.getrandbits(16)
    else:
        h.id = urandom.randint(0, 65535)
    h.seq = 1
    time_data = array("f", (0 for _ in range(0)))

    # init socket
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
    sock.setblocking(0)
    sock.settimeout(timeout/1000)
    addr = usocket.getaddrinfo(host, 1)[0][-1][0]  # ip address
    sock.connect((addr, 1))
    not quiet and print("PING %s (%s): %u data bytes" % (host, addr, len(pkt)))
    seq_loop = -1
    try:
        if loop:
            n_trans = 0
            n_recv = 0
            while True:
                gc.collect()
                utime.sleep_ms(int_loop)
                count = 1
                seq_loop += 1
                seqs = list(range(1, count+1))  # [1,2,...,count]
                c = 1
                t = 0
                finish = False
                while t < timeout:
                    if t == interval and c <= count:
                        # send packet
                        h.checksum = 0
                        h.seq = c
                        h.timestamp = utime.ticks_us()
                        h.checksum = checksum(pkt)
                        if sock.send(pkt) == size:
                            n_trans += 1
                            t = 0  # reset timeout
                        else:
                            seqs.remove(c)
                            if loop:
                                count += 1
                                seqs.append(count)
                        c += 1

                    # recv packet
                    while 1:
                        socks, _, _ = uselect.select([sock], [], [], 0)
                        if socks:
                            resp = socks[0].recv(4096)
                            resp_mv = memoryview(resp)
                            h2 = uctypes.struct(uctypes.addressof(
                                resp_mv[20:]), pkt_desc, uctypes.BIG_ENDIAN)
                            # TODO: validate checksum (optional)
                            seq = h2.seq
                            # 0: ICMP_ECHO_REPLY
                            if h2.type == 0 and h2.id == h.id and (seq in seqs):
                                t_elapsed = (utime.ticks_us()-h2.timestamp) / 1000
                                ttl = ustruct.unpack('!B', resp_mv[8:9])[0]  # time-to-live
                                n_recv += 1
                                not quiet and print("{} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms".format(
                                    len(resp), addr, seq_loop, ttl, t_elapsed))
                                time_data.append(t_elapsed)
                                seqs.remove(seq)
                                if len(seqs) == 0:
                                    finish = True
                                    break
                        else:
                            break

                    if finish:
                        break

                    utime.sleep_ms(1)
                    t += 1

        else:
            seqs = list(range(1, count+1))  # [1,2,...,count]
            c = 1
            t = 0
            n_trans = 0
            n_recv = 0
            finish = False
            while t < timeout:
                if t == interval and c <= count:
                    # send packet
                    h.checksum = 0
                    h.seq = c
                    h.timestamp = utime.ticks_us()
                    h.checksum = checksum(pkt)
                    if sock.send(pkt) == size:
                        n_trans += 1
                        t = 0  # reset timeout
                    else:
                        seqs.remove(c)
                        if loop:
                            count += 1
                            seqs.append(count)
                    c += 1

                # recv packet
                while 1:
                    socks, _, _ = uselect.select([sock], [], [], 0)
                    if socks:
                        resp = socks[0].recv(4096)
                        resp_mv = memoryview(resp)
                        h2 = uctypes.struct(uctypes.addressof(
                            resp_mv[20:]), pkt_desc, uctypes.BIG_ENDIAN)
                        # TODO: validate checksum (optional)
                        seq = h2.seq
                        # 0: ICMP_ECHO_REPLY
                        if h2.type == 0 and h2.id == h.id and (seq in seqs):
                            t_elapsed = (utime.ticks_us()-h2.timestamp) / 1000
                            ttl = ustruct.unpack('!B', resp_mv[8:9])[0]  # time-to-live
                            n_recv += 1
                            not quiet and print("{} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms".format(
                                len(resp), addr, seq, ttl, t_elapsed))
                            time_data.append(t_elapsed)
                            seqs.remove(seq)
                            if loop:
                                count += 1
                                seqs.append(count)
                                utime.sleep_ms(int_loop)
                            if len(seqs) == 0:
                                finish = True
                                break
                    else:
                        break

                if finish:
                    if not loop:
                        break

                utime.sleep_ms(1)
                t += 1
        sock.close()
        if not quiet:
            print('--- {} ping statistics ---'.format(host))
            print("{} packets transmitted, {} packets received, {:.1f}% packet loss".format(
                n_trans, n_recv, (1-(n_recv/n_trans))*100))
            print("round-trip min/avg/max/stddev = {:.2f}/{:.2f}/{:.2f}/{:.2f} ms".format(min(time_data),sum(time_data)/len(time_data),max(time_data), stddev(time_data)))
        gc.collect()
        if rtn:
            return (n_trans, n_recv)
    except KeyboardInterrupt:
        # close
        sock.close()
        gc.collect()
        if not quiet:
            print('^C')
            print('--- {} ping statistics ---'.format(host))
            print("{} packets transmitted, {} packets received, {:.1f}% packet loss".format(
                n_trans, n_recv, (1-(n_recv/n_trans))*100))
            print("round-trip min/avg/max/stddev = {:.2f}/{:.2f}/{:.2f}/{:.2f} ms".format(min(time_data),sum(time_data)/len(time_data),max(time_data), stddev(time_data)))
        if rtn:
            return (n_trans, n_recv)
    except Exception as e:
        print(e)
