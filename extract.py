#!/usr/bin/env python3
'''
the main parse module
'''
import argparse
from utils import AUDIO, VIDEO, SCRIPT
from utils import audio_tag_header


class parse:
    def __init__(self, audio_file, output_file):
        self._output_file = output_file
        self._flv_data = open(audio_file, "rb").read()
        self._size = len(self._flv_data)
        self._bytes_begin = 13 # 3 + 1 + 1 + 4 + 4
        self._acc_data = b""
        self._audio_tag_header = None

    def bytes_to_int(self, bytes_string):
        '''
        pack of the int.from_bytes
        '''
        return int.from_bytes(bytes_string, byteorder="big")

    def header_assert(self):
        '''
        assert the flv header 
        '''
        assert(self._flv_data[0] == ord("F"))
        assert(self._flv_data[1] == ord("L"))
        assert(self._flv_data[2] == ord("V"))
        assert(self._flv_data[3] == 1)# assert the flv version

    def calculate_audio_specific_config(self, bytes_string):
        '''
        calculate sampling frequency index value
        '''
        left = bytes_string[0]
        right = bytes_string[1]
        self._sampling_frequency_index = ((left & 0x7) << 1) | (right >> 7)
        self._audio_object_type = (left & 0xF8) >> 3


    def make_adts_headers(self, tag_data_size):
        '''
        according to the doc, add adts headers
        '''
        # adts_fixed_header
        bit_headers = format(0xFFF, 'b') + "0" + "00" + "1" + \
        format(self._audio_object_type-1, "02b") + format(self._sampling_frequency_index, "04b") + \
        "0" + format(2, "03b") + "0" + "0"
        #adts_variable_header
        bit_headers += "0" + "0" + format(7+tag_data_size, "013b") + format(0x7FF, "011b") + "00"
        int_list = [int(bit_headers[8*x:8*x+8], 2) for x in range(7)]
        return bytes(int_list)

    def audio_extract(self):
        '''
        seperate the audio from the vedio.
        '''
        current = self._bytes_begin
        while current < self._size:
            tag_type = self._flv_data[current]         
            tag_data_size = self.bytes_to_int(self._flv_data[current + 1 : current + 4])
            if tag_type == AUDIO:
                tag_data = self._flv_data[current + 11 : current + 11 + tag_data_size]
                if self._audio_tag_header is None:
                    self._audio_tag_header = audio_tag_header(format(tag_data[0], 'b'))
                    assert(self._audio_tag_header.soundformat == 10)
                    assert(tag_data[1] == 0x00)
                    self.calculate_audio_specific_config(tag_data[2:])
                else:
                    self._acc_data += self.make_adts_headers(tag_data_size-2) + tag_data[2:]

            current += 11 + tag_data_size
            assert(self.bytes_to_int(self._flv_data[current : current + 4]) == 11 + tag_data_size)
            current += 4
    
    def save_acc_data(self, output_file):
        '''
        save the data to the file
        '''
        if output_file.split(".")[-1] != "aac":
            raise RuntimeError("the output file must end with aac!")
        with open(output_file, "wb") as f:
            f.write(self._acc_data)
            
    def start(self):
        '''
        start the project
        '''
        self.header_assert()
        self.audio_extract()
        self.save_acc_data(self._output_file)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--input", help="enter the input file")
    arg_parser.add_argument("-o", "--output", help="enter the output file, end with .aac" )
    args = arg_parser.parse_args()
    client = parse(args.input, args.output)
    client.start()




