# OpenTranscription

Live transcription with overlay using OpenAI's Whisper model, supporting both API and local model options. Auto-translates to English from 51 supported languages. Designed as an assistive tool for people with hearing difficulties, and persons who like to have subtitles on at all times.

## Features

- Real-time transcription with adjustable overlay
- Support for OpenAI API and local Whisper model
- Auto-translation to English
- Customizable font size and opacity
- Hotkey to show/hide overlay
- Session saving option

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/younesbram/opentranscription.git
   cd opentranscription
   ```

2. Install dependencies:
   ```
   pip install pyaudio openai whisper keyboard
   ```

3. (Optional) If using the local model, ensure you have sufficient disk space and RAM.

## Usage

1. Run the script:
   ```
   python opentranscription.py
   ```

2. In the settings window:
   - Enter your OpenAI API key (if using API)
   - Choose between local model and API
   - Set auto-translation if desired
   - Adjust font size and opacity
   - Set a hotkey for showing/hiding the overlay

3. Click "Start Live Transcription"

4. Use the set hotkey to toggle overlay visibility

5. To stop, click "Stop Live Transcription" in the settings window

## TODOs

- [ ] Implement speaker diarization for multi-speaker recognition
- [ ] Improve transcription accuracy and reduce hallucinations
- [ ] Enhance UI/UX for better user experience
- [ ] Add support for more languages
- [ ] Implement real-time punctuation and formatting, test through prompting
- [ ] Optimize performance for longer transcription sessions
- [ ] Add customizable text colors and styles
- [ ] Implement noise reduction for better audio quality
- [ ] Create installers for easy deployment on different OS
- [ ] Add tests and improve code documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Support

For bugs and feature requests, please open an issue on GitHub or contact [@didntdrinkwater](https://x.com/didntdrinkwater) on Twitter.
