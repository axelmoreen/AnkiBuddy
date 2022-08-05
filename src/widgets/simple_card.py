# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Contains SimpleCardView, which is a QWidget that can be shown
representing the back of an Anki card. It can be used from
anywhere and manages its own state / pycmd signals.
"""
from aqt.webview import AnkiWebView
from anki.sound import SoundOrVideoTag
from aqt.sound import av_refs_to_play_icons, av_player
from anki.cards import Card


class SimpleCardView(AnkiWebView):
    """Card web view containing just the back of an Anki card, that can handle
    av tags.
    To use, simply create with an instance of an Anki card object,
    and call .show().
    """
    def __init__(self, card: Card):
        """Creates a window with Anki "Card" object instance that
        will show a simplified back of the card, including sounds.

        This is used for viewing cards that were used in questions,
        without creating an entire Reviewer.

        The window must be made visible with .show(), and like other windows,
            it has to be set as a field of a parent class connected to aqt.mw
            so it doesn't get garbage collected.

        Should play audio tags correctly, but it has only been tested with the
            Core2k deck.

        Args:
            card (Card): Instance of anki.cards.Card to create the view from.
        """
        super().__init__()

        self.card = card

        html = card.answer()
        html = av_refs_to_play_icons(html)

        # a weird way to fix a bug
        # for some reason, to use the default pycmd (e.g. play:a:0)
        #   and setting separate bridge commands
        # resulted in them all playing the same audio
        # ONLY if the webviews are created in the same method scope
        # (i.e. after a Matching question)

        # unknown if this still exists after breaking out this code to its own
        # class.
        # regardless, just putting the av tag into the pycmd directly here.
        for i in range(len(card.answer_av_tags())):
            html = html.replace(
                "play:a:" + str(i), "play:" + card.answer_av_tags()[i].filename
            )

        self.stdHtml(
            html,
            css=["css/reviewer.css"],
            js=[
                "js/mathjax.js",
                "js/vendor/mathjax/tex-chtml.js",
                "js/reviewer.js",
            ],
        )

        def play_tag(inp):
            play, tag = inp.split(":")
            av_player.play_tags([SoundOrVideoTag(tag)])

        self.set_bridge_command(play_tag, self)
