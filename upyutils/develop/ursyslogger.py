import socket
import sys
import machine
import binascii

NILVALUE = '-'
BOM_UTF8 = b'\xef\xbb\xbf'
SP = b' '
# As defined in RFC5424 Section 7
REGISTERED_SD_IDs = ('timeQuality', 'origin', 'meta')
SYSLOG_VERSION = '1'

EMERGENCY = const(70)
EMERG = EMERGENCY
ALERT =const(60)
NOTICE = const(25)


#  facility codes
LOG_KERN = const(0)       # kernel messages
LOG_USER = const(1)       # random user-level messages
LOG_MAIL = const(2)       # mail system
LOG_DAEMON = const(3)     # system daemons
LOG_AUTH = const(4)       # security/authorization messages
LOG_SYSLOG = const(5)     # messages generated internally by syslogd
LOG_LPR = const(6)        # line printer subsystem
LOG_NEWS = const(7)       # network news subsystem
LOG_UUCP = const(8)       # UUCP subsystem
LOG_CRON = const(9)       # clock daemon
LOG_AUTHPRIV = const(10)  # security/authorization messages (private)
LOG_FTP = const(11)       # FTP daemon
#  other codes through 15 reserved for system use
LOG_LOCAL0 = const(16)    # reserved for local use
LOG_LOCAL1 = const(17)    # reserved for local use
LOG_LOCAL2 = const(18)    # reserved for local use
LOG_LOCAL3 = const(19)    # reserved for local use
LOG_LOCAL4 = const(20)    # reserved for local use
LOG_LOCAL5 = const(21)    # reserved for local use
LOG_LOCAL6 = const(22)    # reserved for local use
LOG_LOCAL7 = const(23)    # reserved for local use

# RFC6587 framing
FRAMING_OCTET_COUNTING = const(1)
FRAMING_NON_TRANSPARENT = const(2)

class RsysLogger:

    # priorities (these are ordered)
    LOG_EMERG = 0    # system is unusable
    LOG_ALERT = 1    # action must be taken immediately
    LOG_CRIT = 2     # critical conditions
    LOG_ERR = 3      # error conditions
    LOG_WARNING = 4  # warning conditions
    LOG_NOTICE = 5   # normal but significant condition
    LOG_INFO = 6     # informational
    LOG_DEBUG = 7    # debug-level messages

    priority_map = {
        "DEBUG": LOG_DEBUG,
        "INFO": LOG_INFO,
        "NOTICE": LOG_NOTICE,
        "WARNING": LOG_WARNING,
        "ERROR": LOG_ERR,
        "CRITICAL": LOG_CRIT,
        "ALERT": LOG_ALERT,
        "EMERGENCY": LOG_EMERG,
        "EMERG": LOG_EMERG,
    }


    def __init__(self, addr, port=514, hostname=None, facility=LOG_USER,
                 msg_as_utf8=True, t_offset="+00:00"):

        self.addr = addr
        self.port = port
        self.facility = facility
        self.msg_as_utf8 = msg_as_utf8
        self.sock = None
        self.hostname = f"{hostname}.local"
        if not hostname:
            self.hostname = f"{sys.platform}-{binascii.hexlify(machine.unique_id()).decode()}.local"
        self.time_offset = t_offset
        self.framing=FRAMING_NON_TRANSPARENT
        self.connected = False
        self.connect()


    def connect(self):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.addr, self.port)[0][-1]
        self.sock.connect(addr)
        self.connected = True

    def encode_priority(self, facility, priority):
        return (facility << 3) | self.priority_map.get(priority, self.LOG_WARNING)

    @staticmethod
    def filter_printusascii(str_to_filter):
        return ''.join([x for x in str_to_filter if 33 <= ord(x) <= 126])

    def log_msg(self, msg, level, timestamp, appname):
        msg = self.build_msg(msg, level, timestamp, appname)
        self.transmit(msg)
        # self.sock.sendall(msg)

    def transmit(self, syslog_msg):
        # RFC6587 framing
        if self.framing == FRAMING_NON_TRANSPARENT:
            syslog_msg = syslog_msg.replace(b"\n", b"\\n")
            syslog_msg = b"".join((syslog_msg, b"\n"))
        else:
            syslog_msg = b" ".join((str(len(syslog_msg)).encode("ascii"), syslog_msg))
        
        self.sock.sendall(syslog_msg)


    def build_msg(self, record, level, timestamp, appname):
        # The syslog message has the following ABNF [RFC5234] definition:
        #
        #     SYSLOG-MSG      = HEADER SP STRUCTURED-DATA [SP MSG]
        #
        #     HEADER          = PRI VERSION SP TIMESTAMP SP HOSTNAME
        #                     SP APP-NAME SP PROCID SP MSGID
        #     PRI             = "<" PRIVAL ">"
        #     PRIVAL          = 1*3DIGIT ; range 0 .. 191
        #     VERSION         = NONZERO-DIGIT 0*2DIGIT
        #     HOSTNAME        = NILVALUE / 1*255PRINTUSASCII
        #
        #     APP-NAME        = NILVALUE / 1*48PRINTUSASCII
        #     PROCID          = NILVALUE / 1*128PRINTUSASCII
        #     MSGID           = NILVALUE / 1*32PRINTUSASCII
        #
        #     TIMESTAMP       = NILVALUE / FULL-DATE "T" FULL-TIME
        #     FULL-DATE       = DATE-FULLYEAR "-" DATE-MONTH "-" DATE-MDAY
        #     DATE-FULLYEAR   = 4DIGIT
        #     DATE-MONTH      = 2DIGIT  ; 01-12
        #     DATE-MDAY       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based on
        #                             ; month/year
        #     FULL-TIME       = PARTIAL-TIME TIME-OFFSET
        #     PARTIAL-TIME    = TIME-HOUR ":" TIME-MINUTE ":" TIME-SECOND
        #                     [TIME-SECFRAC]
        #     TIME-HOUR       = 2DIGIT  ; 00-23
        #     TIME-MINUTE     = 2DIGIT  ; 00-59
        #     TIME-SECOND     = 2DIGIT  ; 00-59
        #     TIME-SECFRAC    = "." 1*6DIGIT
        #     TIME-OFFSET     = "Z" / TIME-NUMOFFSET
        #     TIME-NUMOFFSET  = ("+" / "-") TIME-HOUR ":" TIME-MINUTE
        #
        #
        #     STRUCTURED-DATA = NILVALUE / 1*SD-ELEMENT
        #     SD-ELEMENT      = "[" SD-ID *(SP SD-PARAM) "]"
        #     SD-PARAM        = PARAM-NAME "=" %d34 PARAM-VALUE %d34
        #     SD-ID           = SD-NAME
        #     PARAM-NAME      = SD-NAME
        #     PARAM-VALUE     = UTF-8-STRING ; characters '"', '\' and
        #                                  ; ']' MUST be escaped.
        #     SD-NAME         = 1*32PRINTUSASCII
        #                     ; except '=', SP, ']', %d34 (")
        #
        #     MSG             = MSG-ANY / MSG-UTF8
        #     MSG-ANY         = *OCTET ; not starting with BOM
        #     MSG-UTF8        = BOM UTF-8-STRING
        #     BOM             = %xEF.BB.BF
        #
        #     UTF - 8 - STRING = *OCTET ; UTF - 8 string as specified
        #                               ; in RFC 3629
        #
        #     OCTET = % d00 - 255
        #     SP = % d32
        #     PRINTUSASCII = % d33 - 126
        #     NONZERO - DIGIT = % d49 - 57
        #     DIGIT = % d48 / NONZERO - DIGIT
        #     NILVALUE = "-"

        # HEADER
        pri = '<%d>' % self.encode_priority(self.facility, level)
        version = SYSLOG_VERSION
        hostname = self.hostname
        timestamp = f"{timestamp.replace(" ", "T")}{self.time_offset}"
        procid = NILVALUE
        msgid = NILVALUE
        pri = pri.encode('ascii')
        version = version.encode('ascii')
        timestamp = timestamp.encode('ascii')
        hostname = hostname.encode('ascii', 'replace')[:255]
        appname = appname.encode('ascii', 'replace')[:48]
        procid = procid.encode('ascii', 'replace')[:128]
        msgid = msgid.encode('ascii', 'replace')[:32]

        header = b''.join((pri, version, SP, timestamp, SP, hostname, SP, appname, SP, procid, SP, msgid))

        # STRUCTURED-DATA
        enterprise_id = None
        structured_data = {}
        cleaned_structured_data = []
        for sd_id, sd_params in list(structured_data.items()):
            # Clean structured data ID
            sd_id = self.filter_printusascii(sd_id)
            sd_id = sd_id.replace('=', '').replace(' ', '').replace(']', '').replace('"', '')
            if '@' not in sd_id and sd_id not in REGISTERED_SD_IDs and enterprise_id is None:
                raise ValueError("Enterprise ID has not been set. Cannot build structured data ID. "
                       "Please set a enterprise ID when initializing the logging handler "
                       "or include one in the structured data ID.")
            elif '@' in sd_id:
                sd_id, enterprise_id = sd_id.rsplit('@', 1)

            if len(enterprise_id) > 30:
                raise ValueError("Enterprise ID is too long. Impossible to build structured data ID.")

            sd_id = sd_id.replace('@', '')
            if len(sd_id) + len(enterprise_id) > 32:
                sd_id = sd_id[:31 - len(enterprise_id)]
            if sd_id not in REGISTERED_SD_IDs:
                sd_id = '@'.join((sd_id, enterprise_id))
            sd_id = sd_id.encode('ascii', 'replace')

            cleaned_sd_params = []
            # ignore sd params not int key-value format
            if isinstance(sd_params, dict):
                sd_params = sd_params.items()
            else:
                sd_params = []

            # Clean key-value pairs
            for (param_name, param_value) in sd_params:
                param_name = self.filter_printusascii(str(param_name))
                param_name = param_name.replace('=', '').replace(' ', '').replace(']', '').replace('"', '')
                if param_value is None:
                    param_value = ''

                param_value = str(param_value)

                param_value = param_value.replace('\\', '\\\\').replace('"', '\\"').replace(']', '\\]')

                param_name = param_name.encode('ascii', 'replace')[:32]
                param_value = param_value.encode('utf-8', 'replace')

                sd_param = b''.join((param_name, b'="', param_value, b'"'))
                cleaned_sd_params.append(sd_param)

                cleaned_sd_params = SP.join(cleaned_sd_params)

                # build structured data element
                spacer = SP if cleaned_sd_params else b''
                sd_element = b''.join((b'[', sd_id, spacer, cleaned_sd_params, b']'))
                cleaned_structured_data.append(sd_element)

        if cleaned_structured_data:
            structured_data = b''.join(cleaned_structured_data)
        else:
            structured_data = NILVALUE.encode('ascii')

        # MSG
        if record is None or record == "":
            pieces = (header, structured_data)
        else:
            msg = record
        if self.msg_as_utf8:
            msg = b''.join((BOM_UTF8, msg.encode('utf-8')))
        else:
            msg = msg.encode('utf-8')

        pieces = (header, structured_data, msg)
        syslog_msg = SP.join(pieces)

        return syslog_msg
