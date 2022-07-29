from aqt.webview import AnkiWebView
from anki.sound import SoundOrVideoTag
from aqt.sound import av_refs_to_play_icons, av_player

class SimpleCardView(AnkiWebView):
    def __init__(self, card):
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

        # unknown if this still exists after breaking out this code to its own class.
        # regardless, just putting the av tag into the pycmd directly here.
        for i in range(len(card.answer_av_tags())):
            html = html.replace("play:a:"+str(i), "play:"+card.answer_av_tags()[i].filename)

        self.stdHtml(html,
            css=["css/reviewer.css"],
            js=[
                "js/mathjax.js",
                "js/vendor/mathjax/tex-chtml.js",
                "js/reviewer.js",
            ]
        )
        def play_tag(inp):
            play, tag = inp.split(":")
            av_player.play_tags([SoundOrVideoTag(tag)])
        
        self.set_bridge_command(play_tag, self)
