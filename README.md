# AnkiBuddy
AnkiBuddy is an add-on for Anki 2.1 that gives you study lists, multiple choice, and matching questions to learn from outside of your regular notecard review.
This add-on aims to be a Quizlet-clone / Duolingo-clone to give you quizzing or timed practice from your Anki decks with alternative formats.
You can choose subsets to study cards you already know, new cards, cards you struggle most with. This add-on tries to be as customizable as possible, as it allows you to create question templates for each deck based on their model. 
Supports PyQt5 and PyQt6. For best results, use Anki 2.1.54.

# Features


This add-on does not aim to replace the core functionality of Anki in any way (it relies on you to complete your daily repetitions in order to have "learned" a card), nor has it been tested alongside SRS at-length, so your mileage may vary. It is something I made for myself simply for fun and to experiment with. Practice from multiple choice and matching can be great for drilling yourself, but I cannot guarantee any particular outcome. It is easier than remembering a full notecard. 

This add-on also does not write to or modify your existing Anki data at all, it only reads the deck information. So it is safe to use. But keep in mind it is still under development, so other issues in its usage may arise. 

Issues can be directed to the [issue tracker] and contributions are always welcome!

## Demo

# Installation

Until the add-on is published on the Anki website, you may install it by cloning the repo and copying the contents to a folder in your addons directory. The Anki2 directory is usually in your %AppData%/Roaming directory on Windows.
<pre>
Anki2/
├─ addons21/
│  ├─ AnkiBuddy/
│  │  ├─ forms/
│  │  ├─ resources/
│  │  ├─ (files go here)
</pre>


# Changelog

# Planned 
* ~~Hover over timer to see stats in Practice~~
* ~~Options wizard~~
    * Change correct/incorrect sound volume
    * ~~Change timer length~~
    * ~~Change subset group size.~~
    * ~~Change field font / font-sizes~~
    * ~~Matching/multiple choice/written specific customization~~
    * ~~Toggle to play card sound field on button press no matter what~~
    * ~~Toggle-able feature to automatically move on from questions or to confirm answer.~~
    * ~~Toggle to show card information after answering when moving on~~
    * ~~Toggle virtual keyboard~~
    * Show field name (implemented, but not in options yet)
* ~~Sound questions (plays sound from field, can repeat)~~
*~~Practice: Add "Show Answer" after first incorrect~~
    * ~~Be able to hover over answer to see a webview with the full card (implemented differentyl)~~
* ~~Fake random (avoid repeats if possible)~~
* ~~Return missed cards to try again~~
* ~~Convert furigana brackets to ruby tags~~
* ~~Re-implement list view hide front/ hide back~~
* ~~Custom instructions to display with some questions (like, write the Kanji or write the Hiragana) (solved with field hint)~~
* Create custom subsets
* Subsets from field, like Part of Speech
* Rework subsets as "Filters" so you could use multiple at a time
* ~~Virtual Keyboard/Foreign languages keyboard layout for Write the Answer~~
    * Add more virtual keyboards (pinyin in particular)
    * Implment Return properly on keyboard
    * Show shift/caps on display
    * Restyle keyboard so "Checked" buttons are easier to see
* Personal Leaderboard for Timed Mode?
* Test mode
* Profile / presets for the Questions Wizard. 
* Keyboard shortcuts for matching / multiple-choice
* Check your own answer for Write the Answer ("i was right" button)
* Add API for question type for other developers to add custom ones
* ~~List view: export .csv~~
## Known Issues
* ~~Duplicate answers sometimes on multiple choice (not fixed?) ~~
* ~~Fix updating Selected Templates after edit of a template~~
* ~~Allow unselecting buttons in Matching~~
* ~~Play sound button doesn't work~~
* ~~Fix ghost sounds being played sometimes on a new question (matching?)~~
* ~~Should fix MVC design of List class.~~
* In some cases, playing multiple sounds at the same time causes one to not be heard.
* Can't Edit template with just the Selected templates selection.
* QOL: remove templates from the left box, once they are in the right box.
*~~Move "Practice" View logic to its own controller.~~
* Decrease font-size for longer questions/answers
* Fix auto focus on virtual keyboard pyqt5
* Mac is missing spaces in labels?
* Keyboard buttons don't unfocus on pyqt6
* ~~Removing selected templates from questions wizard does not save~~