This is some rudimentary, utterly crappy Python code I worked out for creating wavetable banks for the Synthesis Technology E352/E370 Eurorack modules and the WaveEdit software.

http://synthtech.com/eurorack/E370/
http://synthtech.com/eurorack/E352/
http://synthtech.com/waveedit

I hope somebody more competent than I will come along and make a proper library.

Meanwhile, the Wavetable and Bank classes in Bank.py provide the necessary logic for reading/writing these particular .wav files, plus some basic abstraction and validation.

The example.py script presents a simple demo that can be easily modified for whatever purpose.

-Martin
