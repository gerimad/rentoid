from openai import OpenAI
client = OpenAI()

posting = """
Felszereltség: Klíma Részletek Hosszútávra kiadó a IV. kerületben, a Jázmin Lakóházban egy 37 nm-es, 2 szobás lakás. Az ingatlan ÚJ ÉPÍTÉSŰ, RÉSZBEN BÚTOROZOTT, GÉPESÍTETT. Szobája HÁLÓFÜLKÉS, napfényes, tágas, belső udvarra néző kilátással. KLÍMÁVAL felszerelt. A fürdőszoba(kádas) és a mellékhelyiség külön légtérben található. Közös költség 15.000 Ft/hó. Elhelyezkedése kiváló, pár perc sétatávolságon belül elérhető az M3-as metró, 12, 14-es villamos, 2 havi kaució és egy havi lakbér ellenében AZONNAL költözhető. 
"""

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful real estate assistant designed to analyze apartment postings and create a summary of it's most important features in a concise way."},
        {"role": "system", "content": "You must create the summary in the language of the apartment posting and use a list format."},
        {"role": "user", "content": f"Analyze and create a summary of this apartment listing: {posting}"}
    ]
)

print(completion.choices[0].message.content)