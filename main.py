import datetime
import time

from modules.WordleAnalyzer import WordleAnalyzer

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By

def GetShadowRootObject (driver, tagname):
    query = f"return document.getElementsByTagName ('{tagname}')[0].shadowRoot"
    return driver.execute_script (query)

def FindScriptFile (driver):
    page = driver.find_elements(By.TAG_NAME, 'script')
    for element in page:
        link = str(element.get_attribute('src'))
        if '/games/wordle/main' in link and '.js' == link[-3:]:
            return link

def GotoTab (driver, tabIndex):
    assert len (driver.window_handles) > tabIndex
    driver.switch_to.window(driver.window_handles[tabIndex])

def OpenLinkNewTab (driver, link):
    driver.execute_script(f"window.open('{link}','_blank')")

def AddWordList (wordLists, wordListString):
    wordListString = wordListString.replace("[","").replace("]", "").replace("\"", "")
    wordList = wordListString.split(",")

    for word in wordList:
        word = word.strip()

        if word not in wordLists and len (word) == 5:
            wordLists.append(word)

    return wordLists

def ExtractWordList (driver):
    GotoTab (driver, 1)

    time.sleep(5)

    fileContent = driver.find_elements(by=By.TAG_NAME, value="body")[0].text

    wordLists = []

    # Get List A
    startIndex = fileContent.find("var Ma=")
    subContent = fileContent[startIndex:]

    # print (subContent)

    restartIndex = subContent.find("[")
    endIndex = subContent.find("]")

    wordListString = subContent[restartIndex:endIndex]
    wordLists = AddWordList (wordLists, wordListString)

    # Get List B
    startIndex = subContent.find("[")
    subContent = fileContent[startIndex:]

    restartIndex = subContent.find("[")
    endIndex = subContent.find("]")

    wordListString = subContent[restartIndex:endIndex]
    wordLists = AddWordList (wordLists, wordListString)

    # GotoTab (driver, 0)

    return wordLists

def GuessWord (driver, word):
    # For now, always assume word is valid.
    GotoTab (driver, 0)
    element = driver.find_elements(by=By.TAG_NAME, value="body")[0]

    assert len (word) == 5
    element.send_keys(word)
    element.send_keys(Keys.RETURN)

    todate = datetime.datetime.now().date().isoformat()

    time.sleep(3)
    state = driver.save_screenshot(f'./images/{todate}.png')
    # print (f'Screenshot saved: {state}')

def SaveBase (driver):
    # For now, always assume word is valid.
    GotoTab (driver, 0)
    element = driver.find_elements(by=By.TAG_NAME, value="body")[0]

    time.sleep(3)
    state = driver.save_screenshot(f'./images/base.png')
    # print (f'Base saved: {state}')

def FindWord (attempted, ignoreLetters, knownLetters, lettersWithPlaces):
    for i, word in enumerate(wordList):
        ignoreWord = False

        if len(ignoreLetters) > 0:
            for char in word:
                if char in ignoreLetters:
                    ignoreWord = True
                    break

        if len(lettersWithPlaces) > 0:
            for char, position in lettersWithPlaces:
                if not (word[position] == char):
                    ignoreWord = True
                    break

        if len(knownLetters) > 0:
            for char, position in knownLetters:
                if not char in word or (word[position] == char):
                    ignoreWord = True
                    break
        
        if ignoreWord:
            continue
        
        return word

if __name__ == "__main__":
    binary = FirefoxBinary('C:\\Users\\adamthahir\\Documents\\geckodriver.exe')
    driver = webdriver.Firefox(executable_path='C:\\Users\\adamthahir\\Documents\\geckodriver.exe')

    site = 'https://www.nytimes.com/games/wordle/index.html'
    driver.get(site)
    time.sleep(2)

    driver.find_elements(by=By.TAG_NAME, value="body")[0].click()

    scriptLink = FindScriptFile(driver)
    OpenLinkNewTab(driver, scriptLink)

    wordList = ExtractWordList (driver)
    # print (f'length: {len(wordList)}')

    SaveBase(driver)

    todate = datetime.datetime.now().date().isoformat()
    analyzer = WordleAnalyzer(todate)

    analyzer.MakeBoard()

    attempts = 0

    attempted = []
    ignoreLetters = []
    knownLetters = []
    lettersWithPlaces = []
    
    while True:
        
        if len (attempted) == 0:
            # I like starting with the word AGILE
            word = "agile"
        else:
            word = FindWord(attempted, ignoreLetters, knownLetters, lettersWithPlaces)
        
        GuessWord (driver, word)
        attempts += 1

        yellows, greens = analyzer.RunAttempt(attempts==1)

        if attempts >= 6 or len(greens) >= 5:
            analyzer.Cleanup()
            print (f'\nExit. Attempts: {attempts-1} || Solved: {len(greens) == 5}')
            break

        yellowLetters = [word[i] for i in yellows]
        greenLetters = [word[i] for i in greens]

        if len(yellows) > 0:
            for yellow in yellows:
                attempted.append(word[yellow])
                knownLetters.append( (word[yellow], yellow) )

        if len(greens) > 0:
            for green in greens:
                attempted.append(word[green])
                lettersWithPlaces.append( (word[green], green) )

        for i, char in enumerate(word):
            if not char in yellowLetters and not char in greenLetters:
                ignoreLetters.append(word[i])

        print (f'\nWord: {word}')
        print (f'Yellows: {yellows}')
        print (f'Greens: {greens}')
        print (f'ignore: {ignoreLetters}')


        time.sleep(2)

# assert "Python" in driver.title

# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()