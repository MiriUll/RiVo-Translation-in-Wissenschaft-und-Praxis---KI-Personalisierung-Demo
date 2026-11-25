EXAMPLE_TEXTS = {
    "Beispiel 1 – Nachrichten": "Sport und Bewegung gehören für viele Kinder und Jugendliche nicht mehr zum Alltag. Nur 14 Prozent bewegen sich laut WHO täglich für eine Stunde mäßig bis intensiv. Auch in Deutschland gibt es viele Bewegungsmuffel. ",
    "Beispiel 2 – Wikipedia": "Lego Creator ist ein Lego-Computerspiel aus dem Jahr 1998. Das Spiel wurde von Superscape entwickelt und legt den Fokus darauf, Szenerien aus Legosteinen und Minifiguren zu bauen.",
    "Beispiel 3 – Gesundheitsinformationen": "Die echte Grippe ist eine ernstzunehmende Infektionskrankheit. Besonders bei älteren Menschen kann sie einen schweren Verlauf nehmen und sogar tödlich enden. Deshalb raten Fachleute allen Risikogruppen zur Grippeimpfung.",
    "Beispiel 4 – Hitzewarnung": "Der Deutsche Wetterdienst warnt für Mittwoch vor extremer Hitze mit Temperaturen bis 38 Grad. Ältere Menschen, Kleinkinder und Menschen mit Herz-Kreislauf-Erkrankungen sollten körperliche Anstrengung vermeiden, ausreichend trinken und sich tagsüber in kühlen Räumen aufhalten. Arbeitgeber können bei Temperaturen über 35 Grad in Innenräumen zusätzliche Pausen anordnen.",
}

OWN_TEXT = "Eigener Text"

STRATEGIES = {
    "Einfache Sprache": "Vereinfache den folgenden Text in Einfache Sprache.",
    "Leichte Sprache": "Vereinfache den folgenden Text in Leichte Sprache für Menschen mit Lernbehinderungen.",
    "Kind": "Schreibe den folgenden Text für ein 5-jähriges Kind um.",
    "Anderes": None,  # instruction is entered by the user
}

# Personal situation – decides WHICH information in the text is relevant
# for the reader (e.g. "you belong to the risk group").
BACKGROUNDS = {
    "Keiner": None,
    "Eltern eines Kleinkinds": "Die Person hat ein zweijähriges Kind und will wissen, was der Text für ihre Familie bedeutet.",
    "Über 70 und herzkrank": "Die Person ist 75 Jahre alt und hat eine Herzerkrankung.",
    "Pflegekraft": "Die Person arbeitet als Pflegekraft. Medizinische Fachbegriffe kennt sie, sie hat aber wenig Zeit zum Lesen.",
    "Lernt Deutsch (Muttersprache Arabisch)": "Die Person lernt gerade Deutsch, ihre Muttersprache ist Arabisch. Der Text soll trotzdem auf Deutsch sein, schwierige Wörter dürfen in Klammern auf Englisch übersetzt werden.",
    "Spieleentwickler*in": "Die Person arbeitet in der Spielebranche und kennt sich mit Computerspielen sehr gut aus.",
    "Anderes": None,  # entered by the user
}

# Interests – the model can use them for comparisons and examples.
INTERESTS = {
    "Keine Angabe": None,
    "Fußball": "Die Person interessiert sich sehr für Fußball.",
    "Kochen & Backen": "Die Person kocht und backt sehr gerne.",
    "Minecraft": "Die Person spielt sehr gerne Minecraft.",
    "Tiere": "Die Person interessiert sich sehr für Tiere.",
    "Anderes": None,  # entered by the user
}

# Concrete difficulties – these change the form of the text very visibly.
DIFFICULTIES = {
    "Zahlen und Prozente": "Die Person kann mit Zahlen und Prozentangaben wenig anfangen.",
    "Abkürzungen und Eigennamen": "Die Person kennt Abkürzungen und Namen von Organisationen oder Firmen nicht.",
    "Wenig Zeit / Konzentration": "Die Person kann sich nur kurz konzentrieren und will nur das Wichtigste wissen.",
    "Text wird vorgelesen": "Die Person ist blind und lässt sich den Text von einer Sprachausgabe vorlesen.",
    "Macht sich schnell Sorgen": "Die Person macht sich schnell große Sorgen und bekommt leicht Angst.",
}

# Reading goal – decides what the text should focus on.
GOALS = {
    "Keine Angabe": None,
    "Will wissen, was zu tun ist": "Die Person will vor allem wissen, was sie jetzt konkret tun soll.",
    "Will mehr lernen": "Die Person ist neugierig und möchte die Hintergründe verstehen.",
    "Will es anderen erklären": "Die Person möchte den Inhalt anschließend ihren Enkelkindern erklären.",
}

GENDERS = {
    "keine Angabe": None,
    "Weiblich": "weiblich",
    "Männlich": "männlich",
    "Divers": "divers",
}


# Keeps the model from over-personalising (analogies in every sentence,
# trivialising serious topics, clichés based on the profile).
PERSONALISATION_RULES = (
    "Regeln für die Anpassung:\n"
    "- Nutze die Angaben zur Person nur dort, wo sie das Verstehen wirklich erleichtern "
    "oder zeigen, was für die Person wichtig ist.\n"
    "- Verwende höchstens einen kurzen Vergleich aus den Interessen der Person, und nur, "
    "wenn er einen schwierigen Begriff erklärt. Der restliche Text bleibt sachlich.\n"
    "- Behandle ernste Themen wie Krankheit oder Tod sachlich und respektvoll, nicht verspielt.\n"
    "- Verändere keine Fakten und vermeide Klischees über die Person."
)


def build_prompt(text, strategy_instruction, background=None, interest=None,
                 difficulties=(), goal=None, gender=None):
    """Assemble the prompt from the user's selections."""
    parts = [strategy_instruction.strip()]

    reader = [r.strip() for r in (background, interest, *difficulties, goal) if r and r.strip()]
    if gender:
        reader.append(f"Das Geschlecht der Person ist {gender}.")
    if reader:
        parts.append(
            "Passe den Text an die folgende Person an:\n" + "\n".join(f"- {r}" for r in reader)
        )
        parts.append(PERSONALISATION_RULES)

    parts.append("Gib nur den umgeschriebenen Text aus.")
    parts.append(f"Text:\n{text.strip()}")
    return "\n\n".join(parts)
