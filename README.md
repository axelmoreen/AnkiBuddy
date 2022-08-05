# AnkiBuddy
[Anki Add-On Page](https://ankiweb.net/shared/info/1704476211)
![Questions Wizard](/screenshots/questions_wizard.png?raw=true)
Add-on for Anki with a variety of tools for practice. Create multiple choice, matching, and written answer questions using cards from your Anki deck. 

This add-on does not replace the core functionality of Anki. It is designed to be supplemental practice. It has not been tested at length with flashcards, so your mileage may vary.

This add-on does not write to or modify your existing Anki data at all, it only reads the deck information. So, it is safe to use. But keep in mind this is an early version, so some features may not work as intended.  Supports PyQt5 and PyQt6 with compatibility shims. For best results, use Anki 2.1.54, but other versions of Anki 2.1 will likely work. 

# Features
* List mode for manual practice
    * Custom layout based on card fields
    * Change size of the group to learn  
    * Choose subsets of the deck (All, Learned, Lapsed, Unlearned)
    * Show and hide columns
    * View card information from list
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

# Demo
[Video Demo on YouTube](https://www.youtube.com/watch?v=cCn8Hh09s0c)

## Screenshots
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
│  │  ├─ dialogs/
│  │  ├─ forms/
│  │  ├─ resources/
│  │  ├─ (files go here)
</pre>

## Contribution
Issues or suggestions can be directed to the [issue tracker](https://github.com/axelmoreen/AnkiBuddy/issues) and contributions are welcome.