'''
define the header structure.
'''

class audio_tag_header:
    '''
    define the audio tag header structure
    '''
    def __init__(self, header_bits):
        self.soundformat = int(header_bits[:4], 2)
        self.soundrate = int(header_bits[4:6], 2)
        self.soundsize = int(header_bits[6], 2)
        self.soundtype = int(header_bits[7], 2)