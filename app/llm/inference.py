import openai
# import re
# import huspacy
# import spacy


# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class InferenceEngine():
    # nlp = spacy.load("hu_core_news_lg")
    # def __init__(self):
    #     #huspacy.download() #FIXME
    #     pass

    # def inference(self, text):
    #     text = "summarize: " + self.text_block_preprocessor(text)

    #     tokenizer = AutoTokenizer.from_pretrained("./alberlet_model_save")
    #     inputs = tokenizer(text, return_tensors="pt").input_ids

    #     model = AutoModelForSeq2SeqLM.from_pretrained("./alberlet_model_save")
    #     outputs = model.generate(inputs, max_new_tokens=100, do_sample=False)

    #     return tokenizer.decode(outputs[0], skip_special_tokens=True)
    

    # def preprocessor(self, word):
    #     if type(word) == str:
    #         word = re.sub(r'[^\w\s]', '', word)
    #         word = re.sub(r'<[^>]*>', '', word)
    #         word = re.sub(r'<[0-9]*>', '', word)
    #         word = re.sub(r'[\W]+', '', word)
    #         return word

    # def word_processor(self, line):
    #     tokens = InferenceEngine.nlp(line)
    #     words = []

    #     for token in tokens:
    #         if token.is_stop == False:
    #             token_preprocessed = self.preprocessor(token.lemma_)
    #             if token_preprocessed != '':
    #                 words.append(token_preprocessed)
    #     return (words)

    # def text_block_preprocessor(self,text):

    #     make_sentences = InferenceEngine.nlp(text)

    #     sentences_lemmata_list = [sentence.lemma_.lower() for sentence in make_sentences.sents]

    #     these_processed_sentences = ''

    #     for item in sentences_lemmata_list:
    #         words = self.word_processor(item)
    #         line = ' '.join(words)
    #         these_processed_sentences += (' ' + line)

    #     return these_processed_sentences

    # def create_summary(row):
    #     return f"bérleti díj: {row['price']}, hely: {row['location']}, terület: {row['sqm']}"

    def __init__(self):
        self.model="gpt-3.5-turbo"
        self.client = openai.OpenAI()

    def inference(self, text):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Act as a real estate salesman with 15+ years of experience with selling apartments in Budapest."},
                {"role": "user", "content": 
                """I will give you a real estate advert for an apartment for rent. You will extract the most important features of the apartment and provide it this format:
                Rent price: <rent price>

                Location: <location of the apartment> 

                SQM: <square meters>, <number of rooms> 

                Common costs: <common cost> 

                Methods of transportation: <public transportation opportunities> 

                Availability: <when can you move in and whats the downpayment> 

                Recommended for: <what kind of person would like this place and why> 

                Pros: <pros of the apartment>

                Cons: <cons of the apartment>

                If you cannot extract information about a specific feature then write N/A as value.
                """
                },
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
