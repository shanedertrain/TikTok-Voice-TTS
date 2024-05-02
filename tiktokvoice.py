import enum
import re
import requests
import base64
import sys
from pathlib import Path
from threading import Thread

import configuration_ttv as cfg

class TikTokVoiceTTS:
    class Voices(enum.Enum):
        # DISNEY VOICES
        en_us_ghostface = "Ghost Face"
        en_us_chewbacca = "Chewbacca"
        en_us_c3po = "C3PO"
        en_us_stitch = "Stitch"
        en_us_stormtrooper = "Stormtrooper"
        en_us_rocket = "Rocket"
        # ENGLISH VOICES
        en_au_001 = "English AU - Female"
        en_au_002 = "English AU - Male"
        en_uk_001 = "English UK - Male 1"
        en_uk_003 = "English UK - Male 2"
        en_us_001 = "English US - Female (Int. 1)"
        en_us_002 = "English US - Female (Int. 2)"
        en_us_006 = "English US - Male 1"
        en_us_007 = "English US - Male 2"
        en_us_009 = "English US - Male 3"
        en_us_010 = "English US - Male 4"
        # EUROPE VOICES
        fr_001 = "French - Male 1"
        fr_002 = "French - Male 2"
        de_001 = "German - Female"
        de_002 = "German - Male"
        es_002 = "Spanish - Male"
        # AMERICA VOICES
        es_mx_002 = "Spanish MX - Male"
        br_001 = "Portuguese BR - Female 1"
        br_003 = "Portuguese BR - Female 2"
        br_004 = "Portuguese BR - Female 3"
        br_005 = "Portuguese BR - Male"
        # ASIA VOICES
        id_001 = "Indonesian - Female"
        jp_001 = "Japanese - Female 1"
        jp_003 = "Japanese - Female 2"
        jp_005 = "Japanese - Female 3"
        jp_006 = "Japanese - Male"
        kr_002 = "Korean - Male 1"
        kr_003 = "Korean - Female"
        kr_004 = "Korean - Male 2"
        # SINGING VOICES
        en_female_f08_salut_damour = "Alto"
        en_male_m03_lobby = "Tenor"
        en_female_f08_warmy_breeze = "Warmy Breeze"
        en_male_m03_sunshine_soon = "Sunshine Soon"
        # OTHER
        en_male_narration = "Narrator"
        en_male_funny = "Wacky"
        en_female_emotional = "Peaceful"

    def __init__(self):
        # Define the endpoint data with URLs and corresponding response keys
        self.ENDPOINT_DATA = [
            {
                "url": "https://tiktok-tts.weilnet.workers.dev/api/generation",
                "response": "data"
            },
            {
                "url": "https://countik.com/api/text/speech",
                "response": "v_data"
            },
            {
                "url": "https://gesserit.co/api/tiktok-tts",
                "response": "base64"
            }
        ]

    def tts(self, text: str, voice: Voices, output_filepath: Path = cfg.FOLDER_OUTPUT /"output.mp3") -> None:
        # Specified voice is valid
        if voice not in self.Voices:
            raise ValueError("Voice must be a valid Voices enum value")

        # Text is not empty
        if not text:
            raise ValueError("Text must not be 'None'")

        # Split the text into chunks
        chunks: list[str] = self._split_text(text)

        for entry in self.ENDPOINT_DATA:
            endpoint_valid: bool = True

            # Empty list to store the data from the requests
            audio_data: list[str] = ["" for _ in range(len(chunks))]

            # Generate audio for each chunk in a separate thread
            def generate_audio_chunk(index: int, chunk: str) -> None:
                nonlocal endpoint_valid

                if not endpoint_valid:
                    return

                try:
                    # Request to the endpoint to generate audio for the chunk
                    response = requests.post(
                        entry["url"],
                        json={
                            "text": chunk,
                            "voice": voice.name
                        }
                    )

                    if response.status_code == 200:
                        # Store the audio data for the chunk
                        audio_data[index] = response.json()[entry["response"]]
                    else:
                        endpoint_valid = False

                except requests.RequestException as e:
                    print(f"Error: {e}")
                    sys.exit()

            # Start threads for generating audio for each chunk
            threads: list[Thread] = []
            for index, chunk in enumerate(chunks):
                thread: Thread = Thread(target=generate_audio_chunk, args=(index, chunk))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

            if not endpoint_valid:
                continue

            # Concatenate audio data from all chunks and decode from base64
            audio_bytes = base64.b64decode("".join(audio_data))

            # Write the audio data to a file
            with open(output_filepath, "wb") as file:
                file.write(audio_bytes)
                print(f"File '{output_filepath}' has been generated successfully.")

            # Break after processing a valid endpoint
            break

    # Define a function to split the text into chunks of maximum 300 characters or less
    def _split_text(self, text: str) -> list[str]:
        # Empty list to store merged chunks
        merged_chunks: list[str] = []

        # Split the text into chunks based on punctuation marks
        # Change the regex [.,!?:;-] to add more separation points
        separated_chunks: list[str] = re.findall(r'.*?[.,!?:;-]|.+', text)

        # Iterate through the chunks to check for their lengths
        for i, chunk in enumerate(separated_chunks):
            if len(chunk) > 300:
                # Split chunk further into smaller parts
                separated_chunks[i:i+1] = re.findall(r'.*?[ ]|.+', chunk)

        # Initialize an empty string to hold the merged chunk
        merged_chunk: str = ""

        for separated_chunk in separated_chunks:
            # Check if adding the current chunk would exceed the limit of 300 characters
            if len(merged_chunk) + len(separated_chunk) <= 300:
                merged_chunk += separated_chunk
            else:
                # Start a new merged chunk
                merged_chunks.append(merged_chunk)
                merged_chunk = separated_chunk

        # Append the last merged chunk to the list
        merged_chunks.append(merged_chunk)
        return merged_chunks

    @staticmethod
    def get_voice_by_name(name: str) -> Voices:
        for voice in TikTokVoiceTTS.Voices:
            if voice.name == name:
                return voice
        raise ValueError(f"No voice found with the name '{name}'")