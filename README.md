# ReadMe

WordleCV aims to solve daily wordle challenges using web-scraping and image processing. The application opens any wordle-like webpage and scrapes the JS file for a list of possible words. The program then guesses words from the list based on the feedback from the wordle webpage.

Feedback from the webpage is observed by the program using OpenCV image processing. The program takes a screenshot of the Wordle board, then looks for Yellow and Green blocks just as a person would. Letters guessed but not highlighted are marked as ignored letters. Yellow and green blocks are recorded with their position and used for further guesses.

The idea is to approach the game as a regular person would. While scraping the webpage to process feedback, using image processing is a fun over-engineered approach :)

#### Tested Wordle variants:
- [Wordle - The New York Times](https://www.nytimes.com/games/wordle/index.html)


# Demonstration

![Demonstration](https://raw.githubusercontent.com/AdamThahir/WordleCV/main/demo/20220322.gif)

## Configuration file
The application requires a few things to word properly. These settings have defaults to my own static paths, to use it on another system, they can be defined from the `config.json` file.

- `binary:` The path to your `geckodriver.exe` 
- `driver:` Path to your `geckodriver.exe` (maybe removed later)
- `site:` Wordle website. 
- `jsHeader:` Path to JS file containing word list

> Note: While the configuration should support multiple wordle like websites, only the NY times variant has been tested.

## Web Interactions and Scraping

Web interaction and scraping were done using selenium. All related functions are found under `main.py`.

The application starts by clicking randomly on the screen (by clicking on the `body` element of the HTML). This is to close the instructions modal. Next the application finds the exaact JS file which would contain the word list, and then open this file on a new tab to extract the words. Following this, the applicaiton switches to the newly opened tab and extracts all a wordlist from this file.

The other interaction the application has with the webpage, is guessing a word and taking a screenshot of the feedback. The screenshot is saved under `/images/YYYY-MM-DD.png` for processing. 

Hardcoded delays for a few seconds are implemented before and after most interactions, to ensure the webpage processes our request correctly.

> Note: Before the first guess is made, a screenshot of the board is taken.


## Image Processing

All image processing is handled using OpenCV. Related functions are found under `modules/WordleAnalyzer.py`.

Before processing any image, images are cropped to only show the board without header and on screen keybaord. This allows us to focus on a given area. Currently the application crops images based on hard coded percentages, as a result it sometimes has difficulties if the window size is too small.

The application starts by creating a cropped version of the board saved from the driver at the start of the program. This acts as the base image.

The processed can then be classified into the following steps:
1. Identify rows
2. Identify letter positions of a given word within a row
3. Identify Yellow and Green blocks
4. Identify blocks (letters) that are not yellow or green
5. Return letters of Yellow and Green blocks, along with their positions.

#### Identifying rows
In a standard wordle game, each entry consists of five letters in a row. In order to focus our feedback on newly inputted rows, the program compares the current state of the board (`YYYY-MM-DD.png`) with the previous state of the board located at `board.png` at the start of the game, or `YYYY-MM-DD_PREV.png` during the game.

#### Identifying letter positions
Letter positions are identified as blocks. Each block is a square (to us, either gray, yellow or green). The centers of each square are taken as recorded as a single letter.

#### Identifying letter positions (Green and Yellow)
From the main image (`YYYY-MM-DD.png`) we taken the mask of a given color (Green or Yellow) and get the difference of the mask with the row in the original processed image. This gives us a mask of all the blocks not in the color we need.

From here, we take the centers of all the blocks in the output (letters in colors we do not need). The centers in the first iteration (containing all centers, from previous step) and not in the current output are the letters we need for the given color. 

#### Identifying letter positions - Gray
As the color difference between the background and the gray blocks is quite small, rahter than repeating a similar process to step 3, gray blocks are identified as letters that are not Yellow and not Green.

#### Return letters with their positions.
Indexing the position of the Yellow/Green block centers with the total list of letter centers gives us the positions of each letter in the word, along with their colors.

This information is parsed as a tuple (letter, position) and returned in a list contianing all relevent information.
