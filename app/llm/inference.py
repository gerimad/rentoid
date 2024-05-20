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