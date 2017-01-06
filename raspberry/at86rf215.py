# Register's values for the at86rf215 sub-GHz modem

# MACROS
# modem commands
CMD_RF_NOP = 0x0
CMD_RF_SLEEP = 0x1
CMD_RF_TRXOFF = 0x2
CMD_RF_TXPREP = 0x3
CMD_RF_TX = 0x4
CMD_RF_RX = 0x5
CMD_RF_RESET = 0x7

# modem states
RF_STATE_TRXOFF = 0x2
RF_STATE_TXPREP = 0x3
RF_STATE_TX = 0x4
RF_STATE_RX = 0x5
RF_STATE_TRANSITION = 0x6
RF_STATE_RESET = 0x7

# Radio IRQ Status
IRQS_WAKEUP = 0x01
IRQS_TRXRDY = 0x02
IRQS_EDC = 0x04
IRQS_BATLOW = 0x08
IRQS_TRXERR = 0x10
IRQS_IQIFSF = 0x20

# Baseband IRQ Status
IRQS_RXFS = 0x01
IRQS_RXFE = 0x02
IRQS_RXAM = 0x04
IRQS_RXEM = 0x08
IRQS_TXFE = 0x10
IRQS_AGCH = 0x20
IRQS_AGCR = 0x40
IRQS_FBLI = 0x80

# Reset command
RST_CMD = 0x07

# Addresses

RG_RF09_IRQS = [0x00, 0x00]
RG_RF24_IRQS = [0x00, 0x01]
RG_BBC0_IRQS = [0x00, 0x02]
RG_BBC1_IRQS = [0x00, 0x03]
RG_RF_RST = [0x00, 0x05]
RG_RF_CFG = [0x00, 0x06]
RG_RF_CLKO = [0x00, 0x07]
RG_RF_BMDVC = [0x00, 0x08]
RG_RF_XOC = [0x00, 0x09]
RG_RF_IQIFC0 = [0x00, 0x0A]
RG_RF_IQIFC1 = [0x00, 0x0B]
RG_RF_IQIFC2 = [0x00, 0x0C]
RG_RF_PN = [0x00, 0x0D]
RG_RF_VN = [0x00, 0x0E]

RG_RF09_IRQM = [0x01, 0x00]
RG_RF09_AUXS = [0x01, 0x01]
RG_RF09_STATE = [0x01, 0x02]
RG_RF09_CMD = [0x01, 0x03]
RG_RF09_CS = [0x01, 0x04]
RG_RF09_CCF0L = [0x01, 0x05]
RG_RF09_CCF0H = [0x01, 0x06]
RG_RF09_CNL = [0x01, 0x07]
RG_RF09_CNM = [0x01, 0x08]
RG_RF09_RXBWC = [0x01, 0x09]
RG_RF09_RXDFE = [0x01, 0x0A]
RG_RF09_AGCC = [0x01, 0x0B]
RG_RF09_AGCS = [0x01, 0x0C]
RG_RF09_RSSI = [0x01, 0x0D]
RG_RF09_EDC = [0x01, 0x0E]
RG_RF09_EDD = [0x01, 0x0F]
RG_RF09_EDV = [0x01, 0x10]
RG_RF09_RNDV = [0x01, 0x11]
RG_RF09_TXCUTC = [0x01, 0x12]
RG_RF09_TXDFE = [0x01, 0x13]
RG_RF09_PAC = [0x01, 0x14]

RG_RF24_IRQM = [0x02, 0x00]

RG_BBC0_IRQM = [0x03, 0x00]
RG_BBC0_PC = [0x03, 0x01]
RG_BBC0_PS = [0x03, 0x02]
RG_BBC0_RXFLL = [0x03, 0x04]
RG_BBC0_RXFLH = [0x03, 0x05]
RG_BBC0_TXFLL = [0x03, 0x06]
RG_BBC0_TXFLH = [0x03, 0x07]
RG_BBC0_FBLL = [0x03, 0x08]
RG_BBC0_FBLH = [0x03, 0x09]
RG_BBC0_FBLIL = [0x03, 0x0A]
RG_BBC0_FBLIH = [0x03, 0x0B]

RG_BBC0_OFDMPHRTX = [0x03, 0x0C]
RG_BBC0_OFDMPHRRX = [0x03, 0x0D]
RG_BBC0_OFDMC = [0x03, 0x0E]
RG_BBC0_OFDMSW = [0x03, 0x0F]
RG_BBC0_OQPSKC0 = [0x03, 0x10]
RG_BBC0_OQPSKC1 = [0x03, 0x11]
RG_BBC0_OQPSKC2 = [0x03, 0x12]
RG_BBC0_OQPSKC3 = [0x03, 0x13]
RG_BBC0_OQPSKPHRTX = [0x03, 0x14]
RG_BBC0_OQPSKPHRRX = [0x03, 0x15]
RG_BBC0_FSKC0 = [0x03, 0x60]
RG_BBC0_FSKC1 = [0x03, 0x61]
RG_BBC0_FSKC2 = [0x03, 0x62]
RG_BBC0_FSKC3 = [0x03, 0x63]
RG_BBC0_FSKC4 = [0x03, 0x64]
RG_BBC0_FSKPHRTX = [0x03, 0x6A]
RG_BBC0_FSKPHRRX = [0x03, 0x6B]
RG_BBC0_FSKDM = [0x03, 0x72]
RG_BBC0_FSKPE0 = [0x03, 0x73]
RG_BBC0_FSKPE1 = [0x03, 0x74]
RG_BBC0_FSKPE2 = [0x03, 0x75]

RG_BBC1_IRQM = [0x04, 0x00]

RG_BBC0_FBRXS = [0x20, 0x00]
RG_BBC0_FBRXE = [0x27, 0xFE]
RG_BBC0_FBTXS = [0x28, 0x00]
RG_BBC0_FBTXE = [0x2F, 0xFE]

OFDMPHRRX_MCS_MASK = 0x07

fsk_option1_FEC = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),
    (RG_RF09_RXDFE, 0x1A),
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0xC0),
    (RG_RF09_TXDFE, 0x98),
    (RG_RF09_PAC, 0x64),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x1D),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x01),  # //Direct modulation and preemphasis enabled.
    (RG_BBC0_FSKC0, 0xD6),
    (RG_BBC0_FSKC1, 0x00),
    (RG_BBC0_FSKC2, 0x40),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x0A),  # //FEC enabled. IEEE MODE
    (RG_BBC0_FSKPE0, 0x02),
    (RG_BBC0_FSKPE1, 0x03),
    (RG_BBC0_FSKPE2, 0xFC),
    (RG_BBC0_FSKPHRTX, 0x00)
]

fsk_option2_FEC = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x03),
    (RG_RF09_RXDFE, 0x15),
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x83),
    (RG_RF09_TXDFE, 0x94),
    (RG_RF09_PAC, 0x7F),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.//
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x1D),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x03),  # //Direct modulation and Preemphasis enabled.
    (RG_BBC0_FSKC0, 0xD6),
    (RG_BBC0_FSKC1, 0x01),
    (RG_BBC0_FSKC2, 0x40),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x0A),  # //FEC enabled. IEEE MODE
    (RG_BBC0_FSKPE0, 0x0E),
    (RG_BBC0_FSKPE1, 0x0F),
    (RG_BBC0_FSKPE2, 0xF0),
    (RG_BBC0_FSKPHRTX, 0x00)
]

fsk_option3_FEC = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x03),  # //IF shift, 200 kHz bandwidth
    (RG_RF09_RXDFE, 0x24),  # //find the right values
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x84),  # //find the right values
    (RG_RF09_TXDFE, 0x12),  # //find the right values
    (RG_RF09_PAC, 0x64),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x15),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x03),  # //Direct modulation and Preemphasis enabled.
    (RG_BBC0_FSKC0, 0xC1),
    (RG_BBC0_FSKC1, 0x03),
    (RG_BBC0_FSKC2, 0x00),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x0A),
    (RG_BBC0_FSKPE0, 0x74),
    (RG_BBC0_FSKPE1, 0x7F),
    (RG_BBC0_FSKPE2, 0x80),
    (RG_BBC0_FSKPHRTX, 0x00)
]

fsk_option1 = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),
    (RG_RF09_RXDFE, 0x1A),
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0xC0),
    (RG_RF09_TXDFE, 0x98),
    (RG_RF09_PAC, 0x64),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x1D),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x01),  # //Direct modulation and preemphasis enabled.
    (RG_BBC0_FSKC0, 0xD6),
    (RG_BBC0_FSKC1, 0x00),
    (RG_BBC0_FSKC2, 0x40),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x00),  # //FEC enabled. IEEE MODE
    (RG_BBC0_FSKPE0, 0x02),
    (RG_BBC0_FSKPE1, 0x03),
    (RG_BBC0_FSKPE2, 0xFC),
    (RG_BBC0_FSKPHRTX, 0x00)
]

fsk_option2 = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x03),
    (RG_RF09_RXDFE, 0x15),
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x83),
    (RG_RF09_TXDFE, 0x94),
    (RG_RF09_PAC, 0x64),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.//
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x1D),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x03),  # //Direct modulation and Preemphasis enabled.
    (RG_BBC0_FSKC0, 0xD6),
    (RG_BBC0_FSKC1, 0x01),
    (RG_BBC0_FSKC2, 0x40),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x00),  # //FEC enabled. IEEE MODE
    (RG_BBC0_FSKPE0, 0x0E),
    (RG_BBC0_FSKPE1, 0x0F),
    (RG_BBC0_FSKPE2, 0xF0),
    (RG_BBC0_FSKPHRTX, 0x00)
]

fsk_option3 = [
    (RG_RF09_CMD, 0x02),  # //we make sure we are in the trxoff state
    (RG_RF09_IRQM, 0x1F),  # // TRXERR, BATLOW, EDC, TRXRDY, WAKEUP interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x03),  # //IF shift, 200 kHz bandwidth
    (RG_RF09_RXDFE, 0x24),  # //find the right values
    (RG_RF09_AGCC, 0x01),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x84),  # //find the right values
    (RG_RF09_TXDFE, 0x12),  # //find the right values
    (RG_RF09_PAC, 0x64),  # // Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.
    (RG_BBC0_IRQM, 0x1F),  # // TXFE, RXEM, RXAM, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x15),  # // No FCS filter, 32 bits FCS, FSK.
    (RG_BBC0_FSKDM, 0x03),  # //Direct modulation and Preemphasis enabled.
    (RG_BBC0_FSKC0, 0xC1),
    (RG_BBC0_FSKC1, 0x03),
    (RG_BBC0_FSKC2, 0x00),
    (RG_BBC0_FSKC3, 0x85),
    (RG_BBC0_FSKC4, 0x00),
    (RG_BBC0_FSKPE0, 0x74),
    (RG_BBC0_FSKPE1, 0x7F),
    (RG_BBC0_FSKPE2, 0x80),
    (RG_BBC0_FSKPHRTX, 0x00)
]

oqpsk_rate1 = [
    (RG_BBC0_PC, 0x17),
    (RG_BBC0_OQPSKPHRTX, 0x00),  # MR-OQPSK, rate mode 0
    (RG_BBC0_OQPSKC0, 0x10),  # 100kchips/s, RC-0.8 shaping, direct-modulation enabled
	# (RG_BBC0_OQPSKC1,   0x3F),#// MINIMUM preamble-detection sensitivities, rx-override disabled
	# (RG_BBC0_OQPSKC2,   0x00),#// listen for MR-OQPSK frames only
	# (RG_BBC0_OQPSKC3,   0x00),#// legacy OQPSK, search for SFD_1 only
    (RG_BBC0_IRQM, 0x13),  # // TXFE, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_RF09_IRQM, 0x12),  # // TRXERR, TRXRDY interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),  # Rx BW 160kHz, IF 250kHz
    (RG_RF09_RXDFE, 0x2A),  # //
    (RG_RF09_AGCC, 0x21),
    (RG_RF09_EDD, 0x2B),
    (RG_RF09_AGCS, 0x77),
    (RG_RF09_TXCUTC, 0xC7),  # .PARAMP = 3, .LPFCUT = 7
    (RG_RF09_TXDFE, 0x7A),  # // .SR = 0xA, .RCUT = 3
    (RG_RF09_PAC, 0x64)
]

oqpsk_rate2 = [
    (RG_BBC0_PC, 0x17),
    (RG_BBC0_OQPSKPHRTX, 0x02),  # // MR-OQPSK, rate mode 1
    (RG_BBC0_OQPSKC0, 0x10),  # // 100kchips/s, RC-0.8 shaping, direct-modulation enabled
	# //  (RG_BBC0_OQPSKC1,   0x3F),  // MINIMUM preamble-detection sensitivities, rx-override disabled
	# //  (RG_BBC0_OQPSKC2,   0x00),  // listen for MR-OQPSK frames only
	# //  (RG_BBC0_OQPSKC3,   0x00),  // legacy OQPSK, search for SFD_1 only
    (RG_BBC0_IRQM, 0x13),  # // TXFE, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_RF09_IRQM, 0x12),  # // TRXERR, TRXRDY interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),  # //  Rx BW 160kHz, IF 250kHz
    (RG_RF09_RXDFE, 0x2A),  # //
    (RG_RF09_AGCC, 0x21),
    (RG_RF09_EDD, 0x2B),
    (RG_RF09_AGCS, 0x77),
    (RG_RF09_TXCUTC, 0xC7),  # // .PARAMP = 3, .LPFCUT = 7
    (RG_RF09_TXDFE, 0x7A),  # // .SR = 0xA, .RCUT = 3
    (RG_RF09_PAC, 0x64)
]

oqpsk_rate3 = [
    (RG_BBC0_PC, 0x17),
    (RG_BBC0_OQPSKPHRTX, 0x04),  # // MR-OQPSK, rate mode 2
    (RG_BBC0_OQPSKC0, 0x10),  # // 100kchips/s, RC-0.8 shaping, direct-modulation enabled
	# (RG_BBC0_OQPSKC1,   0x3F),  // MINIMUM preamble-detection sensitivities, rx-override disabled
	# (RG_BBC0_OQPSKC2,   0x00),  // listen for MR-OQPSK frames only
	# (RG_BBC0_OQPSKC3,   0x00),  // legacy OQPSK, search for SFD_1 only
    (RG_BBC0_IRQM, 0x13),  # // TXFE, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_RF09_IRQM, 0x12),  # // TRXERR, TRXRDY interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),  # //  Rx BW 160kHz, IF 250kHz
    (RG_RF09_RXDFE, 0x2A),  # //
    (RG_RF09_AGCC, 0x21),
    (RG_RF09_EDD, 0x2B),
    (RG_RF09_AGCS, 0x77),
    (RG_RF09_TXCUTC, 0xC7),  # # .PARAMP = 3, .LPFCUT = 7
    (RG_RF09_TXDFE, 0x7A),  # # .SR = 0xA, .RCUT = 3
    (RG_RF09_PAC, 0x64)
]

oqpsk_rate4 = [
    (RG_BBC0_PC, 0x17),
    (RG_BBC0_OQPSKPHRTX, 0x06),  # # MR-OQPSK, rate mode 3
    (RG_BBC0_OQPSKC0, 0x10),  ## 100kchips/s, RC-0.8 shaping, direct-modulation enabled
	# (RG_BBC0_OQPSKC1,   0x3F),  # MINIMUM preamble-detection sensitivities, rx-override disabled
	# (RG_BBC0_OQPSKC2,   0x00),  # listen for MR-OQPSK frames only
	# (RG_BBC0_OQPSKC3,   0x00),  # legacy OQPSK, search for SFD_1 only
    (RG_BBC0_IRQM, 0x13),  # # TXFE, RXFE, RXFS interrupts enabled
    (RG_BBC1_IRQM, 0x00),
    (RG_RF09_IRQM, 0x12),  # # TRXERR, TRXRDY interrupts enabled
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x00),  # #  Rx BW 160kHz, IF 250kHz
    (RG_RF09_RXDFE, 0x2A),  # #
    (RG_RF09_AGCC, 0x21),
    (RG_RF09_EDD, 0x2B),
    (RG_RF09_AGCS, 0x77),
    (RG_RF09_TXCUTC, 0xC7),  # # .PARAMP = 3, .LPFCUT = 7
    (RG_RF09_TXDFE, 0x7A),  # # .SR = 0xA, .RCUT = 3
    (RG_RF09_PAC, 0x64)
]

# OFDM

ofdm_1_mcs0 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x19),
    (RG_RF09_RXDFE, 0x83),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x0A),  # recommended value (0x0B)
    (RG_RF09_TXDFE, 0x83),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F. # 0x64 - 0dBm  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x00),
    (RG_BBC0_OFDMPHRTX, 0x00)
]

ofdm_1_mcs1 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x19),
    (RG_RF09_RXDFE, 0x83),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x0A),  # recommended value (0x0B)
    (RG_RF09_TXDFE, 0x83),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F. # 0x64 - 0dBm  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x00),
    (RG_BBC0_OFDMPHRTX, 0x01)
]

ofdm_1_mcs2 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x19),
    (RG_RF09_RXDFE, 0x83),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x0A),  # recommended value (0x0B)
    (RG_RF09_TXDFE, 0x83),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F. # 0x64 - 0dBm  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x00),
    (RG_BBC0_OFDMPHRTX, 0x02)
]

ofdm_1_mcs3 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x19),
    (RG_RF09_RXDFE, 0x83),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x0A),  # recommended value (0x0B)
    (RG_RF09_TXDFE, 0x83),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F. # 0x64 - 0dBm  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x00),
    (RG_BBC0_OFDMPHRTX, 0x03)
]

ofdm_2_mcs0 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x00)
]

ofdm_2_mcs1 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x01)
]

ofdm_2_mcs2 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x02)
]

ofdm_2_mcs3 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x03)
]

ofdm_2_mcs4 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x04)
]

ofdm_2_mcs5 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x17),
    (RG_RF09_RXDFE, 0x43),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x08),  # recommended value ()
    (RG_RF09_TXDFE, 0x63),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x01),
    (RG_BBC0_OFDMPHRTX, 0x05)
]

ofdm_3_mcs1 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x01)
]

ofdm_3_mcs2 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x02)
]

ofdm_3_mcs3 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x03)
]

ofdm_3_mcs4 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x04)
]

ofdm_3_mcs5 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x05)
]

ofdm_3_mcs6 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x04),
    (RG_RF09_RXDFE, 0x46),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x05),  # recommended value ()
    (RG_RF09_TXDFE, 0x66),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x02),
    (RG_BBC0_OFDMPHRTX, 0x06)
]

ofdm_4_mcs2 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x12),
    (RG_RF09_RXDFE, 0x26),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x03),  # recommended value ()
    (RG_RF09_TXDFE, 0x46),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x03),
    (RG_BBC0_OFDMPHRTX, 0x02)
]

ofdm_4_mcs3 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x12),
    (RG_RF09_RXDFE, 0x26),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x03),  # recommended value ()
    (RG_RF09_TXDFE, 0x46),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x03),
    (RG_BBC0_OFDMPHRTX, 0x03)
]

ofdm_4_mcs4 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x12),
    (RG_RF09_RXDFE, 0x26),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x03),  # recommended value ()
    (RG_RF09_TXDFE, 0x46),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x03),
    (RG_BBC0_OFDMPHRTX, 0x04)
]

ofdm_4_mcs5 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x12),
    (RG_RF09_RXDFE, 0x26),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x03),  # recommended value ()
    (RG_RF09_TXDFE, 0x46),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x03),
    (RG_BBC0_OFDMPHRTX, 0x05)
]

ofdm_4_mcs6 = [
    (RG_RF09_CMD, 0x02),
    (RG_RF09_IRQM, 0x1F),
    (RG_RF24_IRQM, 0x00),
    (RG_RF09_RXBWC, 0x12),
    (RG_RF09_RXDFE, 0x26),
    (RG_RF09_AGCC, 0x11),
    (RG_RF09_EDD, 0x7A),
    (RG_RF09_TXCUTC, 0x03),  # recommended value ()
    (RG_RF09_TXDFE, 0x46),
    (RG_RF09_PAC, 0x64),  # Tx Power 5 bits >>. 0x64 = txPwr=>0x04, max: 0x1F.  mettre 0x7F
    (RG_BBC0_IRQM, 0x1F),
    (RG_BBC1_IRQM, 0x00),
    (RG_BBC0_PC, 0x16),  # NO FCS FILTER
    (RG_BBC0_OFDMC, 0x03),
    (RG_BBC0_OFDMPHRTX, 0x06)
]

packet_sizes = [6, 127, 1000, 2047]
# set_frequency(channel_spacing, frequency_0, channel)
frequencies_setup = [
    (200, 863125, 0),  # fsk operating mode 1
    (400, 863225, 0),  # fsk operating mode 2-3
    (1200, 863625, 0),  # ofdm option 1
    (800, 863425, 0),  # ofdm option 2
    (400, 863225, 0),  # ofdm option 3
    (200, 863125, 0),  # ofdm option 4
    (600, 868300, 0),  # oqpsk
    (200, 863125, 17),  # fsk operating mode 1
    (400, 863225, 9),  # fsk operating mode 2-3
    (1200, 863625, 2),  # ofdm option 1
    (800, 863425, 4),  # ofdm option 2
    (400, 863225, 8),  # ofdm option 3
    (200, 863125, 17),  # ofdm option 4
    (600, 868950, 0)  # oqpsk
]

modulation_list_rx = [
    (ofdm_1_mcs0),
    (ofdm_2_mcs0),
    (ofdm_3_mcs1),
    (ofdm_4_mcs2),
    (fsk_option1_FEC),
    (fsk_option2_FEC),
    (fsk_option1),
    (fsk_option2),
    (oqpsk_rate1)
]

modulation_list_tx = [
    (fsk_option1_FEC),  # 01
    (fsk_option2_FEC),  # 02
    (fsk_option1),  # 03
    (fsk_option2),  # 04
    (ofdm_1_mcs0),  # 05
    (ofdm_2_mcs0),  # 06
    (ofdm_1_mcs1),  # 07
    (ofdm_2_mcs1),  # 08
    (ofdm_3_mcs1),  # 09
    (ofdm_1_mcs2),  # 10
    (ofdm_2_mcs2),  # 11
    (ofdm_3_mcs2),  # 12
    (ofdm_4_mcs2),  # 13
    (ofdm_1_mcs3),  # 14
    (ofdm_2_mcs3),  # 15
    (ofdm_3_mcs3),  # 16
    (ofdm_4_mcs3),  # 17
    (ofdm_2_mcs4),  # 18
    (ofdm_3_mcs4),  # 19
    (ofdm_4_mcs4),  # 20
    (ofdm_2_mcs5),  # 21
    (ofdm_3_mcs5),  # 22
    (ofdm_4_mcs5),  # 23
    (ofdm_3_mcs6),  # 24
    (ofdm_4_mcs6),  # 25
    (oqpsk_rate1),  # 26
    (oqpsk_rate2),  # 27
    (oqpsk_rate3),  # 28
    (oqpsk_rate4),  # 29
    (fsk_option3_FEC),  # 30
    (fsk_option3),  # 31
]
