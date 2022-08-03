# AnkiBuddy
AnkiBuddy is an add-on for Anki 2.1 that gives you a variety of different practice tools outside of scheduled review. 

This add-on does not aim to replace the core functionality of Anki in any way (it relies on you to complete your daily repetitions in order to have "learned" a card), nor has it been tested alongside SRS at-length, so your mileage may vary. It is simply for fun and to experiment with. A mixture of different inputs and outputs can be great for drilling yourself, but I cannot guarantee any particular outcome. Multiple choice and matching are easier than remembering a full notecard. 

This add-on also does not write to or modify your existing Anki data at all, it only reads the deck information. So it is safe to use. But keep in mind it is still under development, so other issues in its usage may arise.  Supports PyQt5 and PyQt6 with compatibility shims. For best results, use Anki 2.1.54.

Issues can be directed to the [issue tracker](https://github.com/axelmoreen/AnkiBuddy/issues) and contributions are always welcome.
# Features
* List mode for manual practice
    * Custom layout based on card fields
    * Change size of the group to learn  
    * Create subsets of the deck (All, Learned, Lapsed, Unlearned)
    * Set front / back columns to manually hide and show them
    * Click on a row to view card
    * Export to .csv and to .txt (Experimental)
* Practice mode for quizzing
    * Multiple choice - choose the correct answer from options
    * Matching - match left and right side
    * Write the Answer - type the answer in a box
        * Field hints 
        * Virtual keyboard for language learners to use or reference while typing. (Experimental, Only Japanese supported currently)
    * Correct / incorrect sound feedback
    * Supports sound field questions / answers
    * Supports linked audio to a play on a non-sound field (Experimental) 
    * Balanced deck or true random
    * Revisit mistakes
    * Timed mode or unlimited timer
    * View cards while practicing
    * Furigana support
    * View session stats
The add-on also has an options wizard that lets you customize most aspects, like the font of each field, timer length, sounds, default behavior, etc.

## Demo
[Video Demo](https://www.youtube.com/watch?v=cCn8Hh09s0c)
![List View](/screenshots/list_view.png?raw=true "List View")
![Multiple Choice](/screenshots/multiple_choice2.png?raw=true "Multiple Choice")
![Matching](/screenshots/matching.png?raw=true "Matching")
![Write the Answer](/screenshots/write%20the%20answer.png?raw=true "Write the Answer")

# Installation

Until the add-on is published on the Anki website, you may install it by cloning the repo and linking the contents of src to a folder in your addons directory. The Anki2 directory is usually in your %AppData%/Roaming directory on Windows.
<pre>
Anki2/
├─ addons21/
│  ├─ AnkiBuddy/
│  │  ├─ forms/
│  │  ├─ resources/
│  │  ├─ (files go here)
</pre>


# Planned 
TODO: move this to the issue tracker
* ~~Options wizard~~
    * Change correct/incorrect sound volume
    * Show field name (implemented, but not in options yet)
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
* Better cloze mode (instead of just using the field, use the difference of two)

## Known Issues
* In some cases, playing multiple sounds at the same time causes one to not be heard.
* Can't Edit template with just the Selected templates selection.
* QOL: remove templates from the left box, once they are in the right box.
* Decrease font-size for longer questions/answers
* Fix auto focus on virtual keyboard pyqt5
* Mac is missing spaces in labels?
* Keyboard buttons don't unfocus on pyqt6