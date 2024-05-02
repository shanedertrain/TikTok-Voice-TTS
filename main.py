# author: Giorgio
# date: 19.03.2024
# topic: TikTok-Voice-TTS
# version: 1.1

import argparse

# the script in the directory
from tiktokvoice import TikTokVoiceTTS

def main():
    # adding arguments
    parser = argparse.ArgumentParser(description='TikTok TTS')
    parser.add_argument('-t', help='text input')
    parser.add_argument('-v', help='voice selection', choices=TikTokVoiceTTS.Voices.__members__.keys())
    parser.add_argument('-n', help='output filename', default='output.mp3')
    parser.add_argument('-txt', help='text input from a txt file', type=argparse.FileType('r'))
    parser.add_argument('-play', help='play sound after generating audio', action='store_true')

    args = parser.parse_args()

    # checking if given values are valid
    if not args.t and not args.txt:
        print("Error: insert a valid text or txt file")
        return

    if args.t and args.txt:
        print("Error: only one input type is possible")
        return
    
    if not args.v:
        print("Error: no voice has been selected")
        return
    
    tiktok_voice_tts = TikTokVoiceTTS()

    # executing script
    if args.t:
        tiktok_voice_tts.tts(args.t, args.v, args.n)
    elif args.txt:
        tiktok_voice_tts.tts(args.txt.read(), args.v, args.n)

if __name__ == "__main__":
    main()
