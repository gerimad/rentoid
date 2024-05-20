import re
import huspacy
import spacy

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class InferenceEngine():
    nlp = spacy.load("hu_core_news_lg")
    def __init__(self):
        #huspacy.download() #FIXME
        pass

    def inference(self, text):
        text = "summarize: " + self.text_block_preprocessor(text)

        tokenizer = AutoTokenizer.from_pretrained("./alberlet_model_save")
        inputs = tokenizer(text, return_tensors="pt").input_ids

        model = AutoModelForSeq2SeqLM.from_pretrained("./alberlet_model_save")
        outputs = model.generate(inputs, max_new_tokens=100, do_sample=False)

        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    

    def preprocessor(self, word):
        if type(word) == str:
            word = re.sub(r'[^\w\s]', '', word)
            word = re.sub(r'<[^>]*>', '', word)
            word = re.sub(r'<[0-9]*>', '', word)
            word = re.sub(r'[\W]+', '', word)
            return word

    def word_processor(self, line):
        tokens = InferenceEngine.nlp(line)
        words = []

        for token in tokens:
            if token.is_stop == False:
                token_preprocessed = self.preprocessor(token.lemma_)
                if token_preprocessed != '':
                    words.append(token_preprocessed)
        return (words)

    def text_block_preprocessor(self,text):

        make_sentences = InferenceEngine.nlp(text)

        sentences_lemmata_list = [sentence.lemma_.lower() for sentence in make_sentences.sents]

        these_processed_sentences = ''

        for item in sentences_lemmata_list:
            words = self.word_processor(item)
            line = ' '.join(words)
            these_processed_sentences += (' ' + line)

        return these_processed_sentences

    def create_summary(row):
        return f"bérleti díj: {row['price']}, hely: {row['location']}, terület: {row['sqm']}"
        
if __name__ == "__main__":
    infer = InferenceEngine()
    print(
        infer.inference(
        """
        21. kerületben, Csepelen az Orion utca mellett kiadó egy 1. emeleti, erkélyes, igényesen felújított tégla lakás, két fő részére.
36 nm-es, 1 szobás, kiváló az elrendezése.
Fűtése konvektoros fűtéses.
Bútorozott, a konyha beépített gépekkel felszerelt, így ezekre már nincs gond.
A lakás világos és tágas erkéllyel is rendelkezik, ennek köszönhetően jól átszellőztethető.
Rengeteg busz megáll a közelben, valamint boltok, gyógyszertár, éttermek és rengeteg kiszolgáló egység is üzemel a környéken.
Csendes környezet, parkosított övezet.
Közös költség: 12.600 Ft/hó.
Bérleti díja 130 000 Ft/hó + rezsi.
Ingyen parkolási lehetőség is adott a ház előtt.
Háziállat a lakásban nem tartható és a dohányzás is csak a lakáson kívül megengedett akár az erkélyen.
Hosszútávra kiadó, minimum egy évre, megbízható bérlőknek!
Akár azonnal be is költözhető.
Előre megbeszélt időpontban megtekinthető.

A kép tájékoztató jellegű, (illusztráció) a változtatás jogát az iroda fenn tartja!
Garantáltan ellenőrzött lakások!
Ha ilyen és ehhez hasonló ingatlanok érdeklik akkor hívjon vagy jöjjön be irodánkba!

IRODÁNK CÍME
Albérlet neked! 6. kerület Oktogon Teréz krt. 21. fsz. 28. kaputelefon.
Nyitva tartás : H-CS: 8-17ig P: 8-16ig Szombat: 9-12ig
        """
    ))