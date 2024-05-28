import openai


class InferenceEngine():
    model="gpt-3.5-turbo"
    client = openai.OpenAI()

    @classmethod
    def inference(cls, text):
        response = cls.client.chat.completions.create(
            model= cls.model,
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
