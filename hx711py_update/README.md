# HX711 for Raspbery Pi

This code credited to [underdoeg](https://github.com/underdoeg/)'s [Gist HX711.py](https://gist.github.com/underdoeg/98a38b54f889fce2b237).

I've only made a few modifications on the way the captured bits are processed and to support Two's Complement, which it didn't.

I'm currently trying to improve this version.

## Warning: Possible random values

>  **Possible random values!**
>  Pulling the bits from the HX711 is a time sensitive process as explained its the datasheet. Raspberry runs on Linux which is not a good tool for time sensitive operations using the GPIO pins because tasks are prioritized by the Operative System which might delay a GPIO operation. It could also happen than pulling up and down the pin happens too fast for the HX711.
>
>  If there is a right way to precisely pull the bits with a Raspberry Pi following the datasheet's timing specifications, which is in microseconds, which is a millionth of a second, then this code is probably not doing it in that right way and might return random values if other processes are running simultanously, delaying the GPIO operations, or if the processor is not busy with anything else at all, allowing the GPIO operations to happen too fast.
>
>  I know very little about the OS architecture, but it seems to me that this too scenarios could happen. I'm not event a developer as you can see by how ugly the code and my commits are, haha.
>
>  I recommends using an Arduino instead of a Raspberry Pi. Hope this library helps, though.

## Table of contents

1. [Files description](#files-description)
2. [Instructions](#instructions)
3. [Usage with two channels](#usage-with-two-channels)
4. [Changelog](#changelog)

## Files description

File descriptions:
- `hx711.py`: v0.1 code. Readings are not near as frequent as they could be. Currently, it's barely doing 1 reading per second when the HX711 allows for 10SPS (Samples Per Second), which translates to 10 readings per second.
- `example.py`: Example of how to use `hx711.py`. The exaplanation is not good at all.
- `hx711_emulator.py`: This is a class that emulates the behaviour of my original HX711 class. It's actually more a simulator than an emulator.
- `example_emulator.py`: Show an example but using the emulator class.
- `hx711pi.py`: This a new version I've just created, untested at the moment, with the objective of allowing 10 readings per second. They will be provided by some sort of event I still need to figure out how to create and how to throttle somehow.

## Instructions

To install:

1. Clone or download and unpack this repository
2. In the repository directory, run
```
python setup.py install
```

## About using the two channels of one breakout board

This is a completely unnecessary feature that I, for some reason, decided to include in the original code. Anyway, in theory, it allows using to loadcells at the same time but they'd have different gains so they would provide different values but would both provide weights, just with different accuracy.

I haven't tested the use of two loadcells on the same breakout board at the same time. It might not work.

Channel A has selectable gain of 128 or 64.  Using set_gain(128) or set_gain(64) selects channel A with the specified gain.

Using set_gain(32) selects channel B at the fixed gain of 32. The tare_B(), get_value_B() and get_weight_B() functions do this for you.

This info was obtained from an HX711 datasheet located at:
https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf

## Changelog

### 28/02/2023

I'm only using my lunch time to commit changes in order to close all the HX711 environment on my mac because I need more processing power.

This version adds new methods to allow the use of interrupts as an alternative to polling.

### 25/02/2023

Funily enough and by pure accident, exactly two years after updating the README.md file with false promises, I'm back making a few changes.

My motivation to update this code is to improve the reading frequency.

### 25/02/2021

For the past years I haven't been able to maintain this library because I had too much workload. Now I'm back and I've been working on a few fixes and modifications to simplify this library, and I might be commiting the branch by mid-March. I will also publish it to PIP.